import json
import os
import io
import qrcode
from fpdf import FPDF
from PIL import Image

# ── Configuration ────────────────────────────────────────────────────────────
# GitHub Pages URL — update after deploying.
PLAYER_BASE_URL = "https://chrisy60.github.io/bghitster/player.html"

# Windows fonts (Cyrillic support)
FONT_REGULAR = r"C:\Windows\Fonts\arial.ttf"
FONT_BOLD    = r"C:\Windows\Fonts\arialbd.ttf"

OUTPUT_FILE  = "hitster_bulgaria.pdf"
# ─────────────────────────────────────────────────────────────────────────────

PAGE_W, PAGE_H = 210, 297  # A4 mm


def song_url(youtube_id: str) -> str:
    return f"{PLAYER_BASE_URL}?v={youtube_id}"


def make_qr_buf(url: str):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=12,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


class HitsterPDF(FPDF):
    pass


def add_qr_page(pdf: HitsterPDF, song: dict):
    """Page 1 for each song: just the QR code, large and centred."""
    pdf.add_page()

    # White background (already default)
    # Subtle header
    pdf.set_fill_color(13, 13, 13)
    pdf.rect(0, 0, PAGE_W, 18, "F")
    pdf.set_font("Arial", "B", 10)
    pdf.set_text_color(29, 185, 84)
    pdf.set_xy(0, 4)
    pdf.cell(PAGE_W, 8, "ХИТСТЕР БЪЛГАРИЯ", align="C")

    # QR code — very large, centered vertically
    qr_size = 150
    qr_x = (PAGE_W - qr_size) / 2
    qr_y = (PAGE_H - qr_size) / 2 - 5
    url = song_url(song["youtube_id"])
    buf = make_qr_buf(url)
    pdf.image(buf, qr_x, qr_y, qr_size, qr_size)

    # Tiny instruction below QR
    pdf.set_font("Arial", "", 9)
    pdf.set_text_color(160, 160, 160)
    pdf.set_xy(0, qr_y + qr_size + 8)
    pdf.cell(PAGE_W, 6, "Сканирай с приложението Хитстер БГ", align="C")

    # Subtle footer
    pdf.set_fill_color(13, 13, 13)
    pdf.rect(0, PAGE_H - 14, PAGE_W, 14, "F")


def add_info_page(pdf: HitsterPDF, song: dict):
    """Page 2 for each song: song name, artist, year — large and centred."""
    pdf.add_page()

    # Dark full-page background
    pdf.set_fill_color(13, 13, 13)
    pdf.rect(0, 0, PAGE_W, PAGE_H, "F")

    # Green top bar
    pdf.set_fill_color(29, 185, 84)
    pdf.rect(0, 0, PAGE_W, 6, "F")

    # "ХИТСТЕР БЪЛГАРИЯ" logo
    pdf.set_font("Arial", "B", 11)
    pdf.set_text_color(29, 185, 84)
    pdf.set_xy(0, 18)
    pdf.cell(PAGE_W, 8, "ХИТСТЕР БЪЛГАРИЯ", align="C")

    # Divider
    pdf.set_draw_color(40, 40, 40)
    pdf.set_line_width(0.4)
    pdf.line(30, 32, PAGE_W - 30, 32)

    # Year — big
    pdf.set_font("Arial", "B", 72)
    pdf.set_text_color(29, 185, 84)
    pdf.set_xy(0, 70)
    pdf.cell(PAGE_W, 60, str(song["year"]), align="C")

    # Song name
    pdf.set_font("Arial", "B", 22)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(20, 145)
    pdf.multi_cell(PAGE_W - 40, 12, song["name"], align="C")

    # Artist
    pdf.set_font("Arial", "", 14)
    pdf.set_text_color(160, 160, 160)
    artist_y = pdf.get_y() + 4
    pdf.set_xy(20, artist_y)
    pdf.multi_cell(PAGE_W - 40, 8, song["artist"], align="C")

    # Bottom bar
    pdf.set_fill_color(29, 185, 84)
    pdf.rect(0, PAGE_H - 6, PAGE_W, 6, "F")


def create_pdf(songs: list, output: str):
    pdf = HitsterPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(False)
    pdf.add_font("Arial", "",  FONT_REGULAR)
    pdf.add_font("Arial", "B", FONT_BOLD)

    for song in songs:
        add_qr_page(pdf, song)
        add_info_page(pdf, song)

    pdf.output(output)
    print(f"PDF saved: {output}  ({len(songs)} songs, {len(songs)*2} pages)")


if __name__ == "__main__":
    songs_path = os.path.join(os.path.dirname(__file__), "songs.json")
    with open(songs_path, encoding="utf-8") as f:
        songs = json.load(f)

    create_pdf(songs, OUTPUT_FILE)
