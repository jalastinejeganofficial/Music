/**
 * ==============================================================================
 * MUSIC PLAYER — APPLE-GRADE SHOWCASE ANIMATION ENGINE
 * ==============================================================================
 * Features:
 *  1. Multi-Octave Harmonic Ambient Canvas (Euler Superposition & Cursor Waves)
 *  2. Interactive Acoustic Wave Synthesizer (Harmonic Modes & Real-time HZ Readout)
 *  3. Gyroscopic 3D Bento Card Tilt with Dynamic Specular Spotlight
 *  4. Apple Keynote Scroll Sequencer (Sticky Stage Cards & Phase Transitions)
 *  5. IntersectionObserver Scroll Reveal Pipeline
 *  6. Interactive Hero Studio Simulation (Vinyl, Equalizer, Synced Lyrics Scroller)
 *  7. Cross-Platform Download Tab Matrix
 * ==============================================================================
 */

(function () {
  'use strict';

  /* ============================================================================
     1. AMBIENT BACKGROUND WAVE CANVAS (Fluid Audio Superposition)
     ============================================================================ */
  const ambientCanvas = document.getElementById('ambient-canvas');
  if (ambientCanvas) {
    const ctx = ambientCanvas.getContext('2d');
    let width = (ambientCanvas.width = window.innerWidth);
    let height = (ambientCanvas.height = window.innerHeight);

    let mouse = { x: width * 0.5, y: height * 0.5, targetX: width * 0.5, targetY: height * 0.5 };
    let time = 0;

    window.addEventListener('resize', () => {
      width = ambientCanvas.width = window.innerWidth;
      height = ambientCanvas.height = window.innerHeight;
    });

    window.addEventListener('pointermove', (e) => {
      mouse.targetX = e.clientX;
      mouse.targetY = e.clientY;
    });

    function drawAmbientWaves() {
      // Smooth mouse interpolation
      mouse.x += (mouse.targetX - mouse.x) * 0.05;
      mouse.y += (mouse.targetY - mouse.y) * 0.05;

      ctx.clearRect(0, 0, width, height);

      // 3 overlapping acoustic harmonic waves
      const waves = [
        { freq: 0.002, amp: 45, speed: 0.012, color: 'rgba(255, 0, 51, 0.12)', width: 2.5 },
        { freq: 0.0035, amp: 30, speed: 0.018, color: 'rgba(255, 119, 0, 0.08)', width: 1.8 },
        { freq: 0.0015, amp: 60, speed: 0.008, color: 'rgba(168, 85, 247, 0.09)', width: 2.0 }
      ];

      const centerY = height * 0.55;
      time += 1;

      waves.forEach((wave, idx) => {
        ctx.beginPath();
        ctx.lineWidth = wave.width;
        ctx.strokeStyle = wave.color;

        for (let x = 0; x <= width; x += 6) {
          // Distance attenuation relative to mouse pointer
          const dx = x - mouse.x;
          const dy = centerY - mouse.y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          const mousePerturbation = Math.exp(-dist / 320) * 40 * Math.sin(time * 0.05);

          // Harmonic wave equation: y = A * sin(kx + wt) + perturbation
          const y =
            centerY +
            Math.sin(x * wave.freq + time * wave.speed + idx) * wave.amp +
            Math.sin(x * wave.freq * 2.3 + time * wave.speed * 1.4) * (wave.amp * 0.4) +
            mousePerturbation;

          if (x === 0) {
            ctx.moveTo(x, y);
          } else {
            ctx.lineTo(x, y);
          }
        }
        ctx.stroke();
      });

      requestAnimationFrame(drawAmbientWaves);
    }

    drawAmbientWaves();
  }

  /* ============================================================================
     2. INTERACTIVE ACOUSTIC SYNTHESIZER CANVAS
     ============================================================================ */
  const waveCanvas = document.getElementById('interactive-wave-canvas');
  const waveFreqReadout = document.getElementById('wave-freq');
  const waveModeBtn = document.getElementById('wave-mode-btn');

  if (waveCanvas && waveFreqReadout) {
    const wCtx = waveCanvas.getContext('2d');
    let cWidth = (waveCanvas.width = waveCanvas.offsetWidth || 800);
    let cHeight = (waveCanvas.height = waveCanvas.offsetHeight || 380);

    const resizeWaveCanvas = () => {
      cWidth = waveCanvas.width = waveCanvas.offsetWidth;
      cHeight = waveCanvas.height = waveCanvas.offsetHeight;
    };
    window.addEventListener('resize', resizeWaveCanvas);

    let activeMode = 0;
    const modes = [
      { name: 'Pure Harmonic Superposition', baseFreq: 432.0 },
      { name: 'Chirped Acoustic Membrane', baseFreq: 528.0 },
      { name: 'Fourier Spectral Series', baseFreq: 864.0 }
    ];

    let synthMouse = {
      x: cWidth * 0.5,
      y: cHeight * 0.5,
      isHovering: false,
      ripples: []
    };

    waveCanvas.addEventListener('pointerenter', () => (synthMouse.isHovering = true));
    waveCanvas.addEventListener('pointerleave', () => (synthMouse.isHovering = false));
    waveCanvas.addEventListener('pointermove', (e) => {
      const rect = waveCanvas.getBoundingClientRect();
      synthMouse.x = e.clientX - rect.left;
      synthMouse.y = e.clientY - rect.top;
    });

    waveCanvas.addEventListener('click', (e) => {
      const rect = waveCanvas.getBoundingClientRect();
      synthMouse.ripples.push({
        x: e.clientX - rect.left,
        y: e.clientY - rect.top,
        radius: 1,
        alpha: 1.0
      });
    });

    if (waveModeBtn) {
      waveModeBtn.addEventListener('click', () => {
        activeMode = (activeMode + 1) % modes.length;
        waveModeBtn.textContent = `Mode: ${modes[activeMode].name}`;
      });
    }

    let synthTime = 0;

    function renderAcousticSynthesizer() {
      wCtx.fillStyle = 'rgba(5, 5, 5, 0.28)';
      wCtx.fillRect(0, 0, cWidth, cHeight);

      synthTime += 0.025;

      // Calculate dynamic frequency from mouse position
      const normalizedX = Math.max(0.01, Math.min(1, synthMouse.x / cWidth));
      const normalizedY = Math.max(0.1, Math.min(1, synthMouse.y / cHeight));
      const currentHz = (modes[activeMode].baseFreq * (0.5 + normalizedX)).toFixed(1);
      waveFreqReadout.textContent = `${currentHz} Hz • ${modes[activeMode].name}`;

      // Render ripples
      for (let i = synthMouse.ripples.length - 1; i >= 0; i--) {
        const r = synthMouse.ripples[i];
        r.radius += 4;
        r.alpha -= 0.02;
        wCtx.save();
        wCtx.beginPath();
        wCtx.arc(r.x, r.y, r.radius, 0, Math.PI * 2);
        wCtx.strokeStyle = `rgba(255, 0, 51, ${Math.max(0, r.alpha)})`;
        wCtx.lineWidth = 1.5;
        wCtx.stroke();
        wCtx.restore();

        if (r.alpha <= 0) synthMouse.ripples.splice(i, 1);
      }

      // Draw primary synthesis curves
      const lines = 7;
      const baseAmp = 35 * (1.2 - normalizedY * 0.5);

      for (let l = 0; l < lines; l++) {
        wCtx.beginPath();
        const lineOffset = (l - lines / 2) * 16;
        const lineAlpha = (1 - Math.abs(l - lines / 2) / (lines / 2) * 0.65).toFixed(2);
        wCtx.strokeStyle = `rgba(255, ${Math.floor(40 + l * 25)}, ${Math.floor(70 + l * 20)}, ${lineAlpha})`;
        wCtx.lineWidth = l === 3 ? 2.5 : 1.2;

        for (let x = 0; x <= cWidth; x += 4) {
          let waveY = cHeight * 0.5 + lineOffset;

          if (activeMode === 0) {
            // Harmonic Superposition
            waveY +=
              Math.sin(x * 0.015 * normalizedX + synthTime + l * 0.3) * baseAmp +
              Math.sin(x * 0.035 * normalizedX - synthTime * 1.2) * (baseAmp * 0.45);
          } else if (activeMode === 1) {
            // Chirped Acoustic Membrane
            const chirp = Math.sin(x * 0.005 + synthTime);
            waveY += Math.sin(x * 0.02 * chirp + synthTime * 2) * baseAmp * 1.2;
          } else {
            // Fourier Spectral Series approximation
            waveY +=
              (Math.sin(x * 0.02 + synthTime) +
                (1 / 3) * Math.sin(3 * (x * 0.02 + synthTime)) +
                (1 / 5) * Math.sin(5 * (x * 0.02 + synthTime))) *
              baseAmp;
          }

          // Cursor interactive magnetic depression
          if (synthMouse.isHovering) {
            const distX = Math.abs(x - synthMouse.x);
            if (distX < 140) {
              const pull = Math.cos((distX / 140) * (Math.PI / 2)) * 32;
              waveY += pull * (synthMouse.y > cHeight * 0.5 ? 1 : -1);
            }
          }

          if (x === 0) {
            wCtx.moveTo(x, waveY);
          } else {
            wCtx.lineTo(x, waveY);
          }
        }
        wCtx.stroke();
      }

      requestAnimationFrame(renderAcousticSynthesizer);
    }

    renderAcousticSynthesizer();
  }

  /* ============================================================================
     3. 3D BENTO TILT & SPECULAR SPOTLIGHT
     ============================================================================ */
  const bentoCards = document.querySelectorAll('.bento-tilt');

  bentoCards.forEach((card) => {
    let bounds;

    const onMouseEnter = () => {
      bounds = card.getBoundingClientRect();
    };

    const onMouseMove = (e) => {
      if (!bounds) bounds = card.getBoundingClientRect();

      const mouseX = e.clientX - bounds.left;
      const mouseY = e.clientY - bounds.top;

      const normX = (mouseX / bounds.width - 0.5) * 2; // -1 to 1
      const normY = (mouseY / bounds.height - 0.5) * 2; // -1 to 1

      // Euler rotational spring matrix angles
      const rotateX = (-normY * 9).toFixed(2);
      const rotateY = (normX * 9).toFixed(2);

      card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.015, 1.015, 1.015)`;
      card.style.setProperty('--mouse-x', `${mouseX}px`);
      card.style.setProperty('--mouse-y', `${mouseY}px`);
    };

    const onMouseLeave = () => {
      card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)';
      card.style.setProperty('--mouse-x', '-500px');
      card.style.setProperty('--mouse-y', '-500px');
    };

    card.addEventListener('mouseenter', onMouseEnter);
    card.addEventListener('mousemove', onMouseMove);
    card.addEventListener('mouseleave', onMouseLeave);
  });

  /* ============================================================================
     4. APPLE KEYNOTE STICKY STAGE SEQUENCER
     ============================================================================ */
  const keynoteSection = document.getElementById('overview');
  const stageCards = document.querySelectorAll('.stage-card');
  const stageDots = document.querySelectorAll('.stage-dot');
  const keynoteTitle = document.getElementById('keynote-title');
  const keynoteSubtitle = document.getElementById('keynote-subtitle');

  const keynoteTitles = [
    {
      title: 'Designed with zero compromises.',
      subtitle: 'InnerTube WEB_REMIX architecture streams bufferless high-fidelity audio in under 240ms.'
    },
    {
      title: 'Every syllable in millisecond lockstep.',
      subtitle: 'LRCLIB sync and official YouTube lyrics aligned to 1-millisecond resolution.'
    },
    {
      title: 'Zero terminal windows. True desktop native.',
      subtitle: 'Single-click MSI installer and cross-platform native application bundles.'
    }
  ];

  function setActiveStage(stageIndex) {
    if (stageIndex < 0 || stageIndex >= stageCards.length) return;

    stageCards.forEach((card, idx) => {
      if (idx === stageIndex) {
        card.classList.add('active');
      } else {
        card.classList.remove('active');
      }
    });

    stageDots.forEach((dot, idx) => {
      if (idx === stageIndex) {
        dot.classList.add('active');
      } else {
        dot.classList.remove('active');
      }
    });

    if (keynoteTitle && keynoteSubtitle) {
      keynoteTitle.textContent = keynoteTitles[stageIndex].title;
      keynoteSubtitle.textContent = keynoteTitles[stageIndex].subtitle;
    }
  }

  // Click on dots to jump stages
  stageDots.forEach((dot, index) => {
    dot.addEventListener('click', () => {
      setActiveStage(index);
    });
  });

  // Scroll tracking within keynote section
  if (keynoteSection) {
    window.addEventListener('scroll', () => {
      const rect = keynoteSection.getBoundingClientRect();
      const totalScrollHeight = keynoteSection.offsetHeight - window.innerHeight;
      if (totalScrollHeight <= 0) return;

      const progress = Math.max(0, Math.min(1, -rect.top / totalScrollHeight));

      if (progress < 0.33) {
        setActiveStage(0);
      } else if (progress < 0.67) {
        setActiveStage(1);
      } else {
        setActiveStage(2);
      }
    });
  }

  /* ============================================================================
     5. INTERSECTION OBSERVER SCROLL REVEAL ENGINE
     ============================================================================ */
  const scrollElements = document.querySelectorAll('.animate-on-scroll');

  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(
      (entries, obs) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
            obs.unobserve(entry.target);
          }
        });
      },
      {
        root: null,
        threshold: 0.12,
        rootMargin: '0px 0px -40px 0px'
      }
    );

    scrollElements.forEach((el) => observer.observe(el));
  } else {
    // Fallback for older browsers
    scrollElements.forEach((el) => el.classList.add('is-visible'));
  }

  /* ============================================================================
     6. INTERACTIVE HERO STUDIO SIMULATION
     ============================================================================ */
  const vinylTurntable = document.getElementById('vinyl-turntable');
  const vinylDisc = vinylTurntable ? vinylTurntable.querySelector('.vinyl-disc') : null;
  const eqBars = document.querySelectorAll('.eq-bar');
  const lyricsLines = document.querySelectorAll('.lyrics-line');
  const scrubberProgress = document.querySelector('.scrubber-progress');
  const scrubberHandle = document.querySelector('.scrubber-handle');
  const timeCurrent = document.querySelector('.time-current');

  let isPlaying = true;
  let activeLyricIndex = 2; // initial active line

  if (vinylTurntable && vinylDisc) {
    vinylTurntable.style.cursor = 'pointer';
    vinylTurntable.setAttribute('title', 'Click to toggle Play / Pause');

    vinylTurntable.addEventListener('click', () => {
      isPlaying = !isPlaying;
      if (isPlaying) {
        vinylDisc.classList.add('spinning');
        eqBars.forEach((bar) => (bar.style.animationPlayState = 'running'));
      } else {
        vinylDisc.classList.remove('spinning');
        eqBars.forEach((bar) => (bar.style.animationPlayState = 'paused'));
      }
    });
  }

  // Dynamic Audio Spectrum Jitter
  setInterval(() => {
    if (!isPlaying) return;
    eqBars.forEach((bar) => {
      const height = Math.floor(Math.random() * 46 + 10);
      bar.style.height = `${height}px`;
    });
  }, 120);

  // Synced Lyrics Auto-Progression Simulation
  if (lyricsLines.length > 0) {
    const lyricsData = [
      "I look around and Sin City's cold and empty",
      "No one's around to judge me",
      "I can't see clearly when you're gone...",
      "I said, ooh, I'm blinded by the lights",
      "No, I can't sleep until I feel your touch",
      "I said, ooh, I'm drowning in the night",
      "Oh, when I'm like this, you're the one I trust"
    ];

    let currentLyricalStep = 2;

    setInterval(() => {
      if (!isPlaying) return;
      currentLyricalStep = (currentLyricalStep + 1) % lyricsData.length;

      lyricsLines.forEach((lineEl, idx) => {
        const itemIdx = (currentLyricalStep + idx - 2 + lyricsData.length) % lyricsData.length;
        lineEl.textContent = lyricsData[itemIdx];

        lineEl.classList.remove('past', 'active', 'future');
        if (idx < 2) {
          lineEl.classList.add('past');
        } else if (idx === 2) {
          lineEl.classList.add('active');
        } else {
          lineEl.classList.add('future');
        }
      });
    }, 3200);
  }

  // Simulated Track Progress Scrubber
  let trackSec = 102; // 1:42
  const totalSec = 200; // 3:20

  setInterval(() => {
    if (!isPlaying) return;
    trackSec = (trackSec + 1) % totalSec;

    const mins = Math.floor(trackSec / 60);
    const secs = trackSec % 60;
    const formatted = `${mins}:${secs < 10 ? '0' : ''}${secs}`;
    if (timeCurrent) timeCurrent.textContent = formatted;

    const pct = ((trackSec / totalSec) * 100).toFixed(1);
    if (scrubberProgress) scrubberProgress.style.width = `${pct}%`;
    if (scrubberHandle) scrubberHandle.style.left = `${pct}%`;
  }, 1000);

  /* ============================================================================
     7. CROSS-PLATFORM DOWNLOAD TAB SELECTOR
     ============================================================================ */
  const tabButtons = document.querySelectorAll('.platform-tabs .tab-btn');
  const downloadCards = {
    windows: document.getElementById('pane-windows'),
    linux: document.getElementById('pane-linux'),
    macos: document.getElementById('pane-macos')
  };

  tabButtons.forEach((button) => {
    button.addEventListener('click', () => {
      tabButtons.forEach((btn) => btn.classList.remove('active'));
      button.classList.add('active');

      const platform = button.getAttribute('data-platform');

      Object.values(downloadCards).forEach((card) => {
        if (card) card.classList.remove('active');
      });

      if (downloadCards[platform]) {
        downloadCards[platform].classList.add('active');
      }
    });
  });

  /* ============================================================================
     8. SMART NAVBAR SCROLL BLUR ENHANCEMENT
     ============================================================================ */
  const navbar = document.getElementById('navbar');
  if (navbar) {
    window.addEventListener('scroll', () => {
      if (window.scrollY > 30) {
        navbar.style.background = 'rgba(0, 0, 0, 0.82)';
        navbar.style.borderBottomColor = 'rgba(255, 255, 255, 0.16)';
        navbar.style.boxShadow = '0 10px 30px rgba(0, 0, 0, 0.6)';
      } else {
        navbar.style.background = 'rgba(0, 0, 0, 0.72)';
        navbar.style.borderBottomColor = 'rgba(255, 255, 255, 0.1)';
        navbar.style.boxShadow = 'none';
      }
    });
  }

  // Smooth scroll for anchor links
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener('click', function (e) {
      const targetId = this.getAttribute('href');
      if (targetId === '#') return;
      const targetEl = document.querySelector(targetId);
      if (targetEl) {
        e.preventDefault();
        targetEl.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    });
  });
})();
