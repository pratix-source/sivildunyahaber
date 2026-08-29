import json, datetime, os
from urllib.parse import urlparse
DOMAIN="haber.sivildunya.com"
SAFE_SOURCES=[
("kamusal_duyurular","Resmî Gazete Günlük Sayısı","https://www.resmigazete.gov.tr/"),
("personel_alimi","Kamu İlanları Resmî Duyuru Ekranı","https://kamuilan.sbb.gov.tr/"),
("kamu_personeli_alimleri","Kariyer Kapısı Kamu İşe Alım İlanları","https://kariyerkapisi.gov.tr/isealim"),
("akademik_personel","YÖK Akademik Duyurular","https://www.yok.gov.tr/tr/announcements"),
("sinav","ÖSYM Duyuruları","https://www.osym.gov.tr/Duyurular/Index"),
("sivil_toplum","Sivil Toplumla İlişkiler Genel Müdürlüğü","https://www.siviltoplum.gov.tr/haberler")]
CATS=["kamusal_duyurular","kamu_personeli_alimleri","dernek_ve_stk_gelismeleri","gundem","personel_alimi","akademik_personel","sinav","tayin","kamu_personeli","egitim_burs","sivil_toplum","destekler"]
def valid(u):
    try: p=urlparse(u); return p.scheme in ('http','https') and bool(p.netloc)
    except Exception: return False
def main():
    d={"platform":DOMAIN,"site_url":"https://"+DOMAIN,"tarih":datetime.date.today().isoformat(),"kategoriler":{k:[] for k in CATS}}
    for cat,title,url in SAFE_SOURCES:
        if valid(url): d['kategoriler'][cat].append({"baslik":title,"ozet":"Bu kayıt doğrulanabilir resmî kaynak bağlantısı olarak sunulur. Detay linki bulunmadan içerik uydurulmaz.","kaynak_adi":title,"kaynak_url":url,"dogrulama_durumu":"genel_kaynak"})
    os.makedirs('data',exist_ok=True)
    open('data/duyurular.json','w',encoding='utf-8').write(json.dumps(d,ensure_ascii=False,indent=2))
    items=[]
    for arr in d['kategoriler'].values(): items+=arr
    rss=['<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel>',f'<title>Sivil Dünya Haber</title><link>https://{DOMAIN}</link><description>Doğrulanabilir kaynaklı bülten</description>']
    for x in items: rss.append(f"<item><title>{x['baslik']}</title><link>{x['kaynak_url']}</link><description>{x['ozet']}</description></item>")
    rss.append('</channel></rss>')
    open('rss.xml','w',encoding='utf-8').write('\n'.join(rss))
if __name__=='__main__': main()
