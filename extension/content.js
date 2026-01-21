// Content script - Sahibinden sayfalarindan veri ceker

// Sayfa turunu tespit et
function getPageType() {
  const url = window.location.href;
  if (url.includes('/ilan/') && url.includes('/detay')) {
    return 'detail';
  } else if (url.includes('/arama') || document.querySelector('.searchResultsItem')) {
    return 'search';
  } else if (url.includes('sahibinden.com') && document.querySelector('tr[data-id]')) {
    return 'search';
  }
  return 'other';
}

// Arama sonuclarini cek
function extractSearchResults() {
  const results = [];
  const rows = document.querySelectorAll('.searchResultsItem, tr[data-id]');
  
  rows.forEach(row => {
    const id = row.getAttribute('data-id');
    if (!id) return;
    
    const titleEl = row.querySelector('.classifiedTitle, a[title]');
    const priceEl = row.querySelector('.searchResultsPriceValue');
    const imgEl = row.querySelector('img.s-image');
    const dateEl = row.querySelector('.searchResultsDateValue');
    const locEl = row.querySelector('.searchResultsLocationValue');
    
    let image = imgEl?.src || '';
    if (image.includes('lthmb')) {
      image = image.replace('lthmb', 'xxlmdb');
    }
    
    results.push({
      id,
      title: titleEl?.getAttribute('title') || titleEl?.textContent?.trim() || '',
      price: priceEl?.textContent?.trim().replace(/\s+/g, ' ') || '',
      location: locEl?.textContent?.trim().replace(/\s+/g, ' ') || '',
      date: dateEl?.textContent?.trim().replace(/\s+/g, ' ') || '',
      image,
      url: titleEl?.href || '',
    });
  });
  
  // Toplam sonuc sayisi
  const totalEl = document.querySelector('.result-text');
  let total = 0;
  if (totalEl) {
    const match = totalEl.textContent.match(/([\d.,]+)/);
    if (match) total = parseInt(match[1].replace(/[.,]/g, ''));
  }
  
  return { listings: results, total, url: window.location.href };
}

// Detay sayfasindan bilgi cek
function extractDetailInfo() {
  // Baslik
  let title = '';
  const pageTitle = document.title;
  if (pageTitle) {
    const match = pageTitle.match(/^(.+?)\s+sahibinden\.com/i);
    if (match) title = match[1].trim();
  }
  
  // Fiyat
  let price = '';
  const priceEl = document.querySelector('.classifiedInfo h3');
  if (priceEl) price = priceEl.textContent.trim().split('\n')[0];
  
  // Aciklama
  let description = '';
  const descEl = document.querySelector('#classifiedDescription');
  if (descEl) description = descEl.textContent.trim();
  
  // Satici
  let sellerName = '';
  const sellerEl = document.querySelector('.username-info-area h5');
  if (sellerEl) sellerName = sellerEl.textContent.trim();
  
  // Konum
  let location = '';
  const locEl = document.querySelector('.classifiedInfo address');
  if (locEl) location = locEl.textContent.trim().replace(/\s+/g, ' ');
  
  // Ozellikler
  const specs = {};
  document.querySelectorAll('.classifiedInfoList li').forEach(li => {
    const strong = li.querySelector('strong');
    const span = li.querySelector('span');
    if (strong && span) {
      const key = strong.textContent.trim().replace(':', '');
      const value = span.textContent.trim();
      if (key && value) specs[key] = value;
    }
  });
  
  // Resimler
  const images = [];
  document.querySelectorAll('img.s-image, img[data-big], .classifiedMiniImages img').forEach(img => {
    let src = img.getAttribute('data-big') || img.src;
    if (src && !images.includes(src) && !src.includes('placeholder')) {
      if (src.includes('lthmb')) src = src.replace('lthmb', 'xxlmdb');
      images.push(src);
    }
  });
  
  // Kategori
  let category = '';
  const breadcrumbs = [];
  document.querySelectorAll('.breadcrumb a').forEach(a => {
    const text = a.textContent.trim();
    if (text && text !== 'Ana Sayfa') breadcrumbs.push(text);
  });
  category = breadcrumbs.join(' > ');
  
  // Ilan no
  let listingNo = '';
  const idMatch = window.location.href.match(/(\d{9,})/);
  if (idMatch) listingNo = idMatch[1];
  
  // SORU-CEVAP - Sahibinden.com gercek DOM yapisi
  const questions = [];
  
  // Ana container: section.classified-question-answer veya #soru
  const qaContainer = document.querySelector('section.classified-question-answer, #soru, .classified-question-answer');
  
  if (qaContainer) {
    // Her soru-cevap thread'i: .thread-item
    const threadItems = qaContainer.querySelectorAll('.thread-item');
    
    threadItems.forEach(thread => {
      // Soru kismi: .container-comment-item.type-question
      const questionBlock = thread.querySelector('.container-comment-item.type-question');
      // Cevap kismi: .container-comment-item.type-answer (last-answer-item olan)
      const answerBlock = thread.querySelector('.container-comment-item.type-answer.last-answer-item');
      
      if (questionBlock) {
        // Soran kisi
        const askerEl = questionBlock.querySelector('.name-surname');
        // Soru metni
        const questionTextEl = questionBlock.querySelector('.comment-text');
        // Soru tarihi
        const questionDateEl = questionBlock.querySelector('.comment-date');
        
        let answerText = '';
        let answeredBy = '';
        let answerDate = '';
        
        if (answerBlock) {
          const answerTextEl = answerBlock.querySelector('.comment-text');
          const answererEl = answerBlock.querySelector('.name-surname');
          const answerDateEl = answerBlock.querySelector('.comment-date');
          
          answerText = answerTextEl?.textContent?.trim() || '';
          answeredBy = answererEl?.textContent?.trim() || '';
          answerDate = answerDateEl?.getAttribute('title') || answerDateEl?.textContent?.trim() || '';
        }
        
        const questionText = questionTextEl?.textContent?.trim() || '';
        
        if (questionText) {
          questions.push({
            asker: askerEl?.textContent?.trim() || '',
            question: questionText,
            questionDate: questionDateEl?.getAttribute('title') || questionDateEl?.textContent?.trim() || '',
            answer: answerText || 'Henuz cevaplanmamis',
            answeredBy: answeredBy,
            answerDate: answerDate,
          });
        }
      }
    });
  }
  
  console.log('[Sahibinden Ext] Bulunan soru-cevap sayisi:', questions.length);
  
  // Fiyat gecmisi (varsa)
  const priceHistory = [];
  document.querySelectorAll('.price-history-item, [class*="priceHistory"] li').forEach(item => {
    const priceEl = item.querySelector('.price, [class*="price"]');
    const dateEl = item.querySelector('.date, [class*="date"]');
    if (priceEl) {
      priceHistory.push({
        price: priceEl.textContent.trim(),
        date: dateEl?.textContent?.trim() || '',
      });
    }
  });
  
  // Satici telefonu (gizli olabilir)
  let sellerPhone = '';
  const phoneEl = document.querySelector('.phone-number, [class*="phoneNumber"]');
  if (phoneEl) sellerPhone = phoneEl.textContent.trim();
  
  // Ilan tarihi
  let listingDate = '';
  const dateInfoEl = document.querySelector('.classifiedInfoList li:first-child span');
  if (dateInfoEl && dateInfoEl.textContent.includes('202')) {
    listingDate = dateInfoEl.textContent.trim();
  }
  
  return {
    listingNo,
    title,
    price,
    description,
    sellerName,
    sellerPhone,
    location,
    listingDate,
    specs,
    images,
    category,
    questions,
    priceHistory,
    url: window.location.href,
  };
}

// Mesaj dinleyici
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('[Sahibinden Ext] Mesaj alindi:', request);
  
  if (request.action === 'getPageType') {
    sendResponse({ type: getPageType() });
  }
  else if (request.action === 'extractSearch' || request.type === 'search') {
    const data = extractSearchResults();
    console.log('[Sahibinden Ext] Arama sonuclari:', data.listings.length);
    sendResponse(data);
  }
  else if (request.action === 'extractDetail' || request.type === 'get_listing') {
    const data = extractDetailInfo();
    console.log('[Sahibinden Ext] Detay bilgisi:', data.title);
    sendResponse(data);
  }
  
  return true; // Async response
});

console.log('[Sahibinden Ext] Content script yuklendi:', getPageType());
