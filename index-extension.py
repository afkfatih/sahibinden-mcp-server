"""
Sahibinden MCP Server v2.0 - Chrome Extension Bridge
Gelismis ozellikler: Bolge, Fiyat, Siralama, Soru-Cevap, Detay
"""

from mcp.server.fastmcp import FastMCP
import httpx
import json

mcp = FastMCP("Sahibinden Extension Bridge")
BRIDGE_URL = "http://localhost:8766"

# Sehir kodlari
CITY_CODES = {
    "istanbul": 34, "ankara": 6, "izmir": 35, "bursa": 16, "antalya": 7,
    "adana": 1, "konya": 42, "gaziantep": 27, "mersin": 33, "kayseri": 38,
    "eskisehir": 26, "diyarbakir": 21, "samsun": 55, "denizli": 20, "sanliurfa": 63,
    "kocaeli": 41, "trabzon": 61, "mugla": 48, "hatay": 31, "sakarya": 54,
}

# Istanbul ilce kodlari
ISTANBUL_TOWNS = {
    "adalar": 831, "arnavutkoy": 890, "atasehir": 888, "avcilar": 837,
    "bagcilar": 838, "bahcelievler": 839, "bakirkoy": 840, "basaksehir": 886,
    "bayrampasa": 841, "besiktas": 843, "beykoz": 844, "beylikduzu": 887,
    "beyoglu": 845, "buyukcekmece": 846, "catalca": 848, "cekmekoy": 889,
    "esenler": 849, "esenyurt": 885, "eyup": 850, "fatih": 851,
    "gaziosmanpasa": 852, "gungoren": 853, "kadikoy": 854, "kagithane": 855,
    "kartal": 856, "kucukcekmece": 857, "maltepe": 858, "pendik": 859,
    "sancaktepe": 891, "sariyer": 860, "sile": 861, "silivri": 862,
    "sisli": 863, "sultanbeyli": 864, "sultangazi": 892, "tuzla": 866,
    "umraniye": 867, "uskudar": 868, "zeytinburnu": 869,
}

# Kategori kisayollari
CATEGORIES = {
    "drone": "hobi-oyuncak-rc-araclar",
    "telefon": "cep-telefonu",
    "bilgisayar": "bilgisayar",
    "laptop": "dizustu-notebook",
    "araba": "otomobil",
    "motosiklet": "motosiklet",
    "ev": "kiralik",
    "daire": "satilik-daire",
    "tablet": "tablet",
    "kamera": "fotograf-kamera",
}

async def check_bridge():
    """Bridge baglantisini kontrol et"""
    try:
        async with httpx.AsyncClient() as client:
            health = await client.get(BRIDGE_URL, timeout=5.0)
            status = health.json()
            if not status.get("extension_connected"):
                return False, "Chrome Extension bagli degil! Chrome'u ac ve extension'i kontrol et."
            return True, None
    except Exception:
        return False, f"Bridge Server ({BRIDGE_URL}) calismiyor! 'node bridge.js' calistir."

@mcp.tool()
async def search_sahibinden(
    query: str = None,
    category: str = None,
    city: str = None,
    town: str = None,
    minPrice: int = None,
    maxPrice: int = None,
    sorting: str = None,
    date: str = None,
    limit: int = 50
) -> str:
    """
    Sahibinden.com'da gelismis arama yap.
    
    Args:
        query: Arama metni (orn: "dji mini 3 pro")
        category: Kategori (drone, telefon, araba, laptop, tablet, kamera, motosiklet, ev, daire)
        city: Sehir (istanbul, ankara, izmir, bursa, antalya...)
        town: Ilce - sadece Istanbul (bayrampasa, kadikoy, besiktas, uskudar...)
        minPrice: Minimum fiyat (TL)
        maxPrice: Maksimum fiyat (TL)
        sorting: Siralama (price_asc=ucuzdan pahaliya, price_desc=pahalidan ucuza, date_desc=yeniden eskiye)
        date: Tarih filtresi (1day=bugun, 3days=son 3 gun, 7days=son hafta, 15days, 30days)
        limit: Maksimum sonuc sayisi (varsayilan: 50)
    
    Returns:
        Ilan listesi: baslik, fiyat, konum, tarih, resim, link
    """
    ok, error = await check_bridge()
    if not ok:
        return f"HATA: {error}"
    
    try:
        payload = {
            "query": query,
            "category": CATEGORIES.get(category.lower(), category) if category else None,
            "city": city,
            "town": town,
            "minPrice": minPrice,
            "maxPrice": maxPrice,
            "sorting": sorting,
            "date": date,
            "limit": limit
        }
        
        # None olanlari kaldir
        payload = {k: v for k, v in payload.items() if v is not None}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{BRIDGE_URL}/search", json=payload, timeout=90.0)
            
            if response.status_code != 200:
                return f"HATA: {response.text}"
            
            data = response.json()
            
            if data.get("error"):
                return f"HATA: {data['error']}"
            
            listings = data.get("listings", [])
            total = data.get("total", 0)
            url = data.get("url", "")
            
            output = [f"TOPLAM {total} ILAN BULUNDU ({len(listings)} listelendi)"]
            output.append(f"URL: {url}\n")
            
            for i, item in enumerate(listings[:limit], 1):
                output.append(f"{i}. [{item.get('id', '')}] {item.get('title', '')}")
                output.append(f"   Fiyat: {item.get('price', 'Belirtilmemis')}")
                output.append(f"   Konum: {item.get('location', '')}")
                output.append(f"   Tarih: {item.get('date', '')}")
                if item.get('image'):
                    output.append(f"   Resim: {item.get('image')}")
                output.append(f"   Link: {item.get('url', '')}")
                output.append("")
            
            return "\n".join(output)

    except Exception as e:
        return f"Beklenmeyen Hata: {str(e)}"

@mcp.tool()
async def get_listing_detail(listing_id: str) -> str:
    """
    Belirli bir ilanin TUM detaylarini getir.
    
    Args:
        listing_id: Ilan ID numarasi (URL'den veya arama sonuclarindan)
    
    Returns:
        Detayli ilan bilgisi: baslik, fiyat, aciklama, ozellikler, 
        TUM RESIMLER, SORU-CEVAPLAR, satici bilgisi, kategori
    """
    ok, error = await check_bridge()
    if not ok:
        return f"HATA: {error}"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BRIDGE_URL}/listing", 
                json={"listing_id": listing_id}, 
                timeout=90.0
            )
            data = response.json()
            
            if data.get("error"):
                return f"HATA: {data['error']}"
            
            output = []
            output.append("=" * 60)
            output.append("ILAN DETAYI")
            output.append("=" * 60)
            output.append(f"\nBaslik: {data.get('title', '')}")
            output.append(f"Fiyat: {data.get('price', '')}")
            output.append(f"Ilan No: {data.get('listingNo', '')}")
            output.append(f"Konum: {data.get('location', '')}")
            output.append(f"Kategori: {data.get('category', '')}")
            output.append(f"Satici: {data.get('sellerName', '')}")
            if data.get('sellerPhone'):
                output.append(f"Telefon: {data.get('sellerPhone')}")
            if data.get('listingDate'):
                output.append(f"Ilan Tarihi: {data.get('listingDate')}")
            
            output.append(f"\n{'-' * 40}")
            output.append("ACIKLAMA")
            output.append(f"{'-' * 40}")
            output.append(data.get('description', 'Aciklama yok'))
            
            specs = data.get('specs', {})
            if specs:
                output.append(f"\n{'-' * 40}")
                output.append("OZELLIKLER")
                output.append(f"{'-' * 40}")
                for key, value in specs.items():
                    output.append(f"  {key}: {value}")
            
            images = data.get('images', [])
            if images:
                output.append(f"\n{'-' * 40}")
                output.append(f"RESIMLER ({len(images)} adet)")
                output.append(f"{'-' * 40}")
                for i, img in enumerate(images, 1):
                    output.append(f"  {i}. {img}")
            
            questions = data.get('questions', [])
            if questions:
                output.append(f"\n{'-' * 40}")
                output.append(f"SORU-CEVAPLAR ({len(questions)} adet)")
                output.append(f"{'-' * 40}")
                for i, qa in enumerate(questions, 1):
                    output.append(f"  S{i}: {qa.get('question', '')}")
                    if qa.get('answer'):
                        output.append(f"  C{i}: {qa.get('answer')}")
                    if qa.get('date'):
                        output.append(f"      ({qa.get('date')})")
                    output.append("")
            
            priceHistory = data.get('priceHistory', [])
            if priceHistory:
                output.append(f"\n{'-' * 40}")
                output.append("FIYAT GECMISI")
                output.append(f"{'-' * 40}")
                for ph in priceHistory:
                    output.append(f"  {ph.get('date', '')}: {ph.get('price', '')}")
            
            output.append(f"\nURL: {data.get('url', '')}")
            
            return "\n".join(output)

    except Exception as e:
        return f"Hata: {str(e)}"

@mcp.tool()
async def get_cheapest_listings(
    query: str,
    category: str = None,
    city: str = None,
    town: str = None,
    maxPrice: int = None,
    count: int = 5
) -> str:
    """
    En ucuz ilanlari bul ve detaylarini getir.
    
    Args:
        query: Arama metni (orn: "dji drone")
        category: Kategori (drone, telefon, araba...)
        city: Sehir (istanbul, ankara...)
        town: Ilce - sadece Istanbul (bayrampasa, kadikoy...)
        maxPrice: Maksimum fiyat filtresi (TL)
        count: Kac ilan getir (varsayilan: 5, maks: 10)
    
    Returns:
        En ucuz ilanlarin detaylari
    """
    ok, error = await check_bridge()
    if not ok:
        return f"HATA: {error}"
    
    try:
        # Once en ucuz siralamasi ile ara
        payload = {
            "query": query,
            "category": CATEGORIES.get(category.lower(), category) if category else None,
            "city": city,
            "town": town,
            "maxPrice": maxPrice,
            "sorting": "price_asc",
            "limit": min(count, 10)
        }
        payload = {k: v for k, v in payload.items() if v is not None}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{BRIDGE_URL}/search", json=payload, timeout=90.0)
            data = response.json()
            
            if data.get("error"):
                return f"HATA: {data['error']}"
            
            listings = data.get("listings", [])
            
            if not listings:
                return "Ilan bulunamadi!"
            
            output = []
            output.append(f"EN UCUZ {len(listings)} ILAN")
            output.append(f"Arama: {query}")
            if city:
                output.append(f"Sehir: {city}")
            if town:
                output.append(f"Ilce: {town}")
            output.append("=" * 60)
            
            for i, item in enumerate(listings, 1):
                output.append(f"\n{i}. {item.get('title', '')}")
                output.append(f"   FIYAT: {item.get('price', 'Belirtilmemis')}")
                output.append(f"   Konum: {item.get('location', '')}")
                output.append(f"   Tarih: {item.get('date', '')}")
                output.append(f"   ID: {item.get('id', '')}")
                output.append(f"   Link: {item.get('url', '')}")
            
            return "\n".join(output)

    except Exception as e:
        return f"Hata: {str(e)}"

@mcp.tool()
async def list_city_codes() -> str:
    """
    Desteklenen sehir ve ilce kodlarini listele.
    
    Returns:
        Sehir ve Istanbul ilce listesi
    """
    output = ["DESTEKLENEN SEHIRLER"]
    output.append("=" * 40)
    for city in sorted(CITY_CODES.keys()):
        output.append(f"  - {city}")
    
    output.append("\n\nISTANBUL ILCELERI")
    output.append("=" * 40)
    for town in sorted(ISTANBUL_TOWNS.keys()):
        output.append(f"  - {town}")
    
    output.append("\n\nKATEGORILER")
    output.append("=" * 40)
    for cat in sorted(CATEGORIES.keys()):
        output.append(f"  - {cat}")
    
    return "\n".join(output)

if __name__ == "__main__":
    print("[MCP] Sahibinden Extension MCP Server v2.0 Baslatiliyor...")
    mcp.run()
