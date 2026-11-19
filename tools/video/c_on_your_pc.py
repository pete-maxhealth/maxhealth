"""Clip: MaxedHealth works on your PC too (desktop browser, 1280x720). Doris demo persona. Alba. Low typing: three letters."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from clip_lib import run_clip, sheet
LINES = [
 "MaxedHealth works on your PC too. This is an ordinary desktop browser, with the same sample data as on a phone.",
 "Log, then the magnifier, then type the start of a name. Three letters is enough, and her own library answers first.",
 "Pick the food and a portion, and the calories and macros come from her library.",
 "To move between phone and PC, use a backup file or a QR code. It goes straight between your own devices, not through a server.",
 "Barcode and label photo work best with a phone camera, but everything else is the same. Sample data shown. Not medical advice.",
]
def s0(h): h.wait(2)
def s1(h): h.tap('#maintab-log', 1.0); h.tap('#searchBtn', 0.8); h.wait(0.6); h.page.type('#foodSearchInput', 'pep', delay=450); h.wait(0.8)
def s2(h): h.tap('#foodSearchPanel >> text=Peppers', 1.0); h.tap('button:has-text("150g")', 0.9); h.tap('button:has-text("LOG →")', 1.5)
def s3(h):
    h.tap('#maintab-settings', 0.9); h.tap('#settingstab-import', 1.0); h.smooth('#set-databackup-wrap', 'start'); h.wait(2)
def s4(h): h.wait(2.5)
run_clip('on_your_pc', LINES, [s0, s1, s2, s3, s4], 'http://localhost:5757/?demo=doris', viewport=(1280, 720))
sheet('on_your_pc', [6, 14, 22, 30, 36])
