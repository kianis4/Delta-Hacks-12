import os
import operator
import json
from typing import TypedDict, Annotated, Sequence, List, Optional
from enum import Enum
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import BaseMessage, AIMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_mongodb import MongoDBAtlasVectorSearch
# from langchain_voyageai import VoyageAIEmbeddings
from dotenv import load_dotenv
import certifi
from pymongo import MongoClient
from pydantic import BaseModel, Field
try:
    from agent.tools import find_official_form, find_lawyer_referral
except ImportError:
    from tools import find_official_form, find_lawyer_referral


load_dotenv()

# --- Data Models (Gemini Structured Output) ---

class UserIntent(str, Enum):
    ADVICE = "ADVICE"
    DRAFT = "DRAFT"
    FORM = "FORM"
    CLARIFY = "CLARIFY"
    OFF_TOPIC = "OFF_TOPIC"
    ASK_JURISDICTION = "ASK_JURISDICTION"

class LegalTopic(str, Enum):
    TENANCY = "TENANCY"
    FAMILY = "FAMILY"
    IMMIGRATION = "IMMIGRATION"
    EMPLOYMENT = "EMPLOYMENT"
    CRIMINAL = "CRIMINAL" # Now Supported
    TAX = "TAX"           # Now Supported
    BUSINESS = "BUSINESS" # Now Supported (Corps, etc.)
    OTHER_LEGAL = "OTHER_LEGAL"
    NON_LEGAL = "NON_LEGAL"

class RouterOutput(BaseModel):
    detected_jurisdiction: Optional[str] = Field(
        description="The jurisdiction detected from the user input (e.g., 'ON', 'BC', 'AB'). Return null if not explicitly mentioned or inferred."
    )
    intent: UserIntent = Field(
        description="The determined intent of the user based on their input and history."
    )
    topic: LegalTopic = Field(
        description="The legal topic classification.",
        default=LegalTopic.TENANCY
    )
    legal_issue: str = Field(
        description="A brief 1-sentence summary of the user's legal issue."
    )
    missing_info_question: Optional[str] = Field(
        description="A specific clarification question if intent is CLARIFY or ASK_JURISDICTION."
    )

class Option(BaseModel):
    label: str = Field(description="Button label text")
    action: str = Field(description="Action ID or value")
    description: Optional[str] = Field(description="Tooltip or extra detail")

class ResponseOutput(BaseModel):
    explanation: str = Field(
        description="The main body of the response, including direct answers, drafting text, or helpful explanations. Use Markdown."
    )
class Citation(BaseModel):
    source_title: str = Field(description="The name of the Act or Document (include Jurisdiction).")
    quote: str = Field(description="The exact verbatim text quoted from the source.")
    url: Optional[str] = Field(description="Direct URL to the source document if available in context.", default=None)

class ResponseOutput(BaseModel):
    explanation: str = Field(
        description="The main body of the response, including direct answers, drafting text, or helpful explanations. Use Markdown."
    )
    citations: List[Citation] = Field(
        description="List of relevant legal citations with quotes and URLs.",
        default_factory=list
    )
    options: List[Option] = Field(
        description="List of actionable options/buttons for the user.",
        default_factory=list
    )

# --- State Definition ---
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    jurisdiction: Optional[str]
    legal_issue: Optional[str]
    user_intent: str
    relevant_laws: List[str]
    draft: str # Used for clarification questions or drafts
    debug_logs: List[dict]

# --- LLM Setup ---
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", temperature=0)

# --- Helpers ---
def get_db_connection():
    try:
        # Explicitly configure SSL for Railway/Linux environments
        client = MongoClient(
            os.getenv("MONGODB_URI"), 
            tls=True,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=5000
        )
        return client["juris_db"]["legal_docs"]
    except Exception as e:
        print(f"DB Connection Error: {e}")
        return None

def get_embeddings():
    return GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

# --- Nodes ---

def router_node(state: AgentState):
    """
    Analyzes conversation to extract jurisdiction and intent using Structured Outputs.
    """
    messages = state['messages']
    current_jur = state.get('jurisdiction')
    logs = state.get('debug_logs', [])
    
    # Configure LLM for Router Output
    structured_llm = llm.with_structured_output(RouterOutput)
    
    # Get last few messages for context
    # We explicitly provide system instructions here
    system_prompt = f"""You are a Smart Legal Assistant Router.
    
    CURRENT STATE:
    - Known Jurisdiction: {current_jur if current_jur else "UNKNOWN"}
    
    TASK: Analyze the conversation to determine Jurisdiction, Intent, and Issue.
    
    JURISDICTION LOGIC:
    - If 'Known Jurisdiction' is SET (ON/BC/AB), keep it unless user EXPLICITLY changes it.
    - If 'Known Jurisdiction' is UNKNOWN, try to detect it in input.
    - If still UNKNOWN after checking input and history, intent MUST be 'ASK_JURISDICTION'.
    
    INTENT CATEGORIES:
    - ADVICE: User asks a legal question.
    - DRAFT: User asks to write/draft a document.
    - FORM: User asks for a specific form.
    - CLARIFY: Request is vague/unclear.
    - OFF_TOPIC: Not about law (e.g. recipes, weather).
    - ASK_JURISDICTION: You need to know where they are.
    
    TOPIC CLASSIFICATION:
    - TENANCY: Landlord/Tenant issues (RTA).
    - FAMILY: Divorce, custody, support.
    - IMMIGRATION: Visas, refugee, citizenship.
    - EMPLOYMENT: Wages, severance, dismissal.
    - CRIMINAL: Shoplifting, assault, DUI, Criminal Code.
    - TAX: Income tax, CRA, GST/HST.
    - BUSINESS: Corporations, incorporation, partnerships.
    - OTHER_LEGAL: Personal Injury, Intellectual Property (We do NOT have these).
    - NON_LEGAL: Chitchat.
    
    CRITICAL RULE:
    - If Topic is OTHER_LEGAL (e.g. IP Law), we CANNOT help. Set intent to OFF_TOPIC.
    - If Topic is NON_LEGAL, set intent to OFF_TOPIC.
    
    OUTPUT:
    Return a valid RouterOutput object.
    """
    
    try:
        # Invoke with system prompt + history
        # We wrap messages to ensure correct format
        input_msgs = [SystemMessage(content=system_prompt)] + messages[-5:]
        result: RouterOutput = structured_llm.invoke(input_msgs)
        
        updates = {
            "user_intent": result.intent.value,
            "legal_issue": result.legal_issue,
            "topic": result.topic.value,
            "debug_logs": logs + [{"node": "router", "result": result.model_dump()}]
        }
        
        # Heuristic: If we detected a new jurisdiction, update.
        if result.detected_jurisdiction:
            updates["jurisdiction"] = result.detected_jurisdiction
        
        # Store the question if we need to ask it
        if result.missing_info_question:
            updates["draft"] = result.missing_info_question
            
        print(f"ROUTER: Intent={result.intent.value}, Topic={result.topic.value}, Jur={updates.get('jurisdiction', current_jur)}")
        return updates
        
    except Exception as e:
        print(f"Router Error: {e}")
        # Fallback safe mode
        return {
            "user_intent": "CLARIFY",
            "draft": "I encountered an error analyzing your request. Could you rephrase?",
            "debug_logs": logs + [{"node": "router_error", "error": str(e)}]
        }

def research_node(state: AgentState):
    """
    Queries vector store if intent allows.
    """
    intent = state.get("user_intent")
    
    # Skip research for non-substantive intents
    if intent in ["CLARIFY", "ASK_JURISDICTION", "OFF_TOPIC"]:
        return {"relevant_laws": []}
    
    issue = state.get("legal_issue", "")
    jurisdiction = state.get("jurisdiction", "ON")
    
    print(f"RESEARCH: Searching '{issue}' in '{jurisdiction}'")
    
    # --- Tool Dispatch Logic ---
    
    # 1. Form Search
    if intent == "FORM":
        # Extract form name from issue (heuristic or use LLM extraction, simplify for now)
        # In a real app, Router should extract 'form_name'
        form_result = find_official_form(issue, jurisdiction)
        return {"relevant_laws": [form_result]}

    # 2. Lawyer/Professional Finder (Heuristic: "find a lawyer", "hire help")
    # If the user explicitly asks for representation, we skip Vector DB and go to Referral.
    trigger_words = ["lawyer", "paralegal", "help me find", "directory", "referral", "representation"]
    if any(w in issue.lower() for w in trigger_words):
        # Attempt to extract a more specific location from the issue text
        # Simple heuristic: Look for common cities or just pass the issue if it's short
        # Better: Use the LLM to extract "Specific Location" in the Router, but for now:
        search_location = jurisdiction or "Ontario"
        
        # If the issue mentions a specific city, append it to the search
        # This is a basic improvement. In a real app, we'd use an NER entity extractor.
        # Let's trust the tool's search flexibility.
        
        referral_result = find_lawyer_referral(search_location, state.get("topic", "General"))
        
        # Add a specific city-based search if analyzing the text reveals one (Quick Regex or list)
        # For Hackathon: Just let the user's "in Toronto" flow through if we pass the whole issue?
        # The tool currently takes 'location'.
        # Let's try to pass the 'issue' context to the tool if it seems to contain a location.
        if " in " in issue:
            # "Lawyer in Toronto" -> split
            try:
                potential_loc = issue.split(" in ")[1].split()[0].strip("?.")
                if len(potential_loc) > 3:
                     search_location = f"{potential_loc}, {jurisdiction}"
            except:
                pass

        referral_result = find_lawyer_referral(search_location, state.get("topic", "General"))
        return {"relevant_laws": [referral_result]}

    # 3. Vector DB Search (Standard Path)
    try:
        col = get_db_connection()
        if col is None: 
            return {"relevant_laws": ["Error: Database connection failed."]}
        
        vstore = MongoDBAtlasVectorSearch(col, get_embeddings(), index_name="vector_index")
        
        # Filter by Topic + Jurisdiction
        if jurisdiction and jurisdiction != "General":
            # Include specific jurisdiction AND Federal laws
            filter_query = {"jurisdiction": {"$in": [jurisdiction, "FEDERAL"]}}
        else:
            filter_query = {}
        
        results = vstore.similarity_search(issue, k=3, pre_filter=filter_query)
        
        # Map filenames to Official URLs (Hack fix for ingestion missing URLs)
        SOURCE_URL_MAP = {
            "ontario_rta.html": "https://www.ontario.ca/laws/statute/06r17",
            "criminal_code.xml": "https://laws-lois.justice.gc.ca/eng/acts/C-46/",
            "income_tax.xml": "https://laws-lois.justice.gc.ca/eng/acts/I-3.3/",
            "excise_tax.xml": "https://laws-lois.justice.gc.ca/eng/acts/E-15/",
            "immigration.xml": "https://laws-lois.justice.gc.ca/eng/acts/I-2.5/"
        }
        
        laws = []
        for d in results:
            src = d.metadata.get('source', 'Unknown')
            # Use metadata URL or fallback to the hardcoded map
            url = d.metadata.get('url') or SOURCE_URL_MAP.get(src, "")
            
            txt = d.page_content[:1500]
            laws.append(f"Source: {src}\nURL: {url}\nContent: {txt}")
            
        if not laws:
            laws = ["No specific legal documents found."]
            
        return {"relevant_laws": laws}
        
    except Exception as e:
        print(f"Research Error: {e}")
        return {"relevant_laws": [f"Error searching database: {e}"]}

def response_generator_node(state: AgentState):
    """
    Generates final response specific to the intent.
    """
    intent = state.get("user_intent")
    jurisdiction = state.get("jurisdiction")
    
    # 1. Handle ASK_JURISDICTION manually or with helper
    if intent == "ASK_JURISDICTION":
        msg = state.get("draft") or "To help you better, I need to know your location. Which province are you in?"
        payload = {
            "explanation": msg,
            "citations": [],
            "options": [
                {"label": "Ontario", "action": "Ontario", "description": "ON"},
                {"label": "British Columbia", "action": "British Columbia", "description": "BC"},
                {"label": "Alberta", "action": "Alberta", "description": "AB"}
            ]
        }
        return {"messages": [AIMessage(content=json.dumps(payload))]}

    # 2. General Case using Structured Output
    structured_llm = llm.with_structured_output(ResponseOutput)
    
    prompt = f"""You are a Senior Legal Assistant.
    
    CONTEXT:
    - Intent: {intent}
    - Jurisdiction: {jurisdiction}
    - Issue: {state.get('legal_issue')}
    - Research: {state.get('relevant_laws')}
    
    TASK: Generate a helpful, formatted response.
    
    1. IF CLARIFY: Ask the specific clarification question politely.
    2. IF OFF_TOPIC: Politely decline.
    3. IF ADVICE: Explain the law, reference research, and give next steps.
    4. IF DRAFT: Write the document text in the 'explanation' field.
    5. IF FORM: Provide form name and context.
    6. IF REFERRAL/DIRECTORY: If research contains links to directories or referral services, DISPLAY THEM. Do not refuse.
    
    IMPORTANT INSTRUCTIONS FOR CITATIONS:
    - You MUST populate the 'citations' list with exact 'source_title', 'quote', and 'url'.
    - Look at the 'Research' context provided above. It has 'Source', 'URL', and 'Content'.
    - EXTRACT the 'URL' field for each law you reference.
    - EXTRACT a brief verbatim 'Quote' that supports your advice.
    
    IMPORTANT: 'options' should be buttons for likely user next steps.
    
    SPECIAL HANDLING:
    - If user asks about OTHER_LEGAL (Topic=OTHER_LEGAL), politely decline.
    - If Research says "No specific documents found" and topic is supposedly covered, advise checking official government sites.
    """
    
    try:
        input_msgs = [SystemMessage(content=prompt)] + state['messages'][-5:]
        result: ResponseOutput = structured_llm.invoke(input_msgs)
        
        # Convert Pydantic to Dict for JSON serialization in Message Content
        # The frontend expects a JSON string
        response_dict = result.model_dump()
        
        return {"messages": [AIMessage(content=json.dumps(response_dict))]}
        
    except Exception as e:
        print(f"Generator Error: {e}")
        err_payload = {"explanation": "I'm having trouble generating a response right now.", "citations": [], "options": []}
        return {"messages": [AIMessage(content=json.dumps(err_payload))]}

# --- Graph Construction ---
workflow = StateGraph(AgentState)

workflow.add_node("router", router_node)
workflow.add_node("research", research_node)
workflow.add_node("generator", response_generator_node)

workflow.set_entry_point("router")

workflow.add_edge("router", "research")
workflow.add_edge("research", "generator")
workflow.add_edge("generator", END)

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)
