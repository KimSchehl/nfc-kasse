// --- Grid Columns ---
async function loadGridColumns() {
  try {
    const res = await fetch('/api/settings/grid_columns');
    const data = await res.json();
    document.getElementById('columnInput').value = data.columns || 2;
  } catch {
    document.getElementById('columnInput').value = 2;
  }
}

async function saveGridColumns() {
  const value = document.getElementById('columnInput').value;
  const payload = { type: 'spalten', value: value };
  const res = await fetch('/api/settings/grid_columns/1', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  const data = await res.json();
  const info = document.getElementById('saveInfo');
  info.textContent = data.success ? "Spalten erfolgreich gespeichert!" : (data.message || "Fehler beim Speichern!");
  info.style.color = data.success ? "green" : "red";
}

// --- User Table ---
async function ladeUserTabelle() {
  const res = await fetch('/api/user/all/', { credentials: 'include' });
  const users = await res.json();
  const catRes = await fetch('/api/categories/', { credentials: 'include' });
  const categories = await catRes.json();

  let html = '<table class="user-table">';
  html += '<tr><th>Aktion</th><th>ID</th><th>Username</th><th>Passwort</th>';
  categories.forEach(cat => html += `<th>${cat.display_name}</th>`);
  html += '</tr>';

  users.forEach(user => {
    html += `<tr>
      <td>
        <button class="editUserBtn" data-userid="${user.id}" data-username="${user.username}" data-password="${user.password}" style="padding:4px 10px; border-radius:6px; background:#e3f2fd; color:#1976d2; border:none; cursor:pointer;">Bearbeiten</button>
      </td>
      <td>${user.id}</td>
      <td>${user.username}</td>
      <td>${user.password}</td>`;
    categories.forEach(cat => {
      html += `<td>
        <input type="checkbox"
          ${user.categories.includes(cat.display_name) ? 'checked' : ''}
          data-userid="${user.id}"
          data-category="${cat.display_name}">
      </td>`;
    });
    html += '</tr>';
  });

  html += '</table>';
  document.getElementById('userTableContainer').innerHTML = html;
}

// --- Logging ---
async function logFrontend(message) {
  await fetch('/api/log/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message })
  });
}

// --- Event Handler ---
document.addEventListener('DOMContentLoaded', () => {
  loadGridColumns();
  document.getElementById('saveBtn').onclick = saveGridColumns;

  // Lade die Benutzerverwaltung nur für "admin*" User
  fetch('/api/auth/session_user')
    .then(res => res.json())
    .then(data => {
      if (data.username && data.username.startsWith('admin')) {
        ladeUserTabelle();
        document.getElementById('userTableContainer').style.display = 'block';
        document.getElementById('createUserBtn').style.display = 'inline-block';
      } else {
        document.getElementById('userTableContainer').style.display = 'none';
        document.getElementById('createUserBtn').style.display = 'none';
        document.getElementById('userManagementHeader').style.display = 'none';
      }
    });
});

document.getElementById('backBtn').onclick = () => window.location.href = '/index.html';

document.getElementById('userTableContainer').addEventListener('change', async function(e) {
  if (e.target && e.target.type === 'checkbox') {
    const userId = e.target.getAttribute('data-userid');
    const category = e.target.getAttribute('data-category');
    const allowed = e.target.checked;
    const res = await fetch('/api/user/update_permission/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, category: category, allowed: allowed })
    });
    const result = await res.json();
    logFrontend(`User ${userId} Kategorie ${category} geändert: ${allowed} | Serverantwort: ${JSON.stringify(result)}`);
  }
});

document.getElementById('createUserBtn').onclick = function() {
  document.getElementById('editUserPopup').style.display = 'block';
  document.getElementById('editUserOverlay').style.display = 'block';
  document.getElementById('editUsername').value = '';
  document.getElementById('editPassword').value = '';
  document.getElementById('editUserPopup').removeAttribute('data-userid');
  document.getElementById('deleteUserBtn').style.display = 'none';
};

document.addEventListener('click', function(e) {
  if (e.target.classList.contains('editUserBtn')) {
    document.getElementById('editUserPopup').style.display = 'block';
    document.getElementById('editUserOverlay').style.display = 'block';
    document.getElementById('editUsername').value = e.target.getAttribute('data-username');
    document.getElementById('editPassword').value = e.target.getAttribute('data-password');
    document.getElementById('editUserPopup').setAttribute('data-userid', e.target.getAttribute('data-userid'));
    document.getElementById('deleteUserBtn').style.display = 'inline-block';
  }
  if (e.target.id === 'cancelEditBtn' || e.target.id === 'editUserOverlay') {
    document.getElementById('editUserPopup').style.display = 'none';
    document.getElementById('editUserOverlay').style.display = 'none';
  }
});

document.getElementById('saveEditBtn').onclick = async function() {
  const userId = document.getElementById('editUserPopup').getAttribute('data-userid');
  const username = document.getElementById('editUsername').value;
  const password = document.getElementById('editPassword').value;
  if (userId) {
    await fetch('/api/user/update/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, username: username, password: password })
    });
  } else {
    await fetch('/api/user/add/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: username, password: password })
    });
  }
  document.getElementById('editUserPopup').style.display = 'none';
  document.getElementById('editUserOverlay').style.display = 'none';
  ladeUserTabelle();
};

document.getElementById('deleteUserBtn').onclick = async function() {
  const userId = document.getElementById('editUserPopup').getAttribute('data-userid');
  if (userId && confirm("Wirklich löschen?")) {
    await fetch('/api/user/delete/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId })
    });
    document.getElementById('editUserPopup').style.display = 'none';
    document.getElementById('editUserOverlay').style.display = 'none';
    ladeUserTabelle();
  }
};
