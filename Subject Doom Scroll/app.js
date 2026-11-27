/* CBSE Shorts — app.js */
(function () {
  "use strict";

  const STORAGE_CLASS_KEY = "cbse_shorts_selected_class";
  const STORAGE_SUBJECT_KEY = "cbse_shorts_selected_subject";
  const STORAGE_VOICE_KEY = "cbse_shorts_voice_on";
  const WORDS_PER_SEC = 2.2;

  const state = {
    allShorts: [],
    filteredShorts: [],
    selectedClass: localStorage.getItem(STORAGE_CLASS_KEY)
      ? Number(localStorage.getItem(STORAGE_CLASS_KEY))
      : null,
    selectedSubject: localStorage.getItem(STORAGE_SUBJECT_KEY) || "All",
    voiceOn: localStorage.getItem(STORAGE_VOICE_KEY) !== "false",
    activeIndex: 0,
    isPaused: false,
    elapsedSec: 0,
    totalDurationSec: 50,
    currentSceneIdx: 0,
    rafId: null,
    lastTickTs: null,
    speechSupported: "speechSynthesis" in window && "SpeechSynthesisUtterance" in window
  };

  // DOM Elements
  const feedContainer = document.getElementById("feedContainer");
  const onboardingModal = document.getElementById("onboardingModal");
  const comingSoonPanel = document.getElementById("comingSoonPanel");
  const errorPanel = document.getElementById("errorPanel");
  const errorMessage = document.getElementById("errorMessage");
  const currentClassLabel = document.getElementById("currentClassLabel");
  const openOnboardingBtn = document.getElementById("openOnboardingBtn");
  const voiceToggleBtn = document.getElementById("voiceToggleBtn");
  const voiceIcon = document.getElementById("voiceIcon");
  const voiceLabel = document.getElementById("voiceLabel");
  const csClassBadge = document.getElementById("csClassBadge");
  const csSavedClassText = document.getElementById("csSavedClassText");
  const tryClass9Btn = document.getElementById("tryClass9Btn");
  const changeClassFromCsBtn = document.getElementById("changeClassFromCsBtn");

  // Validate content schema strictly (mirrors check.py rules so bad input is rejected)
  function validateShorts(shorts) {
    const errs = [];
    if (!Array.isArray(shorts)) {
      return ["Content root must be a JSON array"];
    }
    if (shorts.length !== 10) {
      errs.push(`need 10 shorts, got ${shorts.length}`);
    }
    const ids = shorts.map((s) => s && s.id);
    if (new Set(ids).size !== ids.length) {
      errs.push("duplicate ids");
    }
    const requiredKeys = [
      "id",
      "class",
      "subject",
      "chapter",
      "title",
      "hook",
      "narration",
      "terms",
      "scenes",
      "misconception"
    ];
    shorts.forEach((s) => {
      const id = (s && s.id) || "?";
      requiredKeys.forEach((k) => {
        if (!(k in s) || s[k] === "" || s[k] === null || (Array.isArray(s[k]) && s[k].length === 0)) {
          errs.push(`${id}: missing ${k}`);
        }
      });
      const words = ((s && s.narration) || "").match(/\b[\w'-]+\b/g) || [];
      if (words.length < 100 || words.length > 130) {
        errs.push(`${id}: narration ${words.length} words (must be 100-130)`);
      }
      const scenes = (s && s.scenes) || [];
      if (scenes.length < 4 || scenes.length > 6) {
        errs.push(`${id}: scenes count ${scenes.length} (must be 4-6)`);
      }
      const terms = (s && s.terms) || [];
      terms.forEach((t) => {
        const w = ((t && t.word) || "").toLowerCase();
        const nar = ((s && s.narration) || "").toLowerCase();
        if (!w || !nar.includes(w)) {
          errs.push(`${id}: term '${t && t.word}' not in narration`);
        }
      });
    });
    return errs;
  }

  function countWords(text) {
    const m = (text || "").match(/\b[\w'-]+\b/g);
    return m ? m.length : 0;
  }

  // Session random shuffle (Fisher-Yates)
  function shuffleArray(arr) {
    const copy = arr.slice();
    for (let i = copy.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      const tmp = copy[i];
      copy[i] = copy[j];
      copy[j] = tmp;
    }
    return copy;
  }

  // Distinct animated SVG illustrations keyed by visual type / concept
  function renderVisualSVG(visualKey, sceneIdx) {
    const v = (visualKey || "").toLowerCase();

    if (v.includes("track") || v.includes("distance") || v.includes("displacement") || v.includes("circle-lap")) {
      return `
        <svg viewBox="0 0 300 140" aria-label="Distance vs Displacement diagram">
          <defs>
            <linearGradient id="pathGrad" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stop-color="#38bdf8"/>
              <stop offset="100%" stop-color="#34d399"/>
            </linearGradient>
          </defs>
          <!-- Track / Path -->
          <rect x="35" y="25" width="230" height="65" rx="32" fill="none" stroke="#334155" stroke-width="6" stroke-dasharray="8 6"/>
          <path d="M 55 90 L 245 90" stroke="url(#pathGrad)" stroke-width="5" stroke-linecap="round"/>
          <!-- Start / Canteen markers -->
          <circle cx="55" cy="90" r="8" fill="#34d399" class="svg-anim-pulse"/>
          <text x="55" y="114" fill="#94a3b8" font-size="11" text-anchor="middle" font-weight="700">Desk (0 m)</text>
          <circle cx="245" cy="90" r="8" fill="#fbbf24"/>
          <text x="245" y="114" fill="#94a3b8" font-size="11" text-anchor="middle" font-weight="700">Canteen (80 m)</text>
          <!-- Moving student dot -->
          <g class="svg-anim-slide">
            <circle cx="150" cy="90" r="10" fill="#38bdf8"/>
            <text x="150" y="72" fill="#f8fafc" font-size="11" text-anchor="middle" font-weight="800">${
              v.includes("zero") ? "Displacement = 0 m!" : "Path = 160 m | Gap = 0 m"
            }</text>
          </g>
        </svg>`;
    }

    if (v.includes("speed") || v.includes("velocity") || v.includes("roundabout") || v.includes("turning")) {
      return `
        <svg viewBox="0 0 300 140" aria-label="Speed vs Velocity compass and circular turn">
          <!-- Roundabout circle -->
          <circle cx="150" cy="72" r="46" fill="none" stroke="#334155" stroke-width="10"/>
          <circle cx="150" cy="72" r="46" fill="none" stroke="#38bdf8" stroke-width="3" stroke-dasharray="10 8"/>
          <!-- Orbiting scooter & tangent velocity vector -->
          <g class="svg-anim-orbit">
            <circle cx="150" cy="26" r="8" fill="#fbbf24"/>
            <line x1="150" y1="26" x2="188" y2="26" stroke="#34d399" stroke-width="4" stroke-linecap="round"/>
            <polygon points="188,21 198,26 188,31" fill="#34d399"/>
          </g>
          <text x="150" y="76" fill="#f8fafc" font-size="12" text-anchor="middle" font-weight="800">10 m/s</text>
          <text x="150" y="133" fill="#34d399" font-size="11" text-anchor="middle" font-weight="700">Speed fixed • Direction turns → Velocity changes</text>
        </svg>`;
    }

    if (v.includes("train") || v.includes("auto") || v.includes("accel") || v.includes("braking")) {
      return `
        <svg viewBox="0 0 300 140" aria-label="Acceleration velocity steps per second">
          <line x1="25" y1="105" x2="275" y2="105" stroke="#475569" stroke-width="3"/>
          <!-- Step bars for t=0s, 1s, 2s, 3s -->
          <rect x="42" y="95" width="32" height="10" rx="4" fill="#64748b"/>
          <text x="58" y="122" fill="#94a3b8" font-size="10" text-anchor="middle">0s (0m/s)</text>
          <rect x="102" y="75" width="32" height="30" rx="4" fill="#38bdf8"/>
          <text x="118" y="122" fill="#94a3b8" font-size="10" text-anchor="middle">1s (2m/s)</text>
          <rect x="162" y="55" width="32" height="50" rx="4" fill="#34d399"/>
          <text x="178" y="122" fill="#94a3b8" font-size="10" text-anchor="middle">2s (4m/s)</text>
          <rect x="222" y="35" width="32" height="70" rx="4" fill="#fbbf24" class="svg-anim-pulse"/>
          <text x="238" y="122" fill="#fbbf24" font-size="10" text-anchor="middle" font-weight="700">3s (6m/s)</text>
          <text x="150" y="22" fill="#f8fafc" font-size="12" text-anchor="middle" font-weight="800">+2 m/s every second → a = 2 m/s²</text>
        </svg>`;
    }

    if (v.includes("bus") || v.includes("inertia") || v.includes("mass-comparison")) {
      return `
        <svg viewBox="0 0 300 140" aria-label="Bus braking inertia illustration">
          <line x1="20" y1="115" x2="280" y2="115" stroke="#475569" stroke-width="4"/>
          <g class="svg-anim-slide">
            <!-- Bus frame -->
            <rect x="65" y="38" width="160" height="65" rx="12" fill="#1e293b" stroke="#38bdf8" stroke-width="3"/>
            <circle cx="98" cy="106" r="10" fill="#fbbf24"/>
            <circle cx="192" cy="106" r="10" fill="#fbbf24"/>
            <!-- Passenger leaning forward on brake -->
            <circle cx="152" cy="54" r="7" fill="#34d399"/>
            <line x1="142" y1="92" x2="152" y2="62" stroke="#34d399" stroke-width="4" stroke-linecap="round"/>
            <line x1="158" y1="54" x2="184" y2="54" stroke="#fb7185" stroke-width="3"/>
            <polygon points="184,50 192,54 184,58" fill="#fb7185"/>
          </g>
          <text x="150" y="22" fill="#f8fafc" font-size="11.5" text-anchor="middle" font-weight="800">Feet stop with floor • Upper body keeps moving (Inertia)</text>
        </svg>`;
    }

    if (v.includes("ball-on-grass") || v.includes("space-glide") || v.includes("first-law") || v.includes("friction-arrows")) {
      return `
        <svg viewBox="0 0 300 140" aria-label="Newton First Law friction vs deep space">
          <!-- Top: Grass with backward friction -->
          <line x1="25" y1="58" x2="275" y2="58" stroke="#34d399" stroke-width="3" stroke-dasharray="4 3"/>
          <circle cx="115" cy="44" r="12" fill="#fb7185"/>
          <line x1="100" y1="44" x2="68" y2="44" stroke="#fbbf24" stroke-width="3"/>
          <polygon points="68,40 58,44 68,48" fill="#fbbf24"/>
          <text x="195" y="48" fill="#fbbf24" font-size="10.5" font-weight="700">← Friction slows ball</text>
          <!-- Bottom: Deep space zero friction -->
          <g class="svg-anim-slide">
            <circle cx="135" cy="102" r="12" fill="#38bdf8"/>
            <line x1="150" y1="102" x2="195" y2="102" stroke="#38bdf8" stroke-width="3"/>
            <polygon points="195,98 205,102 195,106" fill="#38bdf8"/>
          </g>
          <text x="150" y="130" fill="#38bdf8" font-size="11" text-anchor="middle" font-weight="800">No unbalanced force → constant velocity forever</text>
        </svg>`;
    }

    if (v.includes("microscope") || v.includes("ridge") || v.includes("sliding-book")) {
      return `
        <svg viewBox="0 0 300 140" aria-label="Microscopic interlocking ridges causing friction">
          <text x="150" y="22" fill="#fbbf24" font-size="11.5" text-anchor="middle" font-weight="800">10,000× Zoom: Microscopic Hills Interlock</text>
          <!-- Top surface teeth (Book) -->
          <g class="svg-anim-slide">
            <path d="M 35 45 L 265 45 L 250 72 L 225 52 L 200 74 L 175 52 L 150 74 L 125 52 L 100 74 L 75 52 L 50 72 Z" fill="rgba(56,189,248,0.3)" stroke="#38bdf8" stroke-width="3"/>
          </g>
          <!-- Bottom surface teeth (Desk) -->
          <path d="M 35 105 L 55 68 L 80 90 L 105 68 L 130 90 L 155 68 L 180 90 L 205 68 L 230 90 L 255 68 L 265 105 Z" fill="rgba(251,191,36,0.25)" stroke="#fbbf24" stroke-width="3"/>
          <text x="150" y="128" fill="#94a3b8" font-size="10.5" text-anchor="middle" font-weight="700">Bumps catch into each other → opposing friction force</text>
        </svg>`;
    }

    if (v.includes("truck") || v.includes("bullet") || v.includes("momentum-formula") || v.includes("catcher")) {
      return `
        <svg viewBox="0 0 300 140" aria-label="Momentum equals mass times velocity">
          <rect x="28" y="30" width="110" height="58" rx="10" fill="#1e293b" stroke="#38bdf8" stroke-width="2.5" class="svg-anim-pulse"/>
          <text x="83" y="54" fill="#38bdf8" font-size="12" text-anchor="middle" font-weight="800">BIG MASS (M)</text>
          <text x="83" y="73" fill="#f8fafc" font-size="10.5" text-anchor="middle">× small v = Huge p</text>

          <rect x="162" y="30" width="110" height="58" rx="10" fill="#1e293b" stroke="#fb7185" stroke-width="2.5" class="svg-anim-pulse"/>
          <text x="217" y="54" fill="#fb7185" font-size="12" text-anchor="middle" font-weight="800">BIG VELOCITY (V)</text>
          <text x="217" y="73" fill="#f8fafc" font-size="10.5" text-anchor="middle">× tiny m = Huge p</text>

          <text x="150" y="118" fill="#34d399" font-size="14" text-anchor="middle" font-weight="800">Momentum (p) = mass × velocity</text>
        </svg>`;
    }

    if (v.includes("fma") || v.includes("5kg") || v.includes("15-newtons") || v.includes("cricket-catch")) {
      return `
        <svg viewBox="0 0 300 140" aria-label="F equals m times a worked example 5 kg times 3 m/s squared equals 15 N">
          <line x1="20" y1="108" x2="280" y2="108" stroke="#475569" stroke-width="3"/>
          <g class="svg-anim-slide">
            <!-- Force arrow -->
            <line x1="35" y1="68" x2="95" y2="68" stroke="#34d399" stroke-width="5" stroke-linecap="round"/>
            <polygon points="95,61 108,68 95,75" fill="#34d399"/>
            <text x="68" y="54" fill="#34d399" font-size="12" text-anchor="middle" font-weight="800">F = 15 N</text>
            <!-- 5 kg Cart -->
            <rect x="112" y="42" width="90" height="48" rx="10" fill="#1e293b" stroke="#38bdf8" stroke-width="3"/>
            <text x="157" y="71" fill="#f8fafc" font-size="14" text-anchor="middle" font-weight="800">5 kg</text>
            <circle cx="132" cy="98" r="8" fill="#fbbf24"/>
            <circle cx="182" cy="98" r="8" fill="#fbbf24"/>
            <!-- Accel badge -->
            <text x="244" y="72" fill="#fbbf24" font-size="12.5" text-anchor="middle" font-weight="800">a = 3 m/s²</text>
          </g>
          <text x="150" y="130" fill="#38bdf8" font-size="12" text-anchor="middle" font-weight="800">F = m × a = 5 kg × 3 m/s² = 15 N</text>
        </svg>`;
    }

    if (v.includes("swimmer") || v.includes("different-body") || v.includes("tug") || v.includes("rocket")) {
      return `
        <svg viewBox="0 0 300 140" aria-label="Newton Third Law action and reaction on two different bodies">
          <!-- Pool Wall (Body A) -->
          <rect x="28" y="22" width="34" height="92" rx="6" fill="#334155" stroke="#fb7185" stroke-width="2.5"/>
          <text x="45" y="128" fill="#fb7185" font-size="10.5" text-anchor="middle" font-weight="800">Body A: Wall</text>
          <!-- Action arrow on Wall -->
          <line x1="115" y1="54" x2="68" y2="54" stroke="#fb7185" stroke-width="4"/>
          <polygon points="68,48 56,54 68,60" fill="#fb7185"/>
          <text x="115" y="42" fill="#fb7185" font-size="10.5" font-weight="700">Action on Wall</text>

          <!-- Swimmer (Body B) -->
          <g class="svg-anim-slide">
            <rect x="148" y="48" width="95" height="42" rx="20" fill="#1e293b" stroke="#34d399" stroke-width="2.5"/>
            <text x="195" y="73" fill="#f8fafc" font-size="11.5" text-anchor="middle" font-weight="800">Body B: Swimmer</text>
            <!-- Reaction arrow on Swimmer -->
            <line x1="246" y1="69" x2="282" y2="69" stroke="#34d399" stroke-width="4"/>
            <polygon points="282,63 294,69 282,75" fill="#34d399"/>
          </g>
          <text x="185" y="128" fill="#34d399" font-size="10.5" text-anchor="middle" font-weight="800">Acts on TWO DIFFERENT BODIES → Never cancels!</text>
        </svg>`;
    }

    // Conservation of momentum (rifle recoil)
    return `
      <svg viewBox="0 0 300 140" aria-label="Conservation of momentum rifle recoil vs fast bullet">
        <line x1="150" y1="22" x2="150" y2="108" stroke="#475569" stroke-width="2" stroke-dasharray="4 4"/>
        <!-- Rifle moving back slowly (Big M, small v) -->
        <rect x="48" y="48" width="84" height="34" rx="8" fill="#1e293b" stroke="#fbbf24" stroke-width="2.5"/>
        <text x="90" y="69" fill="#fbbf24" font-size="11" text-anchor="middle" font-weight="800">Rifle: M × (−v)</text>
        <line x1="44" y1="65" x2="20" y2="65" stroke="#fbbf24" stroke-width="4"/>
        <polygon points="20,60 10,65 20,70" fill="#fbbf24"/>

        <!-- Bullet moving forward fast (tiny m, huge V) -->
        <g class="svg-anim-slide">
          <circle cx="205" cy="65" r="9" fill="#38bdf8"/>
          <line x1="218" y1="65" x2="275" y2="65" stroke="#38bdf8" stroke-width="4"/>
          <polygon points="275,60 287,65 275,70" fill="#38bdf8"/>
          <text x="225" y="45" fill="#38bdf8" font-size="11" text-anchor="middle" font-weight="800">Bullet: m × (+V)</text>
        </g>
        <text x="150" y="126" fill="#34d399" font-size="11.5" text-anchor="middle" font-weight="800">Total Momentum Before (0) = Total Momentum After (0)</text>
      </svg>`;
  }

  function buildShortSlide(shortObj, idx, total) {
    const wordCount = countWords(shortObj.narration);
    const estDurationSec = Math.round(wordCount / WORDS_PER_SEC);
    const slide = document.createElement("article");
    slide.className = "short-slide";
    slide.dataset.index = String(idx);
    slide.dataset.shortId = shortObj.id;

    const firstScene = shortObj.scenes[0];
    const firstTerm = shortObj.terms[0];

    const segsHtml = shortObj.scenes
      .map(
        (_, sIdx) =>
          `<div class="scene-seg" data-seg="${sIdx}"><div class="scene-seg-fill" id="seg-${idx}-${sIdx}"></div></div>`
      )
      .join("");

    const termTabsHtml = shortObj.terms
      .map(
        (t, tIdx) =>
          `<button class="term-tab-btn ${tIdx === 0 ? "active" : ""}" data-term-idx="${tIdx}" type="button">${t.word}</button>`
      )
      .join("");

    slide.innerHTML = `
      <div class="short-card" data-card-idx="${idx}">
        <div class="top-progress-wrap">
          <div class="scene-segments">${segsHtml}</div>
          <div class="short-meta-row">
            <span class="chapter-pill">Class ${shortObj.class} • ${shortObj.subject} • ${shortObj.chapter}</span>
            <span class="counter-pill">${idx + 1} / ${total} • ~${estDurationSec}s (${wordCount}w)</span>
          </div>
        </div>

        <div class="header-block">
          <h2 class="short-title">${shortObj.title}</h2>
          <p class="short-hook">💡 ${shortObj.hook}</p>
        </div>

        <div class="scene-stage" id="stage-${idx}">
          <div class="scene-badge-row">
            <span id="scene-counter-${idx}">Scene 1 of ${shortObj.scenes.length}</span>
            <span class="play-status-pill" id="play-pill-${idx}">▶ Playing</span>
          </div>
          <div class="scene-visual-box" id="visual-box-${idx}">
            ${renderVisualSVG(firstScene.visual, 0)}
          </div>
          <div class="scene-big-text" id="scene-text-${idx}">${firstScene.text}</div>
        </div>

        <div class="term-box" id="term-box-${idx}">
          <div class="term-box-header">
            <span class="term-chip-pill" id="term-word-${idx}">🔑 ${firstTerm.word}</span>
            <div class="term-tabs">${termTabsHtml}</div>
          </div>
          <p class="term-meaning" id="term-meaning-${idx}">${firstTerm.meaning}</p>
        </div>

        <div class="misconception-bar">
          <strong>Myth busted:</strong> ${shortObj.misconception}
        </div>

        <div class="footer-controls">
          <span id="time-readout-${idx}">0s / ${estDurationSec}s • Tap card to pause</span>
          <div class="scene-nav-btns">
            <button class="mini-btn" data-action="prev-scene" type="button">◀ Scene</button>
            <button class="mini-btn" data-action="next-scene" type="button">Scene ▶</button>
          </div>
        </div>
      </div>
    `;

    // Card interaction handlers (tap to pause/resume, term tabs, manual scene step)
    const card = slide.querySelector(".short-card");
    card.addEventListener("click", (e) => {
      const termBtn = e.target.closest(".term-tab-btn");
      if (termBtn) {
        e.stopPropagation();
        const tIdx = Number(termBtn.dataset.termIdx);
        selectTermOnSlide(idx, tIdx);
        return;
      }
      const navBtn = e.target.closest("[data-action]");
      if (navBtn) {
        e.stopPropagation();
        const act = navBtn.dataset.action;
        jumpScene(idx, act === "next-scene" ? 1 : -1);
        return;
      }
      togglePauseActiveShort();
    });

    return slide;
  }

  function selectTermOnSlide(slideIdx, termIdx) {
    const shortObj = state.filteredShorts[slideIdx];
    if (!shortObj || !shortObj.terms[termIdx]) return;
    const term = shortObj.terms[termIdx];
    const wordEl = document.getElementById(`term-word-${slideIdx}`);
    const meanEl = document.getElementById(`term-meaning-${slideIdx}`);
    if (wordEl) wordEl.textContent = `🔑 ${term.word}`;
    if (meanEl) meanEl.textContent = term.meaning;

    const slide = feedContainer.querySelector(`.short-slide[data-index="${slideIdx}"]`);
    if (slide) {
      slide.querySelectorAll(".term-tab-btn").forEach((b, i) => {
        b.classList.toggle("active", i === termIdx);
      });
    }
  }

  function updateSlideSceneUI(slideIdx, sceneIdx) {
    const shortObj = state.filteredShorts[slideIdx];
    if (!shortObj) return;
    const clampedIdx = Math.max(0, Math.min(shortObj.scenes.length - 1, sceneIdx));
    const scene = shortObj.scenes[clampedIdx];

    const counterEl = document.getElementById(`scene-counter-${slideIdx}`);
    const visualEl = document.getElementById(`visual-box-${slideIdx}`);
    const textEl = document.getElementById(`scene-text-${slideIdx}`);

    if (counterEl) {
      counterEl.textContent = `Scene ${clampedIdx + 1} of ${shortObj.scenes.length}`;
    }
    if (visualEl) {
      visualEl.innerHTML = renderVisualSVG(scene.visual, clampedIdx);
    }
    if (textEl) {
      textEl.textContent = scene.text;
    }

    // Rotate key-term chip automatically with scenes so every term is highlighted
    const termIdx = clampedIdx % shortObj.terms.length;
    selectTermOnSlide(slideIdx, termIdx);
  }

  function jumpScene(slideIdx, delta) {
    if (slideIdx !== state.activeIndex) return;
    const shortObj = state.filteredShorts[slideIdx];
    if (!shortObj) return;
    const numScenes = shortObj.scenes.length;
    const nextScene = Math.max(0, Math.min(numScenes - 1, state.currentSceneIdx + delta));
    state.currentSceneIdx = nextScene;
    state.elapsedSec = (nextScene / numScenes) * state.totalDurationSec;
    updateSlideSceneUI(slideIdx, nextScene);
    updateProgressUI(slideIdx);
  }

  function updateProgressUI(slideIdx) {
    const shortObj = state.filteredShorts[slideIdx];
    if (!shortObj) return;
    const numScenes = shortObj.scenes.length;
    const totalSec = state.totalDurationSec;
    const elapsed = Math.min(totalSec, state.elapsedSec);
    const segDuration = totalSec / numScenes;

    for (let s = 0; s < numScenes; s++) {
      const fillEl = document.getElementById(`seg-${slideIdx}-${s}`);
      if (!fillEl) continue;
      const segStart = s * segDuration;
      const segProgress = Math.max(0, Math.min(1, (elapsed - segStart) / segDuration));
      fillEl.style.width = `${(segProgress * 100).toFixed(1)}%`;
    }

    const timeEl = document.getElementById(`time-readout-${slideIdx}`);
    if (timeEl) {
      timeEl.textContent = `${Math.floor(elapsed)}s / ${Math.round(totalSec)}s • Tap card to ${
        state.isPaused ? "resume" : "pause"
      }`;
    }
  }

  function stopSpeech() {
    if (state.speechSupported) {
      try {
        window.speechSynthesis.cancel();
      } catch (_) {}
    }
  }

  function startSpeechForShort(shortObj) {
    stopSpeech();
    if (!state.voiceOn || !state.speechSupported || state.isPaused) return;
    try {
      const utter = new SpeechSynthesisUtterance(shortObj.narration);
      utter.lang = "en-IN";
      utter.rate = 0.98;
      // Pick word boundary events when browser provides them to drive exact timing
      utter.onboundary = (ev) => {
        if (ev.name === "word" && typeof ev.charIndex === "number") {
          const ratio = Math.min(1, ev.charIndex / Math.max(1, shortObj.narration.length));
          state.elapsedSec = ratio * state.totalDurationSec;
        }
      };
      window.speechSynthesis.speak(utter);
    } catch (_) {}
  }

  function startPlaybackForIndex(idx) {
    if (state.rafId) {
      cancelAnimationFrame(state.rafId);
      state.rafId = null;
    }
    const shortObj = state.filteredShorts[idx];
    if (!shortObj) return;

    state.activeIndex = idx;
    state.isPaused = false;
    state.elapsedSec = 0;
    state.currentSceneIdx = 0;
    const words = countWords(shortObj.narration);
    state.totalDurationSec = Math.max(30, words / WORDS_PER_SEC);
    state.lastTickTs = performance.now();

    const pill = document.getElementById(`play-pill-${idx}`);
    if (pill) {
      pill.textContent = "▶ Playing";
      pill.classList.remove("paused");
    }

    updateSlideSceneUI(idx, 0);
    updateProgressUI(idx);
    startSpeechForShort(shortObj);

    function tick(now) {
      const dt = (now - state.lastTickTs) / 1000;
      state.lastTickTs = now;

      if (!state.isPaused) {
        state.elapsedSec += dt;
        if (state.elapsedSec >= state.totalDurationSec) {
          state.elapsedSec = 0;
          state.currentSceneIdx = 0;
          updateSlideSceneUI(idx, 0);
          startSpeechForShort(shortObj);
        }
        const numScenes = shortObj.scenes.length;
        const targetScene = Math.min(
          numScenes - 1,
          Math.floor((state.elapsedSec / state.totalDurationSec) * numScenes)
        );
        if (targetScene !== state.currentSceneIdx) {
          state.currentSceneIdx = targetScene;
          updateSlideSceneUI(idx, targetScene);
        }
        updateProgressUI(idx);
      }
      state.rafId = requestAnimationFrame(tick);
    }

    state.rafId = requestAnimationFrame(tick);
  }

  function togglePauseActiveShort() {
    const idx = state.activeIndex;
    state.isPaused = !state.isPaused;
    const pill = document.getElementById(`play-pill-${idx}`);
    if (pill) {
      pill.textContent = state.isPaused ? "⏸ Paused" : "▶ Playing";
      pill.classList.toggle("paused", state.isPaused);
    }
    if (state.speechSupported) {
      try {
        if (state.isPaused) {
          window.speechSynthesis.pause();
        } else if (state.voiceOn) {
          if (window.speechSynthesis.paused) {
            window.speechSynthesis.resume();
          } else {
            startSpeechForShort(state.filteredShorts[idx]);
          }
        }
      } catch (_) {}
    }
    updateProgressUI(idx);
  }

  // IntersectionObserver to detect snapped short slide
  let slideObserver = null;
  function setupSlideObserver() {
    if (slideObserver) slideObserver.disconnect();
    slideObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting && entry.intersectionRatio >= 0.6) {
            const idx = Number(entry.target.dataset.index);
            if (!Number.isNaN(idx) && idx !== state.activeIndex) {
              startPlaybackForIndex(idx);
            }
          }
        });
      },
      { root: feedContainer, threshold: [0.65] }
    );

    feedContainer.querySelectorAll(".short-slide").forEach((el) => slideObserver.observe(el));
  }

  function renderFeed() {
    stopSpeech();
    if (state.rafId) {
      cancelAnimationFrame(state.rafId);
      state.rafId = null;
    }

    const cls = state.selectedClass || 9;
    currentClassLabel.textContent = `Class ${cls}`;

    // Only Class 9 has content in pilot; Classes 6, 7, 8, 10 show Coming Soon & still save in localStorage
    if (cls !== 9) {
      feedContainer.innerHTML = "";
      csClassBadge.textContent = `Class ${cls}`;
      csSavedClassText.textContent = `Class ${cls}`;
      comingSoonPanel.classList.remove("hidden");
      return;
    }

    comingSoonPanel.classList.add("hidden");

    const matching = state.allShorts.filter((s) => {
      const classMatch = Number(s.class) === cls;
      const subjMatch =
        state.selectedSubject === "All" ||
        s.subject.toLowerCase() === state.selectedSubject.toLowerCase();
      return classMatch && subjMatch;
    });

    state.filteredShorts = shuffleArray(matching);
    feedContainer.innerHTML = "";

    state.filteredShorts.forEach((shortObj, idx) => {
      const slide = buildShortSlide(shortObj, idx, state.filteredShorts.length);
      feedContainer.appendChild(slide);
    });

    setupSlideObserver();
    if (state.filteredShorts.length > 0) {
      feedContainer.scrollTo({ top: 0, behavior: "instant" });
      startPlaybackForIndex(0);
    }
  }

  function selectClass(classNum) {
    state.selectedClass = Number(classNum);
    localStorage.setItem(STORAGE_CLASS_KEY, String(state.selectedClass));
    onboardingModal.classList.add("hidden");
    renderFeed();
  }

  function updateVoiceButtonUI() {
    voiceToggleBtn.setAttribute("aria-pressed", state.voiceOn ? "true" : "false");
    voiceIcon.textContent = state.voiceOn ? "🔊" : "🔇";
    voiceLabel.textContent = state.voiceOn ? "Voice On" : "Voice Off";
  }

  function bindEvents() {
    openOnboardingBtn.addEventListener("click", () => {
      stopSpeech();
      onboardingModal.classList.remove("hidden");
    });

    document.querySelectorAll(".class-option").forEach((btn) => {
      btn.addEventListener("click", () => {
        const cls = Number(btn.dataset.class);
        selectClass(cls);
      });
    });

    tryClass9Btn.addEventListener("click", () => {
      selectClass(9);
    });

    changeClassFromCsBtn.addEventListener("click", () => {
      comingSoonPanel.classList.add("hidden");
      onboardingModal.classList.remove("hidden");
    });

    document.querySelectorAll(".subject-chips .chip").forEach((chip) => {
      chip.addEventListener("click", () => {
        const subj = chip.dataset.subject;
        state.selectedSubject = subj;
        localStorage.setItem(STORAGE_SUBJECT_KEY, subj);
        document.querySelectorAll(".subject-chips .chip").forEach((c) => {
          const active = c.dataset.subject === subj;
          c.classList.toggle("active", active);
          c.setAttribute("aria-selected", active ? "true" : "false");
        });
        renderFeed();
      });
    });

    voiceToggleBtn.addEventListener("click", () => {
      state.voiceOn = !state.voiceOn;
      localStorage.setItem(STORAGE_VOICE_KEY, String(state.voiceOn));
      updateVoiceButtonUI();
      if (state.voiceOn && !state.isPaused && state.filteredShorts[state.activeIndex]) {
        startSpeechForShort(state.filteredShorts[state.activeIndex]);
      } else {
        stopSpeech();
      }
    });
  }

  async function init() {
    updateVoiceButtonUI();
    bindEvents();

    // Allow custom content file path via ?content=... for bad-input testing
    const params = new URLSearchParams(window.location.search);
    const contentUrl = params.get("content") || "content/class9_science.json";

    try {
      const resp = await fetch(contentUrl, { cache: "no-store" });
      if (!resp.ok) {
        throw new Error(`HTTP ${resp.status} loading ${contentUrl}`);
      }
      const data = await resp.json();
      const errs = validateShorts(data);
      if (errs.length > 0) {
        errorMessage.textContent = errs.join(" | ");
        errorPanel.classList.remove("hidden");
        console.error("CBSE Shorts content validation error:", errs);
        return;
      }
      state.allShorts = data;
    } catch (err) {
      errorMessage.textContent = err.message || "Failed to load content JSON.";
      errorPanel.classList.remove("hidden");
      console.error("CBSE Shorts load failure:", err);
      return;
    }

    if (!state.selectedClass) {
      onboardingModal.classList.remove("hidden");
    } else {
      renderFeed();
    }
  }

  // Expose validator for testing
  window.CBSEShorts = { validateShorts };

  init();
})();
