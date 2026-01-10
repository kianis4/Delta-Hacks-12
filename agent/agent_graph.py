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

# --- LLM Setup ---
llm = ChatGoogleGenerativeAI(model="gemini-3-flash-preview", temperature=0)

# --- Nodes ---

def triage_node(state: AgentState):
    """Determines the legal domain and issue."""
    messages = state['messages']
    last_message = messages[-1]
    
    prompt = f"""
    You are a Legal Triage Agent. Analyze the user's situation and classify it.
    Exract the distinct legal issue (e.g., "Eviction for Personal Use - N12").
    If it's not a legal issue, say "NOT_LEGAL".
    
    User Input: {last_message.content}
    """
    response = llm.invoke(prompt)
    content = response.content
    if isinstance(content, list):
        # Extract text from list of content blocks if needed
        # Gemini 3 might return [{'type': 'text', 'text': '...'}, ...]
        text_parts = [item['text'] for item in content if isinstance(item, dict) and 'text' in item]
        legal_issue = " ".join(text_parts)
    else:
        legal_issue = str(content)
        
    return {"legal_issue": legal_issue}

def get_embeddings():
    return VoyageAIEmbeddings(model="voyage-law-2")

def research_node(state: AgentState):
    """
    Queries MongoDB Atlas Vector Store for laws.
    """
    issue = state.get("legal_issue", "")
    print(f"DEBUG: Researching issue: {issue}")
    
    try:
        embeddings = get_embeddings()
        vector_store = MongoDBAtlasVectorSearch.from_connection_string(
            connection_string=os.getenv("MONGODB_URI"),
            namespace="juris_db.legal_docs",
            embedding=embeddings,
            index_name="vector_index"
        )
        
        # Perform Similarity Search
        # We query for the issue directly
        results = vector_store.similarity_search(issue, k=3)
        
        found_laws = []
        for doc in results:
            source = doc.metadata.get('source', 'Unknown Source')
            content = doc.page_content[:500] + "..." # Truncate for prompt context
            found_laws.append(f"Source: {source}\nContent: {content}")
            
        if not found_laws:
            found_laws = ["No specific case law found in the database. Relying on general legal principles."]
            
    except Exception as e:
        print(f"VECTOR SEARCH FAILED: {e}")
        found_laws = ["Error connecting to Legal Database. Proceeding with general knowledge."]
    
    return {"relevant_laws": found_laws}

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

workflow.add_node("triage", triage_node)
workflow.add_node("research", research_node)
workflow.add_node("drafter", drafter_node)

workflow.set_entry_point("triage")
workflow.add_edge("triage", "research")
workflow.add_edge("research", "drafter")
workflow.add_edge("drafter", END)

app = workflow.compile()

if __name__ == "__main__":
    # Test run
    inputs = {"messages": [HumanMessage(content="My landlord gave me an N12 but I think he just wants to raise the rent.")]}
    for output in app.stream(inputs):
        for key, value in output.items():
            print(f"Finished Node: {key}")
