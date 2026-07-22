document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.nav-toggle').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var nav = btn.closest('nav') || document;
      var links = nav.querySelector('.nav-links');
      if (!links) return;
      var isOpen = links.classList.toggle('nav-open');
      btn.textContent = isOpen ? '✕' : '☰';
      btn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    });
  });
});
