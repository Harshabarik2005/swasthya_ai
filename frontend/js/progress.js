// Progress tracking
document.addEventListener('DOMContentLoaded', function() {
    const currentUser = localStorage.getItem('currentUser');
    if (!currentUser) {
        window.location.href = 'index.html';
        return;
    }

    loadProgressData();
    updateWeeklyCalendar();
});

function loadProgressData() {
    const completedSessions = getCompletedSessions();
    
    const totalSessions = completedSessions.length;
    const totalDuration = completedSessions.reduce((sum, s) => sum + (s.duration || 30), 0);
    
    // Calculate current streak
    const currentStreak = calculateCurrentStreak(completedSessions);

    document.getElementById('totalProgressSessions').textContent = totalSessions;
    document.getElementById('totalProgressDuration').textContent = totalDuration;
    document.getElementById('currentProgressStreak').textContent = currentStreak;
}

function getCompletedSessions() {
    const currentUser = localStorage.getItem('currentUser');
    const completedSessions = JSON.parse(localStorage.getItem('completedSessions') || '[]');
    return completedSessions.filter(s => s.userEmail === currentUser);
}

function calculateCurrentStreak(sessions) {
    if (sessions.length === 0) return 0;

    const sortedSessions = sessions.sort((a, b) => new Date(b.date) - new Date(a.date));
    
    let streak = 0;
    let currentDate = new Date();
    currentDate.setHours(0, 0, 0, 0);

    for (const session of sortedSessions) {
        const sessionDate = new Date(session.date);
        sessionDate.setHours(0, 0, 0, 0);
        
        const diffDays = Math.floor((currentDate - sessionDate) / (1000 * 60 * 60 * 24));
        
        if (diffDays === streak) {
            streak++;
        } else if (diffDays > streak) {
            break;
        }
    }

    return streak;
}

function updateWeeklyCalendar() {
    const calendar = document.getElementById('weeklyCalendar');
    if (!calendar) return;

    const completedSessions = getCompletedSessions();
    const last7Days = Array.from({ length: 7 }, (_, i) => {
        const date = new Date();
        date.setDate(date.getDate() - (6 - i));
        return date;
    });

    calendar.innerHTML = last7Days.map(date => {
        const dateStr = date.toISOString().split('T')[0];
        const hasSession = completedSessions.some(s => s.date.startsWith(dateStr));
        const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
        
        return `<div class="calendar-day ${hasSession ? 'active' : ''}">
            <span class="day-date">${dayNames[date.getDay()]}</span>
        </div>`;
    }).join('');
}


