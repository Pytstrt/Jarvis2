import os
import pywhatkit, webbrowser, asyncio, edge_tts, time
import psutil 
import threading
import uvicorn
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pygame import mixer
import nest_asyncio
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

# Async support for edge_tts
nest_asyncio.apply()

# --- CONFIGURATION ---
VOICE_ID = "en-US-ChristopherNeural"
BOT_NAME = "jarvis"
# Render Dashboard se API Key uthayega, varna ye default use karega
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# --- INITIALIZE GROQ AI ---
llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model="llama-3.3-70b-versatile",
    temperature=0.4
)

latest_data = {"user": "Ready...", "jarvis": "Online", "status": "online"}

# --- VOICE FUNCTION (Safe for Cloud) ---
def speak(text):
    print(f"Jarvis: {text}")
    # Render (Cloud) par speaker nahi hota, isliye wahan ise skip karenge
    if os.environ.get("RENDER"):
        return

    path = "temp/voice.mp3"
    if not os.path.exists("temp"): os.makedirs("temp")
    
    async def gen():
        await edge_tts.Communicate(text, VOICE_ID, rate="+15%").save(path)
    
    try:
        if mixer.get_init(): mixer.quit()
        asyncio.run(gen())
        mixer.init()
        mixer.music.load(path)
        mixer.music.play()
        while mixer.music.get_busy(): time.sleep(0.1)
        mixer.music.unload()
        mixer.quit()
    except Exception as e:
        print(f"Voice Error (Non-Critical): {e}")

def get_ai_response(user_input):
    global latest_data
    try:
        messages = [
            SystemMessage(content="You are JARVIS. Be brief, witty, and call the user Sir. You are created by Tejas Sir."),
            HumanMessage(content=user_input)
        ]
        response = llm.invoke(messages)
        latest_data["jarvis"] = response.content
        return response.content
    except Exception:
        return "Sir, the neural link is unstable."

# --- MIC ENGINE (Bypassed on Render) ---
def jarvis_mic_engine():
    # Render par Mic libraries install nahi hoti, isliye ye sirf Local par chalega
    try:
        import speech_recognition as sr
        print("🎤 Local Mic System: Initializing...")
        
        while True:
            try:
                r = sr.Recognizer()
                with sr.Microphone() as s:
                    r.adjust_for_ambient_noise(s, duration=0.8)
                    audio = r.listen(s, timeout=None, phrase_time_limit=6)
                    query = r.recognize_google(audio, language='en-in').lower()
                    latest_data["user"] = query
                    
                    if BOT_NAME in query:
                        clean_cmd = query.replace(BOT_NAME, "").strip()
                        if "play" in clean_cmd:
                            song = clean_cmd.replace("play", "").strip()
                            speak(f"Playing {song}")
                            pywhatkit.playonyt(song)
                        elif "open" in clean_cmd:
                            site = clean_cmd.replace("open", "").strip()
                            webbrowser.open(f"https://www.{site}.com")
                        else:
                            answer = get_ai_response(clean_cmd)
                            speak(answer)
            except Exception:
                continue
    except Exception as e:
        print(f"Mic System not available: {e}")

# --- FASTAPI ENDPOINTS ---

@app.get("/")
async def root():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return {"status": "Jarvis Backend is Live", "message": "Tejas Sir, upload index.html for UI."}

@app.get("/chat")
async def chat(message: str = Query(...)):
    response = get_ai_response(message)
    return JSONResponse({"jarvis": response})

@app.get("/status")
async def status():
    return JSONResponse(latest_data)

# --- STARTUP LOGIC ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    
    # Check if running on Cloud or Local
    if not os.environ.get("RENDER"):
        # Local laptop par mic chalu karo
        t = threading.Thread(target=jarvis_mic_engine, daemon=True)
        t.start()
    
    print(f"💎 JARVIS ACTIVE ON PORT {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)