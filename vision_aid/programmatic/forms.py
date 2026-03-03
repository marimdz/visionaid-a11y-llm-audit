from base import AuditBase
import sys
import os

class FormAudit(AuditBase):
    def __init__(self, file_path):
        super().__init__(file_path)
        self.form_controls = self.get_controls()

    def get_controls(self):
        form_controls = []

        for control in self.soup.find_all(["input", "select", "textarea"]):

            # Skip non-interactive input types
            if control.name == "input":
                input_type = (control.get("type") or "text").lower()

                if input_type in [
                    "hidden",
                    "submit",
                    "reset",
                    "button",
                    "image"
                ]:
                    continue

            form_controls.append(control)
        
        return form_controls
    
    def set_legend(self):
        for fieldset in self.soup.find_all("fieldset"):

            legend = fieldset.find("legend")

            # FORM_GROUP_001 — Fieldset missing legend
            if not legend:
                self.results.append(FormAudit.issue(
                    "FORM_GROUP_001",
                    "Fieldset missing legend",
                    fieldset,
                    "Fieldset does not contain a legend element."
                ))
    
    def set_required_fields(self):
        for control in self.form_controls:

            # Already programmatically required
            if "required" in control.attrs:
                continue

            control_id = control.get("id")

            # Heuristic: label contains *
            if control_id:
                label = self.soup.find("label", attrs={"for": control_id})
                if label and "*" in label.get_text():
                    self.results.append(FormAudit.issue(
                        "FORM_REQUIRED_001",
                        "Required field not programmatically designated",
                        control,
                        "Field appears visually required but lacks 'required' attribute."
                    ))
    
    def set_aria(self):
        for control in self.form_controls:

            describedby = control.get("aria-describedby")
            if describedby:
                ids = describedby.split()
                for ref_id in ids:
                    if not self.soup.find(id=ref_id):
                        self.results.append(FormAudit.issue(
                            "FORM_INSTR_001",
                            "aria-describedby reference not found",
                            control,
                            f"aria-describedby references missing ID '{ref_id}'."
                        ))
    
    def set_message_assc(self):
        for control in self.form_controls:

            if control.get("aria-invalid") == "true":
                describedby = control.get("aria-describedby")

                if not describedby:
                    self.results.append(FormAudit.issue(
                        "FORM_ERROR_001",
                        "Error message not programmatically associated",
                        control,
                        "Invalid form control lacks aria-describedby linking to error message."
                    ))

    def set_custom_interactive(self):
        for el in self.soup.find_all(True):

            if el.get("onclick") and el.name not in ["button", "a", "input"]:
                if not el.get("role"):
                    self.results.append(FormAudit.issue(
                        "FORM_CUSTOM_001",
                        "Custom interactive element missing role",
                        el,
                        "Element has click handler but no semantic role."
                    ))

    def run_audit(self):
        self.set_legend()
        self.set_required_fields()
        self.set_aria()
        self.set_message_assc()
        self.set_custom_interactive()
        return self.results

if __name__=='__main__':
    if len(sys.argv) != 2:
        print("Usage: python audit_forms.py <file.html>")
        sys.exit(1)

    file_path = sys.argv[1]

    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)

    form_audit = FormAudit(file_path)
    form_audit.run_audit()

    print("\n=== FORM ACCESSIBILITY AUDIT RESULTS ===\n")

    form_audit.parse_results()