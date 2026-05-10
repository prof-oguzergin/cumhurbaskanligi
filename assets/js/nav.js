/* =========================================
   Mobile hamburger nav toggle
   720px altinda hamburger butonu nav'i acip kapatir
   ========================================= */
(function () {
  'use strict';
  var btn = document.querySelector('.nav-toggle');
  var nav = document.getElementById('site-nav');
  if (!btn || !nav) return;

  function setOpen(open) {
    if (open) {
      nav.classList.add('is-open');
      btn.setAttribute('aria-expanded', 'true');
      btn.setAttribute('aria-label', 'Menüyü kapat');
      document.body.style.overflow = 'hidden';
    } else {
      nav.classList.remove('is-open');
      btn.setAttribute('aria-expanded', 'false');
      btn.setAttribute('aria-label', 'Menüyü aç');
      document.body.style.overflow = '';
    }
  }

  btn.addEventListener('click', function () {
    var isOpen = nav.classList.contains('is-open');
    setOpen(!isOpen);
  });

  // Menü içindeki linke tıklayınca otomatik kapat
  nav.addEventListener('click', function (e) {
    if (e.target.tagName === 'A') setOpen(false);
  });

  // ESC ile kapat
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && nav.classList.contains('is-open')) setOpen(false);
  });

  // Pencere boyutu büyürse (720px+) menü kapansın
  window.addEventListener('resize', function () {
    if (window.innerWidth > 720 && nav.classList.contains('is-open')) setOpen(false);
  });
})();
