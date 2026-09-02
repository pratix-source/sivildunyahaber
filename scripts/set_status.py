from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data/duyurular.json"
VALID_STATUSES = {"inceleme_bekliyor", "yayinda", "yayindan_kaldirildi"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Sivil Dünya Haber editoryal durum güncelleyici")
    parser.add_argument("--id", required=True, help="Kayıt ID’si")
    parser.add_argument("--status", required=True, choices=sorted(VALID_STATUSES), help="Yeni yayın durumu")
    parser.add_argument("--editor", required=True, help="İşlemi yapan editör")
    parser.add_argument("--note", default="", help="Editoryal karar notu")
    args = parser.parse_args()
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    found = None
    for values in data.get("kategoriler", {}).values():
        for item in values or []:
            if item.get("id") == args.id:
                found = item
                break
        if found:
            break
    if not found:
        raise SystemExit(f"Kayıt bulunamadı: {args.id}")
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    found["yayin_durumu"] = args.status
    control = found.setdefault("editoryal_kontrol", {})
    control["manuel_onay_gerekli"] = args.status != "yayinda"
    control["son_karar_tarihi"] = now
    control["son_karar_veren"] = args.editor
    control["son_karar_notu"] = args.note
    found["guncellenme_tarihi"] = now
    DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"id": args.id, "status": args.status, "editor": args.editor, "at": now}, ensure_ascii=False))


if __name__ == "__main__":
    main()
