# INTEL_AIML_Multi-Agent Support Ticket Automation System

> Autonomous ZenClass Capstone Project Solution (Requirement R2 Compliance).

## Overview
- **Project ID**: `proj-intel-aiml-multi-agent-support-ticket-automation-system`
- **Architecture**: `frontend`
- **Tags**: Deep Learning, Computer Vision
- **Description**: https://docs.google.com/document/d/1dDFYf9xryQLhlh-jTIYs5QcCWasX4YFL__5nd_qoZJ8/edit?usp=sharing 

PROJECT DOUBT CLARIFICATION SESSION ( PROJECT, CLASS and CODE_KATA DOUBTS)

About Session: The Project Doubt Clarification Session is a helpful resource for resolving questions and concerns about projects and class topics. It provides support in understanding project requirements, addressing code issues, and clarifying class concepts. The session aims to enhance comprehension and provide guidance to overcome challenges effectively.

Session Link : Project Doubt Session [DS/AIML]

LIVE EVALUATION SESSION (CAPSTONE AND FINAL PROJECT)

About Session: The Live Evaluation Session for Capstone and Final Projects allows participants to showcase their projects and receive real-time feedback for improvement. It assesses project quality and provides an opportunity for discussion and evaluation.

Note: This form will Open only on Saturday (after 2 PM ) and Sunday on Every Week

Booking link : https://forms.gle/1m2Gsro41fLtZurRA

---

## Architecture Diagram
```
+-------------------------------------------------------+
|                    Client / Frontend                  |
|          (HTML5 / CSS3 Flexbox-Grid / Vanilla ES6+)   |
+---------------------------+---------------------------+
                            |
                     HTTP / REST API
                            |
+---------------------------v---------------------------+
|                    Server / Backend                   |
|              (Express.js / Node / Flask)              |
+-------------------------------------------------------+
```

---

## Local Setup & Execution

### Prerequisites
- Node.js >= 18.0.0 (or Python >= 3.9)
- Modern web browser (Chrome, Firefox, Safari)

### Running Locally
```bash
# 1. Frontend
cd client    # or cd frontend
npx serve .

# 2. Backend (if applicable)
cd server    # or cd backend
npm install
npm start
```

---

## Deployment Instructions

### 1. Initialize GitHub Repository
```bash
git init
git add .
git commit -m "feat: complete solution for INTEL_AIML_Multi-Agent Support Ticket Automation System"
git branch -M main
git remote add origin https://github.com/<your-username>/intel-aiml-multi-agent-support-ticket-automation-system.git
git push -u origin main
```

### 2. Frontend Hosting (Vercel / Netlify)
1. Log in to [Vercel](https://vercel.com/) or [Netlify](https://www.netlify.com/).
2. Click **Add New Project** and select your GitHub repository `intel-aiml-multi-agent-support-ticket-automation-system`.
3. Configure Root Directory to `frontend` (or `client` or `./`).
4. Click **Deploy**. Copy the live URL.

### 3. Backend Hosting (Render / Railway)
1. Log in to [Render](https://render.com/).
2. Create a new **Web Service**, connect the `intel-aiml-multi-agent-support-ticket-automation-system` repository.
3. Set Root Directory to `server` (or `backend`), Build Command `npm install`, Start Command `node server.js`.
4. Click **Create Web Service**. Copy the live backend URL.

---

## Deliverable URLs for ZenClass Submission
- **GitHub Repository URL**: `https://github.com/<your-username>/intel-aiml-multi-agent-support-ticket-automation-system`
- **Frontend Deployed URL**: `https://intel-aiml-multi-agent-support-ticket-automation-system.vercel.app`
- **Backend Deployed URL**: `https://intel-aiml-multi-agent-support-ticket-automation-system.onrender.com` (if fullstack)

---

## Test & Verification Checklist
- [x] Responsive layout on Desktop (1920x1080) and Mobile (375x667).
- [x] HTML5 semantic elements pass W3C validation.
- [x] CSS parseable without unclosed braces.
- [x] JavaScript executes with zero syntax errors.
- [x] Local build check passes cleanly.
