const WebSocket = require('ws');
const http = require('http');
const url = require('url');

const WS_PORT = 8765;
const HTTP_PORT = 8766;

// WebSocket Server
const wss = new WebSocket.Server({ port: WS_PORT });
let chromeClient = null;
const pendingRequests = new Map();

console.log(`🚀 Bridge Server Başlatılıyor...`);
console.log(`📡 WebSocket: ws://localhost:${WS_PORT}`);
console.log(`🌐 HTTP API: http://localhost:${HTTP_PORT}`);

wss.on('connection', (ws) => {
    console.log('[WS] Yeni bağlantı');

    ws.on('message', (message) => {
        try {
            const data = JSON.parse(message);

            if (data.type === 'register' && data.client === 'chrome-extension') {
                console.log('[WS] Chrome Extension kaydedildi ✅');
                chromeClient = ws;
            } else if (data.type === 'result') {
                console.log(`[WS] Sonuç alındı (ID: ${data.id}) 📦`);
                const pending = pendingRequests.get(data.id);
                if (pending) {
                    pending.resolve(data.data);
                    pendingRequests.delete(data.id);
                }
            }
        } catch (e) {
            console.error('[WS] Mesaj hatası:', e);
        }
    });

    ws.on('close', () => {
        if (ws === chromeClient) {
            console.log('[WS] Chrome Extension bağlantısı koptu ❌');
            chromeClient = null;
        }
    });
});

// HTTP Server (MCP Server buradan istek atacak)
const server = http.createServer(async (req, res) => {
    const parsedUrl = url.parse(req.url, true);

    // CORS headers
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST');
    res.setHeader('Content-Type', 'application/json');

    if (req.method === 'POST') {
        let body = '';
        req.on('data', chunk => body += chunk);
        req.on('end', async () => {
            try {
                if (!chromeClient) {
                    res.statusCode = 503;
                    return res.end(JSON.stringify({ error: 'Chrome Extension bağlı değil' }));
                }

                const payload = JSON.parse(body);
                const requestId = Date.now().toString();

                console.log(`[HTTP] İstek alındı: ${parsedUrl.pathname} (ID: ${requestId})`);

                // Promise oluştur ve bekle
                const responsePromise = new Promise((resolve, reject) => {
                    const timeout = setTimeout(() => {
                        pendingRequests.delete(requestId);
                        reject(new Error('Timeout'));
                    }, 60000); // 60sn timeout

                    pendingRequests.set(requestId, { resolve, reject, timeout });
                });

                // Extension'a gönder
                if (parsedUrl.pathname === '/search') {
                    chromeClient.send(JSON.stringify({
                        type: 'search',
                        id: requestId,
                        query: payload.query,
                        category: payload.category,
                        city: payload.city,
                        town: payload.town,
                        minPrice: payload.minPrice,
                        maxPrice: payload.maxPrice,
                        sorting: payload.sorting,
                        date: payload.date,
                        limit: payload.limit
                    }));
                } else if (parsedUrl.pathname === '/listing') {
                    chromeClient.send(JSON.stringify({
                        type: 'get_listing',
                        id: requestId,
                        listing_id: payload.listing_id
                    }));
                } else {
                    res.statusCode = 404;
                    return res.end(JSON.stringify({ error: 'Endpoint not found' }));
                }

                // Sonucu bekle ve dön
                const result = await responsePromise;
                res.end(JSON.stringify(result));

            } catch (e) {
                console.error('[HTTP] Hata:', e);
                res.statusCode = 500;
                res.end(JSON.stringify({ error: e.message }));
            }
        });
    } else {
        res.end(JSON.stringify({ status: 'running', extension_connected: !!chromeClient }));
    }
});

server.listen(HTTP_PORT, () => {
    console.log(`[HTTP] Server dinleniyor: ${HTTP_PORT}`);
});
