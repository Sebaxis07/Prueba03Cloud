 // 1. Inicializar Lucide Icons
 lucide.createIcons();
        
 // 2. Lógica para menús desplegables
 const userMenuButton = document.getElementById('user-menu-button');
 const userMenu = document.getElementById('user-menu');
 const mobileMenuButton = document.getElementById('mobile-menu-button');
 const mobileMenu = document.getElementById('mobile-menu');
 const mobileMenuIcon = document.getElementById('mobile-menu-icon');

 if (userMenuButton) {
     userMenuButton.addEventListener('click', (event) => {
         event.stopPropagation();
         userMenu.classList.toggle('hidden');
     });
 }

 if (mobileMenuButton) {
     mobileMenuButton.addEventListener('click', () => {
         const isHidden = mobileMenu.classList.toggle('hidden');
         // Cambiar el ícono de hamburguesa a X y viceversa
         mobileMenuIcon.setAttribute('data-lucide', isHidden ? 'menu' : 'x');
         lucide.createIcons(); // Re-renderizar el ícono
     });
 }

 document.addEventListener('click', (event) => {
     if (userMenu && !userMenu.classList.contains('hidden')) {
         if (!userMenu.contains(event.target) && !userMenuButton.contains(event.target)) {
             userMenu.classList.add('hidden');
         }
     }
 });

 // 3. Animaciones en scroll (Intersection Observer)
 const observerOptions = {
     threshold: 0.1,
     rootMargin: '0px 0px -50px 0px'
 };

 const observer = new IntersectionObserver((entries) => {
     entries.forEach(entry => {
         if (entry.isIntersecting) {
             entry.target.style.opacity = '1';
             entry.target.style.transform = 'translateY(0)';
             observer.unobserve(entry.target); // Dejar de observar una vez animado
         }
     });
 }, observerOptions);

 document.querySelectorAll('.animate-slide-up').forEach(el => {
     el.style.opacity = '0';
     el.style.transform = 'translateY(30px)';
     el.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
     observer.observe(el);
 });