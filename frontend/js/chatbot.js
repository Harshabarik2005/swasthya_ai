// AI Chatbot with Gemini API
class WellnessChatbot {
  constructor() {
    this.isOpen = false;
    this.messages = [];
    this.userData = null;
    this.API = ""; // Relative path for production
    this.init();
  }

  async init() {
    // Load user session data
    const session = JSON.parse(localStorage.getItem("wellness_session") || "null");
    if (session) {
      this.userData = session;
      await this.loadUserProfile();
    }

    this.createChatbotHTML();
    this.attachEventListeners();
    this.showWelcomeMessage();
  }

  async loadUserProfile() {
    try {
      const res = await fetch(`${this.API}/api/user/${this.userData.email}`);
      const json = await res.json();
      if (json.success) {
        this.userData = { ...this.userData, ...json.user };
      }
      await this.getLastRecommendation();
    } catch (err) {
      console.error("Error loading user profile:", err);
    }
  }

  async getLastRecommendation() {
    try {
      const res = await fetch(`${this.API}/api/history/${this.userData.email}`);
      const json = await res.json();
      if (json.success && json.records && json.records.length > 0) {
        this.lastRecommendation = json.records[0]; // Get the most recent one
      }
    } catch (err) {
      console.error("Error loading history:", err);
    }
  }

  createChatbotHTML() {
    const chatbotHTML = `
      <div id="wellness-chatbot" class="wellness-chatbot">
        <!-- Chat Window -->
        <div id="chatbot-window" class="chatbot-window" style="display: none;">
          <div class="chatbot-header">
            <div class="chatbot-header-content">
              <div class="chatbot-avatar">💚</div>
              <div>
                <h3>Wellness Assistant</h3>
                <p class="chatbot-status">Always here for you</p>
              </div>
            </div>
            <button id="chatbot-minimize" class="chatbot-minimize">−</button>
          </div>
          <div id="chatbot-messages" class="chatbot-messages"></div>
          <div class="chatbot-input-container">
            <input 
              type="text" 
              id="chatbot-input" 
              class="chatbot-input" 
              placeholder="Type your message..."
              autocomplete="off"
            />
            <button id="chatbot-send" class="chatbot-send">➤</button>
          </div>
        </div>
        
        <!-- Floating Button -->
        <div id="chatbot-button" class="chatbot-button">
          <div class="chatbot-button-icon">💬</div>
          <div id="chatbot-popup" class="chatbot-popup">
            <span>Feeling low? I can help you! 😊</span>
          </div>
        </div>
      </div>
    `;

    document.body.insertAdjacentHTML('beforeend', chatbotHTML);
  }

  attachEventListeners() {
    const button = document.getElementById('chatbot-button');
    const minimizeBtn = document.getElementById('chatbot-minimize');
    const sendBtn = document.getElementById('chatbot-send');
    const input = document.getElementById('chatbot-input');

    button.addEventListener('click', () => this.toggleChat());
    minimizeBtn.addEventListener('click', () => this.toggleChat());

    sendBtn.addEventListener('click', () => this.sendMessage());
    input.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        this.sendMessage();
      }
    });
  }

  toggleChat() {
    const window = document.getElementById('chatbot-window');
    const button = document.getElementById('chatbot-button');
    const popup = document.getElementById('chatbot-popup');

    this.isOpen = !this.isOpen;

    if (this.isOpen) {
      window.style.display = 'flex';
      button.style.display = 'none';
      popup.style.display = 'none';
      document.getElementById('chatbot-input').focus();
      this.scrollToBottom();
    } else {
      window.style.display = 'none';
      button.style.display = 'flex';
    }
  }

  showWelcomeMessage() {
    const name = this.userData?.name?.split(' ')[0] || "Friend";
    let messages = [];

    if (this.lastRecommendation) {
      const condition = this.lastRecommendation.condition || "health";
      const pose = this.lastRecommendation.yogapose || "exercises";

      messages = [
        `Hey ${name}! 🌿✨`,
        `How is your ${condition} doing today? Did you try the ${pose}?`,
        "I'm here if you need more tips or just want to chat! 💪"
      ];
    } else {
      messages = [
        `Hey ${name}! 🌿✨`,
        "Ready to prioritize your wellness today?",
        "How are you feeling right now?"
      ];
    }

    messages.forEach((msg, index) => {
      setTimeout(() => {
        this.addMessage(msg, 'bot');
      }, index * 1000);
    });
  }

  addMessage(text, sender) {
    const messagesContainer = document.getElementById('chatbot-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chatbot-message ${sender}`;

    const messageContent = document.createElement('div');
    messageContent.className = 'chatbot-message-content';
    messageContent.textContent = text;

    messageDiv.appendChild(messageContent);
    messagesContainer.appendChild(messageDiv);

    this.messages.push({ text, sender });
    this.scrollToBottom();
  }

  scrollToBottom() {
    const messagesContainer = document.getElementById('chatbot-messages');
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  async sendMessage() {
    const input = document.getElementById('chatbot-input');
    const message = input.value.trim();

    if (!message) return;

    // Add user message to chat
    this.addMessage(message, 'user');
    input.value = '';

    // Show typing indicator
    this.showTypingIndicator();

    try {
      const response = await fetch(`${this.API}/api/chatbot`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          email: this.userData?.email || null,
          conversation_history: this.messages.slice(-10), // Last 10 messages for context
          language: localStorage.getItem('wellness_lang') || 'en'
        })
      });

      const data = await response.json();
      this.hideTypingIndicator();

      if (!response.ok) {
        console.error('API Error:', data);
        const errorMsg = data.error || data.details || "Unknown error occurred";
        this.addMessage(`I'm sorry, there was an error: ${errorMsg}. Please try again later. 💚`, 'bot');
        return;
      }

      if (data.success && data.response) {
        this.addMessage(data.response, 'bot');
      } else {
        const errorMsg = data.error || "Unable to generate response";
        console.error('Response error:', data);
        this.addMessage(`I'm sorry, I'm having trouble right now: ${errorMsg}. Please try again later. 💚`, 'bot');
      }
    } catch (error) {
      this.hideTypingIndicator();
      console.error('Chatbot network error:', error);
      this.addMessage("I'm sorry, there was a connection error. Please check your internet connection and try again. 💚", 'bot');
    }
  }

  showTypingIndicator() {
    const messagesContainer = document.getElementById('chatbot-messages');
    const typingDiv = document.createElement('div');
    typingDiv.className = 'chatbot-message bot chatbot-typing';
    typingDiv.id = 'typing-indicator';
    typingDiv.innerHTML = `
      <div class="chatbot-message-content">
        <div class="typing-dots">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    `;
    messagesContainer.appendChild(typingDiv);
    this.scrollToBottom();
  }

  hideTypingIndicator() {
    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator) {
      typingIndicator.remove();
    }
  }
}

// Initialize chatbot when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    // Only initialize if user is logged in
    const session = JSON.parse(localStorage.getItem("wellness_session") || "null");
    if (session) {
      window.wellnessChatbot = new WellnessChatbot();
    }
  });
} else {
  const session = JSON.parse(localStorage.getItem("wellness_session") || "null");
  if (session) {
    window.wellnessChatbot = new WellnessChatbot();
  }
}

