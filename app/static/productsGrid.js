document.getElementById('essenBtn').onclick = function() {
  document.getElementById('sidebar').classList.remove('open');
  document.getElementById('sidebarOverlay').style.display = 'none';
};

let cart = []; // Warenkorb

function zeigeWarenkorb() {
  const cartBox = document.getElementById('cartBox');
  cartBox.innerHTML = '';
  if (cart.length === 0) {
    cartBox.innerHTML = '<span class="cart-empty">Warenkorb ist leer.</span>';
  } else {
    cart.forEach((item, idx) => {
      const div = document.createElement('div');
      div.className = 'cart-item';
      div.textContent = `${item.name} – ${item.info} – ${item.price}`;
      div.onclick = function() {
        log(`${item.name} removed from cart.`);
        cart.splice(idx, 1); // Item entfernen
        zeigeWarenkorb();
      };
      cartBox.appendChild(div);
    });
  }

  // Summe immer aktualisieren
  const sumRow = document.querySelector('.cart-sum-row');
  if (sumRow) {
    const summe = cart.reduce((acc, item) => acc + parseFloat(item.price), 0);
    sumRow.textContent = `Summe: ${summe.toLocaleString('de-DE', {minimumFractionDigits: 2})} €`;
  }
}

async function getGridColumns() {
  try {
    const userId = window.userId || 1;
    const res = await fetch(`/api/settings/grid_columns/${userId}`);
    const data = await res.json();
    return parseInt(data.columns) || 2;
  } catch {
    return 2;
  }
}

window.zeigeProdukteFuerKategorie = async function(catId, catName) {
  const main = document.getElementById('mainContent');
  main.innerHTML = '';

  // Spaltenanzahl holen
  const gridCols = await getGridColumns();

  // Abstand zu den Buttons
  const spacer = document.createElement('div');
  spacer.style.height = '5px';
  main.appendChild(spacer);

  // Produkte laden
  let products = [];
  try {
    const res = await fetch(`/api/products/?category_id=${catId}`);
    products = await res.json();
  } catch (err) {
    products = [];
  }

  // Scrollbox für Produkt-Grid
  const scrollBox = document.createElement('div');
  scrollBox.style.height = '50vh';
  scrollBox.style.overflowY = 'auto';
  scrollBox.style.width = '100%';

  // Produkt-Grid
  const grid = document.createElement('div');
  grid.className = 'product-grid';
  grid.style.setProperty('--grid-cols', gridCols);
  products.forEach(product => {
    const btn = document.createElement('button');
    btn.className = 'product-btn';
    btn.innerHTML = `
      <div class="line1">${product.name}</div>
      <div class="line2">Zusatz Info</div>
      <div class="line3">${product.price}€</div>
    `;
    // Hintergrundfarbe je nach Preis
    if (product.price < 0) {
      btn.style.background = '#ffebee';      // sehr helles Rot
      btn.style.color = '#c62828';           // kräftiges Rot für Text
    } else {
      btn.style.background = '#e3f2fd';      // wie bisher, helles Blau
      btn.style.color = '#1976d2';           // wie bisher, kräftiges Blau
    }
    btn.onclick = function() {
      cart.push({
        id: product.id,
        name: product.name,
        info: "Zusatz Info",
        price: product.price + "€"
      });
      log(`${product.name} added to cart.`);
      zeigeWarenkorb();
    };
    grid.appendChild(btn);
  });

  // --- BonKasse: "Guthaben Auszahlen"-Button ---
  if (catName === "BonKasse") {
    const payoutBtn = document.createElement('button');
    payoutBtn.className = 'product-btn';
    payoutBtn.style.background = '#fff3e0';
    payoutBtn.style.color = '#ef6c00';
    payoutBtn.innerHTML = `
      <div class="line1">Guthaben Auszahlen</div>
      <div class="line2">Setzt Guthaben auf 0€</div>
      <div class="line3"></div>
    `;
    payoutBtn.onclick = async function() {
      const nfc_code = document.getElementById('nfcInput')?.value || null;
      if (!nfc_code) {
        alert("Bitte NFC-Code scannen oder eingeben.");
        return;
      }
      const res = await fetch('/api/transactions/payout', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ nfc_uid: nfc_code })
      });
      const data = await res.json();
      if (data.success) {
        log(`Guthaben für NFC UID ${nfc_code} ausgezahlt und auf 0 gesetzt.`);
        ladeGuthaben(nfc_code);
        alert("Guthaben wurde ausgezahlt!");
      } else {
        log(data.message || "Auszahlung fehlgeschlagen!");
        alert("Auszahlung fehlgeschlagen: " + (data.message || "Unbekannter Fehler"));
      }
    };
    grid.appendChild(payoutBtn);
  }

  scrollBox.appendChild(grid);
  main.appendChild(scrollBox);

  // Abstand zum Warenkorb
  const spacer2 = document.createElement('div');
  spacer2.style.height = '18px';
  main.appendChild(spacer2);

  // Scrollbox für Warenkorb
  const cartBox = document.createElement('div');
  cartBox.id = 'cartBox';
  cartBox.style.height = '18vh';
  cartBox.style.overflowY = 'auto';
  cartBox.style.width = '100%';
  cartBox.style.maxWidth = '380px'; 
  cartBox.style.background = '#fff';
  cartBox.style.borderRadius = '10px';
  cartBox.style.boxShadow = '0 2px 8px rgba(0,0,0,0.07)';
  cartBox.style.padding = '12px';
  cartBox.style.margin = '0 auto 8px auto';
  main.appendChild(cartBox);

  // Summe unterhalb des Warenkorbs anzeigen
  const summe = cart.reduce((acc, item) => acc + parseFloat(item.price), 0);
  const sumRow = document.createElement('div');
  sumRow.className = 'cart-sum-row';
  sumRow.style.textAlign = 'right';
  sumRow.style.maxWidth = '380px';
  sumRow.style.margin = '0 auto 12px auto';
  sumRow.style.fontWeight = 'bold';
  sumRow.style.fontSize = '1.15em';
  sumRow.style.color = '#1976d2';
  sumRow.textContent = `Summe: ${summe.toLocaleString('de-DE', {minimumFractionDigits: 2})} €`;
  main.appendChild(sumRow);

  // Buttons am Seitenende
  const btnRow = document.createElement('div');
  btnRow.className = 'cart-btn-row';

  const confirmBtn = document.createElement('button');
  confirmBtn.textContent = 'Bestätigen';
  confirmBtn.className = 'confirm-btn';

  const cancelBtn = document.createElement('button');
  cancelBtn.textContent = 'Abbrechen';
  cancelBtn.className = 'cancel-btn';

  // NFC Scan Button unten links
  const nfcScanBtn = document.createElement('button');
  nfcScanBtn.id = 'nfcScanBtn';
  nfcScanBtn.textContent = 'NFC Scan';
  nfcScanBtn.className = 'nfc-btn';

  btnRow.appendChild(nfcScanBtn);
  btnRow.appendChild(cancelBtn);
  btnRow.appendChild(confirmBtn);
  main.appendChild(btnRow);

  nfcScanBtn.onclick = function() {
    window.startNFCReader();
  };

  confirmBtn.onclick = function() {
    nfc_code = document.getElementById('nfcInput')?.value || null;
    if (nfc_code === null) {
      alert("Bitte NFC-Code scannen oder eingeben.");
      return;
    }
    bucheWarenkorb(nfc_code, cart);
  };

  cancelBtn.onclick = function() {
    cart = []; // Warenkorb leeren
    log(`cleared cart.`);
    zeigeWarenkorb();
  };

  // Warenkorb anzeigen
  zeigeWarenkorb();
}

async function bucheWarenkorb(nfc_uid, cart) {
  if (document.getElementById('nfcInput').dataset.newCustomer === "true") {
    createNewCustomer(nfc_uid);
    document.getElementById('nfcInput').dataset.newCustomer = "false";
  }
  const productIds = cart.map(item => item.id);
  const res = await fetch('/api/transactions/book', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ nfc_uid, products: productIds })
  });
  log(`Booking transaction for NFC UID: ${nfc_uid} with products: ${productIds}`);
  const data = await res.json();
  if (data.success) {
    log("Buchung erfolgreich! Neues Guthaben: " + data.new_balance + "€");
    cart.length = 0;
    document.getElementById('nfcInput').value = '';
    ladeGuthaben(nfc_uid);
    zeigeWarenkorb(); 
  } else {
    log(data.message || "Buchung fehlgeschlagen!");
    alert("Buchung fehlgeschlagen: " + (data.message || "Unbekannter Fehler"));
  }
}

async function createNewCustomer(nfc_uid) {
  const user = await fetch(`/api/transactions/create_customer/${nfc_uid}`, { method: "POST" });
  const data = await user.json();
  if (!data.success) {
    log(data.message || "Neuer Kunde konnte nicht angelegt werden!");
    alert("Neuer Kunde konnte nicht angelegt werden: " + (data.message || "Unbekannter Fehler"));
    return;
  }
  log(`Neuer Kunde angelegt: ${data.name} mit NFC UID ${data.nfc_uid}`);
}
