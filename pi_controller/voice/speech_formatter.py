"""
Encountered an issue that the LLM generates markdown and that gets spoken out by the assistant
as characters, example * is spoken as "asterix". This formatter is the middle layer between the LLM response and the speech output
"""
import re
from html.parser import HTMLParser
from markdown_it import MarkdownIt


class _SpeechHTMLParser(HTMLParser):
    BLOCK_TAGS = {
        "p", "div", "li", "h1", "h2", "h3",
        "h4", "h5", "h6", "blockquote", "tr",
    }

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.skip_pre = 0

    def handle_starttag(self, tag, attrs):
        if tag == "pre":
            self.skip_pre += 1
            return

        if self.skip_pre:
            return

        if tag in self.BLOCK_TAGS:
            self.parts.append(" ")

        elif tag in ("br", "hr"):
            self.parts.append(". ")

        elif tag in ("td", "th"):
            self.parts.append(", ")

        elif tag == "img":
            alt = dict(attrs).get("alt", "")
            self.parts.append(alt)

    def handle_endtag(self, tag):
        if tag == "pre":
            self.skip_pre = max(0, self.skip_pre - 1)
            return

        if self.skip_pre:
            return

        if tag in self.BLOCK_TAGS:
            self.parts.append(". ")

        elif tag in ("td", "th"):
            self.parts.append(", ")

    def handle_data(self, data):
        if not self.skip_pre:
            self.parts.append(data)


class SpeechTextFormatter:

    def __init__(self):
        self.markdown = MarkdownIt("default", {"html": False})

    def format(self, text: str) -> str:
        if not text or not text.strip():
            return ""

        html = self.markdown.render(text)

        parser = _SpeechHTMLParser()
        parser.feed(html)
        parser.close()

        result = " ".join("".join(parser.parts).split())

        # Make common punctuation sound natural.
        result = re.sub(
            r"\b(\d{1,2}):(\d{2})(?::(\d{2}))?\b",
            lambda m: " ".join(x for x in m.groups() if x is not None),
            result,
        )

        result = re.sub(r":\s*", ", ", result)
        result = re.sub(r";", ",", result)
        result = re.sub(r"(?<=\d)\s*\*\s*(?=\d)", " times ", result)

        result = re.sub(r"\s+([,.!?])", r"\1", result)
        result = re.sub(r"[ \t]+", " ", result)
        result = re.sub(r"(?:\.\s*){2,}", ". ", result)

        return result.strip(" .,")