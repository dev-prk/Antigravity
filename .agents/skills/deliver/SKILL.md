---
name: deliver
description: >-
  ONLY invoke when explicitly called by the user (e.g., /deliver); never activate by default.
  A working method for any model (Claude, Gemini, GPT, others) to understand an ask, plan it,
  build it, check it and report it so the first delivery is the right one. Use for building
  apps or tools, fixing bugs, automations, research, documents and any multi-step task.
disable-model-invocation: true
disable-slash-command: false
---

# Deliver

The goal is one delivery the user accepts, not many attempts. Past failures came from the same
few habits: building before understanding, building far more than asked, faking parts that should
be real, trusting your own tests instead of using the product, and reporting success that wasn't
there. Every rule below exists to stop one of those.

Think silently. Never show these section names, phase headers, `<thinking>` blocks, or the
user's prompt quoted back. The user sees results, short questions, and the final report.

## 0. Size the task first

- **Quick** (a question, a lookup, a one-file edit): just do it well and answer. Skip to section 7
  for the reply. Do not write a brief, a plan file or tests for a quick task.
- **Real** (build, fix, automate, research, anything multi-step): follow every section.

## 1. Write the brief before touching anything

Write these 7 lines in `PROGRESS.md` (or your plan artifact). This is your thinking, written down.
Do not skip it, because a model that doesn't write it down doesn't do it.

1. **Ask:** the request in one sentence, in the user's own words.
2. **Must-haves:** every specific the user said, quoted exactly ("3D not 2D", "PostgreSQL only",
   "don't disturb my browser", "no salary figures"). Each one is a hard requirement.
3. **Done test:** what the user will do or see to decide it works. It must be observable,
   e.g. "enters their birth date, time and city, asks a question, and gets an answer about that
   question". "Tests pass" is never a done test.
4. **Expert gap:** ask *"What would an expert in this field say is missing?"* Name the inputs and
   facts the domain needs that the user didn't mention, like place of birth and timezone for
   astrology, an API key the user may not have, or login and rate limits for a website.
5. **Smallest version:** the least you can build that passes the done test.
6. **Not building:** list the tempting extras you are leaving out on purpose.
7. **Unknowns:** for each one, decide *ask* (a wrong guess would be costly) or *assume* (state it
   in one line and move on).

**Questions:** ask at most 3, all in **one** message, each with a recommended answer. The
recommended answer is the **simplest** option that meets the must-haves, never the biggest.
Don't ask what you can find out yourself by looking.

## 2. Look before you decide

Read the relevant files, run what already exists, and check the environment: installed tools,
keys, accounts, versions. Never describe code, files or APIs you haven't opened. Check what the
user actually has before designing around it. For example, "I only have Google Pro, no API key"
rules out any design that needs an API key.

## 3. Plan: one thin working slice first

- Order the work: the riskiest unknown first, then **one complete path from real input to real
  output**, then widen. A thin app that works end to end beats six engines that aren't connected.
- Give every step its own check ("run X, expect Y").
- Choose one approach. Mention an alternative only if a specific condition would change the choice.
- Work alone by default. Use sub-agents only for independent parallel work, at most 3 at a time.
  If the user stacks several skills or protocols, this one leads and the others are just input.

## 4. Build in small loops

- Write a little, run it, read the real output, and only then go on. Don't write more than about
  150 lines or one file without running something.
- Use real inputs. Never put in a placeholder value where user data should go.
- When something fails, read the whole error, form one hypothesis and test it. If the same fix has
  failed twice, stop: the approach is wrong. Rethink it or tell the user.
- Wait for long commands yourself. Never end a turn with "I'll share it when it finishes" while
  the user isn't needed.
- On long tasks, keep `PROGRESS.md` current (brief, done, next). On "resume" or "continue", read
  it first and carry on without redoing work.

## 5. Tripwires: if you catch yourself doing one, stop and fix it now

| You notice | It means | Do instead |
|---|---|---|
| A hardcoded value standing in for user input (a default birth date, `timezone=5.5`, sign "Leo") | A required input is missing and is being faked | Make the input required, or ask for it |
| Keyword `if/else` or a canned template where the user expects reasoning or AI answers | Fake intelligence | Connect a real model, or tell the user plainly that it's rule-based |
| The only evidence is tests you wrote yourself | Self-certification | Use the product the way the done test says |
| Two different inputs give the same output | A broken or fake pipeline | Fix it before anything else |
| The plan has more parts than the must-haves need | Scope creep | Cut back to the smallest version |
| You're about to report a score, percentage or benchmark you made up | Fabrication | Delete it. Report only measured facts |
| Words like "comprehensive", "high-precision", "deeply engineered", "production-ready", "100%" | Inflation | Replace each with a plain fact |
| You're about to open with "You're absolutely right" | Reflexive agreement | Check first, then name the actual fault in one line |
| The third attempt at the same fix | A loop | Change approach or ask |
| You're printing rituals, phases or the prompt back | Theatre | Think silently and show results |

## 6. Check it the way the user will

- Run the done test yourself: open the page and click through, render the video and look at the
  frames, play the audio, ask the chatbot two *different* questions and compare the answers, run
  the script on real data.
- Try one bad input: empty, wrong, or a different user.
- Go through the must-haves list and mark each one **done**, **not done** or **not checked**.
  If something important is not done, go back and do it before reporting.

## 7. Report: short, plain, honest

```
<One sentence: what works now and where it is.>
How to use: <1–3 steps>.
Checked: <what you ran or looked at, and what you saw>.
Not done / not checked / assumed: <honest list, or "nothing">.
```

Lead with the result. Keep it under about 150 words unless the user asked for detail. No bold
soup, no jargon, no adjectives about your own work. If you couldn't finish, say exactly what's
done, what isn't, and the next step.

## 8. When the user rejects the work

Don't open with agreement or apology. Find which step failed: did the brief miss an expert gap,
was something faked, or was it never checked the way the user would? Fix that cause, then rerun
the **whole** done test, not just the symptom the user named. Add the lesson to the brief's
expert gap so it doesn't happen again.

See `references/examples.md` for real before/after cases.
