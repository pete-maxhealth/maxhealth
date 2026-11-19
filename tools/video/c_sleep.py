"""Clip: Sleep report and Sleep and your food (Reports). Sam demo persona. Alba."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from clip_lib import run_clip, sheet
LINES = [
 "How does Sam's sleep line up with how he eats? Open Insights, then Reports.",
 "The Sleep report shows his average night, how consistent he is, and how his sleep is split.",
 "Below it, Sleep and your food sets good nights against short ones, so you can see whether a short night shows up in what he eats the next day.",
 "It is an association in your own data, never proof of cause, and it only uses nights you actually logged.",
 "Sleep, next to everything else. Sample data shown. Not medical advice.",
]
def s0(h): h.tap('#maintab-insights', 0.9); h.tap('#insightstab-reports', 1.2)
def s1(h): h.smooth('#sleep-report-section', 'start'); h.wait(2)
def s2(h): h.smooth('#sleep-ketosis-section', 'start'); h.wait(2)
def s3(h): h.wait(2.5)
def s4(h): h.wait(2)
run_clip('sleep', LINES, [s0, s1, s2, s3, s4], 'http://localhost:5757/?demo=sam')
sheet('sleep', [6, 14, 24, 32, 38])
