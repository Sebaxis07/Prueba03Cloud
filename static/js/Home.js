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

const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
            entry.target.classList.add('animate-fade-in');
        }
    });
}, observerOptions);

document.querySelectorAll('section').forEach(section => {
    section.style.opacity = '0';
    section.style.transform = 'translateY(50px)';
    section.style.transition = 'opacity 1s ease, transform 1s ease';
    observer.observe(section);
});

function animateCounter(element, target) {
    const isNumeric = !isNaN(target);
    if (!isNumeric) return;
    
    let current = 0;
    const increment = target / 60;
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
            const target = parseInt(entry.target.textContent);
            if (!isNaN(target)) {
                animateCounter(entry.target, target);
            }
            statObserver.unobserve(entry.target);
        }
    });
});

document.querySelectorAll('.counter').forEach(counter => {
    statObserver.observe(counter);
});

let ticking = false;
function updateParallax() {
    const scrolled = window.pageYOffset;
    const parallaxElements = document.querySelectorAll('.absolute');
    
    parallaxElements.forEach((element, index) => {
        const speed = 0.2 + (index * 0.1);
        element.style.transform = `translateY(${scrolled * speed}px)`;
    });
    
    ticking = false;
}

window.addEventListener('scroll', () => {
    if (!ticking) {
        requestAnimationFrame(updateParallax);
        ticking = true;
    }
});

document.querySelectorAll('.card-hover').forEach(card => {
    card.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-8px) scale(1.02)';
    });
    
    card.addEventListener('mouseleave', function() {
        this.style.transform = 'translateY(0) scale(1)';
    });
});

window.addEventListener('load', function() {
    document.body.classList.add('loaded');
    
    setTimeout(() => {
        document.querySelectorAll('.animate-fade-in').forEach(el => {
            el.style.opacity = '1';
        });
    }, 200);
});

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});