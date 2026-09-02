from __future__ import annotations

import json
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from update_script import SOURCES, safe_url  # noqa: E402


def main() -> None:
    data = json.loads((ROOT / "data/duyurular.json").read_text(encoding="utf-8"))
    audit = json.loads((ROOT / "data/audit.json").read_text(encoding="utf-8"))
    rss = (ROOT / "rss.xml").read_text(encoding="utf-8")
    allowed = {host for source in SOURCES for host in source["allowed_hosts"]}
    items = [item for values in data.get("kategoriler", {}).values() for item in values]
    errors: list[str] = []
    for item in items:
        url = safe_url(item.get("kaynak_url"))
        host = (urllib.parse.urlparse(url).hostname or "") if url else ""
        if not url or host not in allowed and not any(host.endswith("." + allowed_host) for allowed_host in allowed):
            errors.append(f"allowlist dışı veya geçersiz URL: {item.get('kaynak_url')}")
        if item.get("yayin_durumu") not in {"inceleme_bekliyor", "yayinda", "yayindan_kaldirildi"}:
            errors.append(f"geçersiz yayın durumu: {item.get('yayin_durumu')}")
        if item.get("yayin_durumu") != "yayinda" and item.get("kaynak_url") in rss:
            errors.append(f"onaysız kayıt RSS içinde: {item.get('id')}")
        control = item.get("editoryal_kontrol", {})
        if item.get("yayin_durumu") != "yayinda" and not control.get("manuel_onay_gerekli"):
            errors.append(f"inceleme kaydında manuel onay işareti eksik: {item.get('id')}")
        if item.get("yayin_durumu") == "yayinda" and not control.get("son_karar_veren"):
            errors.append(f"yayındaki kayıtta editör karar izi eksik: {item.get('id')}")
    expected_published = sum(1 for item in items if item.get("yayin_durumu") == "yayinda")
    expected_review = len(items) - expected_published
    totals = audit.get("totals", {})
    if totals.get("published") != expected_published:
        errors.append("audit published toplamı kayıtlarla eşleşmiyor")
    if totals.get("review_queue") != expected_review:
        errors.append("audit review_queue toplamı kayıtlarla eşleşmiyor")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print(json.dumps({"valid": True, "records": len(items), "published": expected_published, "review_queue": expected_review, "sources": len(audit.get('sources', []))}, ensure_ascii=False))


if __name__ == "__main__":
    main()
