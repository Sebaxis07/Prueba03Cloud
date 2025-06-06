lucide.createIcons();


        // Enhanced Menu Logic
    const userMenuButton = document.getElementById('user-menu-button');
    const userMenu = document.getElementById('user-menu');
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    const mobileMenuIcon = document.getElementById('mobile-menu-icon');

    // User menu toggle (solo si existe)
    if (userMenuButton && userMenu) {
        userMenuButton.addEventListener('click', (event) => {
            event.stopPropagation();
            const isHidden = userMenu.classList.contains('hidden');
            
            if (isHidden) {
                userMenu.classList.remove('hidden');
                userMenu.classList.add('dropdown-enter');
            } else {
                userMenu.classList.add('hidden');
                userMenu.classList.remove('dropdown-enter');
            }
        });
    }

    // Mobile menu toggle
    if (mobileMenuButton) {
        mobileMenuButton.addEventListener('click', (event) => {
            event.stopPropagation();
            const isHidden = mobileMenu.classList.toggle('hidden');
            
            mobileMenuIcon.setAttribute('data-lucide', isHidden ? 'menu' : 'x');
            lucide.createIcons();
        });
    }

    // Click outside to close menus
    document.addEventListener('click', (event) => {
        // Close user menu (solo si existe)
        if (userMenu && userMenuButton && !userMenu.classList.contains('hidden')) {
            if (!userMenu.contains(event.target) && !userMenuButton.contains(event.target)) {
                userMenu.classList.add('hidden');
                userMenu.classList.remove('dropdown-enter');
            }
        }
        
        // Close mobile menu
        if (mobileMenu && !mobileMenu.classList.contains('hidden')) {
            if (!mobileMenu.contains(event.target) && !mobileMenuButton.contains(event.target)) {
                mobileMenu.classList.add('hidden');
                mobileMenuIcon.setAttribute('data-lucide', 'menu');
                lucide.createIcons();
            }
        }
    });

    // Prevent menu close when clicking inside (solo si existe)
    if (userMenu) {
        userMenu.addEventListener('click', (event) => {
            event.stopPropagation();
        });
    }

    if (mobileMenu) {
        mobileMenu.addEventListener('click', (event) => {
            if (event.target.closest('.glassmorphism-strong')) {
                event.stopPropagation();
            }
        });
    }
        // Toggle password visibility
        function togglePassword() {
            const passwordInput = document.getElementById('{{ form.password.id_for_label }}');
            const toggleIcon = document.getElementById('togglePasswordIcon');
            
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                toggleIcon.setAttribute('data-lucide', 'eye-off');
            } else {
                passwordInput.type = 'password';
                toggleIcon.setAttribute('data-lucide', 'eye');
            }
            lucide.createIcons();
        }

        // Form validation enhancements
        document.getElementById('loginForm').addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            const icon = submitBtn.querySelector('i');
            
            // Change button state
            submitBtn.disabled = true;
            submitBtn.classList.add('opacity-75');
            icon.setAttribute('data-lucide', 'loader');
            icon.classList.add('animate-spin');
            
            // Re-create icons
            lucide.createIcons();
        });

        // Input animations
        document.querySelectorAll('.form-input').forEach(input => {
            input.addEventListener('focus', function() {
                this.parentElement.classList.add('scale-105');
            });
            
            input.addEventListener('blur', function() {
                this.parentElement.classList.remove('scale-105');
            });
        });

        // Smart RUT detection (much more conservative)
        const usernameInput = document.getElementById('{{ form.username.id_for_label }}');
        const rutHint = document.getElementById('rutHint');
        
        usernameInput.addEventListener('input', function(e) {
            const value = e.target.value.trim();
            
            // Only show RUT hint if it REALLY looks like a RUT
            if (isLikelyRUT(value)) {
                rutHint.classList.add('show');
                // Optional: format only if user explicitly indicates it's a RUT
                // (e.g., by adding a dash or dots)
                if (value.includes('-') || value.includes('.')) {
                    e.target.value = formatRUT(value);
                }
            } else {
                rutHint.classList.remove('show');
            }
        });

        function isLikelyRUT(value) {
            // More conservative: only consider it a RUT if:
            // 1. It has 8-9 characters
            // 2. It's mostly numbers
            // 3. It ends with a number or K/k
            // 4. It doesn't contain common username patterns (letters mixed with numbers like "user123")
            
            const cleanValue = value.replace(/[.-]/g, '');
            
            // Must be 7-9 chars (without separators)
            if (cleanValue.length < 7 || cleanValue.length > 9) return false;
            
            // Must end with number or K
            if (!/[0-9kK]$/i.test(cleanValue)) return false;
            
            // Must be mostly numbers (at least 7 digits)
            const digitCount = (cleanValue.match(/\d/g) || []).length;
            if (digitCount < 7) return false;
            
            // Exclude common username patterns
            if (/^[a-zA-Z]+\d{1,3}$/.test(cleanValue)) return false; // like "user123"
            if (/^\d{1,3}[a-zA-Z]+/.test(cleanValue)) return false; // like "123user"
            
            // If it looks like a sequence of digits + final char, it's likely a RUT
            return /^\d{7,8}[0-9kK]$/i.test(cleanValue);
        }

        function formatRUT(rut) {
            // Clean the RUT
            let clean = rut.replace(/[^0-9kK]/gi, '');
            
            // Don't format if too short or too long
            if (clean.length < 7 || clean.length > 9) return rut;
            
            // Add the dash before the last character
            if (clean.length >= 2) {
                clean = clean.slice(0, -1) + '-' + clean.slice(-1);
            }
            
            // Add dots for thousands
            if (clean.length > 5) {
                const body = clean.slice(0, -2); // everything except dash and last char
                const end = clean.slice(-2); // dash and last char
                
                // Add dots every 3 digits from right to left
                const formatted = body.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
                clean = formatted + end;
            }
            
            return clean;
        }

        // Intersection Observer for animations
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, observerOptions);

        // Observe elements
        document.querySelectorAll('.animate-slide-up').forEach(el => {
            observer.observe(el);
        });

        // Easter egg: konami code
        let konamiCode = [];
        const correctCode = ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight'];
        
        document.addEventListener('keydown', function(e) {
            konamiCode.push(e.code);
            if (konamiCode.length > correctCode.length) {
                konamiCode.shift();
            }
            
            if (konamiCode.join(',') === correctCode.join(',')) {
                // Add special effect
                document.body.style.filter = 'hue-rotate(180deg)';
                setTimeout(() => {
                    document.body.style.filter = '';
                }, 3000);
            }
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', function(e) {
            // Alt + R to focus RUT/username field
            if (e.altKey && e.key === 'r') {
                e.preventDefault();
                usernameInput.focus();
            }
            
            // Alt + P to focus password field
            if (e.altKey && e.key === 'p') {
                e.preventDefault();
                document.getElementById('{{ form.password.id_for_label }}').focus();
            }
        });