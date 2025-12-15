// Recommendations logic
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('recommendationForm');

    form.addEventListener('submit', function(e) {
        e.preventDefault();

        const formData = new FormData(form);
        const data = {
            age: parseInt(formData.get('age')),
            gender: formData.get('gender'),
            activityLevel: formData.get('activityLevel'),
            problem: formData.get('problem'),
            severity: formData.get('severity'),
            experience: formData.get('experience'),
            timeAvailable: parseInt(formData.get('timeAvailable')),
            timeOfDay: formData.get('timeOfDay'),
            daysPerWeek: parseInt(formData.get('daysPerWeek')),
            styles: Array.from(form.querySelectorAll('input[name="styles"]:checked')).map(cb => cb.value),
            injuries: formData.get('anyInjuries'),
            additionalInfo: formData.get('additionalInfo'),
            date: new Date().toISOString()
        };

        // Generate personalized recommendations
        const recommendations = generateRecommendations(data);

        // Store the recommendations
        storeRecommendation(data, recommendations);

        // Show results page
        showResultsPage(recommendations, data);
    });
});

function generateRecommendations(data) {
    let sessions = [];

    // Generate sessions based on the user's profile
    const daysPerWeek = data.daysPerWeek || 5;
    const timePerSession = data.timeAvailable || 30;
    const styles = data.styles.length > 0 ? data.styles : ['yoga', 'stretching'];

    // Create a 7-day plan
    for (let day = 1; day <= 7; day++) {
        const style = styles[day % styles.length];
        const duration = timePerSession;
        
        sessions.push({
            day: day,
            title: getSessionTitle(style, data.experience),
            duration: duration,
            style: style,
            description: getSessionDescription(style, data.problem, data.experience),
            exercises: generateExercises(style, duration, data.experience, data.problem)
        });
    }

    return sessions;
}

function getSessionTitle(style, experience) {
    const titles = {
        'yoga': {
            'beginner': 'Gentle Yoga Flow',
            'intermediate': 'Vinyasa Yoga Practice',
            'advanced': 'Power Yoga Session'
        },
        'meditation': {
            'beginner': 'Guided Mindfulness',
            'intermediate': 'Deep Meditation',
            'advanced': 'Advanced Contemplation'
        },
        'stretching': {
            'beginner': 'Basic Stretching',
            'intermediate': 'Full Body Stretch',
            'advanced': 'Advanced Flexibility'
        },
        'breathing': {
            'beginner': 'Relaxing Breath Work',
            'intermediate': 'Pranayama Practice',
            'advanced': 'Advanced Breathing Techniques'
        },
        'strength': {
            'beginner': 'Bodyweight Strength',
            'intermediate': 'Resistance Training',
            'advanced': 'Intensive Strength Workout'
        },
        'cardio': {
            'beginner': 'Light Cardio',
            'intermediate': 'Moderate Cardio',
            'advanced': 'High Intensity Cardio'
        }
    };
    return titles[style]?.[experience] || `${style} Session`;
}

function getSessionDescription(style, problem, experience) {
    const descriptions = {
        'yoga': 'Improve flexibility, strength, and mental clarity with this yoga session.',
        'meditation': 'Calm your mind and reduce stress with guided meditation practices.',
        'stretching': 'Increase mobility and reduce tension through targeted stretching.',
        'breathing': 'Enhance your breath control and relaxation through breathing exercises.',
        'strength': 'Build functional strength with bodyweight exercises.',
        'cardio': 'Boost cardiovascular health with energizing movements.'
    };
    return descriptions[style] || 'A personalized wellness session designed for you.';
}

function generateExercises(style, duration, experience, problem) {
    const exercises = [];
    const timePerExercise = Math.floor(duration / 3);

    for (let i = 0; i < 3; i++) {
        exercises.push({
            name: `${style} Exercise ${i + 1}`,
            duration: timePerExercise,
            instructions: `Focus on ${style} techniques for ${timePerExercise} minutes.`
        });
    }

    return exercises;
}

function storeRecommendation(data, recommendations) {
    const currentUser = localStorage.getItem('currentUser');
    if (!currentUser) return;

    const storedRecommendations = JSON.parse(localStorage.getItem('recommendations') || '{}');
    
    const recommendationId = Date.now().toString();
    storedRecommendations[recommendationId] = {
        id: recommendationId,
        userEmail: currentUser,
        profile: data,
        sessions: recommendations,
        created: new Date().toISOString(),
        completed: []
    };

    localStorage.setItem('recommendations', JSON.stringify(storedRecommendations));
    localStorage.setItem('currentRecommendation', recommendationId);
}

function showResultsPage(recommendations, data) {
    const resultsHTML = `
        <div class="results-container">
            <h2>Your Personalized Plan is Ready!</h2>
            <p class="subtitle">Based on your preferences, we've created a 7-day wellness program</p>
            
            <div class="plan-summary">
                <div class="summary-item">
                    <span class="summary-label">Duration:</span>
                    <span class="summary-value">${data.timeAvailable} minutes per session</span>
                </div>
                <div class="summary-item">
                    <span class="summary-label">Frequency:</span>
                    <span class="summary-value">${data.daysPerWeek} days per week</span>
                </div>
                <div class="summary-item">
                    <span class="summary-label">Focus:</span>
                    <span class="summary-value">${data.problem}</span>
                </div>
            </div>

            <div class="sessions-preview">
                ${recommendations.map((session, index) => `
                    <div class="session-card">
                        <div class="session-day">Day ${session.day}</div>
                        <h3>${session.title}</h3>
                        <p>${session.description}</p>
                        <div class="session-meta">
                            <span>⏱️ ${session.duration} min</span>
                            <span>${session.style.charAt(0).toUpperCase() + session.style.slice(1)}</span>
                        </div>
                    </div>
                `).join('')}
            </div>

            <div class="action-buttons">
                <button onclick="window.location.href='dashboard.html'" class="button primary">Start My Journey</button>
                <button onclick="window.location.href='recommendations.html'" class="button secondary">Modify Preferences</button>
            </div>
        </div>
    `;

    // Create a new page with results
    const newPage = window.open('', '_blank');
    newPage.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Your Recommendations</title>
            <link rel="stylesheet" href="styles/main.css">
        </head>
        <body>${resultsHTML}
        <script>
            const currentUser = localStorage.getItem('currentUser');
            if (!currentUser) {
                window.location.href = 'index.html';
            }
        </script>
        </body>
        </html>
    `);
}


