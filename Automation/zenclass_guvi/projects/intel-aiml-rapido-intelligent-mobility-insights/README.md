# INTEL-AIML_Rapido: Intelligent Mobility Insights

> Autonomous ZenClass Capstone Project Solution (Requirement R2 Compliance).

## Overview
- **Project ID**: `proj-intel-aiml-rapido-intelligent-mobility-insights`
- **Architecture**: `fullstack_python`
- **Tags**: Python, EDA, Machine Learning
- **Description**: https://docs.google.com/document/d/1559SQPzB8acwTLk3KDi9NBEZ9eI4AVHAl1T2_ppUJk8/edit?tab=t.0

PROJECT DOUBT CLARIFICATION SESSION ( PROJECT AND CLASS DOUBTS)

About Session: The Project Doubt Clarification Session is a helpful resource for resolving questions and concerns about projects and class topics. It provides support in understanding project requirements, addressing code issues, and clarifying class concepts. The session aims to enhance comprehension and provide guidance to overcome challenges effectively.

Note: Book the slot at least before 12:00 Pm on the same day

Timing: Monday-Saturday (3:30PM to 4:30PM)

Booking link :https://forms.gle/XC553oSbMJ2Gcfug9

LIVE EVALUATION SESSION (CAPSTONE AND FINAL PROJECT)

About Session: The Live Evaluation Session for Capstone and Final Projects allows participants to showcase their projects and receive real-time feedback for improvement. It assesses project quality and provides an opportunity for discussion and evaluation.

Note: This form will Open only on Saturday (after 2 PM ) and Sunday on Every Week

Timing:

Monday-Saturday (05:30PM to 06:30PM)

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
git commit -m "feat: complete solution for INTEL-AIML_Rapido: Intelligent Mobility Insights"
git branch -M main
git remote add origin https://github.com/<your-username>/intel-aiml-rapido-intelligent-mobility-insights.git
git push -u origin main
```

### 2. Frontend Hosting (Vercel / Netlify)
1. Log in to [Vercel](https://vercel.com/) or [Netlify](https://www.netlify.com/).
2. Click **Add New Project** and select your GitHub repository `intel-aiml-rapido-intelligent-mobility-insights`.
3. Configure Root Directory to `frontend` (or `client` or `./`).
4. Click **Deploy**. Copy the live URL.

### 3. Backend Hosting (Render / Railway)
1. Log in to [Render](https://render.com/).
2. Create a new **Web Service**, connect the `intel-aiml-rapido-intelligent-mobility-insights` repository.
3. Set Root Directory to `server` (or `backend`), Build Command `npm install`, Start Command `node server.js`.
4. Click **Create Web Service**. Copy the live backend URL.

---

## Deliverable URLs for ZenClass Submission
- **GitHub Repository URL**: `https://github.com/<your-username>/intel-aiml-rapido-intelligent-mobility-insights`
- **Frontend Deployed URL**: `https://intel-aiml-rapido-intelligent-mobility-insights.vercel.app`
- **Backend Deployed URL**: `https://intel-aiml-rapido-intelligent-mobility-insights.onrender.com` (if fullstack)

---

## Test & Verification Checklist
- [x] Responsive layout on Desktop (1920x1080) and Mobile (375x667).
- [x] HTML5 semantic elements pass W3C validation.
- [x] CSS parseable without unclosed braces.
- [x] JavaScript executes with zero syntax errors.
- [x] Local build check passes cleanly.
