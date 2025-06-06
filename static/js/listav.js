lucide.createIcons();
        
        document.getElementById('mobile-menu-button').addEventListener('click', function() {
            const menu = document.getElementById('mobile-menu');
            const button = this;
            const icon = button.querySelector('i');
            
            menu.classList.toggle('hidden');
            
            if (menu.classList.contains('hidden')) {
                icon.setAttribute('data-lucide', 'menu');
            } else {
                icon.setAttribute('data-lucide', 'x');
            }
            lucide.createIcons();
        });

        function toggleFilters() {
            const form = document.getElementById('filter-form');
            const icon = document.getElementById('filter-icon');
            
            if (form.classList.contains('hidden')) {
                form.classList.remove('hidden');
                icon.style.transform = 'rotate(180deg)';
            } else {
                form.classList.add('hidden');
                icon.style.transform = 'rotate(0deg)';
            }
        }

        function openImageModal(src) {
            document.getElementById('modalImage').src = src;
            document.getElementById('imageModal').classList.remove('hidden');
            document.body.style.overflow = 'hidden';
        }
        
        function closeImageModal() {
            document.getElementById('imageModal').classList.add('hidden');
            document.body.style.overflow = 'auto';
        }
        
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                closeImageModal();
            }
        });

        const filterInputs = document.querySelectorAll('#filter-form select, #filter-form input');
        filterInputs.forEach(input => {
            input.addEventListener('change', function() {
            });
        });

        const searchTerm = '{{ request.GET.q|escapejs }}';
        if (searchTerm) {
            const titles = document.querySelectorAll('h2 a');
            titles.forEach(title => {
                const text = title.textContent;
                const regex = new RegExp(`(${searchTerm})`, 'gi');
                title.innerHTML = text.replace(regex, '<mark>$1</mark>');
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

        document.querySelectorAll('.card-hover').forEach(card => {
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-4px) scale(1.01)';
            });
            
            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0) scale(1)';
            });
        });

        function createParticle() {
            const particle = document.createElement('div');
            particle.style.position = 'fixed';
            particle.style.width = '2px';
            particle.style.height = '2px';
            particle.style.background = '#10B981';
            particle.style.borderRadius = '50%';
            particle.style.pointerEvents = 'none';
            particle.style.zIndex = '1';
            particle.style.opacity = '0.3';
            particle.style.left = Math.random() * 100 + 'vw';
            particle.style.top = '100vh';
            particle.style.animation = 'particleFloat 8s linear infinite';
            
            document.body.appendChild(particle);
            
            setTimeout(() => {
                particle.remove();
            }, 8000);
        }
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

        setInterval(createParticle, 3000);

        const style = document.createElement('style');
        style.textContent = `
            @keyframes particleFloat {
                to {
                    transform: translateY(-100vh) translateX(${Math.random() * 200 - 100}px);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);