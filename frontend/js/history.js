// History page functionality
document.addEventListener('DOMContentLoaded', function() {
    const currentUser = localStorage.getItem('currentUser');
    if (!currentUser) {
        window.location.href = 'index.html';
        return;
    }

    loadHistory();
    setupFilter();
});

function loadHistory() {
    const completedSessions = JSON.parse(localStorage.getItem('completedSessions') || '[]');
    const userSessions = completedSessions.filter(s => s.userEmail === localStorage.getItem('currentUser'));
    
    displayStats(userSessions);
    displaySessions(userSessions);
    
    if (userSessions.length === 0) {
        document.getElementById('emptyState').style.display = 'block';
        document.getElementById('historyList').style.display = 'none';
    }
}

function displayStats(sessions) {
    const totalSessions = sessions.length;
    const totalDuration = sessions.reduce((sum, s) => sum + (s.duration || 30), 0);
    const avgRating = sessions.length > 0 ? 
        (sessions.reduce((sum, s) => sum + (s.rating || 0), 0) / sessions.length).toFixed(1) : 0;

    document.getElementById('totalHistorySessions').textContent = totalSessions;
    document.getElementById('totalDuration').textContent = totalDuration;
    document.getElementById('avgRating').textContent = avgRating;
}

function displaySessions(sessions, filter = 'all') {
    const historyList = document.getElementById('historyList');
    if (!historyList) return;

    let filteredSessions = sessions;
    if (filter !== 'all') {
        filteredSessions = sessions.filter(s => s.style === filter);
    }

    // Sort by date (most recent first)
    filteredSessions.sort((a, b) => new Date(b.date) - new Date(a.date));

    if (filteredSessions.length === 0) {
        historyList.innerHTML = '<p>No sessions found for this filter.</p>';
        return;
    }

    historyList.innerHTML = filteredSessions.map(session => {
        const date = new Date(session.date);
        const dateStr = date.toLocaleDateString('en-US', { 
            weekday: 'short', 
            year: 'numeric', 
            month: 'short', 
            day: 'numeric' 
        });
        
        return `
            <div class="history-item">
                <div class="history-icon">${getSessionIcon(session.style)}</div>
                <div class="history-content">
                    <h3>${session.title || 'Wellness Session'}</h3>
                    <div class="history-meta">
                        <span>📅 ${dateStr}</span>
                        <span>⏱️ ${session.duration || 30} min</span>
                        <span>${getRatingStars(session.rating || 0)}</span>
                    </div>
                    <p class="history-description">${session.description || 'Great session!'}</p>
                </div>
            </div>
        `;
    }).join('');
}

function getSessionIcon(style) {
    const icons = {
        'yoga': '🧘',
        'meditation': '🧘‍♀️',
        'stretching': '🤸',
        'breathing': '💨',
        'strength': '💪',
        'cardio': '🏃',
        'default': '🌸'
    };
    return icons[style] || icons['default'];
}

function getRatingStars(rating) {
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    return '⭐'.repeat(fullStars) + (hasHalfStar ? '✨' : '');
}

function setupFilter() {
    const filterSelect = document.getElementById('filterType');
    if (filterSelect) {
        filterSelect.addEventListener('change', function() {
            const completedSessions = JSON.parse(localStorage.getItem('completedSessions') || '[]');
            const userSessions = completedSessions.filter(s => s.userEmail === localStorage.getItem('currentUser'));
            displaySessions(userSessions, this.value);
        });
    }
}


