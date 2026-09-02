from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import re
import urllib.parse
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup

DOMAIN = "haber.sivildunya.com"
SITE = f"https://{DOMAIN}"
ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
ARCHIVE_DIR = DATA_DIR / "archive"
MAX_PER_SOURCE = int(os.getenv("MAX_PER_SOURCE", "8"))
TIMEOUT = int(os.getenv("SOURCE_TIMEOUT", "20"))

CATEGORIES = [
    "kamusal_duyurular",
    "kamu_personeli_alimleri",
    "dernek_ve_stk_gelismeleri",
    "gundem",
    "personel_alimi",
    "akademik_personel",
    "sinav",
    "tayin",
    "kamu_personeli",
    "egitim_burs",
    "sivil_toplum",
    "destekler",
]

SOURCES = [
    {
        "ad": "Resmî Gazete",
        "url": "https://www.resmigazete.gov.tr/",
        "kategori": "kamusal_duyurular",
        "allowed_hosts": ["resmigazete.gov.tr", "www.resmigazete.gov.tr"],
    },
    {
        "ad": "Kamu İlan",
        "url": "https://kamuilan.sbb.gov.tr/",
        "kategori": "kamu_personeli_alimleri",
        "allowed_hosts": ["kamuilan.sbb.gov.tr"],
    },
    {
        "ad": "Kariyer Kapısı",
        "url": "https://kariyerkapisi.gov.tr/isealim",
        "kategori": "personel_alimi",
        "allowed_hosts": ["kariyerkapisi.gov.tr", "www.kariyerkapisi.gov.tr"],
    },
    {
        "ad": "YÖK Akademik İlanlar",
        "url": "https://www.yok.gov.tr/tr/announcements",
        "kategori": "akademik_personel",
        "allowed_hosts": ["yok.gov.tr", "www.yok.gov.tr"],
    },
    {
        "ad": "ÖSYM Duyurular",
        "url": "https://osym.gov.tr/Duyurular/Index",
        "kategori": "sinav",
        "allowed_hosts": ["osym.gov.tr", "www.osym.gov.tr", "dokuman.osym.gov.tr"],
    },
    {
        "ad": "MEB Duyurular",
        "url": "https://mebsonuc.meb.gov.tr/",
        "kategori": "egitim_burs",
        "allowed_hosts": ["meb.gov.tr", "www.meb.gov.tr", "mebsonuc.meb.gov.tr"],
    },
    {
        "ad": "Sivil Toplumla İlişkiler",
        "url": "https://www.siviltoplum.gov.tr/haberler",
        "kategori": "sivil_toplum",
        "allowed_hosts": ["siviltoplum.gov.tr", "www.siviltoplum.gov.tr", "icisleri.gov.tr", "www.icisleri.gov.tr"],
    },
    {
        "ad": "AB Başkanlığı Duyurular",
        "url": "https://www.ab.gov.tr/42.html",
        "kategori": "destekler",
        "allowed_hosts": ["ab.gov.tr", "www.ab.gov.tr"],
    },
]

CATEGORY_LABELS = {
    "kamusal_duyurular": "Kamusal Duyurular",
    "kamu_personeli_alimleri": "Kamu Personeli Alımları",
    "dernek_ve_stk_gelismeleri": "Dernek ve STK Gelişmeleri",
    "gundem": "Gündem",
    "personel_alimi": "Personel Alımı",
    "akademik_personel": "Akademik Personel",
    "sinav": "Sınav",
    "tayin": "Tayin",
    "kamu_personeli": "Kamu Personeli",
    "egitim_burs": "Eğitim-Burs",
    "sivil_toplum": "Sivil Toplum",
    "destekler": "Destekler",
}

SKIP_TERMS = {
    "ana sayfa",
    "anasayfa",
    "giriş",
    "login",
    "şifremi unuttum",
    "sıkça sorulan sorular",
    "iletişim",
    "kvkk",
    "misyon ve vizyon",
    "yürütme kurulu",
    "denetleme kurulu",
    "önceki başkanlar",
    "allaboutcookies",
    "çerez",
    "english",
    "deutsch",
    "facebook",
    "instagram",
    "twitter",
}

PII_PATTERNS = [
    ("tc_kimlik_no", re.compile(r"(?<!\d)\d{11}(?!\d)")),
    ("telefon", re.compile(r"(?<!\d)(?:\+?90|0)?\s?5\d{2}[\s.-]?\d{3}[\s.-]?\d{2}[\s.-]?\d{2}(?!\d)")),
    ("e_posta", re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b")),
    ("iban", re.compile(r"\bTR\d{2}[A-Z0-9]{20,32}\b", re.I)),
]
SENSITIVE_TERMS = {
    "sağlık verisi",
    "engellilik",
    "cinsel saldırı",
    "cinsel suç",
    "çocuk mağdur",
    "reşit olmayan",
    "t.c. kimlik",
    "tc kimlik",
    "adli sicil",
    "soruşturma",
    "tutuklandı",
    "gözaltına alındı",
}

SESSION = requests.Session()
SESSION.headers.update(
    {
        "User-Agent": "SivilDunyaHaber/2.0 (+https://haber.sivildunya.com; public-source-reader)",
        "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.7",
    }
)


def clean(value: str | None) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def safe_url(value: str | None) -> str | None:
    try:
        parsed = urllib.parse.urlparse((value or "").strip())
    except ValueError:
        return None
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None
    return urllib.parse.urlunparse(parsed._replace(fragment=""))


def same_url(left: str, right: str) -> bool:
    return (safe_url(left) or "").rstrip("/") == (safe_url(right) or "").rstrip("/")


def host_allowed(url: str, source: dict[str, Any]) -> bool:
    host = (urllib.parse.urlparse(url).hostname or "").lower()
    return any(host == item or host.endswith("." + item) for item in source["allowed_hosts"])


def fetch(url: str) -> tuple[str, str, int]:
    response = SESSION.get(url, timeout=TIMEOUT, allow_redirects=True)
    response.raise_for_status()
    response.encoding = response.encoding or "utf-8"
    return response.text, response.url, response.status_code


def soup_text(soup: BeautifulSoup) -> str:
    clone = BeautifulSoup(str(soup), "html.parser")
    for node in clone(["script", "style", "noscript", "svg", "nav", "footer", "header", "form", "aside"]):
        node.decompose()
    preferred = clone.find_all(["article", "main"])
    text = " ".join(node.get_text(" ", strip=True) for node in preferred)
    if len(text) < 180:
        text = clone.get_text(" ", strip=True)
    return clean(text)


def find_title(soup: BeautifulSoup, fallback: str) -> str:
    # Kurum sitelerinde H1 bazen yalnızca kurum adıdır; sayfa başlığı/OG başlığı haber başlığına daha yakındır.
    candidates: list[str] = []
    for selector in ["meta[property='og:title']", "meta[name='twitter:title']", "title", "article h1", ".news-title", ".announcement-title", "h1"]:
        for node in soup.select(selector):
            value = node.get("content") if node.name == "meta" else node.get_text(" ", strip=True)
            value = clean(value)
            if value:
                candidates.append(value)
    fallback = clean(fallback)
    institution_only = {
        "t.c. ölçme, seçme ve yerleştirme merkezi başkanlığı",
        "ölçme, seçme ve yerleştirme merkezi başkanlığı",
        "t.c. millî eğitim bakanlığı",
        "t.c. yükseköğretim kurulu başkanlığı",
    }
    for raw_value in candidates:
        value = re.split(r"\s*[|•–—]\s*", raw_value, maxsplit=1)[0].strip()
        if len(value) >= 12 and value.lower() not in institution_only:
            return value[:220]
    return fallback[:220] or "Resmî duyuru"


def find_date(soup: BeautifulSoup) -> str | None:
    for node in soup.select("time[datetime], meta[property='article:published_time'], meta[name='date'], meta[name='datePublished']"):
        value = clean(node.get("datetime") or node.get("content"))
        parsed = normalize_date(value)
        if parsed:
            return parsed
    return normalize_date(soup.get_text(" ", strip=True))


def normalize_date(value: str | None) -> str | None:
    text = clean(value)
    patterns = [
        (r"(20\d{2})[-/.](\d{1,2})[-/.](\d{1,2})", "%Y-%m-%d"),
        (r"(\d{1,2})[-/.](\d{1,2})[-/.](20\d{2})", "%d.%m.%Y"),
    ]
    for pattern, input_format in patterns:
        match = re.search(pattern, text)
        if match:
            raw = match.group(0).replace("/", ".")
            try:
                if input_format == "%Y-%m-%d":
                    parts = re.split(r"[-/.]", raw)
                    return dt.date(int(parts[0]), int(parts[1]), int(parts[2])).isoformat()
                return dt.datetime.strptime(raw, input_format).date().isoformat()
            except ValueError:
                continue
    months = {"ocak": 1, "şubat": 2, "mart": 3, "nisan": 4, "mayıs": 5, "haziran": 6, "temmuz": 7, "ağustos": 8, "eylül": 9, "ekim": 10, "kasım": 11, "aralık": 12}
    match = re.search(r"(\d{1,2})\s+([a-zçğıöşü]+)\s+(20\d{2})", text.lower())
    if match and match.group(2) in months:
        try:
            return dt.date(int(match.group(3)), months[match.group(2)], int(match.group(1))).isoformat()
        except ValueError:
            pass
    return None


def candidate_links(soup: BeautifulSoup, base_url: str, source: dict[str, Any]) -> list[tuple[int, str, str]]:
    results: dict[str, tuple[int, str]] = {}
    for anchor in soup.find_all("a", href=True):
        text = clean(anchor.get_text(" "))
        url = safe_url(urllib.parse.urljoin(base_url, anchor["href"]))
        if not url or not text or len(text) < 12 or not host_allowed(url, source):
            continue
        if same_url(url, source["url"]):
            continue
        lowered = text.lower()
        if any(term in lowered for term in SKIP_TERMS):
            continue
        path = urllib.parse.urlparse(url).path.lower()
        score = 0
        for term in ("duyuru", "haber", "ilan", "announcement", "news", "detay", "detail", "başvuru", "sınav", "personel", "destek"):
            if term in lowered or term in path:
                score += 3
        if anchor.find_parent("nav"):
            score -= 8
        if len(text) > 20:
            score += 1
        if score < 1:
            continue
        existing = results.get(url)
        if not existing or score > existing[0]:
            results[url] = (score, text[:220])
    return sorted(((score, url, text) for url, (score, text) in results.items()), reverse=True)


def sentences(text: str, limit: int = 2) -> list[str]:
    text = clean(text)
    if not text:
        return []
    chunks = re.split(r"(?<=[.!?])\s+", text)
    return [chunk.strip() for chunk in chunks if len(chunk.strip()) > 35][:limit]


def scan_risk(text: str) -> list[str]:
    lowered = text.lower()
    flags = [name for name, pattern in PII_PATTERNS if pattern.search(text)]
    flags.extend(f"hassas_alan:{term}" for term in sorted(SENSITIVE_TERMS) if term in lowered)
    return sorted(set(flags))


def redacted_summary(title: str, body: str, source_name: str) -> tuple[str, list[str]]:
    raw = " ".join(sentences(body, 2))
    if not raw:
        raw = f"{source_name} kaynağında “{title}” başlıklı resmî kayıt yer alıyor. Ayrıntılar ve varsa başvuru koşulları için kaynak bağlantısı incelenmelidir."
    risk_flags = scan_risk(f"{title} {raw}")
    summary = raw[:520].rstrip()
    for _, pattern in PII_PATTERNS:
        summary = pattern.sub("[kişisel veri gizlendi]", summary)
    return summary, risk_flags


def slug_for(title: str, url: str) -> str:
    raw = clean(title).lower()
    raw = re.sub(r"[^a-z0-9çğıöşüİÇĞÖŞÜ]+", "-", raw, flags=re.I).strip("-")
    digest = hashlib.sha1(url.encode("utf-8")).hexdigest()[:8]
    return f"{raw[:80] or 'duyuru'}-{digest}"


def load_site_config() -> dict[str, Any]:
    path = DATA_DIR / "site-config.json"
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {
        "site_name": "Sivil Dünya Haber",
        "domain": DOMAIN,
        "publisher_name": "",
        "business_address": "",
        "trade_name": "",
        "email": "",
        "phone": "",
        "electronic_notification_address": "",
        "hosting_provider_name": "",
        "hosting_provider_address": "",
        "responsible_editor": "",
        "privacy_email": "",
    }


def load_existing() -> dict[str, Any]:
    path = DATA_DIR / "duyurular.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def make_item(source: dict[str, Any], candidate_url: str, anchor_title: str, detail_html: str | None, detail_url: str | None) -> dict[str, Any]:
    detail_soup = BeautifulSoup(detail_html or "", "html.parser")
    title = find_title(detail_soup, anchor_title)
    final_url = detail_url or candidate_url
    body = soup_text(detail_soup)
    published_date = find_date(detail_soup)
    summary, risk_flags = redacted_summary(title, body, source["ad"])
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    item = {
        "id": slug_for(title, final_url),
        "baslik": title,
        "ozet": summary,
        "kategori": source["kategori"],
        "kaynak_adi": source["ad"],
        "kaynak_url": final_url,
        "kaynak_host": urllib.parse.urlparse(final_url).hostname,
        "kaynak_tarihi": published_date,
        "ilk_yayin_tarihi": now,
        "guncellenme_tarihi": now,
        "yayin_durumu": "inceleme_bekliyor",
        "dogrulama_durumu": "resmî_alan_adı_kontrol_edildi",
        "detay_linki": True,
        "editoryal_kontrol": {
            "kaynak_allowlist": True,
            "dogrudan_kaynak": True,
            "kisisel_veri_taramasi": "uyarı" if risk_flags else "temiz",
            "telif_uygulamasi": "tam_metin_ve_gorsel_kopyalanmadi",
            "manuel_onay_gerekli": True,
            "riskler": risk_flags,
        },
    }
    return item


def collect_source(source: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    health: dict[str, Any] = {"ad": source["ad"], "url": source["url"], "durum": "başarısız", "http_status": None, "aday": 0, "hata": None}
    items: list[dict[str, Any]] = []
    try:
        source_html, source_final_url, status = fetch(source["url"])
        health["http_status"] = status
        source_soup = BeautifulSoup(source_html, "html.parser")
        links = candidate_links(source_soup, source_final_url, source)
        for _, url, text in links[:MAX_PER_SOURCE]:
            try:
                detail_html, detail_final_url, _ = fetch(url)
                if not host_allowed(detail_final_url, source):
                    continue
                items.append(make_item(source, url, text, detail_html, detail_final_url))
            except Exception:
                item = make_item(source, url, text, None, url)
                items.append(item)
        health["durum"] = "başarılı"
        health["aday"] = len(items)
    except Exception as exc:
        health["hata"] = str(exc)[:240]
    return items, health


def merge_items(new_items: list[dict[str, Any]], existing: dict[str, Any]) -> list[dict[str, Any]]:
    by_url: dict[str, dict[str, Any]] = {}
    for category_items in (existing.get("kategoriler") or {}).values():
        for item in category_items or []:
            url = safe_url(item.get("kaynak_url"))
            if url and item.get("yayin_durumu") == "yayinda":
                by_url[url] = item
    for item in new_items:
        url = safe_url(item.get("kaynak_url"))
        if not url:
            continue
        if url in by_url and by_url[url].get("yayin_durumu") == "yayinda":
            preserved = by_url[url]
            preserved["guncellenme_tarihi"] = item["guncellenme_tarihi"]
            preserved["kaynak_tarihi"] = item.get("kaynak_tarihi")
            by_url[url] = preserved
        else:
            by_url[url] = item
    return list(by_url.values())


def build_rss(items: list[dict[str, Any]]) -> str:
    from xml.sax.saxutils import escape

    published = [item for item in items if item.get("yayin_durumu") == "yayinda"][:50]
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0"><channel>',
        f"<title>{escape('Sivil Dünya Haber')}</title>",
        f"<link>{escape(SITE)}</link>",
        f"<description>{escape('Resmî kaynak bağlantılı, editoryal onaylı haber akışı')}</description>",
    ]
    for item in published:
        parts.append(
            "<item>"
            f"<title>{escape(item.get('baslik', 'Duyuru'))}</title>"
            f"<link>{escape(item.get('kaynak_url', ''))}</link>"
            f"<description>{escape(item.get('ozet', ''))}</description>"
            "</item>"
        )
    parts.append("</channel></rss>")
    return "".join(parts)


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    existing = load_existing()
    all_new: list[dict[str, Any]] = []
    health: list[dict[str, Any]] = []
    for source in SOURCES:
        items, source_health = collect_source(source)
        all_new.extend(items)
        health.append(source_health)

    merged = merge_items(all_new, existing)
    categories = {category: [] for category in CATEGORIES}
    for item in sorted(merged, key=lambda value: value.get("guncellenme_tarihi", ""), reverse=True):
        category = item.get("kategori") if item.get("kategori") in categories else "gundem"
        categories[category].append(item)

    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    data = {
        "platform": DOMAIN,
        "site_url": SITE,
        "tarih": now.date().isoformat(),
        "son_guncelleme": now.isoformat(),
        "site": load_site_config(),
        "kategoriler": categories,
        "kaynaklar": [
            {key: source[key] for key in ("ad", "url", "kategori")} for source in SOURCES
        ],
        "uyum": {
            "yayin_modeli": "kaynak bağlantılı kısa özet + manuel editoryal onay",
            "taslaklar_public_feede_girmez": True,
            "kisisel_veri_taramasi": True,
            "iki_yillik_kayit_hedefi": True,
            "not": "Bu teknik kontroller hukuki incelemenin yerine geçmez.",
        },
    }
    (DATA_DIR / "duyurular.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    (ROOT / "rss.xml").write_text(build_rss(merged), encoding="utf-8")

    source_health = {
        "generated_at": now.isoformat(),
        "sources": health,
        "totals": {
            "new_candidates": len(all_new),
            "all_records": len(merged),
            "published": sum(1 for item in merged if item.get("yayin_durumu") == "yayinda"),
            "review_queue": sum(1 for item in merged if item.get("yayin_durumu") != "yayinda"),
            "flagged": sum(1 for item in merged if item.get("editoryal_kontrol", {}).get("riskler")),
        },
    }
    (DATA_DIR / "audit.json").write_text(json.dumps(source_health, ensure_ascii=False, indent=2), encoding="utf-8")
    archive_path = ARCHIVE_DIR / f"{now.date().isoformat()}.json"
    archive_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(source_health["totals"], ensure_ascii=False))


if __name__ == "__main__":
    main()
