import google.generativeai as ai
import pyttsx3
from google import genai
import speech_recognition as sr
import customtkinter as ctk
from PIL import Image, ImageTk, ImageSequence
import threading
import datetime
import webbrowser
import os
import pyaudio
stop_speaking = False
engine = None

ai.configure(api_key="AIzaSyAZ_l661dLBBaQuBPrQPxjQWPmJWic4pDI")
model = ai.GenerativeModel(model_name="gemini-3-flash-preview")     
chat = model.start_chat()

engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)
recognizer = sr.Recognizer()

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("NEXA - An AI-Powered Personal Voice Assistant")
root.geometry("980x650+350+20")

title_label = ctk.CTkLabel(root, text="NEXA", font=("Comic Sans MS", 35, "bold"))
title_label.place(relx=0.5, rely=0.04, anchor="center")

gif_path = "pp.gif"
gif = Image.open(gif_path)
frames = [ImageTk.PhotoImage(frame.convert("RGBA")) for frame in ImageSequence.Iterator(gif)]


frame_index = 0

canvas = ctk.CTkCanvas(root, width=500, height=500, bd=0, highlightthickness=0)
canvas.place(relx=0.21, rely=0.15, anchor="n")
bg_label = canvas.create_image(0, 0, anchor="nw", image=frames[0])

def update_gif():
    global frame_index
    frame_index = (frame_index + 1) % len(frames)
    canvas.itemconfig(bg_label, image=frames[frame_index])
    root.after(100, update_gif)

root.after(100, update_gif)

chat_frame = ctk.CTkScrollableFrame(root, width=480, height=390, fg_color="black")
chat_frame.place(x=470, rely=0.15)

entry = ctk.CTkEntry(root, width=430, placeholder_text="Type your message...")
entry.place(x=490, y=520)

def speak(text):
    global stop_speaking
    stop_speaking = False
    engine = pyttsx3.init()

    sentences = text.strip().split('.')
    limited_sentences = [s.strip() for s in sentences if s.strip()][:4]
    limited_text = '. '.join(limited_sentences) + '.'

    try:
        engine.say(limited_text)
        engine.runAndWait()
    except RuntimeError:
        pass

def handle_commands(command):
    command = command.lower()

    if "open youtube" in command:
        webbrowser.open("https://www.youtube.com")
        return "Opening YouTube"

    elif "open google" in command:
        webbrowser.open("https://www.google.com")
        return "Opening Google"

    elif "open whatsapp" in command:
        webbrowser.open("https://web.whatsapp.com")
        return "Opening WhatsApp"

    elif "open notepad" in command:
        try:
            os.system("notepad.exe")
            return "Opening Notepad"
        except:
            return "Unable to open Notepad."

    elif "time" in command or "what's the time" in command:
        now = datetime.datetime.now().strftime("%I:%M %p")
        return f"The current time is {now}"
    
    elif "day" in command or "date" in command:
        today = datetime.datetime.now().strftime("Today is %A, %d %B, %Y")
        return today
    
    elif "stop" in command:
        global stop_speaking
        stop_speaking = True
        try:
          engine.stop()
        except:
            pass
        return "Okay, speech stopped!"
    
    elif "resume" in command:
        stop_speaking=False
        return"Yay! I'm back to speaking"

    return None

def add_chat(name, message):
    if name.lower()=="you":
        label = ctk.CTkLabel(chat_frame, text=f"{name}:\n{message}",
                         anchor="e", justify="right", wraplength=300, font=("Arial", 14))
        label.pack(anchor="e", padx=13, pady=5,fill="x")
    else:
        label = ctk.CTkLabel(chat_frame, text=f"{name}:\n{message}",
                         anchor="w", justify="left", wraplength=300, font=("Arial", 14))
        label.pack(anchor="w", padx=13, pady=5,fill="x")

def get_response(event=None):
    user_input = entry.get().strip()
    if not user_input:
        return
    add_chat("You", user_input)
    entry.delete(0, "end")

    command_response = handle_commands(user_input)
    if command_response:
        add_chat("NEXA", command_response)
        threading.Thread(target=speak, args=(command_response,)).start()
        return

    try:
        response = chat.send_message(user_input).text
    except Exception:
        response = "Oh nooo! NEXA is tired! Try again in a bit."

    add_chat("NEXA", response)
    threading.Thread(target=speak, args=(response,)).start()

def get_voice_input():
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.8)
            add_chat("NEXA", "Listening... please speak clearly")
            try:
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=7)
            except sr.WaitTimeoutError:
                add_chat("NEXA", "No speech detected within 10 seconds. Please try again.")
                return
            try:
                text = recognizer.recognize_google(audio)
                add_chat("NEXA", f"Heard: {text}")
                entry.delete(0, "end")
                entry.insert(0, text)
                get_response()
            except sr.UnknownValueError:
                add_chat("NEXA", "Sorry! I didn't understand that.")
            except sr.RequestError:
                add_chat("NEXA", "Speech service unavailable. Check your network.")
    except OSError:
        add_chat("NEXA", "Microphone not found. Please check your device.")

send_button = ctk.CTkButton(root, text="Send", command=get_response)
send_button.place(x=490, y=570)

voice_button = ctk.CTkButton(root, text="Speak", command=lambda: threading.Thread(target=get_voice_input, daemon=True).start())
voice_button.place(x=710, y=570)

def auto_greet():
    welcome_text = "Hello there! How can I help you today?"
    add_chat("NEXA", welcome_text)
    threading.Thread(target=speak, args=(welcome_text,), daemon=True).start()

auto_greet()
root.mainloop()