"""Build the animated SVGs used in the README.

    python3 assets/make_demos.py

Writes assets/before-after.svg (a plain agent versus serpwise on the same page)
and assets/auditor.svg (the page auditor's output). Both loop forever and use
only CSS animation, which GitHub renders inside <img>.

The text comes from real runs: examples/audit-without-serpwise.md,
examples/audit-with-serpwise.md, and `npx serpwise audit` on the eval fixture.
Keep it in sync with those files when they change.
"""

import html
import os

OUT = os.path.dirname(os.path.abspath(__file__))

FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
BG, BAR, FG, DIM = "#0d1117", "#161b22", "#e6edf3", "#7d8590"
RED, ORANGE, YELLOW, GRAY, GREEN, BLUE = "#ff7b72", "#ffa657", "#e3b341", "#8b949e", "#3fb950", "#58a6ff"
CHAR_W = 8.43  # width of one 14px monospace character, for the typing effect


class Svg:
    """Collect SVG elements and the per-element CSS keyframes that animate them."""

    def __init__(self, width, height, cycle, label):
        self.w, self.h, self.cycle, self.label = width, height, cycle, label
        self.css, self.body, self.n = [], [], 0

    def _pct(self, seconds):
        """Convert a time in the loop to a keyframe percentage."""
        return round(min(max(seconds / self.cycle * 100, 0), 100), 3)

    def _name(self):
        """Return a fresh keyframes name."""
        self.n += 1
        return f"k{self.n}"

    def window(self, start, end):
        """Keyframes that show an element from `start` to `end` seconds, fading in and out."""
        name = self._name()
        a, b = self._pct(start), self._pct(start + 0.25)
        c, d = self._pct(end - 0.35), self._pct(end)
        self.css.append(
            f"@keyframes {name}{{0%,{a}%{{opacity:0}}{b}%,{c}%{{opacity:1}}{d}%,100%{{opacity:0}}}}"
        )
        return f"opacity:0;animation:{name} {self.cycle}s linear infinite"

    def appear(self, at):
        """Keyframes that show an element from `at` seconds until the loop restarts."""
        name = self._name()
        a, b = self._pct(at), self._pct(at + 0.2)
        self.css.append(f"@keyframes {name}{{0%,{a}%{{opacity:0}}{b}%,100%{{opacity:1}}}}")
        return f"opacity:0;animation:{name} {self.cycle}s linear infinite"

    def text(self, x, y, s, color=FG, style="", weight="normal", size=14, anchor="start"):
        """Add one line of text."""
        bold = ' font-weight="bold"' if weight == "bold" else ""
        self.body.append(
            f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" text-anchor="{anchor}"{bold}'
            f' style="{style}">{html.escape(s)}</text>'
        )

    def typed(self, x, y, s, start, color=FG):
        """Add text that is typed out character by character, starting at `start` seconds."""
        name, clip = self._name(), f"c{self.n}"
        duration = 0.045 * len(s)
        a, b = self._pct(start), self._pct(start + duration)
        width = round(len(s) * CHAR_W + 4, 1)
        self.css.append(
            f"@keyframes {name}{{0%,{a}%{{width:0;animation-timing-function:steps({len(s)},end)}}"
            f"{b}%,100%{{width:{width}px}}}}"
        )
        self.body.append(
            f'<clipPath id="{clip}"><rect x="{x}" y="{y - 15}" height="20" width="0"'
            f' style="animation:{name} {self.cycle}s linear infinite"/></clipPath>'
        )
        self.body.append(
            f'<text x="{x}" y="{y}" fill="{color}" clip-path="url(#{clip})">{html.escape(s)}</text>'
        )
        return start + duration

    def open_group(self, style):
        """Start a group, used for a scene that fades in and out as a whole."""
        self.body.append(f'<g style="{style}">')

    def close_group(self):
        """End the current group."""
        self.body.append("</g>")

    def render(self):
        """Return the finished SVG document, with a terminal window frame."""
        w, h = self.w, self.h
        frame = [
            f'<rect width="{w}" height="{h}" rx="12" fill="{BG}"/>',
            f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="12" fill="none" stroke="#30363d"/>',
            f'<path d="M0 12a12 12 0 0 1 12-12h{w - 24}a12 12 0 0 1 12 12v26H0z" fill="{BAR}"/>',
            '<circle cx="22" cy="19" r="6" fill="#ff5f57"/><circle cx="42" cy="19" r="6" fill="#febc2e"/>'
            '<circle cx="62" cy="19" r="6" fill="#28c840"/>',
        ]
        return "\n".join(
            [
                f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"'
                f' role="img" aria-label="{html.escape(self.label)}">',
                f"<style>text{{font-family:{FONT};font-size:14px;white-space:pre}}"
                + "".join(self.css)
                + "</style>",
                *frame,
                *self.body,
                "</svg>",
            ]
        )


def before_after():
    """A plain agent's audit next to serpwise's audit of the same broken page, as two looping scenes."""
    cycle = 22.0
    svg = Svg(
        900,
        370,
        cycle,
        "Before and after: a plain agent pads its audit with SEO folklore and cites no sources; "
        "with serpwise, every finding is ranked by severity and tied to a Google rule.",
    )
    y0, lh = 74, 25

    # Scene 1: the plain agent. Runs from 0 to 10.5 seconds.
    svg.open_group(svg.window(0, 10.5))
    svg.text(450, 24, "BEFORE  ·  agent without serpwise", DIM, anchor="middle", size=13)
    t = svg.typed(24, y0, "> audit the SEO of index.html and give me a fix list", 0.4, FG)
    rows = [
        ("1. Remove the noindex robots tag", "✓ correct", GREEN),
        ("2. Move the <img> out of <head>", "✓ correct", GREEN),
        ('3. Title: "aim for 50–60 characters"', "✗ Google sets no limit", RED),
        ('4. Description: "write 140–160 characters"', "✗ Google sets no limit", RED),
        ("5. Add <html lang> as an SEO fix", "✗ Google doesn't use it", RED),
    ]
    at = t + 0.5
    # The agent's list appears first, then the verdict on each item.
    for i, (item, _verdict, _color) in enumerate(rows):
        y = y0 + lh * (i + 2)
        svg.text(40, y, item, FG, svg.appear(at + i * 0.45))
    verdict_at = at + len(rows) * 0.45 + 0.6
    for i, (_item, verdict, color) in enumerate(rows):
        y = y0 + lh * (i + 2)
        svg.text(560, y, verdict, color, svg.appear(verdict_at + i * 0.35), weight="bold")
    y = y0 + lh * 8.2
    svg.text(40, y, "Google rules cited: 1 of 17 items", ORANGE, svg.appear(verdict_at + 2.2))
    svg.text(
        40, y + lh, "Finds the blockers, then pads the list with folklore.", DIM, svg.appear(verdict_at + 2.6)
    )
    svg.close_group()

    # Scene 2: the same task with serpwise. Runs from 11 to 22 seconds.
    start = 11.0
    svg.open_group(svg.window(start, cycle))
    svg.text(450, 24, "AFTER  ·  agent with serpwise", BLUE, anchor="middle", size=13)
    t = svg.typed(24, y0, "> /serpwise audit index.html", start + 0.4, FG)
    findings = [
        ("CRITICAL", RED, "noindex blocks indexing", "Block indexing with noindex"),
        ("CRITICAL", RED, "<img> in <head> hides 6 meta tags", "Valid HTML for page metadata"),
        ("HIGH", ORANGE, 'hreflang "uk" is Ukrainian → en-GB', "Localized versions of a page"),
        ("HIGH", ORANGE, "JSON-LD fails to parse (// comment)", "Structured data guidelines"),
        ("MEDIUM", YELLOW, "3 images have no alt text", "Image SEO best practices"),
        ("MYTH", GRAY, "Title length: no character target", "Google sets no limit"),
    ]
    at = t + 0.5
    svg.text(24, y0 + lh * 1.4, "SEVERITY  ISSUE", DIM, svg.appear(at), size=12)
    svg.text(560, y0 + lh * 1.4, "GOOGLE RULE", DIM, svg.appear(at), size=12)
    for i, (sev, color, issue, rule) in enumerate(findings):
        y = y0 + lh * (i + 2.4)
        style = svg.appear(at + 0.3 + i * 0.45)
        svg.text(24, y, sev, color, style, weight="bold")
        svg.text(114, y, issue, FG, style)
        svg.text(560, y, rule, DIM, style)
    done = at + 0.3 + len(findings) * 0.45 + 0.5
    y = y0 + lh * 9.2
    svg.text(24, y, "Google rules cited: 18 of 19 findings, ranked by severity", GREEN, svg.appear(done))
    svg.text(24, y + lh, "Same model, same page. Both reports are in examples/.", DIM, svg.appear(done + 0.4))
    svg.close_group()
    return svg.render()


def auditor():
    """The bundled page auditor run on the eval fixture, looping."""
    cycle = 12.0
    svg = Svg(
        900,
        370,
        cycle,
        "npx serpwise audit output: two Critical findings (a noindex tag and an <img> that ends the head early), "
        "followed by High, Medium and Low findings.",
    )
    y0, lh = 70, 24
    svg.open_group(svg.window(0, cycle))
    svg.text(450, 24, "npx serpwise audit", DIM, anchor="middle", size=13)
    t = svg.typed(24, y0, "$ npx serpwise audit index.html --base-url https://www.stridesupply.com/", 0.4)
    lines = [
        (RED, "bold", "[CRITICAL] (indexing) Robots meta blocks indexing: 'noindex, follow'"),
        (RED, "bold", "[CRITICAL] (html) <img> inside <head> ends the head: 6 meta/link tags ignored"),
        (ORANGE, "normal", "[HIGH] (appearance) Title too vague: 'Home'"),
        (ORANGE, "normal", "[HIGH] (mobile) No viewport meta"),
        (ORANGE, "normal", "[HIGH] (international) Suspicious hreflang codes: ['uk']  (GB, not UK)"),
        (ORANGE, "normal", "[HIGH] (links) 1 link(s) navigate via JS without a real href"),
        (ORANGE, "normal", "[HIGH] (structured-data) 1 JSON-LD block(s) fail to parse"),
        (YELLOW, "normal", "[MEDIUM] (images) 3/3 images missing alt attribute"),
        (GRAY, "normal", "[LOW] (myth) meta keywords present (Google ignores it)"),
        (DIM, "normal", "... 9 more findings"),
    ]
    at = t + 0.6
    for i, (color, weight, s) in enumerate(lines):
        svg.text(24, y0 + lh * (i + 1.6), s, color, svg.appear(at + i * 0.22), weight=weight)
    svg.close_group()
    return svg.render()


def main():
    """Write both SVGs next to this script."""
    for name, content in (("before-after.svg", before_after()), ("auditor.svg", auditor())):
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as fh:
            fh.write(content + "\n")
        print("wrote", os.path.join("assets", name))


if __name__ == "__main__":
    main()
