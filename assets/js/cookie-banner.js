/* =========================================
   KVKK Uyumlu Çerez Banner — Mantık
   Hukuki Dayanak: KVKK Kurul 2022/1358 ve 2022/229

   Davranış:
   - Banner gösterimi (ilk ziyaret)
   - 3 aksiyon: tümünü kabul, tümünü reddet, ayarları yönet
   - Kategori bazlı toggle (zorunlu hariç opt-in)
   - Tercih localStorage'a yazılır (180 gün)
   - Onay verilmeden Google Analytics, YouTube embed yüklenmez
   ========================================= */

(function () {
  'use strict';

  var CONFIG = {
    storageKey: 'cookieConsent',
    storageVersion: '1.0',
    expiryDays: 180,
    gaId: 'G-XQPWBWM9N0',  // GA4 Measurement ID — oguzergin.net
    consentLogUrl: 'https://oguz-ergin-yapay-oguz.hf.space/api/log-consent'  // KVKK m.12/3 ispat logu
  };

  var DEFAULT_PREFS = {
    necessary: true,
    analytics: false,
    functional: false,
    thirdParty: false
  };

  // -------- DOM Helper (XSS-safe element builder) --------

  function el(tag, attrs) {
    var node = document.createElement(tag);
    if (attrs) {
      for (var k in attrs) {
        if (k === 'class') node.className = attrs[k];
        else if (k === 'dataset') Object.assign(node.dataset, attrs[k]);
        else if (k === 'onclick') node.addEventListener('click', attrs[k]);
        else if (k === 'checked' || k === 'disabled') node[k] = attrs[k];
        else node.setAttribute(k, attrs[k]);
      }
    }
    for (var i = 2; i < arguments.length; i++) {
      var c = arguments[i];
      if (c == null) continue;
      if (typeof c === 'string') node.appendChild(document.createTextNode(c));
      else node.appendChild(c);
    }
    return node;
  }

  // -------- Storage --------

  function getConsent() {
    try {
      var raw = localStorage.getItem(CONFIG.storageKey);
      if (!raw) return null;
      var parsed = JSON.parse(raw);
      if (parsed.version !== CONFIG.storageVersion) return null;
      var ageInDays = (Date.now() - parsed.timestamp) / (1000 * 60 * 60 * 24);
      if (ageInDays > CONFIG.expiryDays) return null;
      return parsed;
    } catch (e) {
      return null;
    }
  }

  function saveConsent(prefs, action) {
    var record = {
      version: CONFIG.storageVersion,
      timestamp: Date.now(),
      timestampISO: new Date().toISOString(),
      preferences: prefs,
      userAgent: navigator.userAgent,
      consentText: 'KVKK Çerez Onayı v1.0'
    };
    localStorage.setItem(CONFIG.storageKey, JSON.stringify(record));
    window.cookieConsent = prefs;
    window.dispatchEvent(new CustomEvent('cookieConsentChange', { detail: prefs }));
    loadAllowedScripts(prefs);
    // KVKK m.12/3 ispat — sunucuya anonim onay logu gönder
    sendConsentLog('cookie', action || 'save', prefs);
  }

  function sendConsentLog(type, action, prefs) {
    try {
      // Beacon API (sayfa ayrılırken bile gönderir, yanıt beklemez)
      var payload = JSON.stringify({
        type: type,
        action: action,
        preferences: prefs || {},
        version: CONFIG.storageVersion
      });
      if (navigator.sendBeacon) {
        var blob = new Blob([payload], { type: 'application/json' });
        navigator.sendBeacon(CONFIG.consentLogUrl, blob);
      } else {
        fetch(CONFIG.consentLogUrl, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: payload,
          keepalive: true
        }).catch(function(){});
      }
    } catch (e) {
      // Sessiz başarısızlık — logu kaydedemesek de kullanıcı deneyimini bozma
    }
  }

  // -------- Banner DOM (XSS-safe) --------

  function createBanner() {
    var description = el('p', { class: 'cookie-banner__description' },
      'Site deneyimini iyileştirmek ve performansı analiz etmek için çerez kullanıyoruz. ',
      el('strong', null, 'Zorunlu çerezler'),
      ' dışındakiler için onayınızı alıyoruz. ',
      el('a', { href: 'yasal.html#cerez' }, 'Detaylı bilgi'),
      '.'
    );

    var text = el('div', { class: 'cookie-banner__text' },
      el('p', { class: 'cookie-banner__title' }, 'Çerezleri Kullanıyoruz'),
      description
    );

    var buttons = el('div', { class: 'cookie-banner__buttons' },
      el('button', { class: 'cookie-btn cookie-btn--reject', type: 'button',
                     dataset: { action: 'reject' } }, 'Tümünü Reddet'),
      el('button', { class: 'cookie-btn cookie-btn--manage', type: 'button',
                     dataset: { action: 'manage' } }, 'Ayarları Yönet'),
      el('button', { class: 'cookie-btn cookie-btn--accept', type: 'button',
                     dataset: { action: 'accept' } }, 'Tümünü Kabul Et')
    );

    var content = el('div', { class: 'cookie-banner__content' }, text, buttons);

    return el('div', {
      class: 'cookie-banner',
      role: 'dialog',
      'aria-label': 'Çerez Onayı',
      'aria-live': 'polite'
    }, content);
  }

  function createCategoryRow(catKey, title, description, isChecked, isDisabled) {
    var input = el('input', {
      type: 'checkbox',
      dataset: { category: catKey },
      checked: isChecked,
      disabled: isDisabled
    });
    var slider = el('span', { class: 'toggle-slider' });
    var label = el('label', { class: 'toggle-switch' }, input, slider);

    var header = el('div', { class: 'cookie-category__header' },
      el('p', { class: 'cookie-category__title' }, title),
      label
    );

    return el('div', { class: 'cookie-category' },
      header,
      el('p', { class: 'cookie-category__description' }, description)
    );
  }

  function createModal() {
    var closeBtn = el('button', {
      class: 'cookie-modal__close',
      type: 'button',
      'aria-label': 'Kapat',
      dataset: { action: 'close' }
    }, '×');

    var header = el('div', { class: 'cookie-modal__header' },
      el('h2', { class: 'cookie-modal__title', id: 'cookie-modal-title' }, 'Çerez Tercihleri'),
      closeBtn
    );

    var intro = el('p', { class: 'cookie-modal__intro' },
      'Hangi çerezlere izin vermek istediğinizi seçin. Tercihinizi ',
      el('strong', null, 'dilediğiniz zaman'),
      ' sayfa altındaki "Çerez Tercihleri" bağlantısından değiştirebilirsiniz.'
    );

    var categories = [
      createCategoryRow('necessary', 'Zorunlu Çerezler',
        'Sitenin çalışması için zorunlu çerezler (oturum, güvenlik). Devre dışı bırakılamaz.',
        true, true),
      createCategoryRow('analytics', 'Analitik Çerezler',
        'Google Analytics aracılığıyla site kullanımını ölçer. IP adresi anonimleştirilir.',
        false, false),
      createCategoryRow('functional', 'İşlevsellik Çerezleri',
        'Dil/tema tercihi, form bilgilerinin hatırlanması gibi konfor özellikleri.',
        false, false),
      createCategoryRow('thirdParty', 'Üçüncü Taraf Çerezleri',
        'YouTube embed video, sosyal medya widget\'ları. Yüklendiğinde ilgili platforma IP adresiniz aktarılır.',
        false, false)
    ];

    var footer = el('div', { class: 'cookie-modal__footer' },
      el('button', { class: 'cookie-btn cookie-btn--reject', type: 'button',
                     dataset: { action: 'reject' } }, 'Tümünü Reddet'),
      el('button', { class: 'cookie-btn cookie-btn--accept', type: 'button',
                     dataset: { action: 'save' } }, 'Tercihleri Kaydet')
    );

    var modalNode = el('div', { class: 'cookie-modal', role: 'document' },
      header, intro, categories[0], categories[1], categories[2], categories[3], footer);

    return el('div', {
      class: 'cookie-modal-overlay',
      role: 'dialog',
      'aria-modal': 'true',
      'aria-labelledby': 'cookie-modal-title'
    }, modalNode);
  }

  // -------- Aksiyonlar --------

  var bannerEl, modalEl;

  function updateBodySpacer() {
    if (bannerEl && bannerEl.classList.contains('visible')) {
      // Banner yuksekligi kadar body'ye padding-bottom ekle ki footer banner ustunde kalsin
      document.body.style.paddingBottom = (bannerEl.offsetHeight + 12) + 'px';
    }
  }

  function showBanner() {
    if (bannerEl) return;
    bannerEl = createBanner();
    document.body.appendChild(bannerEl);
    requestAnimationFrame(function () {
      bannerEl.classList.add('visible');
      updateBodySpacer();
    });
    bannerEl.addEventListener('click', handleBannerClick);
    window.addEventListener('resize', updateBodySpacer);
  }

  function hideBanner() {
    if (!bannerEl) return;
    bannerEl.classList.remove('visible');
    document.body.style.paddingBottom = '';
    window.removeEventListener('resize', updateBodySpacer);
    setTimeout(function () { if (bannerEl) bannerEl.remove(); bannerEl = null; }, 300);
  }

  function showModal() {
    if (!modalEl) {
      modalEl = createModal();
      document.body.appendChild(modalEl);
      modalEl.addEventListener('click', handleModalClick);
    }
    var existing = getConsent();
    var consent = (existing && existing.preferences) || DEFAULT_PREFS;
    var inputs = modalEl.querySelectorAll('input[data-category]');
    for (var i = 0; i < inputs.length; i++) {
      var cat = inputs[i].dataset.category;
      if (cat !== 'necessary') inputs[i].checked = !!consent[cat];
    }
    modalEl.classList.add('visible');
  }

  function hideModal() {
    if (modalEl) modalEl.classList.remove('visible');
  }

  function handleBannerClick(e) {
    var target = e.target.closest('[data-action]');
    var action = target && target.dataset.action;
    if (!action) return;

    if (action === 'accept') {
      saveConsent({ necessary: true, analytics: true, functional: true, thirdParty: true }, 'accept-all');
      hideBanner();
    } else if (action === 'reject') {
      saveConsent({ necessary: true, analytics: false, functional: false, thirdParty: false }, 'reject-all');
      hideBanner();
    } else if (action === 'manage') {
      showModal();
    }
  }

  function handleModalClick(e) {
    var target = e.target.closest('[data-action]');
    var action = target && target.dataset.action;
    if (action === 'close') { hideModal(); return; }
    if (action === 'reject') {
      saveConsent({ necessary: true, analytics: false, functional: false, thirdParty: false }, 'reject-all');
      hideModal();
      hideBanner();
      return;
    }
    if (action === 'save') {
      var prefs = { necessary: true };
      modalEl.querySelectorAll('input[data-category]').forEach(function (input) {
        prefs[input.dataset.category] = input.checked;
      });
      saveConsent(prefs, 'save-custom');
      hideModal();
      hideBanner();
    }
  }

  // -------- Onaylanan Script Yükleyiciler --------

  function loadAllowedScripts(prefs) {
    if (prefs.analytics) loadGoogleAnalytics();
    if (prefs.thirdParty) loadEmbeds();
  }

  function loadGoogleAnalytics() {
    if (window._gaLoaded) return;
    if (!CONFIG.gaId || /^G-XXXX/.test(CONFIG.gaId)) {
      console.warn('[CookieBanner] GA Measurement ID girilmedi.');
      return;
    }
    window._gaLoaded = true;

    var script = document.createElement('script');
    script.async = true;
    script.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(CONFIG.gaId);
    document.head.appendChild(script);

    window.dataLayer = window.dataLayer || [];
    function gtag() { window.dataLayer.push(arguments); }
    window.gtag = gtag;
    gtag('js', new Date());
    gtag('config', CONFIG.gaId, { anonymize_ip: true });
  }

  function loadEmbeds() {
    document.querySelectorAll('[data-yt-embed]').forEach(function (placeholder) {
      var videoId = placeholder.dataset.ytEmbed;
      if (!videoId || !/^[A-Za-z0-9_-]{11}$/.test(videoId)) return;
      var title = placeholder.dataset.ytTitle || '';
      var iframe = document.createElement('iframe');
      iframe.src = 'https://www.youtube-nocookie.com/embed/' + videoId;
      iframe.width = '100%';
      iframe.height = '315';
      iframe.frameBorder = '0';
      if (title) iframe.title = title;
      iframe.setAttribute('allow', 'accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture');
      iframe.allowFullscreen = true;
      placeholder.replaceWith(iframe);
    });

    window.dispatchEvent(new CustomEvent('thirdPartyConsentGranted'));
  }

  function attachPrefsLink() {
    document.querySelectorAll('[data-cookie-prefs]').forEach(function (link) {
      link.addEventListener('click', function (e) {
        e.preventDefault();
        showModal();
      });
    });
  }

  // -------- Init --------

  function init() {
    var consent = getConsent();
    if (consent) {
      window.cookieConsent = consent.preferences;
      loadAllowedScripts(consent.preferences);
    } else {
      showBanner();
    }
    attachPrefsLink();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Public API (test/debug)
  window.cookieBannerAPI = {
    show: showBanner,
    showModal: showModal,
    getConsent: getConsent,
    reset: function () { localStorage.removeItem(CONFIG.storageKey); location.reload(); }
  };
})();
