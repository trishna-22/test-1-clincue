// Test 1 Clinicue - Shared Core Module
(function() {
    // Theme Manager
    const initTheme = () => {
        const savedTheme = localStorage.getItem('clinicue-theme') || 'dark';
        document.documentElement.setAttribute('data-theme', savedTheme);
        
        // Add theme button event listener if button exists
        const btn = document.getElementById('theme-toggle');
        if (btn) {
            btn.innerHTML = savedTheme === 'dark' ? '☀️' : '🌙';
            btn.addEventListener('click', () => {
                const currentTheme = document.documentElement.getAttribute('data-theme');
                const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                document.documentElement.setAttribute('data-theme', newTheme);
                localStorage.setItem('clinicue-theme', newTheme);
                btn.innerHTML = newTheme === 'dark' ? '☀️' : '🌙';
            });
        }
    };

    // Progress Manager
    const getProgress = () => {
        const progress = localStorage.getItem('clinicue-progress');
        return progress ? JSON.parse(progress) : {};
    };

    const saveProgress = (progress) => {
        localStorage.setItem('clinicue-progress', JSON.stringify(progress));
        // Dispatch custom event to notify update
        window.dispatchEvent(new CustomEvent('progressUpdated'));
    };

    const getProcedureProgress = (slug, totalSteps) => {
        const progress = getProgress();
        const checkedSteps = progress[slug] || [];
        const percent = totalSteps > 0 ? Math.round((checkedSteps.length / totalSteps) * 100) : 0;
        return {
            checkedSteps,
            percent,
            completed: percent === 100
        };
    };

    const toggleStep = (slug, stepIndex, totalSteps) => {
        const progress = getProgress();
        if (!progress[slug]) progress[slug] = [];
        
        const idx = progress[slug].indexOf(stepIndex);
        if (idx > -1) {
            progress[slug].splice(idx, 1);
        } else {
            progress[slug].push(stepIndex);
        }
        
        saveProgress(progress);
        return getProcedureProgress(slug, totalSteps);
    };

    // Text to Speech / Narration Engine
    class SpeechNarrator {
        constructor() {
            this.synth = window.speechSynthesis;
            this.utterance = null;
            this.steps = [];
            this.currentStepIdx = -1;
            this.isPlaying = false;
            this.onStepChange = null;
            this.onStateChange = null;
            this.rate = 0.95; // slightly slower for educational clarity
            
            // Check for synthesis compatibility
            this.supported = 'speechSynthesis' in window;
        }

        setSteps(steps) {
            this.steps = steps;
            this.currentStepIdx = -1;
        }

        speakStep(index) {
            if (!this.supported || index < 0 || index >= this.steps.length) return;
            
            this.synth.cancel();
            this.currentStepIdx = index;
            
            const stepText = this.steps[index];
            this.utterance = new SpeechSynthesisUtterance(stepText);
            this.utterance.rate = this.rate;
            
            // Apply a nice English voice if available
            const voices = this.synth.getVoices();
            const englishVoice = voices.find(voice => voice.lang.startsWith('en') && voice.name.includes('Google')) ||
                                voices.find(voice => voice.lang.startsWith('en'));
            if (englishVoice) {
                this.utterance.voice = englishVoice;
            }

            this.utterance.onend = () => {
                if (this.isPlaying) {
                    if (this.currentStepIdx < this.steps.length - 1) {
                        this.speakStep(this.currentStepIdx + 1);
                    } else {
                        this.stop();
                    }
                }
            };

            this.utterance.onerror = (e) => {
                console.error("Speech Synthesis Error:", e);
                this.stop();
            };

            if (this.onStepChange) {
                this.onStepChange(this.currentStepIdx);
            }

            this.synth.speak(this.utterance);
        }

        play() {
            if (!this.supported || this.steps.length === 0) return;
            this.isPlaying = true;
            if (this.onStateChange) this.onStateChange(true);
            
            if (this.currentStepIdx === -1 || this.currentStepIdx === this.steps.length - 1) {
                this.speakStep(0);
            } else {
                // Resume or restart current step
                this.speakStep(this.currentStepIdx);
            }
        }

        pause() {
            if (!this.supported) return;
            this.isPlaying = false;
            this.synth.cancel();
            if (this.onStateChange) this.onStateChange(false);
        }

        stop() {
            if (!this.supported) return;
            this.isPlaying = false;
            this.currentStepIdx = -1;
            this.synth.cancel();
            if (this.onStateChange) this.onStateChange(false);
            if (this.onStepChange) this.onStepChange(-1);
        }
    }

    // Export variables globally
    window.Clinicue = {
        initTheme,
        getProgress,
        getProcedureProgress,
        toggleStep,
        SpeechNarrator: new SpeechNarrator()
    };

    // Auto init on page load
    document.addEventListener('DOMContentLoaded', () => {
        initTheme();
        // Load voices initially (helps SpeechSynthesis cache voices list)
        if ('speechSynthesis' in window) {
            window.speechSynthesis.getVoices();
        }
    });
})();
