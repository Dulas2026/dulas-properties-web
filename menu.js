document.addEventListener('DOMContentLoaded', function () {
  // Botón "Colaboradores" en el menú, justo después de "Club Inversor".
  // Lleva a la zona privada; si el comercial no ha iniciado sesión, el servidor
  // le envía a la pantalla de usuario y contraseña.
  document.querySelectorAll('.nav-links').forEach(function (ul) {
    if (ul.querySelector('.colab-link')) return;
    var club = ul.querySelector('a.club-link');
    var li = document.createElement('li');
    var a = document.createElement('a');
    a.href = '/colaboradores/';
    a.className = 'colab-link';
    a.setAttribute('rel', 'nofollow');
    a.innerHTML = '<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 018 0v4"/></svg>Colaboradores';
    if (/^\/(colaboradores|acceso-colaboradores)/.test(location.pathname)) a.classList.add('active');
    li.appendChild(a);
    var liClub = club ? club.closest('li') : null;
    if (liClub && liClub.parentNode === ul) liClub.insertAdjacentElement('afterend', li);
    else ul.appendChild(li);
  });

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
