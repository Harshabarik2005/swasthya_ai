class LanguageManager {
    constructor() {
        this.currentLang = localStorage.getItem('wellness_lang') || 'en';
        this.translations = translations; // Assumes translations.js is loaded
        this.init();
    }

    init() {
        // Apply initial language
        this.setLanguage(this.currentLang);

        // Bind language selector if exists
        const selector = document.getElementById('languageSelector');
        if (selector) {
            selector.value = this.currentLang;
            selector.addEventListener('change', (e) => {
                this.setLanguage(e.target.value);
            });
        }

        // Inject Audio Button
        this.injectAudioButton();
    }

    injectAudioButton() {
        if (document.getElementById('audio-reader-btn')) return;

        const btn = document.createElement('button');
        btn.id = 'audio-reader-btn';
        btn.innerHTML = '🔊';
        btn.title = 'Listen to this page';

        // Styles
        Object.assign(btn.style, {
            position: 'fixed',
            bottom: '20px',
            left: '20px', // Moved to left to avoid chatbot on right
            zIndex: '1000',
            width: '50px',
            height: '50px',
            borderRadius: '50%',
            backgroundColor: '#00a67e', // Primary color
            color: 'white',
            border: 'none',
            fontSize: '24px',
            cursor: 'pointer',
            boxShadow: '0 4px 10px rgba(0,0,0,0.3)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'transform 0.2s, background 0.3s'
        });

        // Hover effect
        btn.onmouseover = () => btn.style.transform = 'scale(1.1)';
        btn.onmouseout = () => btn.style.transform = 'scale(1)';

        // Click event
        btn.onclick = () => this.toggleAudio();

        document.body.appendChild(btn);
    }

    toggleAudio() {
        if (window.speechSynthesis.speaking) {
            window.speechSynthesis.cancel();
            return;
        }
        this.playPageAudio();
    }

    playPageAudio() {
        // Cancel any ongoing speech
        window.speechSynthesis.cancel();

        // Determine text to read - RESTRICTED TO HEADINGS AND LABELS
        let selectors = 'h1, h2, h3, h4, h5, h6, label, .card-title, .feature-title, .hero-title, .hero-subtitle, .page-title, .page-subtitle, .section-title';

        // SPECIAL CASE: For result.html, also read instructions and warnings
        if (window.location.pathname.includes('result.html')) {
            selectors += ', .steps-list li, .warning-banner';
            console.log('Audio: Detected result page, including instructions in selectors.');
        }

        const elements = document.querySelectorAll(selectors);

        console.log('Audio: Searching for elements with selectors:', selectors);

        // Filter visible elements and join their text
        const textParts = [];
        elements.forEach(el => {
            // Check visibility
            if (el.offsetParent !== null && el.innerText.trim().length > 0) {
                textParts.push(el.innerText.trim());
            }
        });

        // Fallback: if no specific headings found, read the first 100 chars of body to prove it works
        let text = textParts.join('. ');
        if (!text.trim()) {
            console.warn('Audio: No headings/labels found. Falling back to body text summary.');
            text = "No headings found. Reading page summary. " + document.body.innerText.substring(0, 100);
        }

        console.log('Audio: Text to read:', text);

        if (!text.trim()) return;

        const utterance = new SpeechSynthesisUtterance(text);

        // Map language codes to BCP 47
        const langMap = {
            'en': 'en-US',
            'te': 'te-IN',
            'kn': 'kn-IN',
            'hi': 'hi-IN'
        };

        const targetLang = langMap[this.currentLang] || 'en-US';
        utterance.lang = targetLang;
        utterance.rate = 0.9;
        utterance.pitch = 1;

        // Visual feedback
        const btn = document.getElementById('audio-reader-btn');
        if (btn) btn.innerHTML = '🛑';

        // Voice Selection Logic
        const voices = window.speechSynthesis.getVoices();
        console.log('Audio: Available voices:', voices.map(v => `${v.name} (${v.lang})`));

        // Try to find an exact match first, then language match
        const selectedVoice = voices.find(v => v.lang === targetLang) ||
            voices.find(v => v.lang.startsWith(targetLang.split('-')[0]));

        if (selectedVoice) {
            console.log('Audio: Selected voice:', selectedVoice.name);
            utterance.voice = selectedVoice;
        } else {
            console.warn('Audio: No matching voice found for', targetLang);
        }

        utterance.onend = () => {
            console.log('Audio: Reading finished.');
            if (btn) btn.innerHTML = '🔊';
        };

        utterance.onerror = (e) => {
            if (btn) btn.innerHTML = '🔊';
            console.error('Audio: Speech synthesis error', e);
            alert("Audio Error: " + (e.error || "Unknown"));
        };

        window.speechSynthesis.speak(utterance);
    }

    setLanguage(lang) {
        if (!this.translations[lang]) return;

        this.currentLang = lang;
        localStorage.setItem('wellness_lang', lang);

        // Update all elements with data-i18n attribute
        const elements = document.querySelectorAll('[data-i18n]');
        elements.forEach(el => {
            const key = el.getAttribute('data-i18n');
            if (this.translations[lang][key]) {
                // Check if element is an input with placeholder
                if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
                    el.placeholder = this.translations[lang][key];
                } else {
                    el.innerHTML = this.translations[lang][key]; // Use innerHTML to support <br>
                }
            }
        });

        // Broadcast event for other components
        window.dispatchEvent(new CustomEvent('languageChanged', { detail: { language: lang } }));
    }

    get(key) {
        return this.translations[this.currentLang][key] || key;
    }
}

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    window.langManager = new LanguageManager();
});
