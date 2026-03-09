from abc import abstractmethod, ABC
from bs4 import BeautifulSoup
import sys

class AuditBase(ABC):

    def __init__(
        self,
        file_path:str
    ):
        self.file_path = file_path
        self.soup = self.get_soup()
        self.results = []

    @staticmethod
    def css_path(el):
        """
        Generate a CSS-like DOM path for an element.
        """
        path = []
        while el and el.name:
            sibling_index = 1
            sibling = el
            while sibling.previous_sibling:
                sibling = sibling.previous_sibling
                if getattr(sibling, "name", None) == el.name:
                    sibling_index += 1

            if sibling_index > 1:
                path.append(f"{el.name}:nth-of-type({sibling_index})")
            else:
                path.append(el.name)

            el = el.parent

        return " > ".join(reversed(path))

    @staticmethod
    def element_location(element):
        """
        Build structured location metadata for an element.
        """
        if element is None:
            return None

        attrs = dict(element.attrs)

        return {
            "tag": element.name,
            "id": attrs.get("id"),
            "class": attrs.get("class"),
            "css_path": AuditBase.css_path(element),
            "attributes": attrs,
            "text_preview": element.get_text(strip=True)[:80]
        }

    @staticmethod
    def issue(rule_id, rule_name, element, description):
        """
        Create a standardized issue object.
        """
        return {
            "rule_id": rule_id,
            "rule_name": rule_name,
            "location": AuditBase.element_location(element),
            "description": description
        }
    
    @staticmethod
    def parse_results(results):
        if not results:
            print("No issues found.")
            sys.exit(0)

        for r in results:
            print(f"[{r['rule_id']}] {r['rule_name']}")

            location = r.get("location")

            if location:
                if location.get("css_path"):
                    print(f"  Location: {location['css_path']}")
                if location.get("id"):
                    print(f"  ID: {location['id']}")
                if location.get("attributes"):
                    print(f"  Attributes: {location['attributes']}")
                if location.get("text_preview"):
                    print(f"  Text Preview: \"{location['text_preview']}\"")

            print(f"  Description: {r['description']}")
            print()
    
    def get_soup(self):
        with open(self.file_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "lxml")
        return soup
    
    @abstractmethod
    def run_audit(self):
        """
        Abstract method for defining programmatic
        audits for each of the element types. 
        """
        pass