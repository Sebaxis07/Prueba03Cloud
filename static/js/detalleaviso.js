lucide.createIcons();
        
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
        
        {% if user.is_authenticated %}
        document.getElementById('comentario-form').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i data-lucide="loader" class="inline h-4 w-4 mr-2 animate-spin"></i>Enviando...';
            
            fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.reset();
                    
                    const comentariosList = document.getElementById('comentarios-lista');
                    
                    let avatarHtml = '';
                    if (data.comentario.foto_perfil) {
                        avatarHtml = `<img src="${data.comentario.foto_perfil}" 
                                           alt="Foto de ${data.comentario.usuario}"
                                           class="w-10 h-10 rounded-full object-cover border-2 border-costa-green/50 shadow-lg">`;
                    } else {
                        avatarHtml = `<div class="w-10 h-10 rounded-full bg-gradient-to-br from-costa-green to-costa-green-dark flex items-center justify-center border-2 border-costa-green/50 shadow-lg">
                                        <i data-lucide="user" class="h-5 w-5 text-white"></i>
                                      </div>`;
                    }
                    
                    const nuevoComentario = `
                        <div class="glassmorphism-light p-4 rounded-xl border border-costa-green/20 hover:border-costa-green/40 transition-all duration-300 animate-slide-up">
                            <div class="flex items-start space-x-4">
                                <div class="flex-shrink-0">
                                    ${avatarHtml}
                                </div>
                                <div class="flex-1">
                                    <div class="flex items-center justify-between mb-2">
                                        <span class="font-medium text-white">${data.comentario.usuario}</span>
                                        <span class="text-sm text-gray-400">${data.comentario.fecha}</span>
                                    </div>
                                    <p class="text-gray-300 leading-relaxed">${data.comentario.contenido}</p>
                                </div>
                            </div>
                        </div>
                    `;
                    
                    if (comentariosList) {
                        comentariosList.insertAdjacentHTML('beforeend', nuevoComentario);
                    } else {
                        // Si no hay comentarios, reemplazar el mensaje vacío
                        const emptyState = document.querySelector('.text-center.py-8');
                        if (emptyState) {
                            emptyState.outerHTML = `<div class="space-y-6" id="comentarios-lista">${nuevoComentario}</div>`;
                        }
                    }
                    
                    const counter = document.querySelector('h2');
                    if (counter && counter.textContent.includes('Comentarios')) {
                        const currentCount = parseInt(counter.textContent.match(/\d+/)[0]);
                        counter.innerHTML = counter.innerHTML.replace(/\d+/, currentCount + 1);
                    }
                    
                    showMessage('¡Comentario agregado exitosamente!', 'success');
                    
                    lucide.createIcons();
                } else {
                    showMessage('Error al agregar comentario', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showMessage('Error de conexión', 'error');
            })
            .finally(() => {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
                lucide.createIcons();
            });
        });
        {% endif %}
        
        function showMessage(text, type) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `fixed top-4 right-4 p-4 rounded-xl z-50 transition-all duration-500 transform translate-x-full glassmorphism-light border shadow-2xl ${
                type === 'success' ? 'border-costa-green/50 text-costa-green' : 
                type === 'warning' ? 'border-yellow-500/50 text-yellow-400' :
                type === 'info' ? 'border-blue-500/50 text-blue-400' :
                'border-red-500/50 text-red-400'
            }`;
            messageDiv.innerHTML = `
                <div class="flex items-center">
                    <div class="p-1 ${type === 'success' ? 'bg-costa-green/20' : type === 'warning' ? 'bg-yellow-500/20' : type === 'info' ? 'bg-blue-500/20' : 'bg-red-500/20'} rounded mr-2">
                        <i data-lucide="${type === 'success' ? 'check-circle' : type === 'warning' ? 'alert-triangle' : type === 'info' ? 'info' : 'alert-circle'}" class="h-4 w-4"></i>
                    </div>
                    <span class="font-medium">${text}</span>
                </div>
            `;
            document.body.appendChild(messageDiv);
            
            lucide.createIcons();
            
            setTimeout(() => {
                messageDiv.classList.remove('translate-x-full');
            }, 100);
            
            setTimeout(() => {
                messageDiv.classList.add('translate-x-full');
                setTimeout(() => {
                    messageDiv.remove();
                }, 300);
            }, 5000);
        }
        
        {% if user.is_authenticated and user == aviso.usuario %}
        function cambiarEstado() {
            const nuevoEstado = document.getElementById('estado-select').value;
            const estadoActual = '{{ aviso.status }}';
            
            if (nuevoEstado === estadoActual) {
                showMessage('El aviso ya tiene ese estado', 'warning');
                return;
            }
            
            fetch('{% url "cambiar_estado_aviso" aviso.id %}', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': '{{ csrf_token }}',
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: JSON.stringify({
                    estado: nuevoEstado
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showMessage(data.mensaje, 'success');
                    setTimeout(() => {
                        window.location.reload();
                    }, 1500);
                } else {
                    showMessage(data.mensaje, 'error');
                    document.getElementById('estado-select').value = estadoActual;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showMessage('Error de conexión', 'error');
                document.getElementById('estado-select').value = estadoActual;
            });
        }
        
        function confirmarEliminar() {
            if (confirm('¿Estás seguro de que quieres eliminar este aviso?\n\nEsta acción no se puede deshacer.')) {
                eliminarAviso();
            }
        }
        
        function eliminarAviso() {
            fetch('{% url "eliminar_aviso" aviso.id %}', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': '{{ csrf_token }}',
                    'X-Requested-With': 'XMLHttpRequest',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showMessage(data.mensaje, 'success');
                    setTimeout(() => {
                        window.location.href = '{% url "mis_avisos" %}';
                    }, 1000);
                } else {
                    showMessage(data.mensaje, 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showMessage('Error de conexión', 'error');
            });
        }
        {% endif %}
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
        setTimeout(() => {
            lucide.createIcons();
        }, 100);