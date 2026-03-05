import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from langchain_groq import ChatGroq
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

groq_api_key = os.getenv("GROQ_API_KEY")
llm = ChatGroq(groq_api_key=groq_api_key, model_name="llama-3.3-70b-versatile")

@app.get("/", response_class=HTMLResponse)
async def get_ui():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    user_message = data.get("message").lower()
    
    # Updated System Prompt for 2 paragraphs and main points
    system_prompt = (
        "You are JARVIS, made by Tejas Munjal. "
        "Rule 1: Never exceed 2 paragraphs in your response. "
        "Rule 2: Always provide information with main points (bullet points). "
        "Rule 3: No 'Sir'. Be direct. "
        "Rule 4: You can provide live information like cricket scores as you have real-time access."
    )
    
    messages = [("system", system_prompt), ("human", user_message)]

    try:
        response = llm.invoke(messages)
        return {"response": response.content}
    except Exception as e:
        return {"response": f"System error: {str(e)}"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
