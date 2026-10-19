"""Proof of concept: builds a print-ready PDF coffee table book from dad-movies.js.

Usage: python3 book/make-book.py   (needs: pip install reportlab)
Page: 8.5 x 11 in portrait plus 0.125 in bleed on every side. Each film is a two-page spread:
poster on the left (even) page, text, quote and fact on the right (odd) page.
"""
import json, subprocess, pathlib
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle

root = pathlib.Path(__file__).resolve().parent.parent
FONTS = "/System/Library/Fonts/Supplemental/"
pdfmetrics.registerFont(TTFont("Serif", FONTS + "Georgia.ttf"))
pdfmetrics.registerFont(TTFont("Serif-Italic", FONTS + "Georgia Italic.ttf"))
pdfmetrics.registerFont(TTFont("Serif-Bold", FONTS + "Georgia Bold.ttf"))

# Films to include in the proof (oldest first): title -> (quote, speaker, fact)
EXTRAS = {
    "The Adventures of Robin Hood": ("Why, you speak treason! ... Fluently.", "Prince John and Robin Hood",
        "Warner Bros. first cast James Cagney as Robin Hood, but the part went to Errol Flynn. The film won three Academy Awards."),
    "The Wizard of Oz": ("There's no place like home.", "Dorothy",
        "Dorothy's slippers are silver in the original book. The filmmakers made them ruby to show off the new Technicolor."),
    "It's a Wonderful Life": ("Every time a bell rings, an angel gets his wings.", "Zuzu",
        "It disappointed at the box office in 1946. It became a Christmas staple decades later, after its copyright lapsed and TV stations began airing it constantly."),
    "Rear Window": ("We've become a race of Peeping Toms.", "Stella",
        "The entire film takes place in one apartment courtyard, a huge set built on a Paramount soundstage."),
    "High Noon": ("I've got to. That's the whole thing.", "Marshal Will Kane",
        "The story runs in close to real time, and clocks appear throughout. Gary Cooper won Best Actor for the role."),
    "The Searchers": ("That'll be the day.", "Ethan Edwards",
        "Buddy Holly wrote his hit \"That'll Be the Day\" after seeing the film. It was shot in Monument Valley."),
    "The Bridge on the River Kwai": ("Madness! ... Madness!", "Major Clipton",
        "It won seven Academy Awards, including Best Picture. Novelist Pierre Boulle was credited with the screenplay, though blacklisted writers Carl Foreman and Michael Wilson wrote it."),
    "Vertigo": ("You shouldn't keep souvenirs of a killing.", "Scottie Ferguson",
        "The film introduced the dolly zoom, now often called the \"Vertigo effect\". It later topped Sight & Sound's poll of the greatest films ever made."),
    "North by Northwest": ("The \"O\" stands for nothing.", "Roger Thornhill",
        "The Mount Rushmore finale was largely built on studio sets. The National Park Service would not allow filming that appeared to disrespect the monument."),
    "To Kill a Mockingbird": ("You never really understand a person until you consider things from his point of view.", "Atticus Finch",
        "Robert Duvall made his film debut as Boo Radley. Gregory Peck won the Oscar for Best Actor."),
    "Jaws": ("You're gonna need a bigger boat.", "Chief Brody",
        "The mechanical shark, nicknamed Bruce, kept breaking down. Spielberg showed it less, which made the film scarier."),
    "The Shawshank Redemption": ("Get busy living, or get busy dying.", "Andy Dufresne",
        "It earned seven Oscar nominations but was a modest box office disappointment. It found its audience later on home video and TV."),
}
PICKS = list(EXTRAS)

js = (root / "dad-movies.js").read_text() + "\nconsole.log(JSON.stringify(MOVIES));"
movies = json.loads(subprocess.run(["node", "-e", js], capture_output=True, text=True, check=True).stdout)
by_title = {m["title"]: m for m in movies}
films = sorted((by_title[t] for t in PICKS), key=lambda m: (m["year"], m["title"]))

BLEED = 0.125 * inch
TRIM_W, TRIM_H = 8.5 * inch, 11 * inch
W, H = TRIM_W + 2 * BLEED, TRIM_H + 2 * BLEED
PAPER = HexColor("#f7f4ee")
INK = HexColor("#1c1c1c")
MUTED = HexColor("#7a756c")
INNER = 1.0 * inch   # gutter-side margin on the text page
OUTER = 0.9 * inch

OUT = root / "book" / "dad-book-proof.pdf"
c = canvas.Canvas(str(OUT), pagesize=(W, H), initialFontName="Serif")
c.setTitle("Dad's Movies")
c.setAuthor("Tim Finnigan")
# Declare the trim box so printers can see where the cut falls
c.setTrimBox((BLEED, BLEED, BLEED + TRIM_W, BLEED + TRIM_H))
c.setBleedBox((0, 0, W, H))

def page_bg():
    c.setFillColor(PAPER)
    c.rect(0, 0, W, H, stroke=0, fill=1)

def tracked(x, y, text, font, size, color, space=2.4, align="left"):
    c.saveState()
    c.setFillColor(color)
    t = c.beginText()
    t.setFont(font, size)
    t.setCharSpace(space)
    width = pdfmetrics.stringWidth(text, font, size) + space * len(text)
    t.setTextOrigin(x - width / 2 if align == "center" else x, y)
    t.textOut(text)
    c.drawText(t)
    c.restoreState()

CX, CY = W / 2, H / 2

def half_title():          # page 1, right
    page_bg()
    tracked(CX, CY + 0.5 * inch, "A COLLECTION OF FAVORITES", "Serif", 8, MUTED, 3, "center")
    c.setFillColor(INK)
    c.setFont("Serif", 40)
    c.drawCentredString(CX, CY - 0.3 * inch, "Dad's Movies")
    c.setStrokeColor(INK)
    c.setLineWidth(0.5)
    c.line(CX - 0.35 * inch, CY - 0.75 * inch, CX + 0.35 * inch, CY - 0.75 * inch)
    c.showPage()

def dedication():          # page 2, left
    page_bg()
    c.setFillColor(INK)
    c.setFont("Serif-Italic", 14)
    c.drawCentredString(CX, CY + 0.1 * inch, "For Dad")
    tracked(CX, CY - 0.4 * inch, "WITH LOVE", "Serif", 7.5, MUTED, 3, "center")
    c.showPage()

def contents():            # page 3, right
    page_bg()
    x = BLEED + INNER
    right = BLEED + TRIM_W - OUTER
    tracked(x, H - BLEED - 1.4 * inch, "CONTENTS", "Serif", 8, MUTED, 3)
    y = H - BLEED - 2.0 * inch
    for i, m in enumerate(films):
        c.setFillColor(INK)
        c.setFont("Serif", 12)
        c.drawString(x, y, m["title"])
        c.setFillColor(MUTED)
        c.setFont("Serif", 9)
        c.drawRightString(right, y, str(4 + 2 * i))
        y -= 0.42 * inch
    c.showPage()

def poster_page(m):        # even (left) page
    page_bg()
    ph = 8.0 * inch
    pw = ph * 780 / 1170
    c.drawImage(str(root / m["poster"]), CX - pw / 2, CY - ph / 2, pw, ph)
    c.showPage()

def text_page(m, n):       # odd (right) page
    page_bg()
    quote, who, fact = EXTRAS[m["title"]]
    x = BLEED + INNER
    tw = TRIM_W - INNER - OUTER

    styles = {
        "title": ParagraphStyle("t", fontName="Serif", fontSize=28, leading=33, textColor=INK),
        "body": ParagraphStyle("b", fontName="Serif", fontSize=10.5, leading=17, textColor=INK),
        "quote": ParagraphStyle("q", fontName="Serif-Italic", fontSize=17, leading=24, textColor=INK),
        "fact": ParagraphStyle("f", fontName="Serif", fontSize=9.5, leading=15, textColor=MUTED),
    }
    title = Paragraph(m["title"], styles["title"])
    body = Paragraph(m["blurb"], styles["body"])
    q = Paragraph("\u201c" + quote + "\u201d", styles["quote"])
    f = Paragraph(fact, styles["fact"])
    h = {k: p.wrap(tw, H)[1] for k, p in (("title", title), ("body", body), ("q", q), ("f", f))}

    y = H - BLEED - 1.4 * inch
    tracked(x, y, str(m["year"]), "Serif", 9, MUTED, 3)
    y -= 0.25 * inch
    title.drawOn(c, x, y - h["title"]); y -= h["title"] + 0.25 * inch
    c.setFillColor(MUTED)
    c.setFont("Serif-Italic", 10.5)
    c.drawString(x, y, "Directed by " + m["director"]); y -= 0.45 * inch
    body.drawOn(c, x, y - h["body"]); y -= h["body"] + 0.75 * inch

    c.setStrokeColor(MUTED)
    c.setLineWidth(0.4)
    c.line(x, y, x + 0.35 * inch, y); y -= 0.4 * inch
    q.drawOn(c, x, y - h["q"]); y -= h["q"] + 0.15 * inch
    c.setFillColor(MUTED)
    c.setFont("Serif", 8.5)
    c.drawString(x, y - 8, "\u2014 " + who); y -= 0.8 * inch

    tracked(x, y, "DID YOU KNOW", "Serif", 7, MUTED, 2.5); y -= 0.22 * inch
    f.drawOn(c, x, y - h["f"])

    c.setFillColor(MUTED)
    c.setFont("Serif", 8)
    c.drawRightString(BLEED + TRIM_W - OUTER, BLEED + 0.5 * inch, str(n))
    c.showPage()

def colophon():            # last page, left
    page_bg()
    c.setFillColor(MUTED)
    c.setFont("Serif", 8)
    c.drawCentredString(CX, CY + 6, "Poster images from TMDB. This product uses the TMDB API")
    c.drawCentredString(CX, CY - 6, "but is not endorsed or certified by TMDB.")
    c.showPage()

half_title()
dedication()
contents()
for i, m in enumerate(films):
    poster_page(m)
    text_page(m, 5 + 2 * i)
colophon()
c.save()
print(f"wrote {OUT.relative_to(root)} ({3 + 2 * len(films) + 1} pages)")
