/* ==========================================================================
   Explorateur Unicode — logique applicative (JavaScript vanilla)

   Le site charge output/data.json (généré par script.py, mis à jour par le
   workflow GitHub Actions). Si le fichier est indisponible (prévisualisation
   locale, ouverture directe du HTML), un petit jeu de démonstration est
   utilisé et un bandeau d'avertissement s'affiche.
   ========================================================================== */

'use strict';

/* --------------------------------------------------------------------------
   Jeu de démonstration (secours hors-ligne)
   -------------------------------------------------------------------------- */
const FALLBACK_DATA = {
  meta: { generated_at: null, unicode_version: null, total: 48, demo: true },
  categories: [
    {
      id: 'smileys', name: 'Smileys & émotions', icon: '😀', count: 16,
      characters: [
        { char: '😀', code: 'U+1F600', name: 'GRINNING FACE' },
        { char: '😁', code: 'U+1F601', name: 'GRINNING FACE WITH SMILING EYES' },
        { char: '😂', code: 'U+1F602', name: 'FACE WITH TEARS OF JOY' },
        { char: '😅', code: 'U+1F605', name: 'SMILING FACE WITH COLD SWEAT' },
        { char: '😍', code: 'U+1F60D', name: 'SMILING FACE WITH HEART-SHAPED EYES' },
        { char: '😎', code: 'U+1F60E', name: 'SMILING FACE WITH SUNGLASSES' },
        { char: '🤔', code: 'U+1F914', name: 'THINKING FACE' },
        { char: '🤪', code: 'U+1F92A', name: 'ZANY FACE' },
        { char: '😴', code: 'U+1F634', name: 'SLEEPING FACE' },
        { char: '🥳', code: 'U+1F973', name: 'FACE WITH PARTY HORN AND PARTY HAT' },
        { char: '😭', code: 'U+1F62D', name: 'LOUDLY CRYING FACE' },
        { char: '😡', code: 'U+1F621', name: 'POUTING FACE' },
        { char: '👍', code: 'U+1F44D', name: 'THUMBS UP SIGN' },
        { char: '👏', code: 'U+1F44F', name: 'CLAPPING HANDS SIGN' },
        { char: '🙏', code: 'U+1F64F', name: 'PERSON WITH FOLDED HANDS' },
        { char: '👋', code: 'U+1F44B', name: 'WAVING HAND SIGN' },
      ],
    },
    {
      id: 'fleches', name: 'Flèches', icon: '➡️', count: 9,
      characters: [
        { char: '←', code: 'U+2190', name: 'LEFTWARDS ARROW' },
        { char: '↑', code: 'U+2191', name: 'UPWARDS ARROW' },
        { char: '→', code: 'U+2192', name: 'RIGHTWARDS ARROW' },
        { char: '↓', code: 'U+2193', name: 'DOWNWARDS ARROW' },
        { char: '↔', code: 'U+2194', name: 'LEFT RIGHT ARROW' },
        { char: '↕', code: 'U+2195', name: 'UP DOWN ARROW' },
        { char: '↩', code: 'U+21A9', name: 'LEFTWARDS ARROW WITH HOOK' },
        { char: '➡', code: 'U+27A1', name: 'BLACK RIGHTWARDS ARROW' },
        { char: '⬅', code: 'U+2B05', name: 'LEFTWARDS BLACK ARROW' },
      ],
    },
    {
      id: 'maths', name: 'Mathématiques', icon: '∑', count: 13,
      characters: [
        { char: '∞', code: 'U+221E', name: 'INFINITY' },
        { char: '∅', code: 'U+2205', name: 'EMPTY SET' },
        { char: '∈', code: 'U+2208', name: 'ELEMENT OF' },
        { char: '∑', code: 'U+2211', name: 'N-ARY SUMMATION' },
        { char: '∏', code: 'U+220F', name: 'N-ARY PRODUCT' },
        { char: '√', code: 'U+221A', name: 'SQUARE ROOT' },
        { char: '∫', code: 'U+222B', name: 'INTEGRAL' },
        { char: '≠', code: 'U+2260', name: 'NOT EQUAL TO' },
        { char: '≤', code: 'U+2264', name: 'LESS-THAN OR EQUAL TO' },
        { char: '≥', code: 'U+2265', name: 'GREATER-THAN OR EQUAL TO' },
        { char: '×', code: 'U+00D7', name: 'MULTIPLICATION SIGN' },
        { char: '÷', code: 'U+00F7', name: 'DIVISION SIGN' },
        { char: '±', code: 'U+00B1', name: 'PLUS-MINUS SIGN' },
      ],
    },
    {
      id: 'symboles', name: 'Symboles', icon: '❤️', count: 10,
      characters: [
        { char: '❤', code: 'U+2764', name: 'HEAVY BLACK HEART' },
        { char: '✨', code: 'U+2728', name: 'SPARKLES' },
        { char: '⭐', code: 'U+2B50', name: 'WHITE MEDIUM STAR' },
        { char: '☀', code: 'U+2600', name: 'BLACK SUN WITH RAYS' },
        { char: '☯', code: 'U+262F', name: 'YIN YANG' },
        { char: '☮', code: 'U+262E', name: 'PEACE SYMBOL' },
        { char: '✔', code: 'U+2714', name: 'HEAVY CHECK MARK' },
        { char: '❌', code: 'U+274C', name: 'CROSS MARK' },
        { char: '⚠', code: 'U+26A0', name: 'WARNING SIGN' },
        { char: '♻', code: 'U+267B', name: 'BLACK UNIVERSAL RECYCLING SYMBOL' },
      ],
    },
  ],
};

/* --------------------------------------------------------------------------
   État & références DOM
   -------------------------------------------------------------------------- */
const els = {
  nav: document.getElementById('cat-nav'),
  grid: document.getElementById('grid'),
  info: document.getElementById('results-info'),
  sentinel: document.getElementById('sentinel'),
  search: document.getElementById('search'),
  modal: document.getElementById('modal'),
  modalBody: document.getElementById('modal-body'),
  toast: document.getElementById('toast'),
  footerInfo: document.getElementById('footer-info'),
  banner: document.getElementById('demo-banner'),
};

const BATCH = 240; // nombre de cellules rendues par lot (chargement progressif)

const state = {
  categories: [],
  active: 'all',
  query: '',
  list: [],
  shown: 0,
};

/* --------------------------------------------------------------------------
   Chargement des données
   -------------------------------------------------------------------------- */
(async function loadData() {
  try {
    const res = await fetch('output/data.json', { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    init(data, false);
  } catch (err) {
    console.warn('data.json indisponible, jeu de démonstration utilisé :', err);
    init(FALLBACK_DATA, true);
  }
})();

function init(data, demo) {
  state.categories = data.categories;

  // Pré-calcul du point de code numérique pour la recherche par code.
  for (const cat of state.categories) {
    for (const c of cat.characters) c.cp = c.char.codePointAt(0);
  }

  buildNav();
  applyFilters();

  if (demo) {
    els.banner.hidden = false;
    els.footerInfo.textContent =
      'Données de démonstration — exécutez « python3 script.py » puis servez le dossier en HTTP pour charger la base complète.';
  } else {
    const d = new Date(data.meta.generated_at);
    const date = Number.isNaN(d.getTime()) ? '' : d.toLocaleString('fr-FR');
    els.footerInfo.textContent =
      `Base Unicode v${data.meta.unicode_version} · ` +
      `${data.meta.total.toLocaleString('fr-FR')} caractères · ` +
      `générée le ${date} · mise à jour automatique quotidienne (GitHub Actions)`;
  }
}

/* --------------------------------------------------------------------------
   Navigation des catégories
   -------------------------------------------------------------------------- */
function buildNav() {
  els.nav.innerHTML = '';
  const total = state.categories.reduce((n, c) => n + c.characters.length, 0);
  els.nav.appendChild(navButton('all', '✨', 'Toutes', total));
  for (const cat of state.categories) {
    els.nav.appendChild(navButton(cat.id, cat.icon, cat.name, cat.characters.length));
  }
}

function navButton(id, icon, name, count) {
  const btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'cat-btn';
  btn.dataset.id = id;

  const spanIcon = document.createElement('span');
  spanIcon.className = 'cat-icon';
  spanIcon.textContent = icon;

  const spanName = document.createElement('span');
  spanName.className = 'cat-name';
  spanName.textContent = name;

  const spanCount = document.createElement('span');
  spanCount.className = 'cat-count';
  spanCount.textContent = count.toLocaleString('fr-FR');

  btn.append(spanIcon, spanName, spanCount);

  btn.addEventListener('click', () => {
    state.active = id;
    syncNavButtons();
    applyFilters();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });

  if (state.active === id) btn.classList.add('active');
  return btn;
}

function syncNavButtons() {
  for (const btn of els.nav.querySelectorAll('.cat-btn')) {
    btn.classList.toggle('active', btn.dataset.id === state.active);
  }
}

/* --------------------------------------------------------------------------
   Filtrage & recherche
   -------------------------------------------------------------------------- */
function buildMatcher(rawQuery) {
  const q = rawQuery.trim();
  if (!q) return () => true;

  // Détection d'un code hexadécimal : "U+1F600", "0x1F600" ou "1f600"
  // (n'importe quel mot contenant un chiffre et uniquement des caractères hex).
  let cp = null;
  const m = q.match(/^(?:u\+|0x)?([0-9a-f]+)$/i);
  if (m && /[0-9]/.test(q)) {
    const parsed = parseInt(m[1], 16);
    if (parsed <= 0x10FFFF) cp = parsed;
  }

  const upper = q.toUpperCase();
  const singleChar = q; // comparaison directe (collage d'un caractère)

  return (c) =>
    c.char === singleChar ||
    (cp !== null && c.cp === cp) ||
    c.name.includes(upper);
}

function applyFilters() {
  const match = buildMatcher(state.query);
  const items = [];

  for (const cat of state.categories) {
    if (state.active !== 'all' && cat.id !== state.active) continue;
    for (const c of cat.characters) {
      if (match(c)) items.push(c);
    }
  }

  state.list = items;
  state.shown = 0;
  els.grid.innerHTML = '';

  const info = `${items.length.toLocaleString('fr-FR')} caractère${items.length > 1 ? 's' : ''}`;
  els.info.textContent = state.query
    ? `${info} pour « ${state.query.trim()} »`
    : info;

  if (items.length === 0) {
    const empty = document.createElement('p');
    empty.className = 'empty';
    empty.textContent = `Aucun caractère ne correspond à « ${state.query.trim()} ». Essayez un nom anglais, un code U+… ou collez directement un caractère.`;
    els.grid.appendChild(empty);
    return;
  }

  renderBatch();
}

/* --------------------------------------------------------------------------
   Rendu progressif de la grille
   -------------------------------------------------------------------------- */
function renderBatch() {
  if (state.shown >= state.list.length) return;

  const frag = document.createDocumentFragment();
  const end = Math.min(state.shown + BATCH, state.list.length);

  for (let i = state.shown; i < end; i++) {
    const c = state.list[i];
    const cell = document.createElement('button');
    cell.type = 'button';
    cell.className = 'char-cell';
    cell.textContent = c.char;
    cell.title = `${c.name}\n${c.code}`;
    cell.addEventListener('click', () => openModal(c));
    frag.appendChild(cell);
  }

  els.grid.appendChild(frag);
  state.shown = end;
}

const observer = new IntersectionObserver(
  (entries) => {
    if (entries[0].isIntersecting) renderBatch();
  },
  { rootMargin: '600px' }
);
observer.observe(els.sentinel);

/* --------------------------------------------------------------------------
   Modale de détail
   -------------------------------------------------------------------------- */
function getDetails(c) {
  const cp = c.char.codePointAt(0);
  const hex = cp.toString(16).toUpperCase();
  const hex4 = hex.padStart(4, '0');

  // Unités UTF-16 (gère les paires de substituts pour les plans astraux).
  const units = [];
  for (let i = 0; i < c.char.length; i++) {
    units.push(c.char.charCodeAt(i).toString(16).toUpperCase().padStart(4, '0'));
  }
  const jsUnits = '\\u' + units.join('\\u');
  const js = cp > 0xFFFF ? `\\u{${hex}}  (ou  ${jsUnits})` : jsUnits;

  const utf8 = Array.from(new TextEncoder().encode(c.char))
    .map((b) => b.toString(16).toUpperCase().padStart(2, '0'))
    .join(' ');

  return [
    ['Caractère', c.char],
    ['Point de code', `${c.code}  (décimal ${cp})`],
    ['HTML (hexa)', `&#x${hex};`],
    ['HTML (décimal)', `&#${cp};`],
    ['CSS', cp > 0xFFFF ? `\\${hex.padStart(6, '0')}` : `\\${hex4}`],
    ['JavaScript', js],
    ['UTF-8', utf8],
  ];
}

function openModal(c) {
  els.modalBody.innerHTML = '';

  const preview = document.createElement('div');
  preview.className = 'modal-preview';
  preview.textContent = c.char;

  const name = document.createElement('h3');
  name.className = 'modal-name';
  name.textContent = c.name;

  els.modalBody.append(preview, name);

  for (const [label, value] of getDetails(c)) {
    const row = document.createElement('div');
    row.className = 'kv';

    const l = document.createElement('span');
    l.className = 'kv-label';
    l.textContent = label;

    const v = document.createElement('code');
    v.className = 'kv-value';
    v.textContent = value;

    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'copy-btn';
    btn.textContent = 'Copier';
    btn.dataset.copy = value;

    row.append(l, v, btn);
    els.modalBody.appendChild(row);
  }

  els.modal.hidden = false;
  document.body.style.overflow = 'hidden';
}

function closeModal() {
  if (els.modal.hidden) return;
  els.modal.hidden = true;
  document.body.style.overflow = '';
}

els.modal.addEventListener('click', (e) => {
  if (e.target.closest('[data-close]')) closeModal();
});

els.modalBody.addEventListener('click', async (e) => {
  const btn = e.target.closest('[data-copy]');
  if (!btn) return;
  await copyText(btn.dataset.copy);
  btn.classList.add('copied');
  btn.textContent = 'Copié ✓';
  setTimeout(() => {
    btn.classList.remove('copied');
    btn.textContent = 'Copier';
  }, 1200);
});

/* --------------------------------------------------------------------------
   Presse-papiers & notification
   -------------------------------------------------------------------------- */
async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text);
  } catch {
    // Repli pour les contextes non sécurisés (file://, http sans HTTPS).
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    ta.remove();
  }

  const short = text.length > 28 ? text.slice(0, 28) + '…' : text;
  showToast(`Copié : ${short}`);
}

let toastTimer = null;
function showToast(message) {
  els.toast.textContent = message;
  els.toast.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => els.toast.classList.remove('show'), 1600);
}

/* --------------------------------------------------------------------------
   Recherche & raccourcis clavier
   -------------------------------------------------------------------------- */
let searchTimer = null;
els.search.addEventListener('input', (e) => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => {
    state.query = e.target.value;
    applyFilters();
  }, 120);
});

document.addEventListener('keydown', (e) => {
  if (e.key === '/' && document.activeElement !== els.search) {
    e.preventDefault();
    els.search.focus();
  } else if (e.key === 'Escape') {
    closeModal();
  }
});
