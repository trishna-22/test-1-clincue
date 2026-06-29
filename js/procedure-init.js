// Test 1 Clinicue - Procedure Initialization and UI Sync Engine
(function() {
    window.initProcedurePage = function(config) {
        const { slug, totalSteps, steps, stepDescriptions } = config;
        
        // State
        let activeTab = 'audio';
        let isAudioPlaying = false;
        let isCombinedPlaying = false;
        let combinedCurrentSlide = 0;
        let combinedInterval = null;
        let ambientAudio = null;

        // Elements
        const tabBtns = document.querySelectorAll('.mode-tab');
        const tabViews = document.querySelectorAll('.mode-view');
        
        // Progress elements
        const progressPctEl = document.getElementById('procedure-progress-pct');
        const progressBarEl = document.getElementById('procedure-progress-bar');
        
        // Audio Tab elements
        const audioPlayBtn = document.getElementById('audio-play-btn');
        const audioProgressSlider = document.getElementById('audio-progress');
        const audioTimeCurrent = document.getElementById('audio-time-current');
        const audioTimeTotal = document.getElementById('audio-time-total');
        const audioVolumeSlider = document.getElementById('audio-volume');
        const ambientAudioEl = document.getElementById('ambient-audio-player');
        
        // Combined Tab elements
        const videoElement = document.getElementById('procedure-video-element');
        const slideNumEl = document.getElementById('slide-number');
        const slideTextEl = document.getElementById('slide-text');
        const slideTrackEl = document.getElementById('slide-tracker');
        const combinedPlayBtn = document.getElementById('combined-play-btn');
        const combinedPrevBtn = document.getElementById('combined-prev-btn');
        const combinedNextBtn = document.getElementById('combined-next-btn');

        // Setup Ambient Audio Track (MP3)
        if (ambientAudioEl) {
            ambientAudio = ambientAudioEl;
            ambientAudio.volume = 0.15; // Set ambient sound soft
            ambientAudio.loop = true;
        }

        // Initialize progress
        function updateProgressUI() {
            const info = Clinicue.getProcedureProgress(slug, totalSteps);
            if (progressPctEl) progressPctEl.textContent = `${info.percent}%`;
            if (progressBarEl) progressBarEl.style.width = `${info.percent}%`;
            
            // Check matching checkboxes
            info.checkedSteps.forEach(idx => {
                const check = document.getElementById(`step-check-${idx}`);
                const card = document.getElementById(`step-card-${idx}`);
                if (check) check.classList.add('checked');
                if (card) card.classList.add('completed');
            });
        }

        // Checklist setup
        const checklistContainer = document.getElementById('checklist-steps-container');
        if (checklistContainer) {
            checklistContainer.innerHTML = '';
            steps.forEach((stepTitle, idx) => {
                const desc = stepDescriptions[idx];
                const card = document.createElement('div');
                card.className = 'step-card glass';
                card.id = `step-card-${idx}`;
                card.innerHTML = `
                    <span class="step-number" id="step-number-${idx}">${idx + 1}</span>
                    <div class="step-header">
                        <h3 class="step-title">${stepTitle}</h3>
                        <div class="step-status-check" id="step-check-${idx}" data-idx="${idx}">✓</div>
                    </div>
                    <p class="step-desc" style="font-size: 14px; color: var(--text-muted);">${desc}</p>
                    <button class="btn-secondary speak-step-btn" data-idx="${idx}" style="padding: 6px 12px; font-size: 12px; margin-top: 12px;">🔊 Read Step</button>
                `;
                checklistContainer.appendChild(card);
            });

            // Event Delegation for Checkbox and Read Step buttons
            checklistContainer.addEventListener('click', (e) => {
                const checkBtn = e.target.closest('.step-status-check');
                if (checkBtn) {
                    const idx = parseInt(checkBtn.getAttribute('data-idx'));
                    const info = Clinicue.toggleStep(slug, idx, totalSteps);
                    
                    // Update classes
                    checkBtn.classList.toggle('checked');
                    document.getElementById(`step-card-${idx}`).classList.toggle('completed');
                    
                    // Update global headers
                    updateProgressUI();
                    return;
                }

                const speakBtn = e.target.closest('.speak-step-btn');
                if (speakBtn) {
                    const idx = parseInt(speakBtn.getAttribute('data-idx'));
                    // Read step aloud
                    Clinicue.SpeechNarrator.stop();
                    Clinicue.SpeechNarrator.setSteps([steps[idx] + ". " + stepDescriptions[idx]]);
                    Clinicue.SpeechNarrator.speakStep(0);
                }
            });
        }

        // Tab Switching
        tabBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const targetTab = btn.getAttribute('data-mode');
                if (targetTab === activeTab) return;

                // Deactivate current
                document.querySelector('.mode-tab.active').classList.remove('active');
                document.querySelector('.mode-view.active').classList.remove('active');

                // Stop all audio/video
                stopAudioNarration();
                stopCombinedNarration();
                if (videoElement) {
                    videoElement.pause();
                }

                // Activate target
                btn.classList.add('active');
                const view = document.getElementById(`${targetTab}-view`);
                if (view) view.classList.add('active');
                
                activeTab = targetTab;
            });
        });

        // ------------------ AUDIO DECK CONTROLS ------------------
        const fullProceduralNarration = steps.map((s, i) => `Step ${i+1}. ${s}. ${stepDescriptions[i]}.`);
        
        function updateAudioDeckUI(isPlaying) {
            const deck = document.getElementById('audio-deck-element');
            if (!deck) return;
            if (isPlaying) {
                deck.classList.add('playing');
                audioPlayBtn.innerHTML = '⏸️';
            } else {
                deck.classList.remove('playing');
                audioPlayBtn.innerHTML = '▶️';
            }
        }

        function playAudioNarration() {
            isAudioPlaying = true;
            updateAudioDeckUI(true);
            
            // Set narration steps
            Clinicue.SpeechNarrator.setSteps(fullProceduralNarration);
            
            // Sync step callback to highlight step card
            Clinicue.SpeechNarrator.onStepChange = (idx) => {
                // Highlight corresponding step card in Checklist
                document.querySelectorAll('.step-card.active-narration').forEach(c => c.classList.remove('active-narration'));
                if (idx >= 0) {
                    const card = document.getElementById(`step-card-${idx}`);
                    if (card) {
                        card.classList.add('active-narration');
                        card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                    }
                    // Update progress slider
                    const pct = Math.round(((idx + 1) / steps.length) * 100);
                    if (audioProgressSlider) audioProgressSlider.value = pct;
                    if (audioTimeCurrent) audioTimeCurrent.textContent = `Step ${idx + 1}`;
                } else {
                    if (audioProgressSlider) audioProgressSlider.value = 0;
                    if (audioTimeCurrent) audioTimeCurrent.textContent = `0:00`;
                }
            };

            Clinicue.SpeechNarrator.onStateChange = (playing) => {
                isAudioPlaying = playing;
                updateAudioDeckUI(playing);
                if (!playing && ambientAudio) {
                    ambientAudio.pause();
                }
            };

            // Play background ambient music
            if (ambientAudio) {
                ambientAudio.play().catch(e => console.log("Ambient Audio Playblocked:", e));
            }

            // Speak
            Clinicue.SpeechNarrator.play();
        }

        function stopAudioNarration() {
            isAudioPlaying = false;
            updateAudioDeckUI(false);
            Clinicue.SpeechNarrator.stop();
            if (ambientAudio) {
                ambientAudio.pause();
            }
            document.querySelectorAll('.step-card.active-narration').forEach(c => c.classList.remove('active-narration'));
        }

        if (audioPlayBtn) {
            audioPlayBtn.addEventListener('click', () => {
                if (isAudioPlaying) {
                    stopAudioNarration();
                } else {
                    playAudioNarration();
                }
            });
        }

        if (audioVolumeSlider) {
            audioVolumeSlider.addEventListener('input', (e) => {
                if (ambientAudio) {
                    ambientAudio.volume = parseFloat(e.target.value);
                }
            });
        }

        // ------------------ COMBINED MODE CONTROLS ------------------
        function updateCombinedUI(isPlaying) {
            if (combinedPlayBtn) {
                combinedPlayBtn.innerHTML = isPlaying ? '⏸️ Pause Auto Guide' : '▶️ Start Auto Guide';
                combinedPlayBtn.className = isPlaying ? 'btn-primary interactive-play-btn' : 'btn-secondary interactive-play-btn';
            }
        }

        function displaySlide(idx) {
            combinedCurrentSlide = idx;
            if (slideNumEl) slideNumEl.textContent = `0${idx + 1}`;
            if (slideTextEl) {
                slideTextEl.innerHTML = `
                    <strong style="display:block; font-size: 22px; color: var(--accent); margin-bottom: 12px;">${steps[idx]}</strong>
                    <span>${stepDescriptions[idx]}</span>
                `;
            }
            if (slideTrackEl) {
                slideTrackEl.textContent = `Step ${idx + 1} of ${steps.length}`;
            }

            // Highlighting
            document.querySelectorAll('.step-card.active-narration').forEach(c => c.classList.remove('active-narration'));
            const card = document.getElementById(`step-card-${idx}`);
            if (card) {
                card.classList.add('active-narration');
                card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
        }

        function playCombinedNarration() {
            isCombinedPlaying = true;
            updateCombinedUI(true);

            // Read the current slide
            const speakCurrentSlide = () => {
                const text = `Step ${combinedCurrentSlide + 1}. ${steps[combinedCurrentSlide]}. ${stepDescriptions[combinedCurrentSlide]}.`;
                Clinicue.SpeechNarrator.stop();
                Clinicue.SpeechNarrator.setSteps([text]);
                
                Clinicue.SpeechNarrator.onStateChange = (playing) => {
                    if (!playing && isCombinedPlaying) {
                        // Move to next slide after a short delay
                        setTimeout(() => {
                            if (isCombinedPlaying) {
                                if (combinedCurrentSlide < steps.length - 1) {
                                    combinedCurrentSlide++;
                                    displaySlide(combinedCurrentSlide);
                                    speakCurrentSlide();
                                } else {
                                    stopCombinedNarration();
                                }
                            }
                        }, 1200);
                    }
                };

                Clinicue.SpeechNarrator.play();
            };

            displaySlide(combinedCurrentSlide);
            speakCurrentSlide();
        }

        function stopCombinedNarration() {
            isCombinedPlaying = false;
            updateCombinedUI(false);
            Clinicue.SpeechNarrator.stop();
            document.querySelectorAll('.step-card.active-narration').forEach(c => c.classList.remove('active-narration'));
        }

        if (combinedPlayBtn) {
            combinedPlayBtn.addEventListener('click', () => {
                if (isCombinedPlaying) {
                    stopCombinedNarration();
                } else {
                    playCombinedNarration();
                }
            });
        }

        if (combinedPrevBtn) {
            combinedPrevBtn.addEventListener('click', () => {
                const wasPlaying = isCombinedPlaying;
                stopCombinedNarration();
                if (combinedCurrentSlide > 0) {
                    combinedCurrentSlide--;
                    displaySlide(combinedCurrentSlide);
                    if (wasPlaying) playCombinedNarration();
                }
            });
        }

        if (combinedNextBtn) {
            combinedNextBtn.addEventListener('click', () => {
                const wasPlaying = isCombinedPlaying;
                stopCombinedNarration();
                if (combinedCurrentSlide < steps.length - 1) {
                    combinedCurrentSlide++;
                    displaySlide(combinedCurrentSlide);
                    if (wasPlaying) playCombinedNarration();
                }
            });
        }

        // Initialize UI
        updateProgressUI();
        displaySlide(0);
    };
})();
