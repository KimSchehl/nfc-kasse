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
    // Hole Session-User-Daten (enthält jetzt auch categories und groups)
    const sessionRes = await fetch('/api/auth/session_user');
    const sessionData = await sessionRes.json();
    const ul = document.querySelector('.sidebar-list');
    ul.innerHTML = '';

    // Kategorien aus session_user (Zugriffsrechte)
    if (Array.isArray(sessionData.categories)) {
      sessionData.categories.forEach(catName => {
        const li = document.createElement('li');
        li.className = 'sidebar-category';
        li.textContent = catName;
        li.onclick = function() {
          log(`switched category: ${catName}`);
          window.zeigeProdukteFuerKategorie && window.zeigeProdukteFuerKategorie(null, catName);
          document.getElementById('sidebar').classList.remove('open');
          document.getElementById('sidebarOverlay').style.display = 'none';
        };
        ul.appendChild(li);
      });
    }

    // Finanzbuchhaltung-Button für alle User mit entsprechender Gruppe
    if (Array.isArray(sessionData.groups) && sessionData.groups.includes("Finanzbuchhaltung")) {
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