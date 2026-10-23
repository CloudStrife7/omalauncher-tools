"""Make the TV guide's art with Codex: Zach plus the one object he is using, on flat green, keyed to
transparent. One image per scene, no text in the art.  python make_art.py [scene ...]"""
import sys, tempfile
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path.home() / "Documents" / "!index" / "shared" / "codex"))
from codex_image import run_image  # noqa: E402

HERE = Path(__file__).resolve().parent
STYLE = HERE / "reference-style.png"
ZACH = Path.home() / "Documents" / "canon" / "characters" / "zach" / "identity" / "ZACH-FRONT-FACING-FIXED-GOATEE.png"

BASE = ("Use the FIRST reference image only for the art style: chunky dithered pixel art with visible pixels, "
        "orange and teal accents, warm rim light. Use the SECOND reference image for the character Zach: spiky red "
        "hair, black sunglasses, goatee, black jacket, fingerless gloves. His eyes are NEVER visible: the sunglasses "
        "have solid opaque black lenses that fully cover his eyes, no eye, iris or eyebrow-gap showing above, below or "
        "through the lenses. He must look like the same person as in the "
        "first image. Draw ONLY Zach and the one object he is using. No room, no furniture except that one object, no "
        "floor, no wall, no scenery. Background: flat solid pure green RGB(0,255,0), nothing green on Zach or the object. "
        "Zach and the object fill the frame, landscape about 4:3, full action pose. NO text, NO letters, NO logos. ")
TAIL = " Generate exactly one image. Do not write any files."

SCENES = {
    "gf-1-under-couch": "Object: the bottom front edge of a dark couch, only a short section, with a gap underneath. "
        "Zach lies on his side on the floor line with one arm stretched far under the couch, a small flashlight in "
        "his other hand, one eye squinting into the gap. A few dust bunnies. Searching for a lost TV remote.",
    "gf-2-cushions": "Object: a dark couch seat with two thick cushions. Zach sits on it leaning forward, both arms "
        "pushed deep between the cushions, one cushion lifted in the air. A coin, a fork and a game cartridge are "
        "popping out of the gap. Puzzled frown.",
    "gf-3-behind-tv": "Object: the back of a big flat TV seen at an angle, with ports and a tangle of cables. Zach is "
        "squeezed behind it, peeking out around its side, a flashlight in his teeth, reaching toward the ports. "
        "Searching for a lost remote.",
    "gf-4-fridge": "Object: an open white fridge, shelves visible, cold blue-white light spilling out. Zach stands "
        "in front of it holding a milk carton, looking confused at the shelves. A small floating pixel question mark "
        "(a symbol, not a letter) above his head.",
    "gf-5-phone-widget": "Object: a modern smartphone held up in Zach's hand, screen toward the viewer. The screen "
        "shows a glowing remote-control widget: a round orange D-pad with four arrows and a centre OK button, plus "
        "small round buttons for home, back and volume. Zach looks relaxed with a confident half-smile, thumb on the "
        "screen. No remote in the picture.",
    "gf-7-empty-armrest": "Object: a whole dark fabric couch, instantly recognizable as a couch: a tall backrest, two "
        "thick seat cushions, and a rounded armrest on each end, short wooden legs, seen from the front at a slight "
        "angle, wide in the frame. Zach stands in front of the left end of the couch, one hand on the back of his "
        "neck and his head tilted, a confused, puzzled posture, looking at the couch's RIGHT armrest. The right "
        "armrest's flat top is EMPTY. An orange DASHED LINE made of small pixel dashes runs from near his head to "
        "the right armrest top, and on that armrest top sits an empty rectangle drawn only as an orange dashed "
        "outline, about the size of a TV remote, marking where the remote should be. Nothing inside the rectangle. "
        "A small floating pixel question mark (a symbol, not a letter) above his head. Landscape about 4:3.",
    "gf-6-pair-code": "Object: an open laptop. Zach sits behind it typing with both hands, leaning in, focused. The "
        "laptop screen faces the viewer and shows a glowing teal input box with a blinking cursor (a plain box, no "
        "letters). A small floating TV icon (a symbol) above the laptop glows orange.",
}


def key_green(im):
    """Green screen to transparent, with the green spill pulled out of the edge pixels."""
    im = im.convert("RGBA")
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            d = g - max(r, b)
            if d > 70:
                px[x, y] = (0, 0, 0, 0)
            elif d > 20:
                px[x, y] = (r, max(r, b), b, int(255 * (70 - d) / 50))
            elif d > 0:
                px[x, y] = (r, max(r, b), b, a)
    return im


def make(name):
    out = HERE / f"{name}.png"
    raw = HERE / "raw" / f"{name}.png"
    if out.exists():
        print("have", name); return
    raw.parent.mkdir(exist_ok=True)
    if not raw.exists():
        print("codex:", name, flush=True)
        with tempfile.TemporaryDirectory() as work:
            r = run_image(BASE + SCENES[name] + TAIL, [STYLE, ZACH], extra_args=("-C", work))
        if not r.images:
            print("NO IMAGE for", name, "exit", r.exit, r.log[-600:], flush=True); return
        Image.open(r.images[-1]).convert("RGB").save(raw)
        for p in r.images:
            p.unlink(missing_ok=True)
        if r.session:
            r.session.unlink(missing_ok=True)
        print("  %.0fs -> %s" % (r.seconds, raw), flush=True)
    im = key_green(Image.open(raw))
    im = im.crop(im.getbbox())
    im.save(out)
    out.with_name(out.name + ".tags.txt").write_text(
        f"{SCENES[name].split(':',1)[1].strip()}\ncharacters: Zach\nscene: TV remote guide, keyed sprite on transparent\nobjects: {name}\n",
        encoding="utf-8")
    print("keyed ->", out, im.size, flush=True)


for n in (sys.argv[1:] or list(SCENES)):
    make(n)
