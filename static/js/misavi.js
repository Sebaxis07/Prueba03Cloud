lucide.createIcons();
        const userMenuButton = document.getElementById('user-menu-button');
    const userMenu = document.getElementById('user-menu');
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    const mobileMenuIcon = document.getElementById('mobile-menu-icon');

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

    if (mobileMenuButton) {
        mobileMenuButton.addEventListener('click', (event) => {
            event.stopPropagation();
            const isHidden = mobileMenu.classList.toggle('hidden');
            
            mobileMenuIcon.setAttribute('data-lucide', isHidden ? 'menu' : 'x');
            lucide.createIcons();
        });
    }

    document.addEventListener('click', (event) => {
        if (userMenu && userMenuButton && !userMenu.classList.contains('hidden')) {
            if (!userMenu.contains(event.target) && !userMenuButton.contains(event.target)) {
                userMenu.classList.add('hidden');
                userMenu.classList.remove('dropdown-enter');
            }
        }
        
        if (mobileMenu && !mobileMenu.classList.contains('hidden')) {
            if (!mobileMenu.contains(event.target) && !mobileMenuButton.contains(event.target)) {
                mobileMenu.classList.add('hidden');
                mobileMenuIcon.setAttribute('data-lucide', 'menu');
                lucide.createIcons();
            }
        }
    });

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

        document.querySelectorAll('.animate-slide-up').forEach(el => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(30px)';
            el.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
            observer.observe(el);
        });

        function animateCounter(element, target) {
            const isNumeric = !isNaN(target);
            if (!isNumeric) return;
            
            let current = 0;
            const increment = target / 50;
            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    element.textContent = target;
                    clearInterval(timer);
                } else {
                    element.textContent = Math.floor(current);
                }
            }, 30);
        }

        const statObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const counter = entry.target.querySelector('.animate-counter');
                    if (counter) {
                        const target = parseInt(counter.textContent);
                        if (!isNaN(target)) {
                            animateCounter(counter, target);
                        }
                    }
                    statObserver.unobserve(entry.target);
                }
            });
        });

        document.querySelectorAll('.stat-card').forEach(card => {
            statObserver.observe(card);
        });

        document.querySelectorAll('.card-hover').forEach(card => {
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-4px) scale(1.01)';
            });
            
            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0) scale(1)';
            });
        });

        document.querySelectorAll('.aviso-item').forEach((item, index) => {
            item.style.animationDelay = `${(index + 5) * 100}ms`;
        });

        const icons = document.querySelectorAll('[data-lucide]');
        icons.forEach((icon, index) => {
            icon.style.opacity = '0';
            icon.style.transform = 'scale(0.8)';
            setTimeout(() => {
                icon.style.opacity = '1';
                icon.style.transform = 'scale(1)';
                icon.style.transition = 'all 0.3s ease';
            }, index * 50);
        });

        setTimeout(() => {
            lucide.createIcons();
        }, 1000);