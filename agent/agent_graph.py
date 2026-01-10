import os
from typing import TypedDict, Annotated, Sequence
import operator
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_voyageai import VoyageAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

# --- State Definition ---
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    legal_issue: str
    relevant_laws: list[str]
    draft: str
    critique: str
    
    # Phase 2: Clarification
    needs_clarification: bool
    needs_clarification: bool
    clarification_question: str
    
    # Phase 3: Jurisdiction
    jurisdiction: str # 'ON', 'BC', 'AB', or 'General'

# --- LLM Setup ---
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", temperature=0)

# --- Nodes ---

def orchestrator_node(state: AgentState):
    """
    Orchestrates the conversation: Analyzes history, extracts intent/jurisdiction, and decides next step.
    """
    messages = state['messages']
    
    # Format conversation history
    chat_history = "\n".join([f"{msg.type}: {msg.content}" for msg in messages])
    
    prompt = f"""
    You are the Brain of a Legal Agent. 
    Analyze the full conversation history to determine the User's Legal Issue and Jurisdiction.
    
    HISTORY:
    {chat_history}
    
    YOUR TASKS:
    1. **Identify Jurisdiction**: ON (Ontario), BC (British Columbia), AB (Alberta), or UNKNOWN.
       - Look for keywords: "Toronto", "Vancouver", "RTB", "N12", etc.
       - If user says "Ontario", that overrides previous unknowns.
       
    2. **Identify Legal Issue**: Summarize the CORE legal problem from the *entire* history.
       - Example History: "My landlord raised rent" -> "Which province?" -> "Ontario"
       - Result Issue: "Rent increase dispute in Ontario" (NOT just "Ontario").
       
    3. **Determine Status**:
       - **CLEAR**: We have both Jurisdiction and a Specific Issue.
       - **CLARIFY**: We are missing Jurisdiction OR the Issue is too vague.
       
    4. **Generate Output**:
       - If CLARIFY: Output "CLARIFY | <Specific Question>"
       - If CLEAR: Output "CLEAR | <Jurisdiction Code> | <Summary of Legal Issue>"
    """
    response = llm.invoke(prompt)
    content = response.content
    
    # Handle Gemini 3 list output
    if isinstance(content, list):
        text_parts = [item['text'] for item in content if isinstance(item, dict) and 'text' in item]
        text_content = " ".join(text_parts)
    else:
        text_content = str(content)
        
    print(f"DEBUG: Orchestrator Decision: {text_content}")
        
    if text_content.startswith("CLEAR"):
        parts = text_content.split("|")
        jurisdiction = parts[1].strip() if len(parts) > 1 else "ON"
        issue = parts[2].strip() if len(parts) > 2 else "General Legal Query"
        return {
            "needs_clarification": False, 
            "jurisdiction": jurisdiction, 
            "legal_issue": issue
        }
    else:
        # Ask question
        question = text_content.split("|")[-1].strip()
        return {
            "needs_clarification": True, 
            "clarification_question": question
        }

def get_embeddings():
    return VoyageAIEmbeddings(model="voyage-law-2")

def research_node(state: AgentState):
    """
    Queries MongoDB Atlas Vector Store for laws.
    """
    issue = state.get("legal_issue", "")
    jurisdiction = state.get("jurisdiction", "ON")
    print(f"DEBUG: Researching issue: {issue} in {jurisdiction}")
    
    try:
        embeddings = get_embeddings()
        vector_store = MongoDBAtlasVectorSearch.from_connection_string(
            connection_string=os.getenv("MONGODB_URI"),
            namespace="juris_db.legal_docs",
            embedding=embeddings,
            index_name="vector_index"
        )
        
        # Perform Similarity Search with Pre-Filtering
        # Syntax depends on langchain version, but filter usually works in kwargs
        filter_query = {"jurisdiction": jurisdiction}
        
        results = vector_store.similarity_search(
            issue, 
            k=3,
            pre_filter=filter_query # Filter by jurisdiction
        )
        
        found_laws = []
        for doc in results:
            source = doc.metadata.get('source', 'Unknown Source')
            content = doc.page_content[:1500] # Increased context window
            found_laws.append(f"Source: {source}\nContent: {content}")
            
        if not found_laws:
            found_laws = ["No specific case law found in the database. Relying on general legal principles."]
            
    except Exception as e:
        print(f"VECTOR SEARCH FAILED: {e}")
        found_laws = ["Error connecting to Legal Database. Proceeding with general knowledge."]
    
    return {"relevant_laws": found_laws}

def explainer_node(state: AgentState):
    """Explains the situation and provides options."""
    issue = state.get("legal_issue")
    laws = state.get("relevant_laws")
    messages = state['messages']
    
    prompt = f"""
    You are a Senior Legal Strategist.
    Issue: {issue}
    Relevant Laws: {laws}
    User Context: {messages[-1].content}
    
    1. **Explain** the legal situation clearly to the user.
    2. **Cite Verbatim**: Quote the specific sections of the laws provided that apply (e.g. "Section 83(1) states..."). Do not paraphrase the law itself.
    3. **Provide Options**: specific, actionable paths forward (e.g. "Option 1: File T6", "Option 2: Negotiate").
    
    RESTRICTION: Do NOT draft a full letter yet. ask the user which option they want to pursue.
    """
    response = llm.invoke(prompt)
    content = response.content
    
    # Handle Gemini 3 list output
    if isinstance(content, list):
        text_parts = [item['text'] for item in content if isinstance(item, dict) and 'text' in item]
        text_content = " ".join(text_parts)
    else:
        text_content = str(content)
        
    ai_message = AIMessage(content=text_content)
    # We map this to 'draft' for now so the UI picks it up without code changes
    return {"draft": text_content, "messages": [ai_message]}

def drafter_node(state: AgentState):
    """Drafts the legal document based on research."""
    issue = state.get("legal_issue")
    laws = state.get("relevant_laws")
    messages = state['messages']
    
    prompt = f"""
    You are an expert Legal Drafter. 
    Issue: {issue}
    Relevant Laws: {laws}
    User Context: {messages[-1].content}
    
    Draft a formal response letter or form content.
    Cite the laws provided. 
    Add a disclaimer at the top.
    """
    response = llm.invoke(prompt)
    content = response.content
    
    # Handle Gemini 3 list output
    if isinstance(content, list):
        text_parts = [item['text'] for item in content if isinstance(item, dict) and 'text' in item]
        draft_text = " ".join(text_parts)
    else:
        draft_text = str(content)
        
    # Create a nice message for the chat history
    ai_message = AIMessage(content=draft_text)
    
    return {"draft": draft_text, "messages": [ai_message]}

# --- Graph Definition ---
workflow = StateGraph(AgentState)

workflow.add_node("orchestrator", orchestrator_node)
workflow.add_node("research", research_node)
workflow.add_node("explainer", explainer_node)

workflow.set_entry_point("orchestrator")

# Conditional Edge
def should_continue(state: AgentState):
    if state.get("needs_clarification"):
        return "end_with_question"
    return "research"

workflow.add_conditional_edges(
    "orchestrator",
    should_continue,
    {
        "end_with_question": END,
        "research": "research"
    }
)

# workflow.add_edge("triage", "research") # Removed
workflow.add_edge("research", "explainer")
workflow.add_edge("explainer", END)

# --- Persistence ---
from langgraph.checkpoint.memory import MemorySaver
memory = MemorySaver()

app = workflow.compile(checkpointer=memory)

if __name__ == "__main__":
    # Test run 1: Vague
    print("--- Test 1: Vague Input ---")
    config = {"configurable": {"thread_id": "test-thread-1"}}
    inputs = {"messages": [HumanMessage(content="My landlord is being mean.")]}
    for output in app.stream(inputs, config=config):
        for key, value in output.items():
            print(f"Finished Node: {key}")
            if key == "clarify":
                print(f"Clarification Result: {value}")

    # Test run 2: Specific
    print("\n--- Test 2: Specific Input ---")
    config = {"configurable": {"thread_id": "test-thread-2"}}
    inputs = {"messages": [HumanMessage(content="I received an N12 notice for personal use.")]}
    for output in app.stream(inputs, config=config):
        for key, value in output.items():
            print(f"Finished Node: {key}")

    # Test run 3: Multi-Turn Context
    print("\n--- Test 3: Multi-Turn (Rent Increase -> Ontario) ---")
    config = {"configurable": {"thread_id": "test-thread-3"}}
    # Turn 1
    print("Turn 1: 'My landlord is raising rent'")
    inputs = {"messages": [HumanMessage(content="My landlord is raising rent")]}
    app.invoke(inputs, config=config)
    
    # Turn 2
    print("Turn 2: 'Ontario'")
    inputs = {"messages": [HumanMessage(content="Ontario")]}
    for output in app.stream(inputs, config=config):
        for key, value in output.items():
            print(f"Finished Node: {key}")
            if key == "orchestrator":
                 print(f"Orchestrator Result: {value}")

