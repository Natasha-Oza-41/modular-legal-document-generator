from __future__ import annotations

import html as html_lib


class PDFRenderer:
    """
    Converts plain-text document output from Claude into an A4 PDF via WeasyPrint.
    """

    _CSS = """
        @page {
            size: A4;
            margin: 2.5cm 2.5cm 2cm 2.5cm;
        }
        body {
            font-family: "Times New Roman", Times, serif;
            font-size: 12pt;
            line-height: 1.6;
            color: #000000;
        }
        h1 {
            text-align: center;
            font-size: 14pt;
            font-weight: bold;
            letter-spacing: 0.05em;
            margin-bottom: 24pt;
        }
        p {
            margin: 0 0 10pt 0;
            text-align: justify;
        }
        .section-heading {
            font-weight: bold;
            margin-top: 16pt;
            margin-bottom: 6pt;
        }
        .note {
            font-size: 10pt;
            color: #444;
            margin-top: 24pt;
            border-top: 1px solid #ccc;
            padding-top: 8pt;
        }
    """

    def render(self, document_text: str) -> bytes:
        from weasyprint import CSS, HTML  # imported here to avoid slow startup if unused

        html_body = self._text_to_html(document_text)
        full_html = (
            "<!DOCTYPE html><html lang='en'><head>"
            "<meta charset='UTF-8'>"
            "</head><body>"
            f"{html_body}"
            "</body></html>"
        )
        pdf_bytes: bytes = HTML(string=full_html).write_pdf(
            stylesheets=[CSS(string=self._CSS)]
        )
        return pdf_bytes

    @staticmethod
    def _text_to_html(text: str) -> str:
        """
        Convert plain text to minimal HTML:
        - Double newlines → paragraph breaks
        - Lines that look like numbered section headings get a class
        - Single newlines within a paragraph → <br>
        - The trailing NOTE section gets special styling
        """
        import re

        escaped = html_lib.escape(text)
        paragraphs = escaped.split("\n\n")
        parts = []
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            # Detect section heading: starts with a digit and a dot
            if re.match(r"^\d+\.\s+[A-Z]", para):
                parts.append(f'<p class="section-heading">{para.replace(chr(10), "<br>")}</p>')
            elif para.startswith("LAST WILL") or para.startswith("THIS IS THE LAST"):
                parts.append(f"<h1>{para.replace(chr(10), '<br>')}</h1>")
            elif para.startswith("---"):
                parts.append(f'<p class="note">{para[3:].strip().replace(chr(10), "<br>")}</p>')
            else:
                parts.append(f"<p>{para.replace(chr(10), '<br>')}</p>")
        return "\n".join(parts)
