# Katkida Bulunma Rehberi

Projeye katki sagladiginiz icin tesekkurler! Bu rehber, katkida bulunma surecini kolaylastirmak icin hazirlanmistir.

## Nasil Katkida Bulunabilirim?

### Bug Raporlama

1. Oncelikle [Issues](../../issues) sayfasinda benzer bir sorunun raporlanip raporlanmadigini kontrol edin
2. Yeni bir issue acarken:
   - Sorunu net bir sekilde aciklayin
   - Hata mesajlarini ekleyin
   - Hangi adimlari izlediginizi belirtin
   - Ortam bilgilerini (OS, Node.js surumu, Python surumu) paylasın

### Yeni Ozellik Onerisi

1. Issues sayfasinda "Feature Request" etiketi ile yeni bir issue acin
2. Onerinizi detayli aciklayin
3. Mumkunse ornek kullanim senaryolari ekleyin

### Kod Katkisi

#### Gelistirme Ortami Kurulumu

```bash
# Repo'yu fork'layin ve klonlayin
git clone https://github.com/YOUR_USERNAME/sahibinden-mcp-server.git
cd sahibinden-mcp-server

# Node.js bagimliklarini yukleyin
npm install

# Python bagimliklarini yukleyin
pip install -r requirements.txt --user

# Chrome Extension'i yukleyin
# chrome://extensions > Developer mode > Load unpacked > extension/
```

#### Kod Standartlari

- **JavaScript:** ES6+ syntax kullanin
- **Python:** PEP 8 standartlarina uyun
- **Commit mesajlari:** Aciklayici ve kisa olsun
  - `fix: Bridge baglanti hatasi duzeltildi`
  - `feat: Yeni siralama secenekleri eklendi`
  - `docs: README guncellendi`

#### Pull Request Sureci

1. Yeni bir branch olusturun:
   ```bash
   git checkout -b feature/yeni-ozellik
   ```

2. Degisikliklerinizi yapin ve commit edin:
   ```bash
   git add .
   git commit -m "feat: Yeni ozellik eklendi"
   ```

3. Fork'unuza push edin:
   ```bash
   git push origin feature/yeni-ozellik
   ```

4. GitHub'da Pull Request acin

5. PR aciklamasinda:
   - Ne degistirdiginizi aciklayin
   - Ilgili issue'lari baglayin (#123 gibi)
   - Test ettiginizi belirtin

## Proje Yapisi

```
sahibinden-mcp-server/
├── bridge.js           # WebSocket/HTTP bridge server
├── index-extension.py  # Python MCP server
├── extension/          # Chrome Extension
│   ├── manifest.json   # Extension config
│   ├── background.js   # Service worker
│   ├── content.js      # DOM scraper
│   ├── popup.html      # UI
│   └── popup.js        # UI logic
├── package.json        # Node.js deps
└── requirements.txt    # Python deps
```

## Gelistirme Alanlari

Katkida bulunabileceginiz alanlar:

### Kolay (Beginner Friendly)
- [ ] Daha fazla sehir kodu ekleme
- [ ] Dokumantasyon iyilestirmeleri
- [ ] Hata mesajlarini daha aciklayici yapma

### Orta
- [ ] Yeni kategori destegi (emlak, vasita vb.)
- [ ] Sayfalama (pagination) destegi
- [ ] Daha fazla detay bilgisi cekme

### Zor
- [ ] Firefox extension destegi
- [ ] Otomatik test altyapisi
- [ ] Rate limiting ve kuyruk sistemi

## Sorular?

Herhangi bir sorunuz varsa [Discussions](../../discussions) bolumunde sorabilirsiniz.

## Lisans

Bu projeye katkida bulunarak, kodunuzun [MIT Lisansi](LICENSE) altinda yayinlanmasini kabul etmis olursunuz.
