# Sivil Dünya Haber — Editoryal ve Hukuki Uyum Taslağı

> **Uyarı:** Bu belge hukuki danışmanlık değildir. Yayın öncesinde Türkiye’de basın, internet, kişisel veri ve fikrî mülkiyet alanlarında yetkin bir avukat tarafından; sitenin gerçek işletmecisi, yayın türü, kullanılan altyapı, reklam modeli ve içerik kapsamı dikkate alınarak gözden geçirilmelidir.

## Amaç

Bu belge, haber.sivildunya.com üzerinde resmî kaynaklardan aday kayıt toplayan otomatik akışın **otomatik olarak hukuka uygun olduğu varsayımını engellemek** için hazırlanmıştır. Teknik sistem, kaynak bağlantısı ve kişisel veri sinyali gibi kontrolleri destekler; yayın kararı ve sorumluluk yayıncı ile sorumlu editör/müdür üzerindedir.

## Uygulama ilkeleri

| Kontrol alanı | Uygulamadaki kural | Editörün onay sorusu |
| --- | --- | --- |
| Kaynak | Sadece `update_script.py` içindeki resmî alan adı allowlist’inden geçen doğrudan bağlantılar aday yapılır. | URL gerçekten kurumun yetkili alan adına mı ait ve içerik güncel mi? |
| Gerçeklik ve güncellik | Kaynak başlığı, kaynak tarihi ve güncelleme zamanı ayrı alanlarda saklanır. | Başlık/özet kaynakta açıkça doğrulanabiliyor mu? |
| Yayın durumu | Yeni kayıt `inceleme_bekliyor`; `yayinda` yapılmadıkça kamu akışına ve RSS’e girmez. | Kayıt yayınlanacak kadar incelendi mi, yoksa sadece aday mı? |
| Kişisel veri | T.C. kimlik numarası, telefon, e-posta, IBAN ve hassas alan sinyalleri taranır; uyarı yayın engeli olarak ele alınır. | Kişisel veri gerekli mi, hukuki dayanak ve kamu yararı var mı, anonimleştirme mümkün mü? |
| Çocuklar ve mağdurlar | Çocuk veya mağdurun tanınmasına yol açabilecek bilgi ve görseller otomatik yayımlanmaz. | Kimlik belirlenebilir mi; yayın kamu yararına rağmen ölçülü mü? |
| Telif | Kaynak metni/görseli kopyalanmaz; özgün kısa özet ve kaynak linki kullanılır. | Görsel/metin kullanım hakkı veya açık izin var mı; alıntı ölçülü mü? |
| Düzeltme/cevap | Yanlış veya kişilik hakkına dokunan içerik için talep kaydı ve hızlı düzeltme süreci tutulur. | Talep alındı mı, sorumlu kişi ve süre kayda girdi mi? |
| Saklama | Üretilen günlük JSON snapshotları ve yayınlanan kayıtlar doğruluk/bütünlük amacıyla saklanır. | Kayıtların değişmezliği, erişim yetkisi ve saklama süresi nasıl korunuyor? |
| İletişim | `data/site-config.json` içinde yayıncı, adres, e-posta, telefon, elektronik tebligat, yer sağlayıcı ve sorumlu editör bilgileri tutulur. | Zorunlu bilgiler ana sayfadan erişilebilir ve güncel mi? |

## Yayın öncesi minimum kontrol

Editör, aday kaydın kaynak URL’sini tarayıcıda açmalı ve başlık ile özetin kaynağı doğru yansıtıp yansıtmadığını kontrol etmelidir. Aday yalnızca bir ana sayfa, yardım sayfası, giriş ekranı veya konu dışı bağlantıysa yayımlanmamalıdır. Kaynakta tarih bulunmuyorsa özet, kesin tarih veya son başvuru tarihi iddiası içermemelidir.

Kaydın metninde bir kişinin adı, fotoğrafı, puanı, kimlik numarası, iletişim bilgisi, sağlık/adli durum bilgisi veya çocuğu belirleyebilecek ayrıntılar varsa kayıt uyarılı kabul edilir. Bu tür veriler gerekli değilse çıkarılmalı; gerekiyorsa anonimleştirme, hukuki dayanak, kamu yararı ve ölçülülük ayrı ayrı belgelenmeden yayın kararı verilmemelidir. KVKK Kurulu’nun yerel haber sitesindeki sınav sonuç belgesi karar özeti, basın özgürlüğünün tek başına sınırsız bir yayın yetkisi olmadığını ve kamu yararı ile ölçülülüğün değerlendirilmesi gerektiğini gösteren önemli bir örnektir [3].

Başkasına ait haber metni, fotoğraf, logo, PDF veya ekran görüntüsü tam olarak kopyalanmamalıdır. Kısa ve özgün bir anlatım, açık kaynak bağlantısı ve gerekiyorsa lisans/izin bilgisi kullanılmalıdır. FSEK yönünden alıntı sınırları, görsel lisansı ve kurum sitelerinin kullanım şartları ayrıca kontrol edilmelidir [4].

## Sorumluluk ve site bilgileri

5187 sayılı Basın Kanunu internet haber sitelerini kapsamına alır. Resmî metin, internet haber sitelerinde iş yeri adresi, ticari unvan, elektronik posta, iletişim telefonu, elektronik tebligat adresi ve yer sağlayıcısı bilgilerinin iletişim başlığı altında kullanıcıların ana sayfadan doğrudan ulaşabileceği şekilde bulunmasını; ilk sunum ve güncelleme tarihlerinin gösterilmesini; içeriklerin doğruluğu ve bütünlüğü sağlanmış biçimde saklanmasını düzenler [1]. Bu alanlar gerçek bilgilerle doldurulmadan siteyi mevzuata tam uyumlu kabul etmeyin.

5651 sayılı Kanun, içerik sağlayıcının kendi sunduğu içerikten sorumluluğunu ve başkasına ait içeriğe bağlantı verilmesi bakımından bağlantının sunuluş biçiminin önemini düzenler [2]. Bu nedenle arayüzde “kaynak” ile Sivil Dünya Haber’in kendi özeti görsel ve metin bakımından ayrıştırılmıştır; bu teknik ayrım, somut olay değerlendirmesinin yerine geçmez.

## Düzeltme, kaldırma ve olay kaydı

Yanlışlık veya kişilik hakkı iddiası geldiğinde talebin geliş zamanı, ilgili URL, talep sahibi, iddia edilen hata, alınan geçici tedbir ve sorumlu editör kayda alınmalıdır. Yayın durumu gerekirse `inceleme_bekliyor` veya `yayindan_kaldirildi` olarak değiştirilmelidir. Düzeltme veya cevap yayımlanacaksa metin, talep ve karar kayıtlarıyla birlikte saklanmalıdır. Kanundaki güncel süre ve usul, somut olay ve içeriğin niteliğine göre avukat tarafından doğrulanmalıdır.

## Teknik sınırlılıklar

Otomatik tarama, HTML yapısının değişmesi, bot koruması, 403/5xx yanıtı, JavaScript ile yüklenen içerik veya yanlış yönlendirme nedeniyle eksik kalabilir. `data/audit.json` içindeki kaynak sağlık durumu yalnızca teknik erişimi gösterir; erişilebilir bir sayfanın hukuken veya editoryal olarak yayınlanabilir olduğu anlamına gelmez.

Yapay zekâ ile daha uzun özet veya haber metni üretilecekse model çıktısı doğrudan yayımlanmamalı; kaynak metni ile karşılaştırmalı editoryal kontrol, kişisel veri maskeleme, belirsizlik dili ve insan onayı zorunlu olmalıdır. Otomatik sistem kesin suç isnadı, kesin sonuç, sağlık teşhisi, hukuki hüküm veya garanti dili üretmemelidir.

## Referanslar

[1]: https://mevzuat.adalet.gov.tr/mevzuat/103226?query=Madde%205 "5187 sayılı Basın Kanunu — UYAP Mevzuat"
[2]: https://www.resmigazete.gov.tr/eskiler/2007/05/20070523-1.htm "5651 sayılı Kanun — Resmî Gazete"
[3]: https://www.kvkk.gov.tr/Icerik/7179/2022-13 "KVKK Kurulu 2022/13 karar özeti"
[4]: https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=5846&MevzuatTur=1&MevzuatTertip=3 "5846 sayılı Fikir ve Sanat Eserleri Kanunu — Mevzuat Bilgi Sistemi"
