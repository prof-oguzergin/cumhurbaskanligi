# Basinda sayfasi konu simgeleri: 24x24, cizgi, currentColor.
YOL = {
    "Tantuni Endeksi": '<path d="M2.8 11.2V4.3c0-.8.7-1.5 1.5-1.5h6.9l10 10-8.4 8.4z"/><circle cx="7.3" cy="7.3" r="1.3"/><text x="13.6" y="16.4" font-size="8.2" font-weight="700" text-anchor="middle" fill="currentColor" stroke="none" font-family="Arial, sans-serif" transform="rotate(45 13.6 13.6)">₺</text>',
    "Yapay zekâ": '<path d="M11 3.5l1.9 5.1 5.1 1.9-5.1 1.9L11 17.5l-1.9-5.1L4 10.5l5.1-1.9z"/><path d="M18 14.5l.8 2.2 2.2.8-2.2.8-.8 2.2-.8-2.2-2.2-.8 2.2-.8z"/>',
    "Akademisyenlere YouTube yasağı": '<rect x="3" y="6" width="18" height="12" rx="3.5"/><path d="M10.3 9.6v4.8l4.1-2.4z"/><path d="M4 3.5l16 17"/>',
    "Yerli işlemci ve çip": '<rect x="7" y="7" width="10" height="10" rx="1.5"/><rect x="10" y="10" width="4" height="4" rx=".5"/><path d="M9.5 3.5v3.5M14.5 3.5v3.5M9.5 17v3.5M14.5 17v3.5M3.5 9.5H7M3.5 14.5H7M17 9.5h3.5M17 14.5h3.5"/>',
    "Eğitim ve üniversite": '<path d="M2 9.5l10-5 10 5-10 5z"/><path d="M6 11.5v4.8c3.2 2.4 8.8 2.4 12 0v-4.8"/><path d="M22 9.5v5.5"/>',
    "Bulut bilişim": '<path d="M7 18.5h10.2a4 4 0 0 0 .4-7.98A6 6 0 0 0 6.2 9.8 4.35 4.35 0 0 0 7 18.5z"/>',
    "Rektör Oldum ve Bilge ve Yonga": '<path d="M3 5.6c2.6-1 6-1 9 1 3-2 6.4-2 9-1v13.6c-2.6-1-6-1-9 1-3-2-6.4-2-9-1z"/><path d="M12 6.6v13.6"/>',
    "Adaylık ve siyaset": '<path d="M4 11h16v9.5H4z"/><path d="M7.5 11V3.5h9V11"/><path d="M9.7 7.3l1.6 1.6 3-3.1"/><path d="M4 14.5h16"/>',
    "Savunma sanayisi ve beyin göçü": '<path d="M12 2.8l8 3.1v6.1c0 4.6-3.4 7.9-8 9.2-4.6-1.3-8-4.6-8-9.2V5.9z"/><path d="M8.5 12h6.5M12.7 9.5l2.5 2.5-2.5 2.5"/>',
    "Adının geçtiği haberler": '<path d="M5 11.5h4v5.5H4v-3.3c0-2.6 1.1-4.6 3.2-6"/><path d="M15 11.5h4v5.5h-5v-3.3c0-2.6 1.1-4.6 3.2-6"/>',
}


def simge(konu, sinif="konu-simge"):
    yol = YOL.get(konu)
    if not yol:
        return ""
    return (f'<svg class="{sinif}" viewBox="0 0 24 24" width="24" height="24" aria-hidden="true" focusable="false" '
            f'fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">{yol}</svg>')
