// Streaks tracking
document.addEventListener('DOMContentLoaded', function() {
    const currentUser = localStorage.getItem('currentUser');
    if (!currentUser) {
        window.location.href = 'index.html';
        return;
    }

    loadStreakData();
    updateActivityCalendar();
    updateMotivationText();
});

function loadStreakData() {
    const currentUser = localStorage.getItem('currentUser');
    const users = JSON.parse(localStorage.getItem('users') || '[]');
    const user = users.find(u => u.email === currentUser);

    if (!user) return;

    // Calculate current streak
    const completedSessions = getCompletedSessions();
    const currentStreak = calculateCurrentStreak(completedSessions);
    const longestStreak = user.longestStreak || 0;
    const totalSessions = completedSessions.length;

    document.getElementById('currentStreak').textContent = currentStreak;
    document.getElementById('longestStreak').textContent = Math.max(currentStreak, longestStreak);
    document.getElementById('totalSessions').textContent = totalSessions;

    // Update user's longest streak
    if (currentStreak > longestStreak) {
        user.longestStreak = currentStreak;
        const usersArray = JSON.parse(localStorage.getItem('users') || '[]');
        const userIndex = usersArray.findIndex(u => u.email === currentUser);
        if (userIndex !== -1) {
            usersArray[userIndex] = user;
            localStorage.setItem('users', JSON.stringify(usersArray));
        }
    }
}

function getCompletedSessions() {
    const currentUser = localStorage.getItem('currentUser');
    const completedSessions = JSON.parse(localStorage.getItem('completedSessions') || '[]');
    return completedSessions.filter(s => s.userEmail === currentUser);
}

function calculateCurrentStreak(sessions) {
    if (sessions.length === 0) return 0;

    // Sort sessions by date
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

function updateActivityCalendar() {
    const calendar = document.getElementById('activityCalendar');
    if (!calendar) return;

    const completedSessions = getCompletedSessions();
    const last30Days = Array.from({ length: 30 }, (_, i) => {
        const date = new Date();
        date.setDate(date.getDate() - i);
        return date;
    });

    calendar.innerHTML = last30Days.map(date => {
        const dateStr = date.toISOString().split('T')[0];
        const hasSession = completedSessions.some(s => s.date.startsWith(dateStr));
        
        return `<div class="calendar-day ${hasSession ? 'active' : ''}">
            <span class="day-date">${date.getDate()}</span>
        </div>`;
    }).join('');
}

function updateMotivationText() {
    const currentStreak = parseInt(document.getElementById('currentStreak').textContent);
    const motivations = [
        "Keep up the great work! Every day counts! 🌟",
        "You're doing amazing! Don't give up now! 💪",
        "Consistency is key! You're building great habits! 🔥",
        "Small steps lead to big results! Keep going! ⭐",
        "You're on a roll! Maintain this momentum! 🚀",
        "Your future self will thank you! Keep it up! 💚"
    ];

    const motivationIndex = Math.min(currentStreak, motivations.length - 1);
    document.getElementById('motivationText').textContent = motivations[motivationIndex];
}


