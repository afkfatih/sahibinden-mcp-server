# Sahibinden MCP Server

Sahibinden.com icin Chrome Extension tabanli MCP (Model Context Protocol) server. Bot detection'i bypass ederek ilan arama ve detay cekme islemlerini gerceklestirir.

## Mimari

```
┌─────────────────┐     HTTP      ┌─────────────────┐    WebSocket    ┌─────────────────┐
│   Cursor/AI     │ ──────────── │   Bridge.js     │ ─────────────── │ Chrome Extension│
│   (MCP Client)  │   :8766      │   (Node.js)     │     :8765       │  (Sahibinden)   │
└─────────────────┘              └─────────────────┘                 └─────────────────┘
        │                                │                                   │
        │ search_sahibinden              │ Forward command                   │ Open tab
        │ get_listing_detail             │                                   │ Extract data
        │ get_cheapest_listings          │                                   │ Close tab
        └────────────────────────────────┴───────────────────────────────────┘
```

## Kurulum

### 1. Node.js Bagimliliklari

```bash
npm install
```

### 2. Chrome Extension Yukleme

1. Chrome'da `chrome://extensions` adresine git
2. "Gelistirici modu" (Developer mode) aktif et
3. "Paketlenmemis ogesini yukle" (Load unpacked) tikla
4. `extension/` klasorunu sec

### 3. Cursor MCP Konfigurasyonu

`~/.cursor/mcp.json` dosyasina ekle:

```json
{
  "mcpServers": {
    "sahibinden": {
      "command": "python",
      "args": ["C:/path/to/sahibinden-mcp-server/index-extension.py"]
    }
  }
}
```

## Kullanim

### 1. Bridge Server'i Baslat

```bash
npm start
# veya
node bridge.js
```

Cikti:
```
Bridge Server Baslatiliyor...
WebSocket: ws://localhost:8765
HTTP API: http://localhost:8766
```

### 2. Chrome Extension Baglantisi

Chrome'da extension yuklendikten sonra otomatik olarak bridge'e baglanir.
Bridge terminalinde goreceksin:
```
[WS] Chrome Extension kaydedildi
```

### 3. MCP Araclari

#### `search_sahibinden`
Sahibinden.com'da arama yapar.

Parametreler:
- `query` (string): Arama sorgusu (ornek: "dji drone")
- `category` (string, opsiyonel): Kategori (drone, telefon, bilgisayar, araba)
- `city` (string, opsiyonel): Sehir (istanbul, ankara, izmir, vb.)
- `town` (string, opsiyonel): Ilce (Istanbul icin: bayrampasa, kadikoy, vb.)
- `minPrice` (int, opsiyonel): Minimum fiyat
- `maxPrice` (int, opsiyonel): Maksimum fiyat
- `sorting` (string, opsiyonel): Siralama (price_asc, price_desc, date_desc)
- `date` (string, opsiyonel): Tarih filtresi (1day, 3days, 7days, 15days, 30days)

#### `get_listing_detail`
Belirli bir ilanin detaylarini getirir.

Parametreler:
- `listing_id` (string): Ilan ID'si

#### `get_cheapest_listings`
En ucuz ilanlari bulur.

Parametreler:
- `query` (string): Arama sorgusu
- `city` (string, opsiyonel): Sehir
- `town` (string, opsiyonel): Ilce
- `maxPrice` (int, opsiyonel): Maksimum fiyat
- `limit` (int, opsiyonel): Sonuc limiti (varsayilan: 10)

#### `list_city_codes`
Desteklenen sehir, ilce ve kategori kodlarini listeler.

## Ornek Kullanim

```
"Istanbul Bayrampasa'daki en ucuz DJI drone'u bul"
```

MCP:
```python
get_cheapest_listings(
    query="dji drone",
    city="istanbul", 
    town="bayrampasa",
    limit=5
)
```

## Dosya Yapisi

```
sahibinden-mcp-server/
├── bridge.js           # Node.js WebSocket/HTTP bridge
├── index-extension.py  # Python MCP server
├── package.json        # Node.js dependencies
├── README.md           # Bu dosya
└── extension/          # Chrome Extension
    ├── manifest.json   # Extension konfigurasyonu
    ├── background.js   # Service worker (bridge iletisimi)
    ├── content.js      # DOM data extraction
    ├── popup.html      # Extension popup UI
    └── popup.js        # Popup logic
```

## Notlar

- Chrome'da Sahibinden.com'a giris yapmis olmaniz gerekir
- Extension kullanici tarayicisinda calistigi icin bot detection bypass edilir
- Bridge server arka planda calismalidir (node bridge.js)
- Her arama icin yeni bir tab acilir ve kapatilir

## Sorun Giderme

### "Chrome Extension bagli degil" hatasi
1. Extension'in yuklü oldugunu kontrol et
2. `chrome://extensions` sayfasinda extension'i yenile
3. Bridge server'i yeniden baslat

### "Port already in use" hatasi
```powershell
Get-NetTCPConnection -LocalPort 8765 | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
Get-NetTCPConnection -LocalPort 8766 | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```

## Lisans

MIT
