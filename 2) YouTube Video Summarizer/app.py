import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import re

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

def get_video_id(url_link):
    match = re.search(r"(?:v=|youtu.be/)([\w-]+)", url_link)
    return match.group(1) if match else None

def get_transcript(video_id):
    try:
        ytt_api = YouTubeTranscriptApi()
        fetched_transcript = ytt_api.fetch(video_id)
        transcript = fetched_transcript.to_raw_data()
        return " ".join([entry['text'] for entry in transcript])
        
    except (TranscriptsDisabled, NoTranscriptFound):
        return None
    except Exception as e:
        error_str = str(e).lower()
        if "blocked" in error_str or "too many requests" in error_str:
            return "BLOCKED_BY_YOUTUBE"
        return f"Error fetching transcript: {str(e)}"

def clean_transcript(text):
    fillers = [r"\blike\b", r"\bum\b", r"\buh\b", r"\bokay\b", r"\bso\b", r"\byou know\b", r"\bi mean\b"]
    pattern = re.compile("|".join(fillers), flags=re.IGNORECASE)
    cleaned = pattern.sub("", text)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def summarize_with_gemini(transcript_text):
    prompt = ("You are a YouTube video summarizer. Please summarize the transcript below into bullet points "
              "within 800 words, highlighting the key takeaways and insights.\n\nTranscript: \n")

    model = genai.GenerativeModel("gemini-2.5-flash")
    
    try:
        response = model.generate_content(prompt + transcript_text)
        return response.text
    except Exception as e:
        error_msg = str(e).lower()
        if "429" in error_msg or "quota" in error_msg:
            return (
                "**Out of Daily Quota:** I have hit my daily limit for the free tier "
                "of Gemini 2.5 Flash (20 requests/day). Please try again tomorrow!"
            )
        elif "404" in error_msg:
            return "**Model Not Found:** The AI model requested does not exist or is not supported."
        else:
            return f"**API Error:** {e}"

def main():
    st.title("YouTube Video Summarizer (Powered by Gemini)")
    st.write("Enter a YouTube video URL to extract and summarize its content.")

    # Group the input and the first button together
    col1, col2 = st.columns([3, 1])
    with col1:
        url = st.text_input("YouTube Video URL", label_visibility="collapsed", placeholder="Paste YouTube link here...")
    with col2:
        fetch_clicked = st.button("Fetch Video")

    if fetch_clicked and url:
        st.session_state.video_url = url

    if "video_url" in st.session_state:
        video_id = get_video_id(st.session_state.video_url)
        
        if not video_id:
            st.error("Invalid YouTube URL. Please check the link and try again.")
            return

        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_container_width=True)

        with st.spinner("Fetching transcript..."):
            transcript = get_transcript(video_id)

        if transcript:
            st.subheader("Transcript Preview")
            st.text_area("Transcript (first 1000 characters):", transcript[:1000], height=200)

            if st.button("Generate a summary response from Gemini"):
                with st.spinner("Generating summary..."):
                    cleaned = clean_transcript(transcript)
                    output = summarize_with_gemini(cleaned)
                    st.subheader("Video Summary")
                    st.write(output)
        else:
            st.warning("Transcript not available for this video. It might not have closed captions enabled.")

if __name__ == "__main__":
    main()
