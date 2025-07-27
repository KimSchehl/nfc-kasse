window.log = function(message) {
  const user = window.currentUser
    ? `${window.currentUser.id} ${window.currentUser.username}`
    : "Unknown";
  const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19);
  fetch('/api/log/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message: `${message}`,
      user: user,
      timestamp: timestamp
    })
  });
};