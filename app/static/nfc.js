window.startNFCReader = async function() {
  const input = document.getElementById("nfcInput");
  if ('NDEFReader' in window) {
    try {
      const reader = new NDEFReader();
      await reader.scan();
      reader.onreading = event => {
        input.value = event.serialNumber || "Keine UID gefunden";
      };
    } catch (error) {
      input.value = "Scanfehler: " + error.message;
    }
  } else {
    input.value = "WebNFC nicht unterstützt!";
  }
};

async function ladeGuthaben(nfc_uid) {
  const res = await fetch(`/api/transactions/balance/${nfc_uid}`);
  const data = await res.json();
  const guthabenEl = document.getElementById('guthabenAnzeige');
  if (guthabenEl) {
    if (data.success) {
      guthabenEl.textContent = Number(data.balance).toFixed(2).replace('.', ',') + "€"; // Formatiert in xx,xx€
    } else {
      // wenn der NFC Code nicht gefunden wurde, soll ein neuer Kunde angelegt werden
      guthabenEl.textContent = "Neuer Kunde";  
      document.getElementById('nfcInput').dataset.newCustomer = "true";
      log(`NFC UID ${nfc_uid} nicht gefunden.`);
    }
  }
}

// --- ENTER-Event für NFC Code Feld ---
document.getElementById('nfcInput').addEventListener('keydown', function(e) {
  if (e.key === 'Enter') {
    if (this.value.trim() === '') {
      alert("Bitte NFC-Code scannen oder eingeben.");
      return;
    }
    ladeGuthaben(this.value);
  }
});