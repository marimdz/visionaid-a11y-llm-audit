import re
import json
from bs4 import BeautifulSoup

GENERIC_LINK_TERMS = {
    "click here", "here", "read more", "more",
    "learn more", "details", "link"
}

def clean(text):
    return re.sub(r"\s+", " ", text.strip()) if text else ""

def extract(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "lxml")

    payload = {}

    # TITLE
    payload["page_title"] = {
        "title": clean(soup.title.string) if soup.title else "",
        "h1": clean(soup.find("h1").get_text()) if soup.find("h1") else ""
    }

    # HEADINGS
    payload["headings"] = [
        {"level": int(h.name[1]), "text": clean(h.get_text())}
        for h in soup.find_all(re.compile("^h[1-6]$"))
    ]

    # LINKS (filtered)
    links = []
    seen = set()
    for a in soup.find_all("a"):
        text = clean(a.get_text())
        aria = clean(a.get("aria-label"))
        if not text or text.lower() in GENERIC_LINK_TERMS or len(text.split()) <= 2:
            key = (text, aria)
            if key not in seen:
                seen.add(key)
                links.append({"text": text, "aria_label": aria or None})
    payload["links"] = links

    # TABLES (sampled)
    tables = []
    for table in soup.find_all("table"):
        caption = clean(table.caption.get_text()) if table.caption else ""
        headers = [clean(th.get_text()) for th in table.find_all("th")]
        tables.append({
            "caption": caption,
            "headers": headers[:20]
        })
    payload["tables"] = tables

    # IFRAMES
    payload["iframes"] = [
        {"title": clean(i.get("title"))}
        for i in soup.find_all("iframe")
    ]

    return payload


if __name__ == "__main__":
    import sys
    print(json.dumps(extract(sys.argv[1]), indent=2))