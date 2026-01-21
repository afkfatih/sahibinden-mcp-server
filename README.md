# Sahibinden MCP Server

MCP + Chrome Extension entegrasyonu örneği. **Eğitim amaçlıdır.**

## ⚠️ Yasal Uyarı

Bu yazılım **"olduğu gibi"** sağlanır. Kullanımdan doğan **tüm sorumluluk kullanıcıya aittir**. Geliştiriciler hiçbir zarardan sorumlu tutulamaz. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## Kurulum

```bash
npm install && pip install -r requirements.txt --user
```

Extension: `chrome://extensions` → Geliştirici modu → `extension/` yükle

## Kullanım

```bash
npm start  # Bridge başlat
```

## Yapı

| Dosya | Açıklama |
|-------|----------|
| `bridge.js` | WebSocket/HTTP köprüsü |
| `index-extension.py` | MCP server |
| `extension/` | Chrome Extension |

## Lisans

MIT
