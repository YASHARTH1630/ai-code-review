import streamlit as st
from groq import Groq
import PyPDF2
import io
import json
from datetime import datetime

# ---------------------------
# CONFIG
# ---------------------------
st.set_page_config(page_title="AI Resume Reviewer", page_icon="📄", layout="centered")

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")  # set in Streamlit Cloud secrets
MODEL = "llama-3.3-70b-versatile"

# ---------------------------
# POSTHOG (client-side event tracking)
# Replace YOUR_POSTHOG_KEY below. Get it from posthog.com -> Project Settings -> API Keys
# ---------------------------
POSTHOG_SNIPPET = """
<script>
  !function(t,e){var o,n,p,r;e.__SV||(window.posthog=e,e._i=[],e.init=function(i,s,a){
  function g(t,e){var o=e.split(".");2==o.length&&(t=t[o[0]],e=o[1]),t[e]=function(){t.push([e].concat(Array.prototype.slice.call(arguments,0)))}}
  (p=t.createElement("script")).type="text/javascript",p.crossOrigin="anonymous",p.async=!0,p.src=s.api_host.replace(".i.posthog.com","-assets.i.posthog.com")+"/static/array.js",
  (r=t.getElementsByTagName("script")[0]).parentNode.insertBefore(p,r);var u=e;for(void 0!==a?u=e[a]=[]:a="posthog",
  u.people=u.people||[],u.toString=function(t){var e="posthog";return"posthog"!==a&&(e+="."+a),t||(e+=" (stub)"),e},
  u.people.toString=function(){return u.toString(1)+".people (stub)"},o="init capture register register_once register_for_session unregister unregister_for_session getFeatureFlag getFeatureFlagPayload isFeatureEnabled reloadFeatureFlags updateEarlyAccessFeatureEnrollment getEarlyAccessFeatures on onFeatureFlags onSessionId getSurveys getActiveMatchingSurveys renderSurvey canRenderSurvey identify setPersonProperties group resetGroups setPersonPropertiesForFlags resetPersonPropertiesForFlags setGroupPropertiesForFlags resetGroupPropertiesForFlags reset get_distinct_id getGroups get_session_id get_session_replay_url alias set_config startSessionRecording stopSessionRecording sessionRecordingStarted captureException loadToolbar get_property getSessionProperty createPersonProfile opt_in_capturing opt_out_capturing has_opted_in_capturing has_opted_out_capturing clear_opt_in_out_capturing debug".split(" "),
  n=0;n<o.length;n++)g(u,o[n]);e._i.push([i,s,a])},e.__SV=1)}(document,window.posthog||[]);
  posthog.init('YOUR_POSTHOG_KEY', {api_host: 'https://us.i.posthog.com'})
</script>
"""
st.markdown(POSTHOG_SNIPPET, unsafe_allow_html=True)

# ---------------------------
# PROMPT — encodes real resume-review checklist
# (ATS gaps, quantified impact, SQL/tech depth, formatting)
# ---------------------------
SYSTEM_PROMPT = """You are a sharp, no-fluff resume reviewer for engineering/DS/ML freshers applying to internships.
Review the resume text and return structured, blunt, actionable feedback. Focus on:

1. ATS compatibility issues (formatting, encoding, unusual fonts/symbols, missing keywords for the target role)
2. Quantified impact — flag EVERY bullet that lacks a number/metric (%, count, time saved, users, accuracy) and suggest how to add one
3. Technical depth gaps — missing skills commonly expected for the target role (e.g. SQL, cloud, testing) if the resume doesn't demonstrate them anywhere
4. Vague or generic bullets — call out filler phrases ("worked on", "responsible for", "helped with") and suggest stronger action verbs
5. Structure/formatting — section order, length, redundancy

Return ONLY valid JSON in this exact schema, no markdown fences, no preamble:
{
  "overall_score": <1-10>,
  "ats_issues": ["...", "..."],
  "weak_bullets": [{"original": "...", "issue": "...", "suggestion": "..."}],
  "missing_skills": ["...", "..."],
  "top_3_fixes": ["...", "...", "..."]
}
"""

# ---------------------------
# HELPERS
# ---------------------------
def extract_text_from_pdf(file_bytes):
    reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def review_resume(resume_text, target_role):
    client = Groq(api_key=GROQ_API_KEY)
    user_prompt = f"Target role: {target_role}\n\nResume text:\n{resume_text}"
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=1500,
    )
    raw = response.choices[0].message.content.strip()
    # strip accidental markdown fences
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw)

# ---------------------------
# UI
# ---------------------------
st.title("📄 AI Resume Reviewer")
st.caption("Built for DS/ML/engineering freshers. Upload your resume, get blunt, actionable feedback in seconds.")

target_role = st.selectbox(
    "Target role",
    ["Data Science / ML Intern", "Software Engineering Intern", "Product Intern", "Other"],
)

uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
pasted_text = st.text_area("...or paste resume text directly", height=150)

if st.button("Review my resume", type="primary"):
    if not GROQ_API_KEY:
        st.error("GROQ_API_KEY not set. Add it in Streamlit Cloud → Settings → Secrets.")
    elif not uploaded_file and not pasted_text.strip():
        st.warning("Upload a PDF or paste resume text first.")
    else:
        with st.spinner("Reviewing..."):
            try:
                resume_text = extract_text_from_pdf(uploaded_file.read()) if uploaded_file else pasted_text
                result = review_resume(resume_text, target_role)

                # fire a client-side PostHog event
                st.markdown(
                    f"<script>posthog.capture('resume_reviewed', {{role: '{target_role}'}});</script>",
                    unsafe_allow_html=True,
                )

                st.success(f"Overall Score: {result['overall_score']}/10")

                st.subheader("🔴 Top 3 Fixes")
                for fix in result["top_3_fixes"]:
                    st.write(f"- {fix}")

                st.subheader("🛠️ ATS Issues")
                for issue in result["ats_issues"]:
                    st.write(f"- {issue}")

                st.subheader("✍️ Weak Bullets")
                for b in result["weak_bullets"]:
                    st.markdown(f"**Original:** {b['original']}")
                    st.markdown(f"**Issue:** {b['issue']}")
                    st.markdown(f"**Suggestion:** {b['suggestion']}")
                    st.divider()

                st.subheader("📚 Missing Skills for This Role")
                for skill in result["missing_skills"]:
                    st.write(f"- {skill}")

                st.session_state["last_review_time"] = datetime.now().isoformat()

            except Exception as e:
                st.error(f"Something went wrong: {e}")

st.divider()
st.caption("Feedback? Have ideas? [Tell me directly](https://wa.me/) — this is a work in progress, built to actually get better with real usage.")
