// Session handling and mock completion
// Updated version - consistent login key + smart redirect

function completeSession(sessionData) {
  const currentUser = JSON.parse(localStorage.getItem("wellness_session"));
  if (!currentUser) {
    alert("Please log in to complete sessions");
    return;
  }

  const completedSessions = JSON.parse(localStorage.getItem("completedSessions") || "[]");

  const newSession = {
    id: Date.now().toString(),
    userEmail: currentUser.email,
    title: sessionData.title,
    style: sessionData.style,
    duration: sessionData.duration,
    description: sessionData.description,
    rating: sessionData.rating || 0,
    date: new Date().toISOString(),
    exercises: sessionData.exercises || []
  };

  completedSessions.push(newSession);
  localStorage.setItem("completedSessions", JSON.stringify(completedSessions));

  return newSession;
}

function getSessionsByStyle(style) {
  const currentUser = JSON.parse(localStorage.getItem("wellness_session"));
  const completedSessions = JSON.parse(localStorage.getItem("completedSessions") || "[]");
  return completedSessions.filter(s => s.userEmail === currentUser?.email && s.style === style);
}

function getTotalSessions() {
  const currentUser = JSON.parse(localStorage.getItem("wellness_session"));
  const completedSessions = JSON.parse(localStorage.getItem("completedSessions") || "[]");
  return completedSessions.filter(s => s.userEmail === currentUser?.email);
}

// ✅ Check authentication only on protected pages
function checkAuth() {
  const currentUser = JSON.parse(localStorage.getItem("wellness_session"));
  const authPages = [
    "dashboard",
    "recommendations",
    "streaks",
    "reminders",
    "history",
    "progress",
    "profile"
  ];

  const currentPage = window.location.pathname.split("/").pop();

  // Only redirect if the page actually needs authentication
  if (authPages.some(page => currentPage.includes(page))) {
    if (!currentUser) {
      window.location.href = "index.html";
      return false;
    }
  }

  return true;
}

// Run authentication check when script loads
if (typeof window !== "undefined") {
  window.addEventListener("DOMContentLoaded", checkAuth);
}
