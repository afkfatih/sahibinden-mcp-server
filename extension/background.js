// Background service worker - Bridge server ile WebSocket iletisimi

const WS_URL = 'ws://localhost:8765';
let ws = null;
let reconnectTimeout = null;

// Alarm ile service worker'i canli tut
chrome.alarms.create('keepAlive', { periodInMinutes: 0.5 });

chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === 'keepAlive') {
    // Baglanti kontrolu yap
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      console.log('[Sahibinden Ext] Alarm: Baglanti yok, yeniden baglaniliyor...');
      connect();
    } else {
      // Ping gonder
      try {
        ws.send(JSON.stringify({ type: 'ping' }));
      } catch (e) {
        console.log('[Sahibinden Ext] Ping hatasi, yeniden baglaniliyor...');
        connect();
      }
    }
  }
});

// WebSocket baglantisi kur
function connect() {
  // Onceki baglanti varsa kapat
  if (ws) {
    try {
      ws.close();
    } catch (e) {}
    ws = null;
  }
  
  // Onceki timeout varsa iptal et
  if (reconnectTimeout) {
    clearTimeout(reconnectTimeout);
    reconnectTimeout = null;
  }
  
  console.log('[Sahibinden Ext] WebSocket baglantisi kuruluyor...');
  
  try {
    ws = new WebSocket(WS_URL);
  } catch (e) {
    console.error('[Sahibinden Ext] WebSocket olusturulamadi:', e);
    scheduleReconnect();
    return;
  }
  
  ws.onopen = () => {
    console.log('[Sahibinden Ext] WebSocket baglandi!');
    
    // Kendimizi kaydet
    ws.send(JSON.stringify({
      type: 'register',
      client: 'chrome-extension'
    }));
  };
  
  ws.onmessage = async (event) => {
    try {
      const data = JSON.parse(event.data);
      console.log('[Sahibinden Ext] Mesaj alindi:', data.type);
      
      if (data.type === 'search') {
        await handleSearch(data);
      } else if (data.type === 'get_listing') {
        await handleGetListing(data);
      }
    } catch (e) {
      console.error('[Sahibinden Ext] Mesaj hatasi:', e);
    }
  };
  
  ws.onclose = () => {
    console.log('[Sahibinden Ext] WebSocket baglantisi kapandi');
    ws = null;
    scheduleReconnect();
  };
  
  ws.onerror = (error) => {
    console.error('[Sahibinden Ext] WebSocket hatasi:', error);
  };
}

function scheduleReconnect() {
  if (!reconnectTimeout) {
    reconnectTimeout = setTimeout(() => {
      reconnectTimeout = null;
      console.log('[Sahibinden Ext] Yeniden baglaniliyor...');
      connect();
    }, 3000);
  }
}

// Sehir kodlari
const CITY_CODES = {
  'istanbul': 34, 'ankara': 6, 'izmir': 35, 'bursa': 16, 'antalya': 7,
  'adana': 1, 'konya': 42, 'gaziantep': 27, 'mersin': 33, 'kayseri': 38,
  'eskisehir': 26, 'diyarbakir': 21, 'samsun': 55, 'denizli': 20, 'sanliurfa': 63,
};

// Istanbul ilce kodlari
const ISTANBUL_TOWNS = {
  'adalar': 831, 'arnavutkoy': 890, 'atasehir': 888, 'avcilar': 837,
  'bagcilar': 838, 'bahcelievler': 839, 'bakirkoy': 840, 'basaksehir': 886,
  'bayrampasa': 841, 'besiktas': 843, 'beykoz': 844, 'beylikduzu': 887,
  'beyoglu': 845, 'buyukcekmece': 846, 'catalca': 848, 'cekmekoy': 889,
  'esenler': 849, 'esenyurt': 885, 'eyup': 850, 'fatih': 851,
  'gaziosmanpasa': 852, 'gungoren': 853, 'kadikoy': 854, 'kagithane': 855,
  'kartal': 856, 'kucukcekmece': 857, 'maltepe': 858, 'pendik': 859,
  'sancaktepe': 891, 'sarıyer': 860, 'sile': 861, 'silivri': 862,
  'sisli': 863, 'sultanbeyli': 864, 'sultangazi': 892, 'tuzla': 866,
  'umraniye': 867, 'uskudar': 868, 'zeytinburnu': 869,
};

// Arama islemi
async function handleSearch(data) {
  console.log('[Sahibinden Ext] Arama yapiliyor:', data.query);
  
  // URL olustur
  let url = 'https://www.sahibinden.com';
  
  if (data.category) {
    // Kategori slug'ini URL'e ekle
    const categoryMap = {
      'drone': 'hobi-oyuncak-rc-araclar',
      'telefon': 'cep-telefonu',
      'bilgisayar': 'bilgisayar',
      'araba': 'otomobil',
    };
    url += '/' + (categoryMap[data.category] || data.category);
  } else {
    url += '/arama';
  }
  
  const params = new URLSearchParams();
  if (data.query) params.append('query_text', data.query);
  params.append('pagingSize', '50');
  
  // Fiyat filtreleri
  if (data.minPrice) params.append('price_min', data.minPrice);
  if (data.maxPrice) params.append('price_max', data.maxPrice);
  
  // Sehir filtresi
  if (data.city) {
    const cityCode = CITY_CODES[data.city.toLowerCase()] || data.city;
    params.append('address_city', cityCode);
  }
  
  // Ilce filtresi (Istanbul)
  if (data.town) {
    const townCode = ISTANBUL_TOWNS[data.town.toLowerCase()] || data.town;
    params.append('address_town', townCode);
  }
  
  // Siralama
  if (data.sorting) {
    params.append('sorting', data.sorting);
  }
  
  // Tarih filtresi
  if (data.date) {
    params.append('date', data.date);
  }
  
  url += '?' + params.toString();
  
  try {
    // Yeni tab ac
    const tab = await chrome.tabs.create({ url, active: false });
    
    // Sayfa yuklenene kadar bekle
    await new Promise(resolve => {
      const listener = (tabId, info) => {
        if (tabId === tab.id && info.status === 'complete') {
          chrome.tabs.onUpdated.removeListener(listener);
          resolve();
        }
      };
      chrome.tabs.onUpdated.addListener(listener);
    });
    
    // Ekstra bekle (Cloudflare icin)
    await new Promise(r => setTimeout(r, 3000));
    
    // Content script'e mesaj gonder
    const result = await chrome.tabs.sendMessage(tab.id, { action: 'extractSearch' });
    
    // Tab'i kapat
    await chrome.tabs.remove(tab.id);
    
    // Sonucu bridge'e gonder
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({
        type: 'result',
        id: data.id,
        data: result
      }));
    }
  } catch (error) {
    console.error('[Sahibinden Ext] Arama hatasi:', error);
    
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({
        type: 'result',
        id: data.id,
        data: { error: error.message }
      }));
    }
  }
}

// Ilan detayi cek
async function handleGetListing(data) {
  console.log('[Sahibinden Ext] Ilan detayi cekiliyor:', data.listing_id);
  
  const url = `https://www.sahibinden.com/ilan/${data.listing_id}/detay`;
  
  try {
    // Yeni tab ac
    const tab = await chrome.tabs.create({ url, active: false });
    
    // Sayfa yuklenene kadar bekle
    await new Promise(resolve => {
      const listener = (tabId, info) => {
        if (tabId === tab.id && info.status === 'complete') {
          chrome.tabs.onUpdated.removeListener(listener);
          resolve();
        }
      };
      chrome.tabs.onUpdated.addListener(listener);
    });
    
    // Ekstra bekle
    await new Promise(r => setTimeout(r, 3000));
    
    // Content script'e mesaj gonder
    const result = await chrome.tabs.sendMessage(tab.id, { action: 'extractDetail' });
    
    // Tab'i kapat
    await chrome.tabs.remove(tab.id);
    
    // Sonucu bridge'e gonder
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({
        type: 'result',
        id: data.id,
        data: result
      }));
    }
  } catch (error) {
    console.error('[Sahibinden Ext] Detay hatasi:', error);
    
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({
        type: 'result',
        id: data.id,
        data: { error: error.message }
      }));
    }
  }
}

// Extension yuklendiginde baglan
connect();

// Popup'tan gelen mesajlari dinle
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'reconnect') {
    console.log('[Sahibinden Ext] Manuel yeniden baglanti istegi');
    connect();
    sendResponse({ status: 'reconnecting' });
  } else if (message.action === 'getStatus') {
    sendResponse({ 
      connected: ws && ws.readyState === WebSocket.OPEN 
    });
  }
  return true;
});

console.log('[Sahibinden Ext] Background service worker basladi');
