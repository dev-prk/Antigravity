# Before / after: real cases from this workspace

## 1. "Make me a plan for a chat and a website chatbot" (astrology + palmistry + others)

**What went wrong:** The agent asked 9 separate questions, one after another, and every
"(Recommended)" option was the biggest one. It built 6 "engines", a claim ledger, a
cross-validator and a model router. Place of birth was missing and the timezone was hardcoded to
5.5. The "AI" chat was keyword if/else that returned the same 6-section block for every question.
It reported "architected, deeply engineered, and verified" because pytest passed on tests it had
written itself. The user's verdict: "absolute garbage."

**With this skill:**
- Brief: Done test = "a person enters birth date, time and **city**, uploads a palm photo, asks
  their own question, and gets an answer to *that* question". Expert gap = birthplace → lat/lon →
  historical timezone/DST, an unknown birth time, and an LLM key (the user has none). Smallest
  version = one page and one chart calculation, a palm read and one LLM answer. Not building =
  numerology, vastu, tarot, multi-profile vault.
- One message with 2 questions: "Which disciplines for v1? (recommended: astrology + palmistry
  only)" and "Do you have an API key? (recommended: free AI Studio key, I'll show you how)".
- Check: ask two different questions and confirm the answers differ and are about each question.

## 2. "Make the animation 3D, not 2D, and the voice natural for kids"

**What went wrong:** The earlier output was flat 2D with a robotic system voice, and the agent's
reports were "launched the render, I will share when it finishes" turns.

**With this skill:** The must-haves are quoted: "3D", "natural", "kid-friendly". Before reporting,
extract frames and look at them (is it actually 3D?), play the audio (is it a neural voice?), and
wait for the render instead of ending the turn.

## 3. "Create a skill that makes any model behave like Claude" with /plan /teamwork /goal

**What went wrong:** The agent spawned about 180 sub-agents, gates and "victory audits", wrote 198
tests and invented scores ("CCRS +68.4%, 100% win rate"). It used up the quota, and the skill it
produced made the model print a `<claude_thinking> PHASE 1: CONSTRAINT ANCHORING` ritual to the
user on every message.

**With this skill:** One agent. Done test = "a weaker model given a real task delivers it in one
go". Smallest version = one short SKILL.md. Check = run it on a real task and read what comes out.
No made-up metrics.

## 4. User: "adding salary figures is not the best idea"

**What went wrong:** The agent had added salary figures to the job profiles without questioning it.

**With this skill:** The expert gap catches it early: recruiters advise against putting salary in
a public profile. Raise it in the brief as an *ask*, with the recommended answer "leave it out".

## 5. "Paste my resume and a JD, tell me how well I match and what to fix"

**What went wrong (first test of this skill):** The agent did look first and wrote a good brief.
It even confirmed that a working Gemini key existed. Then it built a 640-line regex "DBA domain
engine" as the core, with the LLM as "optional", and wrote the user's own strengths and canned
advice into the code as constants. A pastry chef's resume scored a "projected 89/100 after
fixes". The JD's "8+ years" wasn't parsed. It ended the turn with "I will report the verification
results as soon as the browser check completes."

**With this skill:** The model does the matching and rewriting, since a key exists. Code only
extracts text, sends both documents, and shows a structured answer. The resume comes only from
what's pasted. Contrast test: the user's real resume against a matching JD and an unrelated
resume against the same JD. The second must score low and get no tailored DBA bullets. Wait for
the browser check, then report.
