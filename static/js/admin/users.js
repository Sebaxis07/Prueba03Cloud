setTimeout(() => {
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
}, 500);


lucide.createIcons();

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    
    sidebar.classList.toggle('-translate-x-full');
    overlay.classList.toggle('hidden');
}

function toggleUsuario(userId) {
    fetch(`/panel-admin/usuarios/${userId}/toggle/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert('Error: ' + data.mensaje);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al procesar la solicitud');
    });
}

function toggleVerificacion(userId) {
    fetch(`/panel-admin/usuarios/${userId}/verificar/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert('Error: ' + data.mensaje);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al procesar la solicitud');
    });
}

function verDetalles(userId) {

    const usuarios = {{ usuarios|safe }};
    const modal = document.getElementById('userModal');
    const content = document.getElementById('userModalContent');
    
 
    content.innerHTML = `
        <div class="text-center py-8">
            <i data-lucide="loader" class="h-8 w-8 mx-auto mb-4 text-costa-green animate-spin"></i>
            <p class="text-gray-400">Cargando detalles del usuario...</p>
        </div>
    `;
    
    modal.classList.remove('hidden');
    lucide.createIcons();
    

    setTimeout(() => {
        content.innerHTML = `
            <div class="text-center py-8">
                <p class="text-gray-400">Funcionalidad en desarrollo</p>
                <p class="text-sm text-gray-500 mt-2">Próximamente mostrará estadísticas detalladas del usuario</p>
            </div>
        `;
    }, 1000);
}

function closeUserModal() {
    document.getElementById('userModal').classList.add('hidden');
}