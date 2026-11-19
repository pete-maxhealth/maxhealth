"""Clip: Statistics (ask your own data a question and keep the answer). Sam demo persona. Alba."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from clip_lib import run_clip, sheet
LINES = [
 "Statistics is where you ask your own data a question, and keep the answer.",
 "Here are Sam's top ten foods by calories over the last thirty days, with the protein, fat and carbs behind each one.",
 "Filter by food, or by how things change over time.",
 "Tap Create to ask a new question. Each answer can be saved to your library, or shared.",
 "Your own numbers, answering your own questions. Sample data shown. Not medical advice.",
]
def s0(h): h.tap('#maintab-insights', 0.9); h.tap('#insightstab-stats', 1.2)
def s1(h): h.page.evaluate("window.scrollBy({top:260,behavior:'smooth'})"); h.wait(2.5); h.page.evaluate("window.scrollBy({top:260,behavior:'smooth'})"); h.wait(2)
def s2(h):
    h.page.evaluate("window.scrollTo({top:0,behavior:'smooth'})"); h.wait(1.2); h.tap('span.mh-chip:has-text("Over time")', 1.5); h.tap('span.mh-chip:has-text("All")', 1.0)
def s3(h): h.page.evaluate("window.scrollTo({top:0,behavior:'smooth'})"); h.wait(1); h.tap('button.run-btn:has-text("Create")', 2.5)
def s4(h): h.wait(2)
run_clip('statistics', LINES, [s0, s1, s2, s3, s4], 'http://localhost:5757/?demo=sam')
sheet('statistics', [6, 12, 20, 27, 34])
