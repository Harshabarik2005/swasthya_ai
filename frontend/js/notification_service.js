/**
 * Global Notification Service
 * Checks for due reminders every 10 seconds and triggers notifications.
 * Works across all pages where this script is included.
 */

(function() {
    // Request permission immediately if not denied
    if ("Notification" in window && Notification.permission !== "denied" && Notification.permission !== "granted") {
        Notification.requestPermission();
    }

    function checkGlobalReminders() {
        const reminders = JSON.parse(localStorage.getItem("wellness_reminders") || "[]");
        const now = new Date();
        let updated = false;

        reminders.forEach(r => {
            if (!r.notified) {
                const reminderTime = new Date(`${r.date}T${r.time}`);
                // Check if time has passed (within the last minute to avoid old spam)
                // But for simplicity, if it's past time and not notified, we notify.
                if (now >= reminderTime) {
                    showGlobalNotification(r.activity);
                    r.notified = true;
                    updated = true;
                }
            }
        });

        if (updated) {
            localStorage.setItem("wellness_reminders", JSON.stringify(reminders));
            // Dispatch event so reminders.html can update its list if open
            window.dispatchEvent(new Event('remindersUpdated'));
        }
    }

    function showGlobalNotification(activity) {
        // 1. Browser Notification (Visible even if tab is background)
        if ("Notification" in window && Notification.permission === "granted") {
            new Notification("Wellness Reminder 🌿", {
                body: `It's time for your ${activity}!`,
                icon: "images/logo.png", // Ensure this path is correct or generic
                requireInteraction: true // Keep it visible until clicked
            });
        }

        // 2. Audio Alert
        try {
            const audio = new Audio('https://actions.google.com/sounds/v1/alarms/beep_short.ogg');
            audio.play().catch(e => console.log("Audio play failed (user interaction needed first)", e));
        } catch (e) {
            console.error(e);
        }

        // 3. In-app Alert (Only if tab is focused, otherwise it might be annoying or blocked)
        if (!document.hidden) {
             // Create a custom toast instead of alert() to not block UI
             createToast(`🔔 It's time for your ${activity}!`);
        }
    }

    function createToast(message) {
        const toast = document.createElement('div');
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #00a67e;
            color: white;
            padding: 15px 25px;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            z-index: 10000;
            font-family: 'Poppins', sans-serif;
            animation: slideIn 0.5s ease-out;
            display: flex;
            align-items: center;
            gap: 10px;
        `;
        toast.innerHTML = `<span>${message}</span>`;
        
        document.body.appendChild(toast);

        // Add keyframes if not exists
        if (!document.getElementById('toast-style')) {
            const style = document.createElement('style');
            style.id = 'toast-style';
            style.innerHTML = `
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
                @keyframes fadeOut {
                    from { opacity: 1; }
                    to { opacity: 0; }
                }
            `;
            document.head.appendChild(style);
        }

        setTimeout(() => {
            toast.style.animation = 'fadeOut 0.5s ease-out';
            setTimeout(() => toast.remove(), 500);
        }, 5000);
    }

    // Start checking
    setInterval(checkGlobalReminders, 10000); // Check every 10 seconds
    
    // Initial check
    checkGlobalReminders();

})();
