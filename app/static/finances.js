document.getElementById('backBtn').onclick = () => window.location.href = '/index.html';

async function fetchTransactions() {
  const res = await fetch('/api/finances/transactions');
  return await res.json();
}

function createTable(transactions, columns) {
  const container = document.getElementById('financesTableContainer');
  container.innerHTML = '';

  // Filter- und Sortierstatus
  let sortCol = null, sortAsc = true;
  let filters = {};

  // Tabelle erstellen
  const table = document.createElement('table');
  table.style.width = '100%';
  table.style.borderCollapse = 'collapse';

  // Kopfzeile mit Sortierfunktion
  const thead = document.createElement('thead');
  const headerRow = document.createElement('tr');
  columns.forEach(col => {
    const th = document.createElement('th');
    th.textContent = col.label;
    th.style.cursor = 'pointer';
    th.onclick = () => {
      sortAsc = sortCol === col.key ? !sortAsc : true;
      sortCol = col.key;
      renderRows();
    };
    headerRow.appendChild(th);
  });
  thead.appendChild(headerRow);

  // Filterzeile
  const filterRow = document.createElement('tr');
  columns.forEach(col => {
    const td = document.createElement('td');
    const input = document.createElement('input');
    input.type = 'text';
    input.placeholder = 'Filtern...';
    input.style.width = '95%';
    input.oninput = () => {
      filters[col.key] = input.value.toLowerCase();
      renderRows();
    };
    td.appendChild(input);
    filterRow.appendChild(td);
  });
  thead.appendChild(filterRow);
  table.appendChild(thead);

  // Tabellenkörper
  const tbody = document.createElement('tbody');
  table.appendChild(tbody);

  function renderRows() {
    tbody.innerHTML = '';
    let rows = [...transactions];

    // Filtern
    Object.keys(filters).forEach(key => {
      if (filters[key]) {
        rows = rows.filter(row => (row[key] + '').toLowerCase().includes(filters[key]));
      }
    });

    // Sortieren
    if (sortCol) {
      rows.sort((a, b) => {
        if (a[sortCol] < b[sortCol]) return sortAsc ? -1 : 1;
        if (a[sortCol] > b[sortCol]) return sortAsc ? 1 : -1;
        return 0;
      });
    }

    // Zeilen einfügen
    rows.forEach(row => {
      const tr = document.createElement('tr');
      columns.forEach(col => {
        const td = document.createElement('td');
        td.textContent = row[col.key];
        tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });
  }

  renderRows();
  container.appendChild(table);
}

(async function() {
  // Spalten-Definition
  const columns = [
    { key: 'id', label: 'ID' },
    { key: 'timestamp', label: 'Zeitpunkt' },
    { key: 'nfc_uid', label: 'NFC UID' },
    { key: 'product_name', label: 'Produkt' }
  ];

  // Hole Transaktionen
  const transactions = await fetchTransactions();
  if (!Array.isArray(transactions)) {
    alert(transactions.message || "Fehler beim Laden der Transaktionen!");
    return;
  }
  console.log(transactions);
  createTable(transactions, columns);
})();