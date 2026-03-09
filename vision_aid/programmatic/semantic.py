from base import AuditBase
import sys
import os
import re

class SemanticAudit(AuditBase):
    def __init__(self, file_path):
        super().__init__(file_path)
        self.LANGUAGE_TAG_REGEX = re.compile(r"^[a-zA-Z]{2,3}(-[a-zA-Z0-9]{2,8})*$")

    def set_titles(self):
        titles = self.soup.find_all("title")

        # PAGE_TITLE_001 — Missing <title>
        if len(titles) == 0:
            head = self.soup.find("head")
            self.results.append(SemanticAudit.issue(
                "PAGE_TITLE_001",
                "Missing <title>",
                head,
                "The page does not contain a <title> element."
            ))

        # PAGE_TITLE_002 — Multiple <title>
        if len(titles) > 1:
            for t in titles:
                self.results.append(SemanticAudit.issue(
                    "PAGE_TITLE_002",
                    "Multiple <title> elements",
                    t,
                    "More than one <title> element found."
                ))

        # PAGE_TITLE_003 — Empty <title>
        if titles and not titles[0].get_text(strip=True):
            self.results.append(SemanticAudit.issue(
                "PAGE_TITLE_003",
                "Empty <title>",
                titles[0],
                "<title> element exists but contains no text."
            ))

    def set_lang(self):
        html = self.soup.find("html")
        if html:
            lang = html.get("lang")

            if not lang:
                self.results.append(SemanticAudit.issue(
                    "LANG_001",
                    "Missing primary language",
                    html,
                    "<html> element missing lang attribute."
                ))

            # LANG_002 — Invalid primary language code
            elif not self.LANGUAGE_TAG_REGEX.match(lang):
                self.results.append(SemanticAudit.issue(
                    "LANG_002",
                    "Invalid primary language code",
                    html,
                    f"Invalid language code '{lang}' on <html>."
                ))

        # LANG_003 — Invalid inline language code
        for el in self.soup.find_all(attrs={"lang": True}):
            lang_val = el.get("lang")
            if not self.LANGUAGE_TAG_REGEX.match(lang_val):
                self.results.append(SemanticAudit.issue(
                    "LANG_003",
                    "Invalid inline language code",
                    el,
                    f"Invalid lang attribute '{lang_val}'."
                ))

    def set_landmark(self):
        # HTML5 landmark elements mapped to ARIA landmark roles
        landmark_map = {
            "header": "banner",
            "nav": "navigation",
            "main": "main",
            "footer": "contentinfo",
            "aside": "complementary"
        }

        aria_landmark_roles = {
            "banner",
            "navigation",
            "main",
            "contentinfo",
            "complementary",
            "search",
            "form",
            "region"
        }

        landmarks = []

        # Collect semantic landmark elements
        for tag, role in landmark_map.items():
            for el in self.soup.find_all(tag):
                landmarks.append((el, role))

        # Collect ARIA landmark roles
        for el in self.soup.find_all(attrs={"role": True}):
            role = el.get("role")
            if role in aria_landmark_roles:
                landmarks.append((el, role))

        role_map = {}

        for el, role in landmarks:
            role_map.setdefault(role, []).append(el)

        # LAND_001 — No main landmark
        if "main" not in role_map:
            body = self.soup.find("body")
            self.results.append(SemanticAudit.issue(
                "LAND_001",
                "Missing main landmark",
                body,
                "Page does not contain a <main> landmark."
            ))

        # LAND_002 — Multiple main landmarks
        if len(role_map.get("main", [])) > 1:
            for el in role_map["main"]:
                self.results.append(SemanticAudit.issue(
                    "LAND_002",
                    "Multiple main landmarks",
                    el,
                    "More than one 'main' landmark found."
                ))

        # LAND_003 — Multiple banner landmarks
        if len(role_map.get("banner", [])) > 1:
            for el in role_map["banner"]:
                self.results.append(SemanticAudit.issue(
                    "LAND_003",
                    "Multiple banner landmarks",
                    el,
                    "More than one 'banner' landmark found."
                ))

        # LAND_004 — Multiple contentinfo landmarks
        if len(role_map.get("contentinfo", [])) > 1:
            for el in role_map["contentinfo"]:
                self.results.append(SemanticAudit.issue(
                    "LAND_004",
                    "Multiple contentinfo landmarks",
                    el,
                    "More than one 'contentinfo' landmark found."
                ))

        # LAND_005 — Multiple same-type landmarks without labels
        for role, elements in role_map.items():
            if len(elements) > 1:
                for el in elements:
                    if not el.get("aria-label") and not el.get("aria-labelledby"):
                        self.results.append(SemanticAudit.issue(
                            "LAND_005",
                            f"Multiple '{role}' landmarks without accessible labels",
                            el,
                            f"Multiple '{role}' landmarks should have distinguishing aria-label or aria-labelledby attributes."
                        ))

        # LAND_006 — Content outside landmark regions
        landmark_elements = [el for el, _ in landmarks]
        body = self.soup.find("body")

        if body:
            for child in body.find_all(recursive=False):
                if child not in landmark_elements and child.name not in ["script", "style"]:
                    if child.get_text(strip=True):
                        self.results.append(SemanticAudit.issue(
                            "LAND_006",
                            "Content outside landmark regions",
                            child,
                            "Content found directly under <body> that is not contained within a landmark region."
                        ))
                        break
    
    def set_headings(self):
        headings = self.soup.find_all(re.compile("^h[1-6]$"))
        previous_level = 0

        # HEAD_001 — Skipped heading levels
        for h in headings:
            level = int(h.name[1])
            if previous_level and level > previous_level + 1:
                self.results.append(SemanticAudit.issue(
                    "HEAD_001",
                    "Skipped heading level",
                    h,
                    "Heading level skipped (e.g., h2 to h4)."
                ))
            previous_level = level

        h1_elements = [h for h in headings if h.name == "h1"]

        # HEAD_003 — Missing <h1>
        if len(h1_elements) == 0:
            body = self.soup.find("body")
            self.results.append(SemanticAudit.issue(
                "HEAD_003",
                "Missing <h1> element",
                body,
                "The page does not contain an <h1> element."
            ))

        # HEAD_002 — Multiple <h1>
        if len(h1_elements) > 1:
            for h in h1_elements:
                self.results.append(SemanticAudit.issue(
                    "HEAD_002",
                    "Multiple <h1> elements",
                    h,
                    "More than one <h1> found."
                ))

        # HEAD_004 — Empty heading
        for h in headings:
            if not h.get_text(strip=True):
                self.results.append(SemanticAudit.issue(
                    "HEAD_004",
                    "Empty heading",
                    h,
                    "Heading element contains no text."
                ))

    def set_links(self):
        for a in self.soup.find_all("a"):

            # LINK_001 — Missing accessible name
            if not a.get_text(strip=True) and not a.get("aria-label"):
                self.results.append(SemanticAudit.issue(
                    "LINK_001",
                    "Link without accessible name",
                    a,
                    "Link has no text or aria-label."
                ))

            # LINK_002 — Anchor without href
            if not a.get("href"):
                self.results.append(SemanticAudit.issue(
                    "LINK_002",
                    "Anchor without href",
                    a,
                    "Anchor element does not contain an href attribute."
                ))

    def set_skip_links(self):
        skip_links = []

        # Identify potential skip links (anchor with internal target and "skip" text)
        for a in self.soup.find_all("a"):
            href = a.get("href")
            text = a.get_text(strip=True).lower()

            if href and href.startswith("#") and "skip" in text:
                skip_links.append(a)

        # NAV_001 — Skip link not present
        if not skip_links:
            body = self.soup.find("body")
            self.results.append(SemanticAudit.issue(
                "NAV_001",
                "Skip link not present",
                body,
                "Page does not contain a skip navigation link."
            ))
        else:
            # Validate each skip link
            for skip in skip_links:
                target_id = skip.get("href")[1:]
                target_element = self.soup.find(id=target_id)

                # NAV_002 — Skip link target missing
                if not target_element:
                    self.results.append(SemanticAudit.issue(
                        "NAV_002",
                        "Skip link target does not exist",
                        skip,
                        f"Skip link points to '#{target_id}' but no element with that ID exists."
                    ))

            # NAV_003 — Skip link is not first focusable element
            focusable_elements = []

            for el in self.soup.find_all(True):
                if el.name in ["a", "button", "input", "select", "textarea"]:
                    if el.name != "a" or el.get("href"):
                        focusable_elements.append(el)
                elif el.get("tabindex") and el.get("tabindex").isdigit():
                    if int(el.get("tabindex")) >= 0:
                        focusable_elements.append(el)

            if focusable_elements:
                first_focusable = focusable_elements[0]
                if first_focusable not in skip_links:
                    self.results.append(SemanticAudit.issue(
                        "NAV_003",
                        "Skip link is not first focusable element",
                        first_focusable,
                        "The first focusable element on the page is not a skip navigation link."
                    ))

    def set_tab_index(self):
        # FOCUS_001 — Positive tabindex used
        for el in self.soup.find_all(attrs={"tabindex": True}):
            val = el.get("tabindex")
            if val.isdigit() and int(val) > 0:
                self.results.append(SemanticAudit.issue(
                    "FOCUS_001",
                    "Positive tabindex used",
                    el,
                    "tabindex greater than 0 should not be used."
                ))

    def set_tables(self):
        for table in self.soup.find_all("table"):

            # TABLE_001 — Missing caption
            if not table.find("caption"):
                self.results.append(SemanticAudit.issue(
                    "TABLE_001",
                    "Missing table caption",
                    table,
                    "Data table does not contain a <caption>."
                ))

            # TABLE_002 — Missing headers
            if not table.find("th"):
                self.results.append(SemanticAudit.issue(
                    "TABLE_002",
                    "Missing table headers",
                    table,
                    "Table does not contain <th> elements."
                ))
    
    def set_iframes(self):
        for iframe in self.soup.find_all("iframe"):

            # IFRAME_001 — Missing title
            title = iframe.get("title")
            if not title:
                self.results.append(SemanticAudit.issue(
                    "IFRAME_001",
                    "Missing iframe title",
                    iframe,
                    "Iframe does not have a title attribute."
                ))

            # IFRAME_002 — Empty title
            elif not title.strip():
                self.results.append(SemanticAudit.issue(
                    "IFRAME_002",
                    "Empty iframe title",
                    iframe,
                    "Iframe title attribute is empty."
                ))
    
    def set_duplicate_ids(self):
        ids = {}
        for el in self.soup.find_all(attrs={"id": True}):
            id_val = el.get("id")
            if id_val in ids:
                self.results.append(SemanticAudit.issue(
                    "PARSE_001",
                    "Duplicate ID",
                    el,
                    f"Duplicate id '{id_val}' found."
                ))
            else:
                ids[id_val] = el

    def run_audit(self):
        self.set_titles()
        self.set_lang()
        self.set_landmark()
        self.set_headings()
        self.set_links()
        self.set_skip_links()
        self.set_tab_index()
        self.set_tables()
        self.set_iframes()
        self.set_duplicate_ids()
        return self.results
    
if __name__=='__main__':
    if len(sys.argv) != 2:
        print("Usage: python audit.py <file.html>")
        sys.exit(1)

    file_path = sys.argv[1]

    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)

    semantic_audit = SemanticAudit(file_path=file_path)
    results = semantic_audit.run_audit()

    print("\n=== SEMANTIC ACCESSIBILITY AUDIT RESULTS ===\n")

    semantic_audit.parse_results(results)

    sys.exit(2)