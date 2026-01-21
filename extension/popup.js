// Popup script

const statusEl = document.getElementById('status');
const resultEl = document.getElementById('result');

// Bridge baglantisini kontrol et
async function checkBridge() {
  try {
    const response = await fetch('http://localhost:8766', { 
      method: 'GET',
      mode: 'cors'
    });
    if (response.ok) {
      const data = await response.json();
      if (data.extension_connected) {
        statusEl.className = 'status connected';
        statusEl.textContent = 'Bridge bagli - Extension aktif';
        return true;
      } else {
        statusEl.className = 'status disconnected';
        statusEl.textContent = 'Bridge calisiyor - Extension baglanmadi\nAsagidaki "Baglantıyı Yenile" butonuna tikla';
        return false;
      }
    }
  } catch (e) {
    console.error('Bridge kontrol hatasi:', e);
  }
  statusEl.className = 'status disconnected';
  statusEl.textContent = 'Bridge bagli degil!\nnode bridge.js calistir';
  return false;
}

// Baglantıyı yenile butonu
document.getElementById('reconnect')?.addEventListener('click', async () => {
  resultEl.textContent = 'Baglanti yenileniyor...';
  
  // Background script'e mesaj gonder
  try {
    await chrome.runtime.sendMessage({ action: 'reconnect' });
    await new Promise(r => setTimeout(r, 2000));
    await checkBridge();
    resultEl.textContent = 'Baglanti durumu yukarida gosteriliyor.';
  } catch (e) {
    resultEl.textContent = 'Hata: ' + e.message;
  }
});

// Bu sayfayi analiz et
document.getElementById('testCurrent').addEventListener('click', async () => {
  resultEl.textContent = 'Sayfa analiz ediliyor...';
  
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    if (!tab.url.includes('sahibinden.com')) {
      resultEl.textContent = 'Once sahibinden.com\'a git!';
      return;
    }
    
    // Sayfa tipini belirle
    const typeResponse = await chrome.tabs.sendMessage(tab.id, { action: 'getPageType' });
    const pageType = typeResponse.type;
    
    let data;
    if (pageType === 'search') {
      data = await chrome.tabs.sendMessage(tab.id, { action: 'extractSearch' });
      resultEl.textContent = `ARAMA SAYFASI\n` +
        `Bulunan: ${data.listings?.length || 0} ilan\n` +
        `Toplam: ${data.total || 0}\n\n` +
        (data.listings?.slice(0, 3).map(item => 
          `- ${item.title}\n  ${item.price}`
        ).join('\n\n') || 'Ilan yok');
    } else if (pageType === 'detail') {
      data = await chrome.tabs.sendMessage(tab.id, { action: 'extractDetail' });
      resultEl.textContent = `DETAY SAYFASI\n\n` +
        `Baslik: ${data.title}\n` +
        `Fiyat: ${data.price}\n` +
        `Satici: ${data.sellerName}\n` +
        `Konum: ${data.location}\n` +
        `Resim: ${data.images?.length || 0} adet`;
    } else {
      resultEl.textContent = 'Bilinmeyen sayfa tipi: ' + pageType + '\n\nArama veya ilan detay sayfasina git.';
    }
  } catch (error) {
    resultEl.textContent = 'Hata: ' + error.message + '\n\nSayfayi yenile ve tekrar dene.';
  }
});

// Ornek arama testi (bridge uzerinden)
document.getElementById('testSearch').addEventListener('click', async () => {
  resultEl.textContent = 'Bridge uzerinden arama yapiliyor...\n(Bu islem 10-15 saniye surebilir)';
  
  try {
    const response = await fetch('http://localhost:8766/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: 'dji',
        category: 'drone',
        limit: 5
      })
    });
    
    if (!response.ok) {
      throw new Error('Bridge hatasi: ' + response.status);
    }
    
    const data = await response.json();
    
    if (data.error) {
      resultEl.textContent = 'Hata: ' + data.error;
    } else {
      resultEl.textContent = `ARAMA SONUCU\n` +
        `Bulunan: ${data.listings?.length || 0} ilan\n\n` +
        (data.listings?.slice(0, 3).map(item => 
          `- ${item.title}\n  ${item.price}`
        ).join('\n\n') || 'Ilan yok');
    }
  } catch (error) {
    resultEl.textContent = 'Hata: ' + error.message + '\n\nBridge calismiyor olabilir.\nnode bridge.js calistir.';
  }
});

// Sayfa yuklendiginde bridge'i kontrol et
checkBridge();
