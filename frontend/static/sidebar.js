function buildSidebar(activePath) {
  const role = sessionStorage.getItem('role') || localStorage.getItem('role') || '';
  const fullName = sessionStorage.getItem('full_name') || localStorage.getItem('full_name') || '';

  const baseItems = [
    { label: 'GUM vs AWT HANDBOOK', path: '/handbook' },
    { label: 'GUM vs AWT Dashboard', path: '/dashboard' },
    { label: 'DATA Collection', path: '/data-collection' },
    { label: 'Overview Batch-KSK', path: '/overview-batch' },
    { label: 'Table', path: '/table' },
    { label: 'Revision History', path: '/revision-history' },
    { label: 'Profile', path: '/profile' },
  ];

  if (role === 'admin') {
    baseItems.push({ label: 'Admin', path: '/admin' });
  }

  const itemsHTML = baseItems.map(item => `
    <button onclick="window.location.href='${item.path}'"
      class="w-full block border-2 rounded-xl p-4 text-center font-bold text-base
             transition-all duration-200 hover:shadow-lg
             ${activePath === item.path
               ? 'bg-gradient-to-r from-red-600 to-red-700 text-white border-black shadow-md'
               : 'bg-white text-gray-800 border-gray-300 hover:border-red-600 hover:text-red-600'
             }">
      ${item.label}
    </button>
  `).join('');

  const html = `
    <!-- Hover trigger zone -->
    <div id="sidebar-trigger" class="fixed right-0 top-0 bottom-0 w-4 z-30"></div>

    <!-- Sidebar -->
    <div id="sidebar" class="fixed top-0 right-0 h-full w-80 bg-gradient-to-br from-gray-50 to-gray-100
                              shadow-2xl z-40 border-l-4 border-red-600 p-6 overflow-y-auto
                              transition-transform duration-300 translate-x-full"
         style="font-family:'Segoe UI',sans-serif;">

      <!-- Header -->
      <div class="bg-gradient-to-r from-red-600 to-black text-white rounded-xl p-4 mb-6 text-center shadow-lg">
        <h2 class="text-xl font-bold">Navigation Menu</h2>
        <p class="text-xs mt-1 opacity-90">Dashboard de Suivi</p>
      </div>

      <!-- Menu Items -->
      <div class="space-y-3">${itemsHTML}</div>

      <!-- Logout -->
      <div class="mt-6">
        <button onclick="handleLogout()"
          class="w-full block border-2 rounded-xl p-4 text-center font-bold text-base
                 bg-white text-red-600 border-red-300 hover:bg-red-600 hover:text-white
                 transition-all duration-200">
          Logout
        </button>
      </div>

      <!-- Footer -->
      <div class="mt-6 pt-4 border-t-2 border-gray-300 text-center">
        <p class="text-xs text-gray-600 font-semibold">YAZAKI Manufacturing Dashboard</p>
        ${fullName ? `<p class="text-xs text-gray-500 mt-1">${fullName}</p>` : ''}
      </div>
    </div>
  `;

  document.body.insertAdjacentHTML('beforeend', html);

  const trigger = document.getElementById('sidebar-trigger');
  const sidebar = document.getElementById('sidebar');

  trigger.addEventListener('mouseenter', () => {
    sidebar.classList.remove('translate-x-full');
    sidebar.classList.add('translate-x-0');
  });

  sidebar.addEventListener('mouseleave', () => {
    sidebar.classList.remove('translate-x-0');
    sidebar.classList.add('translate-x-full');
  });
}

async function handleLogout() {
  await fetch('/api/auth/logout', { method: 'POST' });
  sessionStorage.clear();
  localStorage.removeItem('role');
  localStorage.removeItem('full_name');
  window.location.href = '/';
}

async function checkAuth() {
  const res = await fetch('/api/auth/me');
  if (!res.ok) {
    window.location.href = '/';
    return null;
  }
  const data = await res.json();
  sessionStorage.setItem('role', data.role);
  sessionStorage.setItem('full_name', data.full_name);
  return data;
}