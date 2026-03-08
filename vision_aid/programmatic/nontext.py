from base import AuditBase
import sys
import os

class NontextAudit(AuditBase):
    def __init__(self, file_path):
        super().__init__(file_path)

    def set_img_alt_txt(self):
        # Images that convey content MUST have programmatically-discernible alternative text.
        for img in self.soup.find_all("img"):

            # NON_TEXT_001 — Missing alt attribute
            if img.get("alt") is None:
                self.results.append(NontextAudit.issue(
                    "NON_TEXT_001",
                    "Image missing alt attribute",
                    img,
                    "<img> element does not contain an alt attribute."
                ))

        # All actionable images MUST have alternative text.
        for a in self.soup.find_all("a"):
            img = a.find("img")
            if img:
                alt = img.get("alt")
                if alt is None or alt.strip() == "":
                    self.results.append(NontextAudit.issue(
                        "NON_TEXT_002",
                        "Actionable image missing alt text",
                        img,
                        "Image inside a link must have non-empty alt text."
                    ))

        # Form inputs with type="image" MUST have alternative text.
        for inp in self.soup.find_all("input", attrs={"type": "image"}):
            alt = inp.get("alt")
            if alt is None or alt.strip() == "":
                self.results.append(NontextAudit.issue(
                    "NON_TEXT_003",
                    "Image input missing alt text",
                    inp,
                    "Form input type='image' must have non-empty alt text."
                ))

    def set_img_maps(self):
        # The alternative text for the <area> element MUST be available.
        for area in self.soup.find_all("area"):
            alt = area.get("alt")
            if alt is None or alt.strip() == "":
                self.results.append(NontextAudit.issue(
                    "NON_TEXT_004",
                    "Image map area missing alt text",
                    area,
                    "<area> element must have non-empty alt text."
                ))
    
    def set_svg(self):
        # SVG SHOULD NOT be embedded via <object> or <iframe>.
        for obj in self.soup.find_all(["object", "iframe"]):
            src = obj.get("data") or obj.get("src")
            if src and src.lower().endswith(".svg"):
                self.results.append(NontextAudit.issue(
                    "NON_TEXT_005",
                    "SVG embedded via object or iframe",
                    obj,
                    "SVG should not be embedded using <object> or <iframe>."
                ))

    def set_canvas(self):
        # All <canvas> elements MUST have a text alternative.
        for canvas in self.soup.find_all("canvas"):
            if not canvas.get_text(strip=True):
                self.results.append(NontextAudit.issue(
                    "NON_TEXT_006",
                    "Canvas missing fallback text",
                    canvas,
                    "<canvas> element must contain fallback text content."
                ))

    def set_plug_ins(self):
        # All <object> elements MUST have alternative text.
        for obj in self.soup.find_all("object"):
            if not obj.get_text(strip=True):
                self.results.append(NontextAudit.issue(
                    "NON_TEXT_007",
                    "Object missing alternative text",
                    obj,
                    "<object> element must contain alternative text content."
                ))
    
    def run_audit(self):
        self.set_img_alt_txt()
        self.set_img_maps()
        self.set_svg()
        self.set_canvas()
        self.set_plug_ins()
        return self.results

if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage: python audit_nontext.py <file.html>")
        sys.exit(1)

    file_path = sys.argv[1]

    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)

    nontext_audit = NontextAudit(file_path)
    results = nontext_audit.run_audit()

    print("\n=== NON-TEXT ACCESSIBILITY AUDIT RESULTS ===\n")

    nontext_audit.parse_results(results)