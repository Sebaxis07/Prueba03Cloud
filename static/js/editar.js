// Inicializar iconos Lucide
lucide.createIcons();
        
// Confirmar antes de salir si hay cambios
let formChanged = false;
const form = document.getElementById('editar-aviso-form');

if (form) {
    // Obtener valores iniciales
    const initialValues = new FormData(form);
    
    form.addEventListener('input', function() {
        formChanged = true;
    });
    
    // Limpiar flag cuando se envía el formulario
    form.addEventListener('submit', function() {
        formChanged = false;
    });
}

window.addEventListener('beforeunload', function(e) {
    if (formChanged) {
        e.preventDefault();
        e.returnValue = '';
    }
});

// Función para mostrar mensajes
function showMessage(text, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `fixed top-4 right-4 p-4 rounded-xl z-50 transition-all duration-300 backdrop-blur-sm ${
        type === 'success' ? 'bg-green-900/20 text-green-300 border border-green-500/30' : 
        type === 'warning' ? 'bg-yellow-900/20 text-yellow-300 border border-yellow-500/30' :
        type === 'info' ? 'bg-blue-900/20 text-blue-300 border border-blue-500/30' :
        'bg-red-900/20 text-red-300 border border-red-500/30'
    }`;
    messageDiv.innerHTML = `
        <div class="flex items-center">
            <i data-lucide="${type === 'success' ? 'check-circle' : type === 'warning' ? 'alert-triangle' : type === 'info' ? 'info' : 'alert-circle'}" class="h-5 w-5 mr-2"></i>
            ${text}
        </div>
    `;
    document.body.appendChild(messageDiv);
    
    // Re-inicializar iconos
    lucide.createIcons();
    
    setTimeout(() => {
        messageDiv.remove();
    }, 3000);
}

// Validación de imagen en tiempo real
const imageInput = document.querySelector('input[type="file"]');
if (imageInput) {
    imageInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            // Validar tamaño (5MB máximo)
            if (file.size > 5 * 1024 * 1024) {
                showMessage('La imagen es muy grande. Máximo 5MB.', 'error');
                this.value = '';
                return;
            }
            
            // Validar tipo
            const allowedTypes = ['image/jpeg', 'image/png', 'image/gif'];
            if (!allowedTypes.includes(file.type)) {
                showMessage('Tipo de archivo no válido. Solo JPEG, PNG y GIF.', 'error');
                this.value = '';
                return;
            }
            
            showMessage('Nueva imagen seleccionada', 'success');
        }
    });
}

// Animaciones en scroll
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
// Initialize Lucide Icons
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
// Observar elementos para animación
document.querySelectorAll('.animate-slide-up').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(30px)';
    el.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
    observer.observe(el);
});

// Efectos hover para cards
document.querySelectorAll('.card-hover').forEach(card => {
    card.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-4px) scale(1.01)';
    });
    
    card.addEventListener('mouseleave', function() {
        this.style.transform = 'translateY(0) scale(1)';
    });
});