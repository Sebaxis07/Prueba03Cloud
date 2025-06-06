lucide.createIcons();


        Chart.defaults.color = '#9CA3AF';
        Chart.defaults.backgroundColor = 'rgba(16, 185, 129, 0.1)';
        Chart.defaults.borderColor = 'rgba(16, 185, 129, 0.3)';

        function toggleSidebar() {
            const sidebar = document.getElementById('sidebar');
            const overlay = document.getElementById('sidebar-overlay');
            
            sidebar.classList.toggle('-translate-x-full');
            overlay.classList.toggle('hidden');
        }


        const avisosData = {{ avisos_por_mes|safe }};
        const usuariosData = {{ usuarios_por_mes|safe }};
        const estadosData = {{ estados_avisos|safe }};
        const prioridadesData = {{ prioridades_avisos|safe }};
        const tiposData = {{ tipos_avisos|safe }};
        const actividadData = {{ actividad_por_hora|safe }};
        const topUsuariosData = {{ top_usuarios|safe }};


        const avisosCtx = document.getElementById('avisosChart').getContext('2d');
        const avisosChart = new Chart(avisosCtx, {
            type: 'line',
            data: {
                labels: avisosData.map(item => item.mes),
                datasets: [{
                    label: 'Avisos Creados',
                    data: avisosData.map(item => item.count),
                    borderColor: '#10B981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#10B981',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(75, 85, 99, 0.3)'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(75, 85, 99, 0.3)'
                        }
                    }
                }
            }
        });


        const usuariosCtx = document.getElementById('usuariosChart').getContext('2d');
        const usuariosChart = new Chart(usuariosCtx, {
            type: 'bar',
            data: {
                labels: usuariosData.map(item => item.mes),
                datasets: [{
                    label: 'Nuevos Usuarios',
                    data: usuariosData.map(item => item.count),
                    backgroundColor: 'rgba(16, 185, 129, 0.8)',
                    borderColor: '#10B981',
                    borderWidth: 1,
                    borderRadius: 8,
                    borderSkipped: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(75, 85, 99, 0.3)'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(75, 85, 99, 0.3)'
                        }
                    }
                }
            }
        });

  
        const estadosCtx = document.getElementById('estadosChart').getContext('2d');
        const estadosChart = new Chart(estadosCtx, {
            type: 'doughnut',
            data: {
                labels: ['Activos', 'En Proceso', 'Resueltos'],
                datasets: [{
                    data: [estadosData.activos, estadosData.en_proceso, estadosData.resueltos],
                    backgroundColor: [
                        '#EF4444',
                        '#F59E0B',
                        '#10B981'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    }
                }
            }
        });


        const prioridadesCtx = document.getElementById('prioridadesChart').getContext('2d');
        const prioridadesChart = new Chart(prioridadesCtx, {
            type: 'polarArea',
            data: {
                labels: ['Urgente', 'Alta', 'Media', 'Baja'],
                datasets: [{
                    data: [prioridadesData.urgente, prioridadesData.alta, prioridadesData.media, prioridadesData.baja],
                    backgroundColor: [
                        'rgba(239, 68, 68, 0.8)',
                        'rgba(245, 158, 11, 0.8)',
                        'rgba(59, 130, 246, 0.8)',
                        'rgba(107, 114, 128, 0.8)'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    }
                }
            }
        });


        const tiposCtx = document.getElementById('tiposChart').getContext('2d');
        const tiposChart = new Chart(tiposCtx, {
            type: 'bar',
            data: {
                labels: tiposData.map(item => {
                    // Convertir nombre del tipo a display name
                    const displayNames = {
                        'robo': 'Robo',
                        'vandalismo': 'Vandalismo',
                        'ruido': 'Ruido',
                        'iluminacion': 'Iluminación',
                        'basura': 'Basura',
                        'trafico': 'Tráfico',
                        'drogas': 'Drogas',
                        'asalto': 'Asalto',
                        'otro': 'Otro'
                    };
                    return displayNames[item.nombre] || item.nombre;
                }),
                datasets: [{
                    data: tiposData.map(item => item.total),
                    backgroundColor: 'rgba(16, 185, 129, 0.8)',
                    borderColor: '#10B981',
                    borderWidth: 1,
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(75, 85, 99, 0.3)'
                        }
                    },
                    y: {
                        grid: {
                            color: 'rgba(75, 85, 99, 0.3)'
                        }
                    }
                }
            }
        });


        const actividadCtx = document.getElementById('actividadChart').getContext('2d');
        const actividadChart = new Chart(actividadCtx, {
            type: 'line',
            data: {
                labels: Array.from({length: 24}, (_, i) => `${i}:00`),
                datasets: [{
                    label: 'Avisos Creados',
                    data: actividadData,
                    borderColor: '#10B981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(75, 85, 99, 0.3)'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(75, 85, 99, 0.3)'
                        }
                    }
                }
            }
        });


        function cargarTopUsuarios() {
            const container = document.getElementById('topUsuarios');
            
            if (topUsuariosData.length === 0) {
                container.innerHTML = `
                    <div class="text-center py-8">
                        <i data-lucide="users" class="h-12 w-12 mx-auto mb-4 text-gray-500 opacity-50"></i>
                        <p class="text-gray-400">No hay usuarios activos aún</p>
                        <p class="text-sm text-gray-500 mt-2">Los usuarios aparecerán aquí cuando creen avisos o comentarios</p>
                    </div>
                `;
                lucide.createIcons();
                return;
            }

            container.innerHTML = topUsuariosData.map((user, index) => `
                <div class="flex items-center justify-between p-4 glassmorphism rounded-lg border border-gray-700">
                    <div class="flex items-center space-x-3">
                        <div class="w-8 h-8 rounded-full btn-gradient flex items-center justify-center text-white font-bold text-sm">
                            ${index + 1}
                        </div>
                        <div>
                            <p class="text-sm font-medium text-white">${user.get_full_name || user.username}</p>
                            <p class="text-xs text-gray-400">${user.total_avisos} avisos • ${user.total_comentarios} comentarios</p>
                        </div>
                    </div>
                    <div class="text-right">
                        <div class="text-sm font-medium text-costa-green">${user.total_actividad}</div>
                        <div class="text-xs text-gray-400">total</div>
                    </div>
                </div>
            `).join('');
        }


        function cambiarPeriodo(periodo) {
            
            console.log('Cambiar período a:', periodo);
            
        }

        function exportarCSV() {
            
            const fechaActual = new Date().toISOString().split('T')[0];
            
            let csvContent = "data:text/csv;charset=utf-8,";
            csvContent += "Reporte de Estadisticas - CostaVerde\n";
            csvContent += `Fecha de Generacion,${fechaActual}\n\n`;

            csvContent += "ESTADISTICAS GENERALES\n";
            csvContent += "Metrica,Valor\n";
            csvContent += `Total Avisos,{{ total_avisos }}\n`;
            csvContent += `Total Usuarios,{{ total_usuarios }}\n`;
            csvContent += `Total Comentarios,{{ total_comentarios }}\n`;
            csvContent += `Avisos Últimos 30 días,{{ avisos_recientes }}\n`;
            csvContent += `Usuarios Últimos 30 días,{{ usuarios_recientes }}\n`;
            csvContent += `Comentarios Últimos 30 días,{{ comentarios_recientes }}\n\n`;
            

            csvContent += "ESTADOS DE AVISOS\n";
            csvContent += "Estado,Cantidad\n";
            csvContent += `Activos,${estadosData.activos}\n`;
            csvContent += `En Proceso,${estadosData.en_proceso}\n`;
            csvContent += `Resueltos,${estadosData.resueltos}\n\n`;
            

            csvContent += "PRIORIDADES DE AVISOS\n";
            csvContent += "Prioridad,Cantidad\n";
            csvContent += `Urgente,${prioridadesData.urgente}\n`;
            csvContent += `Alta,${prioridadesData.alta}\n`;
            csvContent += `Media,${prioridadesData.media}\n`;
            csvContent += `Baja,${prioridadesData.baja}\n\n`;
            

            csvContent += "TIPOS DE AVISOS\n";
            csvContent += "Tipo,Cantidad\n";
            tiposData.forEach(tipo => {
                const displayNames = {
                    'robo': 'Robo',
                    'vandalismo': 'Vandalismo',
                    'ruido': 'Ruido',
                    'iluminacion': 'Iluminación',
                    'basura': 'Basura',
                    'trafico': 'Tráfico',
                    'drogas': 'Drogas',
                    'asalto': 'Asalto',
                    'otro': 'Otro'
                };
                const nombre = displayNames[tipo.nombre] || tipo.nombre;
                csvContent += `${nombre},${tipo.total}\n`;
            });
            

            const encodedUri = encodeURI(csvContent);
            const link = document.createElement("a");
            link.setAttribute("href", encodedUri);
            link.setAttribute("download", `estadisticas_costaverde_${fechaActual}.csv`);
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }

        
        cargarTopUsuarios();