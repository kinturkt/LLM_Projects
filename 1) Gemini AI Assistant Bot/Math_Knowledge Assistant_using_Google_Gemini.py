import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
import speech_recognition as sr

# Load environment variables from .env file
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

# Check if the API key was loaded
if not gemini_api_key:
    st.sidebar.error("API key not found! Please ensure your .env file contains the GEMINI_API_KEY variable.")
    st.stop()

# Configure the Gemini API client with the API key
genai.configure(api_key=gemini_api_key)

# Set up the Streamlit page
st.set_page_config(page_title="Gemini AI Math & Knowledge Assistant", layout="wide")
st.markdown("<h1 style='text-align: center; color: #ff6600; font-size: 42px; font-weight: bold;'>Gemini AI Math & Knowledge Assistant</h1>", unsafe_allow_html=True)

# Define a helper function to generate responses using Google Gemini
def generate_response(prompt, model_name="gemini-2.0-flash"):  # Use a valid model name
    try:
        model = genai.GenerativeModel(model_name)  # Initialize the model
        response = model.generate_content(prompt)  # Generate response
        return response.text.strip() if response.text else "No response generated."
    except Exception as e:
        return f"Error: {e}"

# Initialize session state for chat history and current query index
if "history" not in st.session_state:
    st.session_state["history"] = [{
        "role": "assistant",
        "content": "Hello! I'm your AI-powered knowledge assistant, capable of solving mathematical challenges, clarifying complex ideas, and conducting in-depth research. What would you like to learn or solve?"
    }]

if "current_query" not in st.session_state:
    st.session_state["current_query"] = "A car travels 150 km in 3 hours. It then increases its speed and covers another 200 km in 2 hours. What was the average speed of the car for the entire journey?"  # Default question for first query

# Sidebar for reset chat, download chat history, and voice input instructions

# Chat history download section
st.sidebar.write("*Chat history can be downloaded as a text file for future reference.*")
chat_text = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in st.session_state["history"]])
st.sidebar.download_button("Download Chat History", chat_text, file_name="chat_history.txt", key="download_chat_btn")

# Voice input instructions and button section
st.sidebar.write("🎤 **Voice Input Instructions:** Speak your question clearly and concisely for best results.")

if st.sidebar.button("Use Voice Input", key="voice_input_btn_sidebar"):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.sidebar.write("Listening... Speak your question.")
        try:
            audio = recognizer.listen(source, timeout=5)  # Adjust timeout as needed
            spoken_input = recognizer.recognize_google(audio)  # Convert speech to text using Google Speech Recognition API
            st.sidebar.success(f"You said: {spoken_input}")
            st.session_state["current_query"] = spoken_input.strip()  # Update current query with voice input
            st.rerun()  # Refresh to process voice input immediately
        except sr.UnknownValueError:
            st.sidebar.error("Sorry, I couldn't understand what you said. Please try again.")
        except sr.RequestError as e:
            st.sidebar.error(f"Could not request results; {e}")

# Reset Chat button in sidebar (optional)
if st.sidebar.button("Reset Chat", key="reset_chat_btn"):
    st.session_state["history"] = [{
        "role": "assistant",
        "content": "Hello! I'm here to help solve math problems and perform research. How can I help you today?"
    }]
    st.session_state["current_query"] = "A car travels 150 km in 3 hours. It then increases its speed and covers another 200 km in 2 hours. What was the average speed of the car for the entire journey?"  # Reset to default question
    st.rerun() 

# Display chat history dynamically in main content area
for message in st.session_state["history"]:
    role = message["role"]
    content = message["content"]
    if role == "assistant":
        st.chat_message(role).write(f"<span style='font-size: 18px;'>{content}</span>", unsafe_allow_html=True)
    else:
        st.chat_message(role).write(f"<span style='font-size: 18px;'>{content}</span>", unsafe_allow_html=True)

# Text area for user input (only one active at a time)
user_input = st.text_area(
    "Enter your question or problem:",
    value=st.session_state["current_query"],  # Use current_query from session state (default question or empty string)
    height=100,
)

# Submit button for the current query text box
if st.button("Submit Query"):
    user_input = user_input.strip()
    
    if user_input:
        # Add user input to chat history
        st.session_state["history"].append({"role": "user", "content": user_input})
        st.chat_message("user").write(f"<span style='font-size: 18px;'>{user_input}</span>", unsafe_allow_html=True)

        with st.spinner("Processing your request..."):
            response = generate_response(user_input)

        # Add assistant's response to chat history
        st.session_state["history"].append({"role": "assistant", "content": response})
        st.chat_message("assistant").write(f"<span style='font-size: 18px;'>{response}</span>", unsafe_allow_html=True)

        # Clear current query after processing and refresh UI for next question (ensure empty box appears)
        st.session_state["current_query"] = ""  # Reset current query to empty string explicitly after submission
        st.rerun()