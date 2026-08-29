import os,re,json,html,hashlib,requests
from pathlib import Path
from datetime import datetime,timezone
from email.utils import format_datetime
SITE_URL="https://haber.sivildunya.com"; DATA=Path("data/duyurular.json"); RSS=Path("rss.xml"); MAX=100
CATS={"kamusal_duyurular":"Kamusal Duyurular","kamu_personeli_alimleri":"Kamu Personeli Alımları","dernek_ve_stk_gelismeleri":"Dernek ve STK Gelişmeleri"}
def now(): return datetime.now(timezone.utc)
def today(): return now().date().isoformat()
def clean(x): return re.sub(r"\s+"," ",str(x or "")).strip()
def slug(x): return re.sub(r"[^a-z0-9]+","-",x.lower().translate(str.maketrans("çğıöşüâîû","cgiosuaiu"))).strip("-")[:80] or "duyuru"
def mid(t,c,u): return slug(t)+"-"+hashlib.sha256(f"{c}|{t}|{u}".encode()).hexdigest()[:10]
def norm(i):
 c=clean(i.get("category")); c=c if c in CATS else "kamusal_duyurular"; t=clean(i.get("title")) or "Güncel Duyuru"; u=clean(i.get("source_url") or i.get("url") or SITE_URL); u=u if u.startswith("http") else SITE_URL
 tags=i.get("tags",[]); tags=tags if isinstance(tags,list) else []
 return {"id":clean(i.get("id")) or mid(t,c,u),"category":c,"title":t[:180],"summary":clean(i.get("summary") or i.get("description"))[:500] or "Ayrıntılar için resmi kaynak bağlantısını kontrol ediniz.","source_name":clean(i.get("source_name") or i.get("source") or "Resmi Kaynak")[:120],"source_url":u,"tags":[clean(x) for x in tags if clean(x)][:8],"date":clean(i.get("date")) or today(),"importance":clean(i.get("importance") or "normal") if clean(i.get("importance") or "normal") in ["low","normal","high"] else "normal","created_at":clean(i.get("created_at")) or now().isoformat()}
def seed():
 d=today(); return [norm({"category":"kamusal_duyurular","title":"Kamusal Duyurular Günlük Bülteni","summary":"Kamu kurumları tarafından yayımlanan genel duyurular ve bilgilendirmeler takip edilmelidir.","source_name":"Resmî Gazete","source_url":"https://www.resmigazete.gov.tr/","tags":["kamusal duyuru","resmi kaynak"],"date":d}),norm({"category":"kamu_personeli_alimleri","title":"Kamu Personeli Alım İlanları Takibi","summary":"Kamu kurumlarının personel alımı ilanları resmi kanallardan düzenli kontrol edilmelidir.","source_name":"Kamu İlanları","source_url":"https://www.resmigazete.gov.tr/","tags":["personel alımı","kamu"],"date":d,"importance":"high"}),norm({"category":"dernek_ve_stk_gelismeleri","title":"Dernek ve STK Gelişmeleri Bülteni","summary":"Dernekler, vakıflar ve STK alanındaki hibe, proje ve mevzuat gelişmeleri takip edilmelidir.","source_name":"Sivil Toplumla İlişkiler Genel Müdürlüğü","source_url":"https://www.siviltoplum.gov.tr/","tags":["stk","dernek","hibe"],"date":d})]
def existing():
 try: return [norm(x) for x in json.loads(DATA.read_text(encoding="utf-8"))]
 except Exception: return []
def extract(s):
 m=re.search(r"```(?:json)?\s*(.*?)```",s,re.S|re.I); s=m.group(1) if m else s; m=re.search(r"\[\s*{.*}\s*\]",s,re.S); return json.loads(m.group(0) if m else s)
def gemini():
 key=os.getenv("GEMINI_API_KEY",""); model=os.getenv("GEMINI_MODEL","gemini-1.5-flash")
 if not key: return seed()
 prompt=f"Bugünün tarihi {today()}. Türkiye odaklı kamusal_duyurular, kamu_personeli_alimleri, dernek_ve_stk_gelismeleri kategorilerinde 9-12 güvenli bülten üret. Kesin başvuru tarihi/kontenjan uydurma. Resmi source_url kullan. Sadece JSON array döndür. Alanlar: category,title,summary,source_name,source_url,tags,date,importance."
 try:
  r=requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}",json={"contents":[{"parts":[{"text":prompt}]}],"generationConfig":{"temperature":0.35,"maxOutputTokens":4096}},timeout=60); r.raise_for_status(); txt=r.json()["candidates"][0]["content"]["parts"][0]["text"]; return [norm(x) for x in extract(txt)]
 except Exception as e:
  print("Gemini hatası:",e); return seed()
def rss(items):
 out=[]
 for i in items[:50]:
  try: dt=datetime.fromisoformat(i["date"]).replace(tzinfo=timezone.utc)
  except Exception: dt=now()
  out.append(f"<item><title>{html.escape(i['title'])}</title><link>{SITE_URL}/#duyuru-{html.escape(i['id'])}</link><guid isPermaLink='false'>{html.escape(i['id'])}</guid><pubDate>{format_datetime(dt)}</pubDate><category>{html.escape(CATS.get(i['category'],i['category']))}</category><description>{html.escape(i['summary'])}</description><source url='{html.escape(i['source_url'])}'>{html.escape(i['source_name'])}</source></item>")
 RSS.write_text(f"<?xml version='1.0' encoding='UTF-8'?><rss version='2.0'><channel><title>Sivil Dünya Haber Bülteni</title><link>{SITE_URL}</link><description>Kamu ve sivil toplum bülteni</description><language>tr-TR</language><lastBuildDate>{format_datetime(now())}</lastBuildDate>{''.join(out)}</channel></rss>",encoding="utf-8")
def main():
 seen=set(); items=[]
 for x in gemini()+existing():
  n=norm(x); fp=n['id']
  if fp not in seen: seen.add(fp); items.append(n)
 items=sorted(items,key=lambda x:(x['date'],x['created_at']),reverse=True)[:MAX]; DATA.parent.mkdir(exist_ok=True); DATA.write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding="utf-8"); rss(items)
if __name__=="__main__": main()
