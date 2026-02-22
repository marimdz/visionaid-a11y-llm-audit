import re
from bs4 import BeautifulSoup
from collections import Counter

VALID_LANG_PATTERN = re.compile(r"^[a-zA-Z]{2,3}(-[a-zA-Z]{2})?$")

def element_info(el):
    return {
        "tag": el.name,
        "id": el.get("id"),
        "class": el.get("class"),
        "snippet": str(el)[:200]
    }

def analyze_html(file_path):
    findings = []

    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "lxml")

    # --------------------
    # Missing H1
    # --------------------
    h1_tags = soup.find_all("h1")
    if len(h1_tags) == 0:
        findings.append({
            "issue_code": "MISSING_H1",
            "element": {"tag": "document"},
            "checklist_item": "Main content should start with <h1>",
            "wcag": {
                "criterion": "1.3.1",
                "name": "Info and Relationships",
                "level": "A"
            }
        })

    # --------------------
    # Empty ALT
    # --------------------
    for img in soup.find_all("img"):
        if img.get("alt") is None:
            findings.append({
                "issue_code": "IMG_MISSING_ALT",
                "element": element_info(img),
                "checklist_item": "Images must have alt attribute",
                "wcag": {
                    "criterion": "1.1.1",
                    "name": "Non-text Content",
                    "level": "A"
                }
            })
        elif img.get("alt").strip() == "":
            findings.append({
                "issue_code": "IMG_EMPTY_ALT",
                "element": element_info(img),
                "checklist_item": "Non-decorative images must have meaningful alt text",
                "wcag": {
                    "criterion": "1.1.1",
                    "name": "Non-text Content",
                    "level": "A"
                }
            })

    # --------------------
    # Links without text
    # --------------------
    for a in soup.find_all("a"):
        if not a.get_text(strip=True) and not a.get("aria-label"):
            findings.append({
                "issue_code": "LINK_NO_TEXT",
                "element": element_info(a),
                "checklist_item": "Links must have discernible text",
                "wcag": {
                    "criterion": "2.4.4",
                    "name": "Link Purpose (In Context)",
                    "level": "A"
                }
            })

    # --------------------
    # Duplicate IDs
    # --------------------
    ids = [tag["id"] for tag in soup.find_all(attrs={"id": True})]
    duplicates = [i for i, c in Counter(ids).items() if c > 1]

    for dup in duplicates:
        for el in soup.find_all(id=dup):
            findings.append({
                "issue_code": "DUPLICATE_ID",
                "element": element_info(el),
                "checklist_item": "IDs must be unique within a page",
                "wcag": {
                    "criterion": "4.1.1",
                    "name": "Parsing",
                    "level": "A"
                }
            })

    # --------------------
    # Iframe title
    # --------------------
    for iframe in soup.find_all("iframe"):
        if not iframe.get("title") or iframe.get("title").strip() == "":
            findings.append({
                "issue_code": "IFRAME_NO_TITLE",
                "element": element_info(iframe),
                "checklist_item": "Iframes must have descriptive title",
                "wcag": {
                    "criterion": "4.1.2",
                    "name": "Name, Role, Value",
                    "level": "A"
                }
            })

    return findings


if __name__ == "__main__":
    import sys, json
    results = analyze_html(sys.argv[1])
    print(json.dumps(results, indent=2))