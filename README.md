# AI Resume Reviewer

An AI-powered resume reviewer built for DS/ML/engineering freshers. Upload a resume, get blunt, structured feedback in seconds — ATS issues, weak bullets, missing skills, and top fixes. Built with Streamlit + Groq (`llama-3.3-70b-versatile`).

**Live demo:** 👉 _[ADD YOUR STREAMLIT LINK HERE]_ 👈

**GitHub:** `YASHARTH1630/ai-resume-reviewer`

---

## What This Is

Freshers applying to DS/ML/SWE internships rarely get specific, actionable feedback on their resumes — most rejections are silent, and generic advice ("add more keywords") doesn't fix the real issues: unquantified bullets, ATS-breaking formatting, or missing role-relevant skills. This tool runs a resume through an LLM-driven checklist and returns a structured breakdown in under 10 seconds.

---

## Setup — Local

**1. Install dependencies**
```bash
pip install -r requirements.txt
```

**2. Add your Groq API key**

Create a file at `.streamlit/secrets.toml`:
```toml
GROQ_API_KEY = "your_groq_key_here"
```
Get a free key at [console.groq.com/keys](https://console.groq.com/keys) (under 2 minutes, no card needed).

**3. Run it**
```bash
streamlit run app.py
```
Opens at `localhost:8501`.

---

## Deploy (Streamlit Community Cloud — free)

1. Push this repo to GitHub: `YASHARTH1630/ai-resume-reviewer`
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app** → connect the repo → set entry point to `app.py`
3. Under **Settings → Secrets**, paste:
   ```toml
   GROQ_API_KEY = "your_groq_key_here"
   ```
4. Click **Deploy**. You'll get a public URL like `ai-resume-reviewer.streamlit.app` — that's your live demo link. Add it to the top of this file and to your application email.

---

## Analytics (PostHog)

Already wired into `app.py` — just needs your key.

1. Sign up free at [posthog.com](https://posthog.com)
2. **Project Settings → Project API Key** → copy it
3. In `app.py`, find `YOUR_POSTHOG_KEY` inside the `posthog.init(...)` line and replace it with your real key
4. Push the change — Streamlit Cloud auto-redeploys
5. Share the live link with 20–30 people (hall groups, DS/ML communities, LinkedIn)
6. After 24–48 hours, screenshot your PostHog dashboard: total visits → resumes reviewed. That funnel screenshot is your proof of product analytics for the application.

---

## Prompt Eval

A lightweight eval to show the model actually works, not just that it runs.

| Resume Sample | Expected Issue | Caught? (Y/N) | Notes |
|---|---|---|---|
| Own resume (old draft) | Vague bullets, no SQL, no metrics | | |
| Friend's resume | ATS-breaking formatting (tables/columns) | | |
| Friend's resume #2 | Missing quantified impact | | |
| ... 5–7 more samples ... | | | |

Run 8–10 samples through the app, check what it catches vs. misses, and note:
- Whether output stays consistent across repeated runs at `temperature=0.3`
- Any JSON parsing failures
- One fix you'd make (e.g. few-shot examples, lower temperature) — this is your eval "finding" for the application.

---

## Case Study (for the application)

- **Problem:** Freshers get generic or no feedback on resumes; ATS rejections are silent, and common issues (no quantified impact, missing role-specific skills, formatting that breaks parsers) go uncaught.
- **What I built:** A Groq-powered resume reviewer, live at [your link] — checks ATS compatibility, flags every unquantified bullet with a rewrite suggestion, and surfaces missing role-relevant skills.
- **PLG angle for scaling to 1 lakh users:** Shareable score card as a referral loop (fresher shares "7/10, here's what I'm fixing" → drives their peers to try it), campus ambassador seeding across engineering colleges, LinkedIn embed of the score.
- **Analytics:** PostHog funnel — visits → resumes uploaded → feedback generated → shared. [insert screenshot]
- **Eval learnings:** [fill in after running your eval — 1-2 sentences]
- **What's next:** Mobile version; backlog — cover letter review, resume version diffing (before/after score), role-specific scoring presets (DS vs SWE vs Product).

---

## Tech Stack

| Layer | Tool |
|---|---|
| UI | Streamlit |
| LLM | Groq API — `llama-3.3-70b-versatile` |
| PDF parsing | PyPDF2 |
| Analytics | PostHog |

**Customize:** Edit `SYSTEM_PROMPT` in `app.py` to change what the reviewer checks for, or add options to `target_role` for more role types.
