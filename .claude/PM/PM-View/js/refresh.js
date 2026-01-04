// Floating refresh button for PM Wiki
(function() {
  const btn = document.createElement('button');
  btn.innerHTML = '↻';
  btn.id = 'refresh-btn';
  btn.title = 'Hard refresh (bypass cache)';
  btn.onclick = function() {
    // Force hard reload with cache-busting timestamp
    const url = new URL(window.location.href);
    url.searchParams.set('_t', Date.now());
    window.location.href = url.toString();
  };
  document.body.appendChild(btn);
})();
