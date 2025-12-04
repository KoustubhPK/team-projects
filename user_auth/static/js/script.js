document.addEventListener('DOMContentLoaded', () => {
    const registerForm = document.getElementById('registerForm');
    const loginForm = document.getElementById('loginForm');
    const messageDiv = document.getElementById('message');

    // --------------------
    // REGISTER
    // --------------------
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const data = {
                username: registerForm.username.value,
                email: registerForm.email.value,
                password: registerForm.password.value
            };

            const res = await fetch('/api/register', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });

            const result = await res.json();

            messageDiv.innerHTML =
                `<div class="alert alert-${res.ok ? 'success' : 'danger'}">
                    ${result.message}
                </div>`;

            if (res.ok) registerForm.reset();
        });
    }

    // --------------------
    // LOGIN
    // --------------------
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
    
            const data = {
                email: loginForm.email.value,
                password: loginForm.password.value
            };

            const res = await fetch('/api/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });

            const result = await res.json();
            if (!res.ok) {
                // Show ONLY error messages
                messageDiv.innerHTML = `
                    <div class="alert alert-danger">${result.message}</div>
                `;
                return;
            }
            window.location.href = '/profile_page';
        });
    }
});