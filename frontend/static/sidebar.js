// ── Yazaki Dashboard — Shared Sidebar ─────────────────────────────────────────
// Matches the Figma Layout.tsx design exactly.
// Trigger zone (right: 0, z-index 30) → panel slides in (translateX, z-index 40).

const MENU_ITEMS = [
  { label: 'GUM vs AWT HANDBOOK', path: '/handbook',          perm: 'handbook'        },
  { label: 'Batch-KSK',           path: '/batch-ksk',         perm: 'BatchKsk'        },
  { label: 'Table',               path: '/table',              perm: 'table'           },
  { label: 'Revision History',    path: '/revision-history',  perm: 'revisionHistory' },
];

// ── checkAuth ─────────────────────────────────────────────────────────────────
async function checkAuth() {
  try {
    const res = await fetch('/api/auth/me');
    if (!res.ok) { window.location.href = '/'; return null; }
    const user = await res.json();
    if (!user || user.error) { window.location.href = '/'; return null; }
    return user;
  } catch(e) {
    window.location.href = '/';
    return null;
  }
}

// ── checkPermission ───────────────────────────────────────────────────────────
function checkPermission(user, pageName) {
  if (!user) { window.location.href = '/'; return false; }
  if (user.role === 'admin') return true;
  const perms = user.permissions || [];
  if (!perms.includes(pageName)) {
    window.location.href = '/handbook';
    return false;
  }
  return true;
}

// ── buildSidebar ──────────────────────────────────────────────────────────────
// Matches Figma: full-width bordered buttons, active = red gradient.
function buildSidebar(activePath, user) {
  const menu = document.getElementById('sidebar-menu');
  if (!menu) return;
  menu.innerHTML = '';

  const perms   = user.permissions || [];
  const isAdmin = user.role === 'admin';

  const btnClass = (isActive) =>
    'sidebar-btn' + (isActive ? ' active' : '');

  MENU_ITEMS.forEach(item => {
    if (!isAdmin && !perms.includes(item.perm)) return;
    const a = document.createElement('a');
    a.href = item.path;
    a.className = btnClass(activePath === item.path);
    a.textContent = item.label;
    menu.appendChild(a);
  });

  // Profile — always visible
  const profileLink = document.createElement('a');
  profileLink.href = '/profile';
  profileLink.className = btnClass(activePath === '/profile');
  profileLink.textContent = 'Profile';
  menu.appendChild(profileLink);

  // Admin — admin only
  if (isAdmin) {
    const adminLink = document.createElement('a');
    adminLink.href = '/admin';
    adminLink.className = btnClass(activePath === '/admin');
    adminLink.textContent = 'Admin Panel';
    menu.appendChild(adminLink);
  }

  // Show username
  const userEl = document.getElementById('sidebar-user');
  if (userEl) userEl.textContent = user.full_name || '';
}

// ── handleLogout ──────────────────────────────────────────────────────────────
async function handleLogout() {
  try { await fetch('/api/auth/logout', { method: 'POST' }); } catch(e) {}
  window.location.href = '/';
}

// ── Sidebar open / close ──────────────────────────────────────────────────────
// onmouseenter on #sidebar-trigger → open
// onmouseleave on #sidebar-panel   → close
// Panel z-index (40) > trigger z-index (30), so panel covers trigger when open.
function openSidebar()  { document.getElementById('sidebar-panel').classList.add('open');    }
function closeSidebar() { document.getElementById('sidebar-panel').classList.remove('open'); }
