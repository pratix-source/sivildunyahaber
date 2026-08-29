import json, os, requests, html
from pathlib import Path
from datetime import datetime, timezone
DATA=Path('data/duyurular.json'); RSS=Path('rss.xml'); SITE='https://haber.sivildunya.com'
def today(): return datetime.now(timezone.utc).date().isoformat()
def load():
    return json.loads(DATA.read_text('utf-8')) if DATA.exists() else {"platform":"haber.sivildunya.com","tarih":today(),"kategoriler":{}}
def rss(data):
    items=[]
    for cat, arr in data.get('kategoriler',{}).items():
        for i,x in enumerate(arr[:10]):
            title=x.get('baslik') or x.get('kurum','Duyuru'); desc=x.get('ozet') or ' · '.join(filter(None,[x.get('kadro'),x.get('basvuru_tarihleri'),x.get('mecra')]))
            items.append(f'<item><title>{html.escape(title)}</title><link>{SITE}/</link><guid>{cat}-{i}-{data.get("tarih")}</guid><description>{html.escape(desc)}</description><category>{cat}</category></item>')
    RSS.write_text('<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Sivil Dünya Haberler</title><link>'+SITE+'</link><description>Güncel duyurular</description>'+''.join(items)+'</channel></rss>',encoding='utf-8')
def main():
    data=load(); data['platform']='haber.sivildunya.com'; data['tarih']=today()
    DATA.parent.mkdir(exist_ok=True); DATA.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8'); rss(data)
if __name__=='__main__': main()
