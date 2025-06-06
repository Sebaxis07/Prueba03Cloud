// Inicializar iconos Lucide
lucide.createIcons();
        
// Mostrar/ocultar el formulario de detalles de asalto según el tipo seleccionado
const tipoSelect = document.getElementById('{{ form.tipo.id_for_label }}');
if (tipoSelect) {
    tipoSelect.addEventListener('change', function(e) {
        const detalleAsalto = document.getElementById('detalle-asalto');
        const selectedOption = e.target.selectedOptions[0];
        
        // Verificar si el texto de la opción contiene "asalto" (case insensitive)
        if (selectedOption && selectedOption.textContent.toLowerCase().includes('asalto')) {
            detalleAsalto.classList.remove('hidden');
            detalleAsalto.style.animation = 'slideUp 0.6s ease-out';
        } else {
            detalleAsalto.classList.add('hidden');
        }
    });
}

// Función para guardar como borrador
function saveAsDraft() {
    const formData = new FormData(document.getElementById('crear-aviso-form'));
    
    // Guardar en localStorage como backup
    const draftData = {};
    for (let [key, value] of formData.entries()) {
        if (value && key !== 'csrfmiddlewaretoken') {
            draftData[key] = value;
        }
    }
    
    if (Object.keys(draftData).length > 0) {
        localStorage.setItem('aviso_draft', JSON.stringify(draftData));
        showMessage('Borrador guardado localmente', 'success');
    } else {
        showMessage('No hay contenido para guardar', 'warning');
    }
}

// Cargar borrador si existe
function loadDraft() {
    const draft = localStorage.getItem('aviso_draft');
    if (draft) {
        try {
            const draftData = JSON.parse(draft);
            for (let [key, value] of Object.entries(draftData)) {
                const field = document.querySelector(`[name="${key}"]`);
                if (field && field.type !== 'file') {
                    if (field.type === 'checkbox') {
                        field.checked = value === 'on';
                    } else {
                        field.value = value;
                    }
                }
            }
            showMessage('Borrador cargado', 'info');
        } catch (e) {
            console.error('Error cargando borrador:', e);
        }
    }
}

// Auto-guardar cada 2 minutos
setInterval(function() {
    const form = document.getElementById('crear-aviso-form');
    if (form) {
        const titulo = form.querySelector('[name="titulo"]');
        const descripcion = form.querySelector('[name="descripcion"]');
        
        if ((titulo && titulo.value) || (descripcion && descripcion.value)) {
            saveAsDraft();
        }
    }
}, 120000); // 2 minutos

// Confirmar antes de salir si hay cambios
let formChanged = false;
const form = document.getElementById('crear-aviso-form');

if (form) {
    form.addEventListener('input', function() {
        formChanged = true;
    });
    
    // Limpiar flag cuando se envía el formulario
    form.addEventListener('submit', function() {
        formChanged = false;
        // Limpiar borrador al enviar
        localStorage.removeItem('aviso_draft');
    });
}

window.addEventListener('beforeunload', function(e) {
    if (formChanged) {
        e.preventDefault();
        e.returnValue = '';
    }
});

// Cargar borrador al cargar la página
window.addEventListener('load', loadDraft);
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
            
            showMessage('Imagen válida seleccionada', 'success');
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