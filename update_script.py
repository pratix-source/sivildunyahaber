import json, datetime, os, re, urllib.parse
from xml.sax.saxutils import escape
try:
    import requests
    from bs4 import BeautifulSoup
except Exception:
    requests = None
    BeautifulSoup = None
DOMAIN='haber.sivildunya.com'; SITE='https://'+DOMAIN
SOURCES=[
 {'ad':'Resmî Gazete','url':'https://www.resmigazete.gov.tr/','kategori':'kamusal_duyurular'},
 {'ad':'Kamu İlan','url':'https://kamuilan.sbb.gov.tr/','kategori':'kamu_personeli_alimleri'},
 {'ad':'Kariyer Kapısı','url':'https://kariyerkapisi.gov.tr/isealim','kategori':'personel_alimi'},
 {'ad':'YÖK Akademik İlanlar','url':'https://www.yok.gov.tr/tr/announcements','kategori':'akademik_personel'},
 {'ad':'ÖSYM Duyurular','url':'https://osym.gov.tr/Duyurular/Index','kategori':'sinav'},
 {'ad':'MEB Duyurular','url':'https://mebsonuc.meb.gov.tr/','kategori':'egitim_burs'},
 {'ad':'Sivil Toplumla İlişkiler','url':'https://www.siviltoplum.gov.tr/haberler','kategori':'sivil_toplum'},
 {'ad':'AB Başkanlığı Duyurular','url':'https://www.ab.gov.tr/42.html','kategori':'destekler'},]
CATS=['kamusal_duyurular','kamu_personeli_alimleri','dernek_ve_stk_gelismeleri','gundem','personel_alimi','akademik_personel','sinav','tayin','kamu_personeli','egitim_burs','sivil_toplum','destekler']
def clean(s): return re.sub(r'\s+',' ',s or '').strip()
def valid(u):
    try: return urllib.parse.urlparse(u).scheme in ('http','https')
    except Exception: return False
def fetch_source(src, limit=5):
    if not requests or not BeautifulSoup: return []
    out=[]
    try:
        r=requests.get(src['url'],timeout=15,headers={'User-Agent':'Mozilla/5.0'})
        r.raise_for_status(); soup=BeautifulSoup(r.text,'html.parser')
        base=r.url
        for a in soup.find_all('a',href=True):
            t=clean(a.get_text(' ')); href=urllib.parse.urljoin(base,a['href'])
            if len(t)<12 or not valid(href): continue
            if href.rstrip('/')==src['url'].rstrip('/'): continue
            out.append({'baslik':t[:180],'ozet':'Bu kayıt resmî kaynaktan bağlantı ile alınmıştır. Ayrıntılar için bağlantıyı açın.','kaynak_adi':src['ad'],'kaynak_url':href,'dogrulama_durumu':'dogrulanmis','detay_linki':True})
            if len(out)>=limit: break
    except Exception as e:
        print('Kaynak okunamadı:',src['ad'],e)
    return out
def main():
    data={'platform':DOMAIN,'site_url':SITE,'tarih':datetime.date.today().isoformat(),'kategoriler':{c:[] for c in CATS},'kaynaklar':SOURCES}
    seen=set()
    for s in SOURCES:
        for it in fetch_source(s):
            if it['kaynak_url'] in seen: continue
            seen.add(it['kaynak_url']); data['kategoriler'][s['kategori']].append(it)
    os.makedirs('data',exist_ok=True)
    open('data/duyurular.json','w',encoding='utf-8').write(json.dumps(data,ensure_ascii=False,indent=2))
    items=[]
    for arr in data['kategoriler'].values(): items+=arr
    rss='<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Sivil Dünya Haber</title><link>'+SITE+'</link><description>Doğrulanabilir kaynaklı bülten</description>'
    for it in items[:50]: rss+='<item><title>'+escape(it['baslik'])+'</title><link>'+escape(it['kaynak_url'])+'</link><description>'+escape(it.get('ozet',''))+'</description></item>'
    rss+='</channel></rss>'; open('rss.xml','w',encoding='utf-8').write(rss)
if __name__=='__main__': main()
