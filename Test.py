import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from langchain_groq import ChatGroq
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

# CORS settings taaki browser se request block na ho
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key load karna (Jo aapne Render dashboard par daali hai)
groq_api_key = os.getenv("GROQ_API_KEY")
model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# ChatGroq Setup
llm = ChatGroq(groq_api_key=groq_api_key, model_name=model_name)

@app.get("/", response_class=HTMLResponse)
async def get_ui():
    # Ye aapki index.html file ko load karega
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    user_message = data.get("message")
    
    if not user_message:
        return {"response": "Sir, mujhe kuch sunai nahi diya."}

    # AI se jawab mangna
    try:
        response = llm.invoke(user_message)
        return {"response": response.content}
    except Exception as e:
        return {"response": f"Error: {str(e)}"}

if __name__ == "__main__":
    # Local testing ke liye (Render par ye command dashboard se chalti hai)
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
