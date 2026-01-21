# Sahibinden MCP Server

> **Eğitim Amaçlı Proje** - MCP (Model Context Protocol) ve Chrome Extension geliştirme öğrenmek için hazırlanmıştır.

Chrome Extension + MCP entegrasyonu örneği. Cursor/AI ile nasıl çalıştığını gösterir.

---

## YASAL UYARI VE SORUMLULUK REDDİ

**ÖNEMLİ: BU YAZILIMI KULLANMADAN ÖNCE OKUYUN**

Bu yazılım **YALNIZCA EĞİTİM VE ARAŞTIRMA AMAÇLIDIR**.

### Sorumluluk Reddi

1. Bu yazılımın geliştiricileri, yazılımın kullanımından doğabilecek **HİÇBİR DOĞRUDAN, DOLAYLI, ARIZİ, ÖZEL VEYA SONUÇ OLARAK ORTAYA ÇIKAN ZARARDAN SORUMLU DEĞİLDİR**.

2. Bu yazılım **"OLDUĞU GİBİ"** sağlanmaktadır. Herhangi bir garanti verilmemektedir.

3. Yazılımı indiren, kuran veya kullanan kişi, **TÜM RİSKİ ÜSTLENDİĞİNİ** ve kullanımdan doğabilecek **TÜM YASAL, MALİ VE CEZAİ SORUMLULUĞU KABUL ETTİĞİNİ** beyan eder.

4. Bu yazılım **Sahibinden.com ile hiçbir şekilde bağlantılı değildir**. Resmi bir ürün veya hizmet değildir.

5. Web scraping yasaları ülkeden ülkeye farklılık gösterir. **Kendi ülkenizin yasalarına uygun hareket etmek TAMAMEN SİZİN SORUMLULUĞUNUZDADIR**.

6. Hedef web sitelerinin kullanım koşullarını ihlal etmek yasal sonuçlar doğurabilir. **Bu tür ihlallerden doğacak sonuçlardan geliştirici sorumlu tutulamaz**.

### Kullanım Şartları

Bu yazılımı kullanarak:
- Yukarıdaki tüm şartları okuduğunuzu ve kabul ettiğinizi,
- Yazılımı yalnızca eğitim amaçlı kullanacağınızı,
- Ticari amaçla kullanmayacağınızı,
- Üçüncü taraf haklarını ihlal etmeyeceğinizi

**KABUL VE BEYAN ETMİŞ OLURSUNUZ**.

Bu şartları kabul etmiyorsanız, yazılımı kullanmayınız.

---

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

MIT - Detaylar için LICENSE dosyasına bakınız.
