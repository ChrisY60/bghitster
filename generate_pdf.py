import json
import os
import io
import qrcode
from fpdf import FPDF
from PIL import Image

# ── Configuration ────────────────────────────────────────────────────────────
# After hosting player.html (e.g. GitHub Pages), set this to your URL.
# Example: "https://your-name.github.io/hitster/player.html"
# Leave as None to use direct YouTube links instead (title will be visible).
PLAYER_BASE_URL = None

CARD_W  = 90   # mm
CARD_H  = 130  # mm
COLS    = 2
ROWS    = 3

# Windows system fonts (Cyrillic support)
FONT_REGULAR = r"C:\Windows\Fonts\arial.ttf"
FONT_BOLD    = r"C:\Windows\Fonts\arialbd.ttf"

OUTPUT_FILE = "hitster_bulgaria.pdf"
# ─────────────────────────────────────────────────────────────────────────────


def song_url(youtube_id: str) -> str:
    if PLAYER_BASE_URL:
        return f"{PLAYER_BASE_URL}?v={youtube_id}"
    return f"https://www.youtube.com/watch?v={youtube_id}"


def make_qr_bytes(url: str) -> bytes:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
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


def draw_card(pdf: HitsterPDF, song: dict, x: float, y: float):
    # ── Card background ───────────────────────────────────────────────────────
    pdf.set_fill_color(248, 248, 248)
    pdf.rect(x, y, CARD_W, CARD_H, "F")

    # ── Outer border ─────────────────────────────────────────────────────────
    pdf.set_draw_color(20, 90, 180)
    pdf.set_line_width(0.8)
    pdf.rect(x, y, CARD_W, CARD_H)

    # ── Header bar ───────────────────────────────────────────────────────────
    pdf.set_fill_color(20, 90, 180)
    pdf.rect(x, y, CARD_W, 14, "F")

    pdf.set_font("Arial", "B", 9)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(x, y + 3)
    pdf.cell(CARD_W, 7, "ХИТСТЕР  БЪЛГАРИЯ", align="C")

    # ── QR code ──────────────────────────────────────────────────────────────
    qr_size = 62
    qr_x = x + (CARD_W - qr_size) / 2
    qr_y = y + 18
    url = song_url(song["youtube_id"])
    qr_buf = make_qr_bytes(url)
    pdf.image(qr_buf, qr_x, qr_y, qr_size, qr_size)

    # ── Divider line ─────────────────────────────────────────────────────────
    div_y = qr_y + qr_size + 4
    pdf.set_draw_color(200, 200, 200)
    pdf.set_line_width(0.3)
    pdf.line(x + 6, div_y, x + CARD_W - 6, div_y)

    # ── Song name ─────────────────────────────────────────────────────────────
    pdf.set_font("Arial", "B", 10)
    pdf.set_text_color(20, 20, 20)
    pdf.set_xy(x + 3, div_y + 3)
    pdf.multi_cell(CARD_W - 6, 5.5, song["name"], align="C")

    # ── Artist ────────────────────────────────────────────────────────────────
    pdf.set_font("Arial", "", 8.5)
    pdf.set_text_color(90, 90, 90)
    pdf.set_xy(x + 3, pdf.get_y() + 1)
    pdf.multi_cell(CARD_W - 6, 4.5, song["artist"], align="C")

    # ── Year (bottom strip) ───────────────────────────────────────────────────
    strip_h = 20
    strip_y = y + CARD_H - strip_h
    pdf.set_fill_color(240, 246, 255)
    pdf.rect(x, strip_y, CARD_W, strip_h, "F")

    pdf.set_draw_color(20, 90, 180)
    pdf.set_line_width(0.3)
    pdf.line(x + 6, strip_y, x + CARD_W - 6, strip_y)

    pdf.set_font("Arial", "B", 22)
    pdf.set_text_color(20, 90, 180)
    pdf.set_xy(x, strip_y + 2)
    pdf.cell(CARD_W, strip_h - 4, str(song["year"]), align="C")


def create_pdf(songs: list, output: str):
    pdf = HitsterPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(False)
    pdf.add_font("Arial", "",  FONT_REGULAR)
    pdf.add_font("Arial", "B", FONT_BOLD)

    page_w, page_h = 210, 297
    cards_per_page = COLS * ROWS

    margin_x = (page_w - COLS * CARD_W) / (COLS + 1)
    margin_y = (page_h - ROWS * CARD_H) / (ROWS + 1)

    for i, song in enumerate(songs):
        if i % cards_per_page == 0:
            pdf.add_page()

        slot = i % cards_per_page
        col  = slot % COLS
        row  = slot // COLS

        card_x = margin_x + col * (CARD_W + margin_x)
        card_y = margin_y + row * (CARD_H + margin_y)

        draw_card(pdf, song, card_x, card_y)

    pdf.output(output)
    print(f"PDF saved: {output}  ({len(songs)} cards)")


if __name__ == "__main__":
    songs_path = os.path.join(os.path.dirname(__file__), "songs.json")
    with open(songs_path, encoding="utf-8") as f:
        songs = json.load(f)

    create_pdf(songs, OUTPUT_FILE)
