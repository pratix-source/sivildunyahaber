# Sivil Dünya Haber

`haber.sivildunya.com` için kaynak bağlantılı haber ve duyuru dashboardu. Uygulama GitHub Pages üzerinde statik olarak yayınlanır; veri taraması GitHub Actions ile altı saatte bir çalışır.

## Çalışma modeli

Sistem sağ sütunda tanımlı resmî kaynakları tarar, kaynak alan adı allowlist’inden geçmeyen bağlantıları aday kayda almaz ve başlık/özet/kaynak tarihi/URL gibi alanları `data/duyurular.json` içinde saklar. Kaynak sayfasının tam metni veya görseli kopyalanmaz. Her adayın yayın durumu varsayılan olarak `inceleme_bekliyor` olur; yalnızca sorumlu editörün kontrol edip `yayin_durumu` alanını `yayinda` yaptığı kayıtlar kamuya açık yayın akışına ve RSS’e girer.

Dashboard, yayımlanmış kayıtları, inceleme kuyruğunu, kişisel veri/hassas alan uyarılarını, kaynak erişim durumunu ve zorunlu iletişim bilgilerinin doldurulma oranını gösterir. Statik GitHub Pages ortamında güvenli yönetici oturumu bulunmadığı için dashboard bir **okuma ve kontrol arayüzüdür**; yayın kararı JSON dosyası üzerinden ve GitHub commit geçmişiyle verilmelidir.

## Dosyalar

| Dosya | İşlev |
| --- | --- |
| `index.html` | Yayın akışı, inceleme kuyruğu, kaynak sağlığı ve uyum dashboardu |
| `update_script.py` | Resmî kaynak taraması, alan adı kontrolü, kısa özet, kişisel veri sinyali ve audit üretimi |
| `data/duyurular.json` | Dashboardun okuduğu aday/yayın kayıtları |
| `data/audit.json` | Son taramanın kaynak bazlı sağlık ve sayısal özetleri |
| `data/archive/` | Günlük veri snapshotları; iki yıllık saklama hedefi için teknik arşiv izi |
| `data/site-config.json` | Yayıncı, sorumlu editör, iletişim ve yer sağlayıcı alanları |
| `rss.xml` | Yalnızca `yayin_durumu: yayinda` kayıtları içerir |
| `.github/workflows/update-data.yml` | Elle veya altı saatte bir tarama ve commit akışı |
| `LEGAL_EDITORIAL_POLICY.md` | Yayın öncesi mevzuat-uyumlu editoryal kontrol taslağı |

## İlk kurulum

Önce `data/site-config.json` içindeki boş alanları gerçek ve doğrulanabilir bilgilerle doldurun. İnternet haber sitesi niteliğine, iletişim başlığına, sorumlu müdür/editör bilgilerine ve yer sağlayıcı bilgilerine ilişkin alanlar yayına almadan önce hukuk danışmanı ve yayın sahibi tarafından kontrol edilmelidir. Alanlar doldurulmadan dashboard bunu eksik yapılandırma olarak gösterir.

GitHub deposunda **Actions** sekmesinden `Güncel Veri Topla` iş akışını seçip `Run workflow` ile ilk taramayı başlatabilirsiniz. İş akışı `data/duyurular.json`, `data/audit.json`, `data/archive/` ve `rss.xml` dosyalarını doğrular; değişiklik varsa GitHub Actions botu ile commit eder. GitHub Pages alan adı `CNAME` dosyasıyla korunur.

Yerelde kontrol için Python 3.11 ve iki paket yeterlidir:

```bash
python -m pip install requests beautifulsoup4
python update_script.py
python -m http.server 8000
```

Daha sonra `http://localhost:8000` adresini açın. Tarayıcı güvenlik politikaları nedeniyle JSON dosyalarının `file://` üzerinden değil, HTTP sunucusu üzerinden açılması gerekir.

## Editoryal onay akışı

Bir adayın yayınlanabilmesi için önce kaynak sayfası açılmalı, başlık ve özetin kaynağı doğru yansıtıp yansıtmadığı kontrol edilmeli, yayın tarihi ile güncelleme tarihi ayrıştırılmalı, kişisel veri ve hassas alan uyarıları incelenmeli, telifli tam metin/görsel kopyalanmadığı doğrulanmalı ve gerekiyorsa düzeltme/cevap veya kaldırma süreci için kayıt açılmalıdır.

Onaylanan kayıtta `yayin_durumu` alanı `yayinda` yapılır ve değişiklik commit edilir. Bu işlemi karar iziyle yapmak için kayıt ID’sini dashboard verisinden alıp şu komutu kullanabilirsiniz:

```bash
python scripts/set_status.py --id "KAYIT_ID" --status yayinda --editor "Editör Adı" --note "Kaynak kontrol edildi; başlık ve özet onaylandı."
```

Yayından kaldırma veya yeniden incelemeye alma da aynı yardımcı betikle yapılabilir. Otomatik tarama, yayınlanmış kaydı URL’si üzerinden korur; ancak başlık, özet ve güncellik değişiklikleri yeniden editoryal kontrolden geçirilmelidir. Uyarılı bir kayıt için yalnızca uyarıyı görmezden gelmek yerine gerekçe ve editör notu eklenmesi tavsiye edilir.

## Hukuki kullanım sınırı

Bu proje hukuki danışmanlık veya otomatik hukuki uygunluk garantisi vermez. 5187 sayılı Basın Kanunu, 5651 sayılı internet yayınları mevzuatı, 6698 sayılı KVKK ve 5846 sayılı FSEK yönünden yayıncı tarafından güncel uzman incelemesi yapılmalıdır. Özellikle çocuklar, suç isnadı, soruşturma, sağlık verisi, sınav sonuçları, iletişim bilgileri ve fotoğraflar otomatik yayına bırakılmamalıdır. Ayrıntılı çalışma taslağı `LEGAL_EDITORIAL_POLICY.md` dosyasındadır.

## Katkı ve geri alma

Veri güncellemeleri ve editoryal değişiklikler normal Git commit’leriyle izlenir. Hatalı bir yayın için önce kaydı `yayindan_kaldirildi` veya `inceleme_bekliyor` durumuna çekin, ardından düzeltme/kaldırma talebini ve alınan kararı ayrı bir editoryal notla saklayın. İş akışının oluşturduğu günlük snapshot, değişikliklerin geriye dönük denetimini kolaylaştırır.

## Kaynaklar

[1]: https://mevzuat.adalet.gov.tr/mevzuat/103226?query=Madde%205 "5187 sayılı Basın Kanunu — UYAP Mevzuat"
[2]: https://www.resmigazete.gov.tr/eskiler/2007/05/20070523-1.htm "5651 sayılı Kanun — Resmî Gazete"
[3]: https://www.kvkk.gov.tr/Icerik/7179/2022-13 "KVKK Kurulu 2022/13 karar özeti"
[4]: https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=5846&MevzuatTur=1&MevzuatTertip=3 "5846 sayılı Fikir ve Sanat Eserleri Kanunu — Mevzuat Bilgi Sistemi"
