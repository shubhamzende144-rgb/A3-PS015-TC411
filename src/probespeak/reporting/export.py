"""Text, CSV, JSON, Markdown, and a small PDF export. No network."""
from __future__ import annotations

import csv
import io
import json
from pathlib import Path

from .privacy import sanitize

def _lines(result: dict) -> list[str]:
    lines = [
        "ProbeSpeak diagnostic report",
        f"Mode: {result.get('mode')}",
        f"Scenario: {result.get('title') or result.get('id') or 'live'}",
        f"Finding: {result.get('titleFinding') or result.get('finding')}",
        f"Verdict: {result.get('verdict')}",
        "",
        "Plain explanation",
        result.get("plain") or "",
        "",
        "Technical",
        result.get("technical") or result.get("outcomeDetail") or "",
        "",
        "Checks",
    ]
    checks = result.get("checks") or {}
    for key, check in checks.items():
        lines.append(f"- {key}: {check.get('band')} — {check.get('detail')}")
    if result.get("after"):
        lines += ["", "Retest", result["after"].get("technical") or ""]
    lines += [
        "",
        "Limitations",
        "Resolved means only that a later retest passed every check.",
        "This report does not claim a broken cable, Wi-Fi interference, or an ISP-internal fault.",
        "Lab results are stored numbers. They are not a test of this computer.",
    ]
    return [sanitize(line) for line in lines]

def to_text(result: dict) -> str:
    return "\n".join(_lines(result)) + "\n"

def to_markdown(result: dict) -> str:
    body = _lines(result)
    return "# " + body[0] + "\n\n" + "\n".join(body[1:]) + "\n"

def to_json(result: dict) -> str:
    cloned = json.loads(sanitize(json.dumps(result)))
    return json.dumps(cloned, indent=2)

def to_csv(result: dict) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["check", "band", "detail"])
    for key, check in (result.get("checks") or {}).items():
        writer.writerow([sanitize(key), sanitize(str(check.get("band"))), sanitize(str(check.get("detail")))])
    return buf.getvalue()

def to_pdf(result: dict) -> bytes:
    """Single-page PDF of the text report. Enough for a local export, not a designed brochure."""
    text = to_text(result).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    chunks = []
    y = 800
    for raw in text.splitlines()[:48]:
        line = raw[:110]
        chunks.append(f"BT /F1 10 Tf 40 {y} Td ({line}) Tj ET")
        y -= 14
        if y < 40:
            break
    stream = "\n".join(chunks).encode()
    objects = [
        b"1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj\n",
        b"2 0 obj<< /Type /Pages /Kids [3 0 R] /Count 1 >>endobj\n",
        b"3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 842] /Contents 4 0 R /Resources<< /Font<< /F1 5 0 R >> >> >>endobj\n",
        b"4 0 obj<< /Length " + str(len(stream)).encode() + b" >>stream\n" + stream + b"\nendstream\nendobj\n",
        b"5 0 obj<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>endobj\n",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for obj in objects:
        offsets.append(len(out))
        out += obj
    xref = len(out)
    out += f"xref\n0 {len(offsets)}\n".encode()
    out += b"0000000000 65535 f \n"
    for off in offsets[1:]:
        out += f"{off:010d} 00000 n \n".encode()
    out += f"trailer<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF".encode()
    return bytes(out)

def write_report(result: dict, folder: str | Path, stem: str) -> dict[str, str]:
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    paths = {
        "txt": folder / f"{stem}.txt",
        "md": folder / f"{stem}.md",
        "json": folder / f"{stem}.json",
        "csv": folder / f"{stem}.csv",
        "pdf": folder / f"{stem}.pdf",
    }
    paths["txt"].write_text(to_text(result), encoding="utf-8")
    paths["md"].write_text(to_markdown(result), encoding="utf-8")
    paths["json"].write_text(to_json(result), encoding="utf-8")
    paths["csv"].write_text(to_csv(result), encoding="utf-8")
    paths["pdf"].write_bytes(to_pdf(result))
    return {key: str(value) for key, value in paths.items()}
