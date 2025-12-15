// Dashboard functionality
document.addEventListener('DOMContentLoaded', function() {
    loadDashboardStats();
});

function loadDashboardStats() {
    const currentUser = localStorage.getItem('currentUser');
    if (!currentUser) return;

    const users = JSON.parse(localStorage.getItem('users') || '[]');
    const user = users.find(u => u.email === currentUser);
    
    if (!user) return;

    // Get completed sessions
    const completedSessions = getCompletedSessions();
    const currentStreak = calculateCurrentStreak(completedSessions);
    const longestStreak = user.longestStreak || 0;
    const totalSessions = completedSessions.length;

    // Update displays
    document.getElementById('currentStreakDisplay').textContent = currentStreak + ' days';
    document.getElementById('totalSessionsDisplay').textContent = totalSessions;
    document.getElementById('longestStreakDisplay').textContent = Math.max(currentStreak, longestStreak) + ' days';

    // Update user's longest streak if needed
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


