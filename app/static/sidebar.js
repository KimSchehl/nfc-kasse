document.getElementById('burgerBtn').onclick = function() {
  document.getElementById('sidebar').classList.add('open');
  document.getElementById('sidebarOverlay').style.display = 'block';
};
document.getElementById('sidebarOverlay').onclick = function() {
  document.getElementById('sidebar').classList.remove('open');
  document.getElementById('sidebarOverlay').style.display = 'none';
};
document.querySelector('.sidebar-category').onclick = function() {
  document.getElementById('sidebar').classList.remove('open');
  document.getElementById('sidebarOverlay').style.display = 'none';
  // Hier kannst du weitere Aktionen ausführen, z.B. das Grid anzeigen
};

async function ladeKategorien() {
  try {
    const res = await fetch('/api/categories/', { credentials: 'include' });
    const kategorien = await res.json();

    const ul = document.querySelector('.sidebar-list');
    ul.innerHTML = '';

    kategorien.forEach(cat => {
      const li = document.createElement('li');
      li.className = 'sidebar-category';
      li.textContent = cat.display_name;
      li.dataset.catId = cat.id;
      li.onclick = function() {
        const catId = this.dataset.catId;
        const catName = this.textContent;  
        log(`switched category: ${catId} (${catName})`);
        window.zeigeProdukteFuerKategorie(catId, catName);
        document.getElementById('sidebar').classList.remove('open');
        document.getElementById('sidebarOverlay').style.display = 'none';
      };
      ul.appendChild(li);
    });

    // Finanzbuchhaltung-Button nur für berechtigte User
    const sessionRes = await fetch('/api/auth/session_user');
    const sessionData = await sessionRes.json();
    if (sessionData.group === "Finanzbuchhaltung") {
      const financesLi = document.createElement('li');
      financesLi.className = 'sidebar-category';
      financesLi.textContent = 'Finanzen';
      financesLi.onclick = function() {
        window.location.href = '/finances.html';
      };
      document.querySelector('.sidebar-list').appendChild(financesLi);
    }
  } catch (err) {
    console.error('Fehler beim Laden der Kategorien:', err);
  }
}

document.addEventListener('DOMContentLoaded', ladeKategorien);

document.getElementById('logoutBtn').onclick = function() {
  fetch('/api/auth/logout', {method: 'POST'})
    .then(() => window.location.href = "/login.html");
};