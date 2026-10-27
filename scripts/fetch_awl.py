"""Fetch the AWL family-list source without replacing an existing snapshot."""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "data" / "awl"
URLS = {
    "awl-families.pdf": "https://www.wgtn.ac.nz/lals/resources/academicwordlist/publications/awlsublists1.pdf",
    "awl-headwords.pdf": "https://www.wgtn.ac.nz/lals/resources/academicwordlist/awl-headwords/Headwords-of-the-Academic-Word-List.pdf",
}


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    records = []
    for filename, url in URLS.items():
        target = DEST / filename
        if target.exists():
            print(f"Already present: {filename}", flush=True)
            continue
        try:
            req = Request(url, headers={"User-Agent": "Mozilla/5.0 (educational research)"})
            with urlopen(req, timeout=30) as response:
                content = response.read()
                final_url = response.url
            if not content.startswith(b"%PDF"):
                raise ValueError("The response is not a PDF")
            target.write_bytes(content)
            records.append({
                "filename": filename, "url": url, "resolved_url": final_url,
                "retrieved_utc": datetime.now(timezone.utc).isoformat(),
                "sha256": hashlib.sha256(content).hexdigest(), "bytes": len(content),
            })
            print(f"Saved {filename}: {len(content)} bytes", flush=True)
        except Exception as error:
            print(f"FAILED {url}: {type(error).__name__}: {error}", flush=True)
    if records:
        (DEST / "download-provenance.json").write_text(json.dumps(records, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
