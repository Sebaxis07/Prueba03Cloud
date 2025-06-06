lucide.createIcons();

function togglePassword(fieldId) {
    const passwordInput = document.getElementById(fieldId);
    const iconId = fieldId.includes('password1') ? 'togglePassword1Icon' : 'togglePassword2Icon';
    const toggleIcon = document.getElementById(iconId);
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        toggleIcon.setAttribute('data-lucide', 'eye-off');
    } else {
        passwordInput.type = 'password';
        toggleIcon.setAttribute('data-lucide', 'eye');
    }
    lucide.createIcons();
}

const rutInput = document.getElementById('id_rut');
const rutValidIcon = document.getElementById('rutValidIcon');
const rutInvalidIcon = document.getElementById('rutInvalidIcon');

if (rutInput) {
    rutInput.addEventListener('input', function(e) {
        let value = e.target.value;
        
        value = value.replace(/[^0-9kK]/g, '');
        
        if (value.length > 1) {
            let resultado = '';
            let i = 0;
            
            for (i = value.length - 1; i > 0; i--) {
                if (i === value.length - 1) {
                    resultado = '-' + value.charAt(i) + resultado;
                } else if ((value.length - i - 1) % 3 === 0) {
                    resultado = '.' + value.charAt(i) + resultado;
                } else {
                    resultado = value.charAt(i) + resultado;
                }
            }
            resultado = value.charAt(0) + resultado;
            
            e.target.value = resultado;
        }
    });
    
    rutInput.addEventListener('blur', function(e) {
        let rut = e.target.value;
        if (rut && rut.length >= 8) {
            if (validateRut(rut)) {
                if (rutValidIcon) rutValidIcon.classList.remove('hidden');
                if (rutInvalidIcon) rutInvalidIcon.classList.add('hidden');
                rutInput.classList.remove('border-red-500');
                rutInput.classList.add('border-green-500');
            } else {
                if (rutInvalidIcon) rutInvalidIcon.classList.remove('hidden');
                if (rutValidIcon) rutValidIcon.classList.add('hidden');
                rutInput.classList.remove('border-green-500');
                rutInput.classList.add('border-red-500');
            }
        } else {
            if (rutValidIcon) rutValidIcon.classList.add('hidden');
            if (rutInvalidIcon) rutInvalidIcon.classList.add('hidden');
        }
    });
}

function validateRut(rut) {
    // Limpiar RUT
    const cleanRut = rut.replace(/[^0-9kK]/g, '');
    if (cleanRut.length < 8) return false;

    const body = cleanRut.slice(0, -1);
    const dv = cleanRut.slice(-1).toLowerCase();

    let sum = 0;
    let multiplier = 2;

    for (let i = body.length - 1; i >= 0; i--) {
        sum += parseInt(body[i]) * multiplier;
        multiplier = multiplier < 7 ? multiplier + 1 : 2;
    }

    const expectedDv = 11 - (sum % 11);
    const computedDv = expectedDv === 11 ? '0' : expectedDv === 10 ? 'k' : expectedDv.toString();

    return dv === computedDv;
}

const password1 = document.getElementById('id_password1');
const password2 = document.getElementById('id_password2');
const strengthIndicator = document.getElementById('passwordStrength');
const strengthText = document.getElementById('passwordStrengthText');
const passwordMatch = document.getElementById('passwordMatch');

function checkPasswordStrength(password) {
    let score = 0;
    let isCommon = false;

    const commonPasswords = ['password', '123456', '12345678', 'qwerty', 'abc123', 'password123'];
    isCommon = commonPasswords.some(common => password.toLowerCase().includes(common.toLowerCase()));

    const lengthIcon = document.getElementById('req-length')?.querySelector('i');
    if (lengthIcon) {
        if (password.length >= 8) {
            score += 1;
            lengthIcon.setAttribute('data-lucide', 'check-circle');
            lengthIcon.className = 'h-3 w-3 mr-2 text-green-400';
        } else {
            lengthIcon.setAttribute('data-lucide', 'circle');
            lengthIcon.className = 'h-3 w-3 mr-2 text-gray-400';
        }
    }

    const commonIcon = document.getElementById('req-common')?.querySelector('i');
    if (commonIcon) {
        if (!isCommon && password.length > 0) {
            score += 1;
            commonIcon.setAttribute('data-lucide', 'check-circle');
            commonIcon.className = 'h-3 w-3 mr-2 text-green-400';
        } else {
            commonIcon.setAttribute('data-lucide', 'circle');
            commonIcon.className = 'h-3 w-3 mr-2 text-gray-400';
        }
    }

    if (/[A-Z]/.test(password)) score += 1;
    if (/[a-z]/.test(password)) score += 1;
    if (/[0-9]/.test(password)) score += 1;
    if (/[^A-Za-z0-9]/.test(password)) score += 1;

    const numbersIcon = document.getElementById('req-numbers')?.querySelector('i');
    if (numbersIcon) {
        if (!/^\d+$/.test(password) && password.length > 0) {
            numbersIcon.setAttribute('data-lucide', 'check-circle');
            numbersIcon.className = 'h-3 w-3 mr-2 text-green-400';
        } else {
            numbersIcon.setAttribute('data-lucide', 'circle');
            numbersIcon.className = 'h-3 w-3 mr-2 text-gray-400';
        }
    }

    if (strengthIndicator && strengthText) {
        if (score <= 2) {
            strengthIndicator.className = 'strength-indicator strength-weak';
            strengthText.textContent = 'Débil';
            strengthText.className = 'text-xs text-red-400';
        } else if (score <= 4) {
            strengthIndicator.className = 'strength-indicator strength-medium';
            strengthText.textContent = 'Medio';
            strengthText.className = 'text-xs text-yellow-400';
        } else if (score <= 6) {
            strengthIndicator.className = 'strength-indicator strength-good';
            strengthText.textContent = 'Bueno';
            strengthText.className = 'text-xs text-costa-green';
        } else {
            strengthIndicator.className = 'strength-indicator strength-strong';
            strengthText.textContent = 'Fuerte';
            strengthText.className = 'text-xs text-green-400';
        }
    }

    lucide.createIcons();
}

function validatePasswords() {
    if (password1 && password2 && password1.value && password2.value && passwordMatch) {
        const icon = passwordMatch.querySelector('i');
        const text = passwordMatch.querySelector('span');
        
        if (icon && text) {
            if (password1.value === password2.value) {
                icon.setAttribute('data-lucide', 'check-circle');
                icon.className = 'h-3 w-3 mr-2 text-green-400';
                text.textContent = '¡Las contraseñas coinciden!';
                text.className = 'text-xs text-green-400';
                password2.classList.remove('border-red-500');
                password2.classList.add('border-green-500');
            } else {
                icon.setAttribute('data-lucide', 'x-circle');
                icon.className = 'h-3 w-3 mr-2 text-red-400';
                text.textContent = 'Las contraseñas no coinciden';
                text.className = 'text-xs text-red-400';
                password2.classList.remove('border-green-500');
                password2.classList.add('border-red-500');
            }
            lucide.createIcons();
        }
    }
}

if (password1) {
    password1.addEventListener('input', function() {
        checkPasswordStrength(this.value);
        validatePasswords();
    });
}

if (password2) {
    password2.addEventListener('input', validatePasswords);
}

const registerForm = document.getElementById('registerForm');
if (registerForm) {
    registerForm.addEventListener('submit', function(e) {
        const submitBtn = document.getElementById('submitBtn');
        const submitText = document.getElementById('submitText');
        
        if (submitBtn && submitText) {
            const icon = submitBtn.querySelector('i');
            
            submitBtn.disabled = true;
            submitBtn.classList.add('opacity-75');
            submitText.textContent = 'Creando cuenta...';
            if (icon) {
                icon.setAttribute('data-lucide', 'loader');
                icon.classList.add('animate-spin');
            }
            
            lucide.createIcons();
            
        }
    });
}

document.querySelectorAll('.form-input').forEach(input => {
    input.addEventListener('focus', function() {
        if (this.parentElement) {
            this.parentElement.classList.add('scale-105');
        }
    });
    
    input.addEventListener('blur', function() {
        if (this.parentElement) {
            this.parentElement.classList.remove('scale-105');
        }
    });
});

setTimeout(() => {
    lucide.createIcons();
}, 100);