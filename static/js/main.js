/* ResumeIQ Main Client Script */

document.addEventListener('DOMContentLoaded', () => {
  initThemeToggle();
  initToastAlerts();
  initCopyHelpers();
  initSidebarToggle();
});

// 1. Theme Toggle (Dark / Light)
function initThemeToggle() {
  const themeBtn = document.getElementById('themeToggleBtn');
  if (!themeBtn) return;

  themeBtn.addEventListener('click', () => {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('careerpilot_theme', newTheme);
    
    const icon = themeBtn.querySelector('i');
    if (icon) {
      icon.className = newTheme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-stars-fill';
    }
  });

  // Load saved theme
  const savedTheme = localStorage.getItem('careerpilot_theme') || 'dark';
  document.documentElement.setAttribute('data-theme', savedTheme);
  const icon = themeBtn.querySelector('i');
  if (icon) {
    icon.className = savedTheme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-stars-fill';
  }
}

// 2. Toast Alert Auto Dismiss
function initToastAlerts() {
  const alerts = document.querySelectorAll('.alert-dismissible');
  alerts.forEach(alert => {
    setTimeout(() => {
      const bsAlert = new bootstrap.Alert(alert);
      bsAlert.close();
    }, 4500);
  });
}

// 3. Copy Text Helper
function initCopyHelpers() {
  document.querySelectorAll('.btn-copy-text').forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('data-target');
      const targetElem = document.getElementById(targetId);
      if (targetElem) {
        navigator.clipboard.writeText(targetElem.innerText);
        const origText = btn.innerHTML;
        btn.innerHTML = '<i class="bi bi-check2"></i> Copied!';
        setTimeout(() => {
          btn.innerHTML = origText;
        }, 2000);
      }
    });
  });
}

// 4. Sidebar Toggle (Mobile)
function initSidebarToggle() {
  const sidebarBtn = document.getElementById('sidebarToggleBtn');
  const sidebar = document.getElementById('appSidebar');
  
  if (sidebarBtn && sidebar) {
    sidebarBtn.addEventListener('click', () => {
      sidebar.classList.toggle('show');
    });

    // Close sidebar if user clicks outside of it on mobile
    document.addEventListener('click', (e) => {
      if (window.innerWidth <= 991.98 && sidebar.classList.contains('show')) {
        if (!sidebar.contains(e.target) && !sidebarBtn.contains(e.target)) {
          sidebar.classList.remove('show');
        }
      }
    });
  }
}
