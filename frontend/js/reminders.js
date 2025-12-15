// Reminders functionality
document.addEventListener('DOMContentLoaded', function() {
    const currentUser = localStorage.getItem('currentUser');
    if (!currentUser) {
        window.location.href = 'index.html';
        return;
    }

    loadSavedReminders();
    setupFormHandlers();
});

function loadSavedReminders() {
    const reminders = JSON.parse(localStorage.getItem('reminders') || '[]');
    const userReminders = reminders.filter(r => r.userEmail === localStorage.getItem('currentUser'));

    if (userReminders.length > 0) {
        const reminder = userReminders[0]; // Get the latest reminder
        document.getElementById('dailyReminder').checked = reminder.enabled;
        document.getElementById('reminderTime').value = reminder.time;
        document.getElementById('reminderType').value = reminder.type;
        
        if (reminder.days) {
            reminder.days.forEach(day => {
                const checkbox = document.querySelector(`input[name="days"][value="${day}"]`);
                if (checkbox) checkbox.checked = true;
            });
        }
    }

    displayActiveReminders(userReminders);
}

function setupFormHandlers() {
    const form = document.getElementById('reminderForm');
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        saveReminders();
    });

    // Update time selector based on checkbox
    document.getElementById('dailyReminder').addEventListener('change', function() {
        const timeSelector = document.getElementById('timeSelector');
        if (this.checked) {
            timeSelector.style.display = 'block';
        } else {
            timeSelector.style.display = 'none';
        }
    });

    // Initialize display
    if (document.getElementById('dailyReminder').checked) {
        document.getElementById('timeSelector').style.display = 'block';
    } else {
        document.getElementById('timeSelector').style.display = 'none';
    }
}

function saveReminders() {
    const enabled = document.getElementById('dailyReminder').checked;
    const time = document.getElementById('reminderTime').value;
    const type = document.getElementById('reminderType').value;
    const selectedDays = Array.from(document.querySelectorAll('input[name="days"]:checked')).map(cb => cb.value);

    if (enabled && !time) {
        alert('Please set a reminder time!');
        return;
    }

    if (enabled && selectedDays.length === 0) {
        alert('Please select at least one day!');
        return;
    }

    const currentUser = localStorage.getItem('currentUser');
    const reminders = JSON.parse(localStorage.getItem('reminders') || '[]');
    const userReminders = reminders.filter(r => r.userEmail !== currentUser);

    const newReminder = {
        userEmail: currentUser,
        enabled: enabled,
        time: time,
        days: selectedDays,
        type: type,
        created: new Date().toISOString()
    };

    if (enabled) {
        userReminders.push(newReminder);
        alert('Reminders saved successfully! You\'ll receive notifications at ' + time);
    } else {
        alert('Reminders disabled.');
    }

    localStorage.setItem('reminders', JSON.stringify(userReminders));
    displayActiveReminders([newReminder]);
}

function displayActiveReminders(reminders) {
    const reminderList = document.getElementById('reminderList');
    if (!reminderList) return;

    if (reminders.length === 0 || !reminders[0].enabled) {
        reminderList.innerHTML = '<p>No active reminders. Set your reminders above to start receiving notifications!</p>';
        return;
    }

    const reminder = reminders[0];
    const daysText = reminder.days.length === 7 ? 'Every day' : 
                     reminder.days.length === 0 ? 'No days selected' :
                     reminder.days.join(', ');

    reminderList.innerHTML = `
        <div class="reminder-display">
            <div class="reminder-time">⏰ ${reminder.time}</div>
            <div class="reminder-days">📅 ${daysText}</div>
            <div class="reminder-type">${getReminderTypeText(reminder.type)}</div>
        </div>
    `;
}

function getReminderTypeText(type) {
    const types = {
        'gentle': '💚 Gentle',
        'motivational': '💪 Motivational',
        'supportive': '🤗 Supportive'
    };
    return types[type] || type;
}


