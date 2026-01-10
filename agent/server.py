from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
try:
    from agent.agent_graph import app as agent_app
except ImportError:
    from agent_graph import app as agent_app
from langchain_core.messages import HumanMessage

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    jurisdiction: str = "ON"
    thread_id: str

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        inputs = {"messages": [HumanMessage(content=request.message)]}
        config = {"configurable": {"thread_id": request.thread_id}}
        
        # Debugging: Print current state to verify memory
        print(f"--- Chat Request: {request.thread_id} ---")
        
        # Run the agent with state persistence
        final_state = agent_app.invoke(inputs, config=config)
        
        # Check for clarification
        if final_state.get("needs_clarification"):
            return {
                "response": final_state.get("clarification_question"),
                "legal_issue": "Additional Info Required",
                "draft": None
            }
        
        # Extract the last message content
        return {
            "response": final_state["messages"][-1].content,
            "legal_issue": final_state.get("legal_issue"),
            "draft": final_state.get("draft")
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
