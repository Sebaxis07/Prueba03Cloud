lucide.createIcons();

        function toggleSidebar() {
            const sidebar = document.getElementById('sidebar');
            const overlay = document.getElementById('sidebar-overlay');
            
            sidebar.classList.toggle('-translate-x-full');
            overlay.classList.toggle('hidden');
        }

      
        setTimeout(() => {
            window.location.reload();
        }, 30000);


        function animateCounter(element, target) {
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
            }, 20);
        }

        
        document.addEventListener('DOMContentLoaded', () => {
            const counters = document.querySelectorAll('.stat-card .text-2xl');
            counters.forEach(counter => {
                const target = parseInt(counter.textContent);
                animateCounter(counter, target);
            });
        });