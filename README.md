# Sahibinden MCP Server

Chrome Extension tabanlı Sahibinden.com scraper. Cursor/AI ile entegre çalışır.

## Kurulum

```bash
# 1. Bağımlılıklar
npm install
pip install -r requirements.txt --user

# 2. Chrome Extension
# chrome://extensions > Geliştirici modu > Paketlenmemiş yükle > extension/

# 3. MCP Config (~/.cursor/mcp.json)
{
  "mcpServers": {
    "sahibinden": {
      "command": "python",
      "args": ["C:/path/to/index-extension.py"]
    }
  }
}
```

## Kullanım

```bash
# Bridge'i başlat
npm start
```

Extension otomatik bağlanır. Terminalde `Chrome Extension kaydedildi` görmelisin.

## MCP Araçları

| Araç | Açıklama |
|------|----------|
| `search_sahibinden` | İlan ara (şehir, ilçe, fiyat, tarih filtreleri) |
| `get_listing_detail` | İlan detayı çek |
| `get_cheapest_listings` | En ucuz ilanları bul |
| `list_city_codes` | Desteklenen şehir/ilçe kodları |

### Örnek

```
"Bayrampaşa'daki en ucuz DJI drone'u bul"
```

## Yapı

```
├── bridge.js           # WebSocket/HTTP köprüsü
├── index-extension.py  # MCP server
└── extension/          # Chrome Extension
    ├── background.js   # Köprü iletişimi
    └── content.js      # Sayfa scraper
```

## Sorun Giderme

**Extension bağlanmıyor:**
Extension'ı yenile veya bridge'i yeniden başlat.

**Port meşgul:**
```powershell
Get-NetTCPConnection -LocalPort 8765 | % { Stop-Process -Id $_.OwningProcess -Force }
```

## Lisans

MIT
