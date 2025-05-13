document.addEventListener('DOMContentLoaded', function () {
    const loginForm = document.querySelector('form.needs-validation');
    let otpModal, timerInterval;
    let countdownSeconds = 10 * 60;

    if (loginForm) {
        loginForm.addEventListener('submit', async function (e) {
            e.preventDefault();
            e.stopPropagation();

            if (!loginForm.checkValidity()) {
                loginForm.classList.add('was-validated');
                return;
            }

            const submitBtn = loginForm.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Caricamento...';

            try {
                const formData = new FormData(loginForm);
                const response = await fetch('/login', { method: 'POST', body: formData });
                const data = await response.json();

                if (data.show_otp_modal) {
                    otpModal = new bootstrap.Modal(document.getElementById('otpModal'));
                    otpModal.show();
                    setTimeout(() => {
                        document.getElementById('otpInput').focus();
                    }, 500);
                    startOtpCountdown();
                } else if (data.error) {
                    showFlashMessage(data.error, 'danger', 'login');
                }
            } catch (error) {
                console.error('Error:', error);
                showFlashMessage('Errore durante il login', 'danger', 'login');
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="bi bi-box-arrow-in-right me-2"></i> Accedi';
            }
        });
    }

    function startOtpCountdown() {
        countdownSeconds = 10 * 60;
        updateCountdownDisplay();
    
        clearInterval(timerInterval);
        timerInterval = setInterval(() => {
            countdownSeconds--;
            updateCountdownDisplay();
    
            if (countdownSeconds <= 0) {
                clearInterval(timerInterval);
                document.getElementById('otpInput').disabled = true;
                document.getElementById('resendOtpBtn').disabled = false;
                document.getElementById('otpCountdown').textContent = "Tempo scaduto! Richiedi un nuovo OTP.";
            }
        }, 1000);
    }

    function updateCountdownDisplay() {
        const minutes = Math.floor(countdownSeconds / 60).toString().padStart(2, '0');
        const seconds = (countdownSeconds % 60).toString().padStart(2, '0');
        document.getElementById('otpCountdown').textContent = `Tempo rimasto: ${minutes}:${seconds}`;
    }

    const otpForm = document.getElementById('otpForm');
    if (otpForm) {
        otpModal = new bootstrap.Modal(document.getElementById('otpModal'));

        otpForm.addEventListener('submit', async function (e) {
            e.preventDefault();
            const otp = document.getElementById('otpInput').value.trim();
            const verifyBtn = otpForm.querySelector('button[type="submit"]');

            verifyBtn.disabled = true;
            verifyBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Verifica...';

            try {
                const response = await fetch('/verify-otp', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ otp: otp })
                });

                const result = await response.json();
                if (result.success) {
                    clearInterval(timerInterval);
                    otpModal.hide();
                    window.location.href = "/";
                } else {
                    showFlashMessage(result.error || 'Codice OTP errato o scaduto', 'danger', 'otp');
                    document.getElementById('otpInput').value = '';
                }
            } catch (error) {
                console.error('Error:', error);
                showFlashMessage('Errore durante la verifica OTP', 'danger', 'otp');
            } finally {
                verifyBtn.disabled = false;
                verifyBtn.innerHTML = 'Verifica';
            }
        });

        document.getElementById('resendOtpBtn').addEventListener('click', async function () {
            const resendBtn = this;
            const otpField = document.getElementById('otpInput');

            resendBtn.disabled = true;
            resendBtn.innerHTML = 'Invio in corso...';

            try {
                const response = await fetch('/resend-otp', { method: 'POST' });
                const result = await response.json();

                if (result.success) {
                    otpField.disabled = false;
                    otpField.removeAttribute('readonly');
                    otpField.removeAttribute('aria-disabled');
                    otpField.style.pointerEvents = 'auto';
                    otpField.style.opacity = 1;
                    otpField.value = '';
                    otpField.focus();
                    startOtpCountdown();
                } else {
                    showFlashMessage('Errore nel rinviare l\'OTP: ' + (result.error || 'Riprova più tardi'), 'danger', 'otp');
                }
            } catch (error) {
                console.error('Error:', error);
                showFlashMessage('Errore durante il reinvio OTP', 'danger', 'otp');
            } finally {
                resendBtn.disabled = false;
                resendBtn.innerHTML = 'Rinvia OTP';
            }
        });
    }

    function showFlashMessage(message, category, context = 'login') {
        const target = context === 'otp'
            ? document.getElementById('otpAlertsContainer')
            : document.getElementById('loginAlertsContainer');
    
        if (!target) return;
    
        target.innerHTML = '';
    
        const wrapper = document.createElement('div');
    
        if (context === 'otp') {
            wrapper.innerHTML = `
                <div class="alert alert-${category} d-flex justify-content-center align-items-center gap-2 text-center fade show" role="alert">
                    <i class="bi bi-exclamation-triangle-fill fs-5"></i>
                    <span>${message}</span>
                </div>
            `;
        } else {
            wrapper.className = `alert alert-${category} alert-dismissible fade show animated-shake`;
            wrapper.innerHTML = `
                <i class="bi ${category === 'danger' ? 'bi-exclamation-triangle-fill' :
                                category === 'success' ? 'bi-check-circle-fill' :
                                'bi-info-circle-fill'} me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;
        }
    
        target.appendChild(wrapper);
    
        setTimeout(() => {
            wrapper.classList.remove('show');
            setTimeout(() => wrapper.remove(), 500);
        }, 5000);
    }

    const otpInput = document.getElementById('otpInput');
    if (otpInput) {
        otpInput.addEventListener('input', function(e) {
            this.value = this.value.replace(/[^0-9]/g, '');
            
            if (this.value.length > 6) {
                this.value = this.value.slice(0, 6);
            }
        });
    }
});