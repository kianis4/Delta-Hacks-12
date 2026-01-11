from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import uuid
try:
    from agent.agent_graph import app as agent_app
    from agent.pdf_service import generate_legal_pdf
except ImportError:
    # Fallback if running directly or path issues
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from agent.agent_graph import app as agent_app
    from agent.pdf_service import generate_legal_pdf
from langchain_core.messages import HumanMessage

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow Vercel deployments
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
            # Use the actual message content (JSON) instead of the plain text summary
            last_msg_content = final_state["messages"][-1].content
            return {
                "response": last_msg_content,
                "legal_issue": "Additional Info Required",
                "draft": None,
                "debug_info": final_state.get("debug_logs", [])
            }
        
        # Extract the last message content
        return {
            "response": final_state["messages"][-1].content,
            "legal_issue": final_state.get("legal_issue"),
            "draft": final_state.get("draft"),
            "debug_info": final_state.get("debug_logs", [])
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "ok"}

class PDFRequest(BaseModel):
    text: str

@app.post("/generate-pdf")
async def generate_pdf(request: PDFRequest):
    try:
        filename = f"draft_{uuid.uuid4()}.pdf"
        filepath = os.path.join(os.getcwd(), filename)
        
        generate_legal_pdf(request.text, filepath)
        
        return FileResponse(filepath, media_type='application/pdf', filename="Legal_Notice_Draft.pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
