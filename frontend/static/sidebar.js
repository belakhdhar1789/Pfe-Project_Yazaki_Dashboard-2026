// ── Yazaki Dashboard — Shared Sidebar ─────────────────────────────────────────
// Used by all main pages (handbook, dashboard, data-collection, etc.)
// Sidebar slides in from the RIGHT on hover.

const MENU_ITEMS = [
  { label: 'GUM vs AWT HANDBOOK', path: '/handbook',        icon: 'book',    perm: 'handbook'        },
  { label: 'GUM vs AWT Dashboard', path: '/dashboard',      icon: 'chart',   perm: 'dashboard'       },
  { label: 'DATA Collection',      path: '/data-collection',icon: 'table',   perm: 'dataCollection'  },
  { label: 'Batch-KSK',            path: '/batch-ksk',      icon: 'grid',    perm: 'BatchKsk'        },
  { label: 'Table',                path: '/table',           icon: 'list',    perm: 'table'           },
  { label: 'Revision History',     path: '/revision-history',icon: 'clock',  perm: 'revisionHistory' },
];

const ICONS = {
  book:  `<svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/></svg>`,
  chart: `<svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>`,
  table: `<svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M3 14h18M10 4v16M6 4h12a2 2 0 012 2v12a2 2 0 01-2 2H6a2 2 0 01-2-2V6a2 2 0 012-2z"/></svg>`,
  grid:  `<svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zm10 0a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zm10 0a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"/></svg>`,
  list:  `<svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M3 6h18M3 14h18M3 18h18"/></svg>`,
  clock: `<svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>`,
  user:  `<svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>`,
  shield:`<svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>`,
};

// ── checkAuth ─────────────────────────────────────────────────────────────────
// Fetches /api/auth/me, redirects to / if not authenticated.
// Returns the user object (includes role and permissions[]).
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
// Call this at the top of any protected page.
// pageName: e.g. 'table', 'dashboard', 'handbook'
// Admin always has access. Users need the permission granted by admin.
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
// activePath: current page path e.g. '/table'
// user: object returned by checkAuth()
function buildSidebar(activePath, user) {
  const menu = document.getElementById('sidebar-menu');
  if (!menu) return;
  menu.innerHTML = '';

  const perms    = user.permissions || [];
  const isAdmin  = user.role === 'admin';

  MENU_ITEMS.forEach(item => {
    // Hide menu item if user doesn't have permission (admin sees everything)
    if (!isAdmin && !perms.includes(item.perm)) return;

    const isActive = activePath === item.path;
    const a = document.createElement('a');
    a.href = item.path;
    a.className = 'sidebar-link' + (isActive ? ' active' : '');
    a.innerHTML = ICONS[item.icon] + `<span>${item.label}</span>`;
    menu.appendChild(a);
  });

  // Divider
  const hr = document.createElement('div');
  hr.className = 'mx-4 my-2 border-t border-gray-100';
  menu.appendChild(hr);

  // Profile — always visible
  const profileActive = activePath === '/profile';
  const profileLink = document.createElement('a');
  profileLink.href = '/profile';
  profileLink.className = 'sidebar-link' + (profileActive ? ' active' : '');
  profileLink.innerHTML = ICONS['user'] + '<span>Profile</span>';
  menu.appendChild(profileLink);

  // Admin — only for admin role
  if (isAdmin) {
    const adminActive = activePath === '/admin';
    const adminLink = document.createElement('a');
    adminLink.href = '/admin';
    adminLink.className = 'sidebar-link' + (adminActive ? ' active' : '');
    adminLink.innerHTML = ICONS['shield'] + '<span>Admin Panel</span>';
    menu.appendChild(adminLink);
  }
}

// ── handleLogout ──────────────────────────────────────────────────────────────
async function handleLogout() {
  try { await fetch('/api/auth/logout', { method: 'POST' }); } catch(e) {}
  window.location.href = '/';
}
