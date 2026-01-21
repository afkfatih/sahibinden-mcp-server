# Sahibinden MCP Server

> **Eğitim Amaçlı Proje** - MCP (Model Context Protocol) ve Chrome Extension geliştirme öğrenmek için hazırlanmıştır.

Chrome Extension + MCP entegrasyonu örneği. Cursor/AI ile nasıl çalıştığını gösterir.

## Disclaimer

Bu proje **yalnızca eğitim ve araştırma amaçlıdır**. 

- Sahibinden.com'un resmi bir ürünü veya iş ortağı değildir
- Ticari kullanım için tasarlanmamıştır
- Web scraping yasaları ülkeden ülkeye değişir, kendi sorumluluğunuzdadır
- Hedef sitenin robots.txt ve kullanım koşullarına uygun davranın

**Kullanımdan doğacak her türlü sorumluluk kullanıcıya aittir.**

## Ne Öğrenirsin?

- MCP server nasıl yazılır (Python)
- Chrome Extension ile MCP nasıl entegre edilir
- WebSocket/HTTP bridge mimarisi
- Content script ile DOM scraping

## Kurulum

```bash
npm install
pip install -r requirements.txt --user
```

Chrome: `chrome://extensions` > Geliştirici modu > `extension/` klasörünü yükle

## Kullanım

```bash
npm start
```

## Yapı

```
├── bridge.js           # WebSocket/HTTP köprüsü
├── index-extension.py  # MCP server (Python)
└── extension/          # Chrome Extension
    ├── background.js   # Service worker
    └── content.js      # DOM scraper
```

## Lisans

MIT - Eğitim amaçlı kullanım için.
