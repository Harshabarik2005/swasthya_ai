// Authentication handling
document.addEventListener('DOMContentLoaded', function() {
    const signUpForm = document.getElementById('signUpForm');
    const signInForm = document.getElementById('signInForm');

    // Handle Sign Up
    if (signUpForm) {
        signUpForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const name = document.getElementById('name').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirmPassword').value;

            // Validation
            if (password !== confirmPassword) {
                alert('Passwords do not match!');
                return;
            }

            if (password.length < 8) {
                alert('Password must be at least 8 characters long!');
                return;
            }

            // Store user data
            const userData = {
                name: name,
                email: email,
                password: password,
                joinedDate: new Date().toISOString(),
                streak: 0,
                longestStreak: 0,
                totalSessions: 0
            };

            // Check if email already exists
            const existingUsers = JSON.parse(localStorage.getItem('users') || '[]');
            if (existingUsers.find(u => u.email === email)) {
                alert('Email already registered! Please sign in.');
                return;
            }

            existingUsers.push(userData);
            localStorage.setItem('users', JSON.stringify(existingUsers));

            // Store current user
            localStorage.setItem('currentUser', email);

            alert('Account created successfully! Redirecting to dashboard...');
            window.location.href = 'dashboard.html';
        });
    }

    // Handle Sign In
    if (signInForm) {
        signInForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const errorMessage = document.getElementById('errorMessage');

            const users = JSON.parse(localStorage.getItem('users') || '[]');
            const user = users.find(u => u.email === email && u.password === password);

            if (user) {
                // Clear any previous error
                if (errorMessage) {
                    errorMessage.style.display = 'none';
                }
                localStorage.setItem('currentUser', email);
                window.location.href = 'dashboard.html';
            } else {
                // Show error message
                if (errorMessage) {
                    errorMessage.textContent = '❌ Invalid email or password! Please try again or sign up.';
                    errorMessage.style.display = 'block';
                } else {
                    alert('Invalid email or password!');
                }
            }
        });

        // Clear error message when user starts typing
        const emailInput = document.getElementById('email');
        const passwordInput = document.getElementById('password');
        
        if (emailInput) {
            emailInput.addEventListener('input', function() {
                const errorMessage = document.getElementById('errorMessage');
                if (errorMessage) errorMessage.style.display = 'none';
            });
        }
        
        if (passwordInput) {
            passwordInput.addEventListener('input', function() {
                const errorMessage = document.getElementById('errorMessage');
                if (errorMessage) errorMessage.style.display = 'none';
            });
        }
    }

    // Check if already logged in
    const currentUser = localStorage.getItem('currentUser');
    if (currentUser && window.location.pathname.includes('auth.html')) {
        window.location.href = 'dashboard.html';
    }

    if (currentUser && window.location.pathname.includes('get-started.html')) {
        window.location.href = 'dashboard.html';
    }
});

