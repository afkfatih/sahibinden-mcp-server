"""
Sahibinden MCP Server v2.0 - Chrome Extension Bridge
Gelismis ozellikler: Bolge, Fiyat, Siralama, Soru-Cevap, Detay
Bridge.js otomatik baslatma destegi
Resim goruntuleme destegi
"""

from mcp.server.fastmcp import FastMCP, Image
import httpx
import json
import subprocess
import os
import sys
import time
import atexit
import base64
from io import BytesIO

mcp = FastMCP("Sahibinden Extension Bridge")
BRIDGE_URL = "http://localhost:8766"

# Bridge process referansi
bridge_process = None

def start_bridge():
    """Bridge.js'i arka planda baslat"""
    global bridge_process
    
    # Zaten calisiyor mu kontrol et
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 8766))
        sock.close()
        if result == 0:
            # Port acik, bridge zaten calisiyor
            return True
    except:
        pass
    
    # Bridge.js yolunu bul
    script_dir = os.path.dirname(os.path.abspath(__file__))
    bridge_path = os.path.join(script_dir, "bridge.js")
    
    if not os.path.exists(bridge_path):
        return False
    
    try:
        # Windows icin CREATE_NO_WINDOW flag
        startupinfo = None
        if sys.platform == "win32":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
        
        bridge_process = subprocess.Popen(
            ["node", bridge_path],
            cwd=script_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            startupinfo=startupinfo
        )
        
        # Bridge'in baslamasini bekle
        time.sleep(1.5)
        return bridge_process.poll() is None
    except Exception as e:
        return False

def stop_bridge():
    """MCP kapanirken bridge'i de kapat"""
    global bridge_process
    if bridge_process and bridge_process.poll() is None:
        bridge_process.terminate()
        try:
            bridge_process.wait(timeout=3)
        except:
            bridge_process.kill()

# MCP kapanirken bridge'i de kapat
atexit.register(stop_bridge)

# Baslangicta bridge'i baslat
start_bridge()

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
    """Bridge baglantisini kontrol et, gerekirse baslat"""
    try:
        async with httpx.AsyncClient() as client:
            health = await client.get(BRIDGE_URL, timeout=5.0)
            status = health.json()
            if not status.get("extension_connected"):
                return False, "Chrome Extension bagli degil! Chrome'u ac ve extension'i kontrol et."
            return True, None
    except Exception:
        # Bridge calismiyorsa baslatmayi dene
        if start_bridge():
            time.sleep(1)
            try:
                async with httpx.AsyncClient() as client:
                    health = await client.get(BRIDGE_URL, timeout=5.0)
                    status = health.json()
                    if not status.get("extension_connected"):
                        return False, "Bridge baslatildi ama Chrome Extension bagli degil! Chrome'u ac."
                    return True, None
            except:
                pass
        return False, f"Bridge Server ({BRIDGE_URL}) baslatilamadi! Node.js yuklu mu kontrol et."

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

@mcp.tool()
async def view_listing_images(listing_id: str, max_images: int = 3) -> list:
    """
    Bir ilanin resimlerini indir ve goruntulenebilir formatta dondur.
    
    Args:
        listing_id: Ilan ID numarasi
        max_images: Maksimum kac resim getirilsin (varsayilan: 3, maks: 5)
    
    Returns:
        Resimlerin base64 kodlanmis hali (AI tarafindan gorulebilir)
    """
    ok, error = await check_bridge()
    if not ok:
        return [f"HATA: {error}"]
    
    try:
        # Once ilan detayini al
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BRIDGE_URL}/listing", 
                json={"listing_id": listing_id}, 
                timeout=90.0
            )
            data = response.json()
            
            if data.get("error"):
                return [f"HATA: {data['error']}"]
            
            images = data.get('images', [])
            if not images:
                return ["Bu ilanda resim bulunamadi."]
            
            # Resimleri filtrele - sadece gercek resimler
            valid_images = []
            for img in images:
                if img and 'shbdn.com' in img and 'blank' not in img and 'placeholder' not in img:
                    # Buyuk resim URL'sine cevir
                    if 'thmb_' in img:
                        img = img.replace('thmb_', 'x5_')
                    elif 'lthmb' in img:
                        img = img.replace('lthmb', 'xxlmdb')
                    valid_images.append(img)
            
            if not valid_images:
                return ["Gecerli resim bulunamadi."]
            
            # Maksimum resim sayisini sinirla
            max_images = min(max_images, 5)
            images_to_fetch = valid_images[:max_images]
            
            results = []
            results.append(f"ILAN: {data.get('title', listing_id)}")
            results.append(f"FIYAT: {data.get('price', 'Belirtilmemis')}")
            results.append(f"Toplam {len(valid_images)} resim mevcut, {len(images_to_fetch)} tanesi gosteriliyor.\n")
            
            # Resimleri indir ve base64'e cevir
            for i, img_url in enumerate(images_to_fetch, 1):
                try:
                    img_response = await client.get(
                        img_url, 
                        timeout=30.0,
                        headers={
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                            "Referer": "https://www.sahibinden.com/"
                        }
                    )
                    
                    if img_response.status_code == 200:
                        # Content type belirle
                        content_type = img_response.headers.get('content-type', 'image/jpeg')
                        if 'jpeg' in content_type or 'jpg' in content_type:
                            media_type = 'image/jpeg'
                        elif 'png' in content_type:
                            media_type = 'image/png'
                        elif 'webp' in content_type:
                            media_type = 'image/webp'
                        else:
                            media_type = 'image/jpeg'
                        
                        # Base64'e cevir
                        img_base64 = base64.b64encode(img_response.content).decode('utf-8')
                        
                        # Image objesi olustur
                        results.append(Image(data=img_base64, media_type=media_type))
                        results.append(f"Resim {i}/{len(images_to_fetch)}")
                    else:
                        results.append(f"Resim {i} indirilemedi (HTTP {img_response.status_code})")
                        
                except Exception as img_err:
                    results.append(f"Resim {i} hatasi: {str(img_err)}")
            
            return results

    except Exception as e:
        return [f"Hata: {str(e)}"]

if __name__ == "__main__":
    print("[MCP] Sahibinden Extension MCP Server v2.0 Baslatiliyor...")
    mcp.run()
