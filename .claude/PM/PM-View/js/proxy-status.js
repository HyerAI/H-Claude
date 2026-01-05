// Proxy Status Checker for PM Wiki
(function() {
    const PROXIES = [
        { name: 'HC-Reas-A', port: 2410, purpose: 'Heavy reasoning (Claude)' },
        { name: 'HC-Reas-B', port: 2411, purpose: 'Challenger reasoning' },
        { name: 'HC-Work', port: 2412, purpose: 'Workers & scouts' },
        { name: 'HC-Work-R', port: 2413, purpose: 'Workers with thinking' },
        { name: 'HC-Orca', port: 2414, purpose: 'Light coordination' },
        { name: 'HC-Orca-R', port: 2415, purpose: 'Heavy coordination' },
        { name: 'CG-Image', port: 2407, purpose: 'Image generation' }
    ];

    async function checkProxy(proxy) {
        try {
            const controller = new AbortController();
            const timeout = setTimeout(() => controller.abort(), 3000);

            const response = await fetch(`http://localhost:${proxy.port}/health`, {
                signal: controller.signal
            });
            clearTimeout(timeout);

            if (response.ok) {
                const data = await response.json();
                return {
                    ...proxy,
                    status: 'online',
                    model: data.model || 'unknown'
                };
            }
            return { ...proxy, status: 'error', model: '-' };
        } catch (e) {
            return { ...proxy, status: 'offline', model: '-' };
        }
    }

    async function checkAllProxies() {
        const table = document.getElementById('proxy-status-table');
        if (!table) return;

        const tbody = table.querySelector('tbody');
        if (!tbody) return;

        // Show loading state
        tbody.innerHTML = PROXIES.map(p => `
            <tr>
                <td><span class="status-indicator status-checking"></span></td>
                <td><strong>${p.name}</strong></td>
                <td>${p.port}</td>
                <td>Checking...</td>
                <td>${p.purpose}</td>
            </tr>
        `).join('');

        // Check all proxies in parallel
        const results = await Promise.all(PROXIES.map(checkProxy));

        // Update table with results
        tbody.innerHTML = results.map(r => `
            <tr>
                <td><span class="status-indicator status-${r.status}" title="${r.status}"></span></td>
                <td><strong>${r.name}</strong></td>
                <td>${r.port}</td>
                <td><code>${r.model}</code></td>
                <td>${r.purpose}</td>
            </tr>
        `).join('');

        // Update summary
        const online = results.filter(r => r.status === 'online').length;
        const summary = document.getElementById('proxy-summary');
        if (summary) {
            summary.innerHTML = `<strong>${online}/${results.length}</strong> proxies online`;
            summary.className = online === results.length ? 'summary-ok' : (online > 0 ? 'summary-partial' : 'summary-fail');
        }

        // Update timestamp
        const timestamp = document.getElementById('proxy-timestamp');
        if (timestamp) {
            timestamp.textContent = new Date().toLocaleTimeString();
        }
    }

    // Run on page load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', checkAllProxies);
    } else {
        checkAllProxies();
    }

    // Expose for manual refresh
    window.refreshProxyStatus = checkAllProxies;
})();
