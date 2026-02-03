DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agentic Honey-Pot | Live Threat Map</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        cyber: '#0f172a',
                        neon: '#0ea5e9',
                        alert: '#ef4444'
                    }
                }
            }
        }
    </script>
    <style>
        body { background-color: #0f172a; color: white; font-family: 'Inter', sans-serif; }
        .glass { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1); }
        .pulse-dot {
            height: 10px; width: 10px; background-color: #22c55e; border-radius: 50%;
            display: inline-block; box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7);
            animation: pulse-green 2s infinite;
        }
        @keyframes pulse-green {
            0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); }
            70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(34, 197, 94, 0); }
            100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
        }
    </style>
</head>
<body class="p-8">
    <div class="max-w-6xl mx-auto">
        <header class="flex justify-between items-center mb-10 border-b border-gray-700 pb-5">
            <div>
                <h1 class="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-neon to-purple-400">Agentic Honey-Pot</h1>
                <p class="text-gray-400 text-sm mt-1">Autonomous Scam Detection & Intelligence Extraction</p>
            </div>
            <div class="flex items-center gap-2 px-4 py-2 rounded-full glass">
                <span class="pulse-dot"></span>
                <span class="text-xs font-mono text-green-400">SYSTEM ACTIVE</span>
            </div>
        </header>

        <!-- Stats Grid -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
            <div class="glass p-6 rounded-xl border-l-4 border-neon">
                <h3 class="text-gray-400 text-sm uppercase tracking-wider">Active Sessions</h3>
                <p class="text-4xl font-bold mt-2" id="activeSessions">0</p>
            </div>
            <div class="glass p-6 rounded-xl border-l-4 border-alert">
                <h3 class="text-gray-400 text-sm uppercase tracking-wider">Scams Intercepted</h3>
                <p class="text-4xl font-bold mt-2" id="scamsDetected">0</p>
            </div>
            <div class="glass p-6 rounded-xl border-l-4 border-purple-500">
                <h3 class="text-gray-400 text-sm uppercase tracking-wider">Intel Points Extracted</h3>
                <p class="text-4xl font-bold mt-2" id="intelCount">0</p>
            </div>
        </div>

        <!-- Live Feed -->
        <div class="glass rounded-xl p-6 min-h-[400px]">
            <h2 class="text-xl font-semibold mb-6 flex items-center gap-2">
                <svg class="w-5 h-5 text-neon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
                Live Intelligence Feed
            </h2>
            <div class="overflow-x-auto">
                <table class="w-full text-left">
                    <thead class="text-xs text-gray-400 uppercase border-b border-gray-700">
                        <tr>
                            <th class="px-4 py-3">Timestamp</th>
                            <th class="px-4 py-3">Last Message</th>
                            <th class="px-4 py-3">Extracted Intel</th>
                            <th class="px-4 py-3">Status</th>
                        </tr>
                    </thead>
                    <tbody id="intelTable" class="text-sm">
                        <!-- Rows injected via JS -->
                        <tr>
                            <td colspan="4" class="px-4 py-8 text-center text-gray-500 italic">Waiting for incoming threats...</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        async function fetchStats() {
            try {
                const res = await fetch('/api/stats');
                const data = await res.json();
                
                // Update counters
                document.getElementById('activeSessions').innerText = data.active_sessions;
                document.getElementById('scamsDetected').innerText = data.scams_detected;
                document.getElementById('intelCount').innerText = data.intel_items;

                // Update Table
                const tbody = document.getElementById('intelTable');
                if (data.recent_intel && data.recent_intel.length > 0) {
                    tbody.innerHTML = data.recent_intel.reverse().map(item => `
                        <tr class="border-b border-gray-800 hover:bg-white/5 transition">
                            <td class="px-4 py-3 text-gray-500 text-xs">${new Date().toLocaleTimeString()}</td>
                            <td class="px-4 py-3 max-w-xs truncate text-gray-300" title="${item.last_message}">${item.last_message}</td>
                            <td class="px-4 py-3">
                                ${item.phones.length ? `<span class="bg-blue-900/50 text-blue-300 border border-blue-700 px-2 py-1 rounded text-[10px] mr-1">📞 ${item.phones[0]}</span>` : ''}
                                ${item.upis.length ? `<span class="bg-green-900/50 text-green-300 border border-green-700 px-2 py-1 rounded text-[10px] mr-1">💸 UPI</span>` : ''}
                                ${item.links.length ? `<span class="bg-red-900/50 text-red-300 border border-red-700 px-2 py-1 rounded text-[10px]">🔗 LINK</span>` : ''}
                                ${!item.phones.length && !item.upis.length && !item.links.length ? '<span class="text-gray-600 text-[10px]">Keywords Only</span>' : ''}
                            </td>
                            <td class="px-4 py-3"><span class="text-green-400 font-mono text-[10px] px-2 py-1 bg-green-900/20 rounded-full border border-green-800/30">LOCKED ON</span></td>
                        </tr>
                    `).join('');
                }
            } catch (e) {
                console.error("Error fetching stats", e);
            }
        }

        // Poll every 3 seconds
        setInterval(fetchStats, 3000);
        fetchStats();
    </script>
</body>
</html>
"""
