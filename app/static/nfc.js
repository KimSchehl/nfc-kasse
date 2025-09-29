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
      guthabenEl.textContent = data.balance + "€";
      log(`Guthaben für NFC UID ${nfc_uid}: ${data.balance}€`);
    } else {
      guthabenEl.textContent = "error";
    }
  }
}

// --- ENTER-Event für NFC Code Feld ---
document.getElementById('nfcInput').addEventListener('keydown', function(e) {
  if (e.key === 'Enter') {
    ladeGuthaben(this.value);
  }
});