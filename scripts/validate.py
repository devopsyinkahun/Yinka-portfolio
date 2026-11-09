from html.parser import HTMLParser
from pathlib import Path

class Validator(HTMLParser):
    def error(self, message):
        raise RuntimeError(message)

root = Path(__file__).resolve().parents[1]
html = (root / "index.html").read_text(encoding="utf-8")
Validator().feed(html)
for required in ["#about", "#skills", "#projects", "#cv", "#contact"]:
    if required not in html:
        raise SystemExit(f"Missing required section link: {required}")
for asset in ["styles.css", "script.js", "assets/Olayinka_Odeneye_CV.pdf"]:
    if not (root / asset).is_file():
        raise SystemExit(f"Missing required asset: {asset}")
print("Portfolio HTML and required assets validated.")
