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
        
        document.getElementById('foto-perfil-input').addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                if (file.size > 5 * 1024 * 1024) {
                    showMessage('La imagen no puede superar los 5MB', 'error');
                    e.target.value = '';
                    return;
                }
                
                if (!file.type.startsWith('image/')) {
                    showMessage('Solo se permiten archivos de imagen', 'error');
                    e.target.value = '';
                    return;
                }
                
                const reader = new FileReader();
                reader.onload = function(e) {
                    const container = document.querySelector('.profile-image-container');
                    container.innerHTML = `
                        <img src="${e.target.result}" alt="Foto de perfil" class="profile-image" id="profile-image">
                        <div class="upload-overlay" onclick="document.getElementById('foto-perfil-input').click();">
                            <i data-lucide="camera" class="h-8 w-8 text-white"></i>
                        </div>
                    `;
                    lucide.createIcons();
                };
                reader.readAsDataURL(file);
                
                showMessage('Imagen cargada. Recuerda guardar los cambios.', 'info');
            }
        });
        
        function eliminarFotoPerfil() {
            if (confirm('¿Estás seguro de que quieres eliminar tu foto de perfil?')) {
                fetch('{% url "eliminar_foto_perfil" %}', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': '{{ csrf_token }}',
                        'X-Requested-With': 'XMLHttpRequest',
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const container = document.querySelector('.profile-image-container');
                        container.innerHTML = `
                            <div class="default-avatar" onclick="document.getElementById('foto-perfil-input').click();">
                                <i data-lucide="user" class="h-16 w-16 text-white"></i>
                                <div class="upload-overlay">
                                    <i data-lucide="camera" class="h-8 w-8 text-white"></i>
                                </div>
                            </div>
                        `;
                        lucide.createIcons();
                        showMessage(data.mensaje, 'success');
                    } else {
                        showMessage(data.mensaje, 'error');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showMessage('Error de conexión', 'error');
                });
            }
        }
        
        function cambiarContrasena() {
            showMessage('Función disponible próximamente', 'info');
        }
        
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
        
        document.getElementById('perfil-form').addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i data-lucide="loader" class="inline h-4 w-4 mr-2 animate-spin"></i>Guardando...';
            
            setTimeout(() => {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
                lucide.createIcons();
            }, 5000);
        });
        
        setTimeout(() => {
            lucide.createIcons();
        }, 100);