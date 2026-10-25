/**
 * Curriculum Management System - Core Client Script
 */

document.addEventListener('DOMContentLoaded', function () {
  // 1. Initialise all Bootstrap Toasts
  const toastElements = document.querySelectorAll('.toast');
  toastElements.forEach(el => {
    const toast = new bootstrap.Toast(el, { autohide: true, delay: 5000 });
    toast.show();
  });

  // 2. Mobile sidebar toggle
  const sidebar = document.getElementById('sidebar');
  const sidebarToggle = document.getElementById('sidebar-toggle');

  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', function (e) {
      e.stopPropagation();
      sidebar.classList.toggle('show');
    });

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function (e) {
      if (window.innerWidth <= 768 && sidebar.classList.contains('show')) {
        if (!sidebar.contains(e.target) && e.target !== sidebarToggle) {
          sidebar.classList.remove('show');
        }
      }
    });
  }

  // 3. Mapping input validation (accepts 1, 2, 3 or blank)
  const mappingInputs = document.querySelectorAll('.mapping-grid input[type="number"]');
  mappingInputs.forEach(inp => {
    inp.addEventListener('input', function () {
      const val = parseInt(this.value, 10);
      if (this.value !== '' && (isNaN(val) || val < 1 || val > 3)) {
        this.classList.add('is-invalid');
      } else {
        this.classList.remove('is-invalid');
      }
    });
  });

  // 4. Generic data-confirm handlers for destructive operations
  document.querySelectorAll('[data-confirm]').forEach(btn => {
    btn.addEventListener('click', function (e) {
      const message = this.getAttribute('data-confirm') || 'Are you sure you want to proceed?';
      if (!window.confirm(message)) {
        e.preventDefault();
        e.stopImmediatePropagation();
        return false;
      }
    });
  });
});
