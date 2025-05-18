import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import re

# Load environment variables
load_dotenv()

# Set up Gemini API key
GEMINI_API_KEY = os.getenv("YOUR_YOUTUBE_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

def get_video_id(url_link):
    match = re.search(r"(?:v=|youtu.be/)([\w-]+)", url_link)
    return match.group(1) if match else None

def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([entry['text'] for entry in transcript])
    except (TranscriptsDisabled, NoTranscriptFound):
        return None
    except Exception as e:
        return f"Error fetching transcript: {str(e)}"

def clean_transcript(text):
    fillers = [r"\blike\b", r"\bum\b", r"\buh\b", r"\bokay\b", r"\bso\b", r"\byou know\b", r"\bi mean\b"]
    pattern = re.compile("|".join(fillers), flags=re.IGNORECASE)
    cleaned = pattern.sub("", text)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def summarize_with_gemini(transcript_text, prompt_type="default"):
    if prompt_type == "prompt-1":
        prompt = ("You are a YouTube video summarizer. Generate a title based on the video's main topic or keywords. "
                    "Then, generate subtitles or sections followed by a detailed summary in each section within 400 words.\n\nTranscript: \n")
    elif prompt_type == "prompt-2":
        prompt = ("Summarize the following YouTube transcript into 5-7 concise bullet points. Emphasize action steps, key insights, or tips shared. "
                    "Avoid filler language and keep the output structured and informative.\n\nTranscript: \n")
    elif prompt_type == "flashcards":
        prompt = ("You are a flashcard generator. Read the following YouTube transcript and generate at least 5 flashcards in the format:\n\n"
                    "Q: <Question based on key idea>\nA: <Short, correct answer>\n\nTranscript: \n")
    elif prompt_type == "quiz":
        prompt = ("You are a quiz generator. Read the following YouTube transcript and create a short quiz of 5 multiple-choice questions. "
                    "Each question should include 1 correct answer and 3 plausible distractors.\n\nTranscript: \n")
    else:
        prompt = ("You are a YouTube video summarizer. Please summarize the transcript below into bullet points "
                    "within 400 words, highlighting the key takeaways and insights.\n\nTranscript: \n")

    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt + transcript_text)
    return response.text

def main():
    st.title("🎥 YouTube Video Summarizer (Powered by Gemini)")
    st.write("Enter a YouTube video URL to extract and summarize its content.")

    url = st.text_input("YouTube Video URL")
    prompt_type = st.selectbox("Choose Output Type:", ("default", "prompt-1", "prompt-2", "flashcards", "quiz"))

    if url:
        video_id = get_video_id(url)
        if not video_id:
            st.error("Invalid YouTube URL")
            return

        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_container_width=True)

        with st.spinner("Fetching transcript..."):
            transcript = get_transcript(video_id)

        if transcript:
            st.subheader("Transcript Preview")
            st.text_area("Transcript (first 1000 characters):", transcript[:1000], height=200)

            if st.button("Generate Output with Gemini"):
                with st.spinner("Generating with Gemini..."):
                    cleaned = clean_transcript(transcript)
                    output = summarize_with_gemini(cleaned, prompt_type=prompt_type)
                    st.subheader("📘 Output")
                    st.write(output)
        else:
            st.warning("Transcript not available for this video.")

if __name__ == "__main__":
    main()