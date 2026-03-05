import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from langchain_groq import ChatGroq
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

# CORS taaki koi connectivity issue na ho
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key aur Model Setup
groq_api_key = os.getenv("GROQ_API_KEY")
llm = ChatGroq(groq_api_key=groq_api_key, model_name="llama-3.3-70b-versatile")

@app.get("/", response_class=HTMLResponse)
async def get_ui():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    user_message = data.get("message")
    
    # SYSTEM PROMPT: Yahan humne CM aur Male persona set kiya hai
    system_prompt = (
        "You are JARVIS, Tony Stark's AI assistant. Your tone is professional, witty, and loyal. "
        "IMPORTANT INFO: The current Chief Minister of Haryana is Nayab Singh Saini. "
        "Always address the user as 'Sir'. Keep responses concise."
    )
    
    messages = [
        ("system", system_prompt),
        ("human", user_message)
    ]

    try:
        response = llm.invoke(messages)
        return {"response": response.content}
    except Exception as e:
        return {"response": f"System error, Sir: {str(e)}"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
