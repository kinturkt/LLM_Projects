import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import json

# Load the .env variables
load_dotenv()

# Configure the Gemini API
try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
except Exception as e:
    st.error(f"Failed to configure Gemini API: {e}. Ensure GOOGLE_API_KEY is set.")
    st.stop()

# --- Helper Functions ---

def get_gemini_response(prompt_text, purpose="evaluation"):
    """
    Calls the Gemini API with the formatted prompt and requests JSON output.
    """
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(
            prompt_text,
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json"
            )
        )
        return response.text
    except Exception as e:
        st.error(f"Error calling Gemini API for {purpose}: {e}")
        return None

def input_pdf_text(uploaded_file):
    """
    Extracts text from the uploaded PDF file.
    """
    try:
        reader = pdf.PdfReader(uploaded_file)
        text = ""
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            page_text = page.extract_text()
            if page_text:
                text += page_text
        if not text:
            st.warning("Could not extract any text from the PDF. The PDF might be image-based, empty, or corrupted.")
        return text
    except Exception as e:
        st.error(f"Error reading or parsing PDF: {e}")
        return None

# --- Prompt Templates ---

input_prompt_template = """
You are a highly sophisticated AI-powered Application Tracking System (ATS) with specialized expertise in evaluating resumes for roles in the tech industry, including software engineering, data science, data analysis, and big data engineering. Your primary goal is to provide a comprehensive evaluation of the submitted resume against the provided job description. The job market is highly competitive, so your feedback must be precise, actionable, and aimed at significantly improving the candidate's chances.

**Resume Analysis Task:**

Based on the provided resume text and job description (JD), perform the following analysis:

1.  **Job Description (JD) Match Percentage:** Calculate a percentage (as a string, e.g., "85%") representing how well the resume matches the requirements outlined in the JD.
2.  **Resume Strengths:** Identify 2-4 key strengths of the resume when compared against the JD.
3.  **Missing Keywords & Skill Gaps:** Identify 3-5 critical keywords and skills from the JD that are missing or not sufficiently highlighted in the resume. For each, provide a brief, actionable suggestion on how the candidate might address this.
4.  **Areas for Resume Improvement (General):** Provide 2-3 actionable pieces of advice beyond just keywords (e.g., for structure, clarity, or impact).
5.  **Action Verb Usage:** Evaluate the action verbs used in the resume's experience section. Are they strong and impactful? Provide general feedback. If specific improvements are identifiable, list up to 3 suggestions, noting the original phrase/verb and the suggested stronger alternative. If usage is already strong, acknowledge it.
6.  **Quantification of Achievements:** Assess how well the resume quantifies achievements and responsibilities using numbers, data, or specific metrics. Provide general feedback and suggest 2-3 specific areas or phrases where quantification could be added or improved to demonstrate impact. If quantification is already well-utilized, acknowledge it.
7.  **ATS Format Friendliness:** Evaluate the resume's general structure and formatting for typical ATS parsability. Provide a qualitative score (e.g., "Excellent", "Good", "Fair", "Needs Improvement") and brief feedback (1-2 sentences).
8.  **Optimized Profile Summary:** Craft a concise and impactful profile summary (2-3 sentences) that a recruiter would find compelling, highlighting the candidate's most relevant skills and experiences tailored to the JD.

**Output Format:**

Provide your entire response as a single, valid JSON string. The JSON object must strictly adhere to the following structure:

{{
    "JD Match": "string",
    "ResumeStrengths": ["string"],
    "MissingKeywordsAndGaps": [
    {{"keyword": "string", "suggestion": "string"}}
    ],
    "AreasForImprovement": ["string"],
    "ActionVerbAnalysis": {{
    "Feedback": "string",
    "Suggestions": [
    {{"original": "string", "suggestion": "string"}}
    ] /* Empty array if no specific suggestions */
    }},
    "QuantificationAnalysis": {{
    "Feedback": "string",
    "Suggestions": ["string"] /* Empty array if no specific suggestions, or examples of phrases that could be quantified */
    }},
    "ATSFormatFeedback": {{
    "Score": "string",
    "Feedback": "string"
    }},
    "OptimizedProfileSummary": "string"
}}

**Input Data:**

Resume Text:
{text}

Job Description:
{jd}

Ensure high accuracy. Be factual and constructive.
"""

cover_letter_prompt_template = """
Based on the following resume text and job description, generate 2-3 distinct, concise, and impactful snippets that the candidate could use in their cover letter. These snippets should highlight the candidate's key qualifications from the resume that directly match the requirements in the job description. Focus on creating compelling sentences that bridge the resume to the job.

Alternatively, you can generate a strong opening paragraph (3-4 sentences) for the cover letter.

Output the result as a simple JSON string: {{"cover_letter_suggestions": ["suggestion1", "suggestion2", ...]}}

Resume Text:
{text}

Job Description:
{jd}
"""

# --- Streamlit App UI ---

st.set_page_config(layout="wide", page_title="Gemini Powered Smart ATS System")

# Initialize session state variables if they don't exist
if 'resume_text_for_cl' not in st.session_state:
    st.session_state.resume_text_for_cl = None
if 'jd_for_cl' not in st.session_state:
    st.session_state.jd_for_cl = None
if 'cover_letter_response' not in st.session_state:
    st.session_state.cover_letter_response = None
if 'ats_evaluation_done' not in st.session_state:
    st.session_state.ats_evaluation_done = False

# --- Main App Layout ---
st.title("🚀 Gemini Powered Smart ATS System")
st.markdown("Evaluate your resume against job descriptions and get actionable feedback to stand out!")
st.markdown("---")

# --- Input Column ---
col1, col2 = st.columns([0.4, 0.6], gap="large")

with col1:
    st.header("📝 Provide Job Details")
    jd_input = st.text_area("Paste the Job Description (JD) here:", height=300, placeholder="Enter the full job description...")
    uploaded_file = st.file_uploader(
        "📁 Upload Your Resume (PDF only):",
        type="pdf",
        help="Please upload your resume in PDF format only. Other formats are not supported and will not be processed."
    )
    submit_button = st.button("✨ Evaluate My Resume", type="primary", use_container_width=True)

# --- Output Column ---
with col2:
    st.header("📊 ATS Evaluation Results")

    if submit_button:
        st.session_state.ats_evaluation_done = False
        st.session_state.cover_letter_response = None

        if not os.getenv("GOOGLE_API_KEY"):
            st.error("API Key not configured. Please set the GOOGLE_API_KEY environment variable.")
        elif uploaded_file is not None and jd_input:
            with st.spinner("📄 Extracting text from PDF..."):
                resume_text_extracted = input_pdf_text(uploaded_file)

            if resume_text_extracted:
                # Store for potential cover letter generation
                st.session_state.resume_text_for_cl = resume_text_extracted
                st.session_state.jd_for_cl = jd_input

                with st.spinner("🧠 Analyzing resume with Gemini AI... This may take a moment."):
                    formatted_prompt = input_prompt_template.format(text=resume_text_extracted, jd=jd_input)
                    response_text = get_gemini_response(formatted_prompt, purpose="resume evaluation")

                if response_text:
                    try:
                        response_json = json.loads(response_text)
                        st.session_state.ats_evaluation_done = True

                        # --- Displaying Results ---
                        st.subheader("🎯 Job Description Match")
                        jd_match_str = response_json.get('JD Match', '0%')
                        try:
                            jd_match_val = int(jd_match_str.replace('%', ''))
                            st.progress(jd_match_val / 100.0)
                            st.metric(label="Match Percentage", value=f"{jd_match_val}%")
                        except ValueError:
                            st.warning(f"Could not parse JD Match percentage: {jd_match_str}")
                            st.write(f"**JD Match:** {jd_match_str}")

                        st.subheader("👤 Optimized Profile Summary")
                        summary = response_json.get('OptimizedProfileSummary', 'No summary provided.')
                        st.info(summary if summary else "N/A")

                        tab_titles = [
                            "👍 Strengths", "🔑 Missing Keywords", "💡 Improvements",
                            "🏃 Action Verbs", "🔢 Quantification", "🤖 ATS Format"
                        ]
                        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(tab_titles)

                        with tab1:
                            st.markdown("**Your Resume's Strong Points:**")
                            strengths = response_json.get('ResumeStrengths', [])
                            if strengths:
                                for strength in strengths: st.markdown(f"- {strength}")
                            else: st.markdown("No specific strengths identified.")

                        with tab2:
                            st.markdown("**Keywords/Skills to Emphasize:**")
                            missing = response_json.get('MissingKeywordsAndGaps', [])
                            if missing:
                                for item in missing: st.markdown(f"- **{item.get('keyword', 'N/A')}:** {item.get('suggestion', 'N/A')}")
                            else: st.markdown("No missing keywords or skill gaps identified.")

                        with tab3:
                            st.markdown("**General Suggestions for Enhancement:**")
                            improvements = response_json.get('AreasForImprovement', [])
                            if improvements:
                                for improve in improvements: st.markdown(f"- {improve}")
                            else: st.markdown("No general areas for improvement identified.")

                        with tab4:
                            st.markdown("**Analysis of Action Verb Usage:**")
                            action_verb_data = response_json.get('ActionVerbAnalysis', {})
                            st.write(f"**Feedback:** {action_verb_data.get('Feedback', 'N/A')}")
                            suggestions = action_verb_data.get('Suggestions', [])
                            if suggestions:
                                st.markdown("**Suggestions for Stronger Verbs:**")
                                for sug in suggestions:
                                    st.markdown(f"- Original: *{sug.get('original', 'N/A')}* → Suggested: **{sug.get('suggestion', 'N/A')}**")
                            else:
                                st.markdown("No specific verb suggestions provided, or current usage is strong.")

                        with tab5:
                            st.markdown("**Analysis of Achievement Quantification:**")
                            quant_data = response_json.get('QuantificationAnalysis', {})
                            st.write(f"**Feedback:** {quant_data.get('Feedback', 'N/A')}")
                            quant_suggestions = quant_data.get('Suggestions', [])
                            if quant_suggestions:
                                st.markdown("**Suggestions for Quantification:**")
                                for sug in quant_suggestions:
                                    st.markdown(f"- {sug}")
                            else:
                                st.markdown("No specific quantification suggestions provided, or current usage is strong.")

                        with tab6:
                            st.markdown("**How ATS-Friendly is Your Resume Format?**")
                            ats_feedback = response_json.get('ATSFormatFeedback', {})
                            st.success(f"**Score:** {ats_feedback.get('Score', 'N/A')}")
                            st.write(f"**Feedback:** {ats_feedback.get('Feedback', 'No feedback provided.')}")

                    except json.JSONDecodeError:
                        st.error("Error: The response from the AI (resume evaluation) was not in the expected JSON format.")
                        st.warning("Displaying raw response from AI:")
                        st.text_area("Raw AI Response", response_text, height=200)
                    except Exception as e:
                        st.error(f"An error occurred while processing the resume evaluation response: {e}")
                        st.text_area("Raw AI Response (if available)", response_text if 'response_text' in locals() else "N/A", height=200)
                else:
                    st.error("Failed to get a response from the AI for resume evaluation.")
        elif not uploaded_file:
            st.warning("⚠️ Please upload your resume PDF.")
        elif not jd_input:
            st.warning("⚠️ Please paste the Job Description.")
    else:
        st.info("Fill in the job description, upload your resume, and click 'Evaluate My Resume' to see the analysis here.")

    # --- Cover Letter Snippet Generation Section ---
    if st.session_state.ats_evaluation_done:
        st.markdown("---")
        st.subheader("💌 Cover Letter Assistance")
        if st.button("Generate Cover Letter Snippets", use_container_width=True):
            if st.session_state.resume_text_for_cl and st.session_state.jd_for_cl:
                with st.spinner("✍️ Generating cover letter snippets..."):
                    cl_prompt = cover_letter_prompt_template.format(
                        text=st.session_state.resume_text_for_cl,
                        jd=st.session_state.jd_for_cl
                    )
                    cl_response_text = get_gemini_response(cl_prompt, purpose="cover letter generation")
                    if cl_response_text:
                        try:
                            cl_response_json = json.loads(cl_response_text)
                            st.session_state.cover_letter_response = cl_response_json.get('cover_letter_suggestions', [])
                        except json.JSONDecodeError:
                            st.error("Error: The cover letter response from AI was not valid JSON.")
                            st.text_area("Raw CL Response", cl_response_text, height=100)
                            st.session_state.cover_letter_response = ["Error processing AI response for cover letter."] # Fallback
                        except Exception as e:
                            st.error(f"Error processing cover letter response: {e}")
                            st.session_state.cover_letter_response = ["Error during cover letter generation."] # Fallback
                    else:
                        st.error("Failed to get cover letter snippets from AI.")
                        st.session_state.cover_letter_response = ["Failed to generate snippets."]
            else:
                st.warning("Please evaluate a resume first to enable cover letter snippet generation.")

        if st.session_state.cover_letter_response:
            st.markdown("**Suggested Cover Letter Snippets/Openers:**")
            if isinstance(st.session_state.cover_letter_response, list) and st.session_state.cover_letter_response:
                for snippet in st.session_state.cover_letter_response:
                    st.markdown(f"- {snippet}")
            elif st.session_state.cover_letter_response:
                st.markdown(f"- {st.session_state.cover_letter_response}")
            else:
                st.markdown("No snippets generated yet, or an error occurred.")

st.markdown("---")
st.caption("Powered by Google Gemini | Developed for educational and illustrative purposes.")