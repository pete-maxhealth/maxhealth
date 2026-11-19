"""Clip: the Move tab (steps, exercise with calories and effort worked out, What if, Sessions and routines). Alex demo persona. Alba."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from clip_lib import run_clip, sheet
LINES = [
 "This is Alex, and this is the Move tab. Steps, exercise and training all live in one place.",
 "Tick an exercise, type just the minutes, and the calories and effort are worked out for you.",
 "Not sure what a walk is worth? What if lets you try it first. Pick an exercise, tap how hard, and nothing is saved until you tap Log.",
 "Sessions and routines are right here too, so strength training logs the same way.",
 "Steps, exercise and training, without a spreadsheet. Sample data shown. Not medical advice.",
]
def s0(h): h.tap('#maintab-today', 0.8); h.tap('#todaytab-move', 1.2)
def s1(h):
    h.page.evaluate("document.getElementById('activityCard').scrollIntoView({behavior:'smooth',block:'start'})"); h.wait(1.4)
    h.tap('#activityCard input[type=checkbox] >> nth=0', 0.6)
    h.tap('#activityCard input.activity-dur >> nth=0', 0.4); h.page.keyboard.type('40', delay=300); h.wait(1.5)
def s2(h):
    h.smooth('#whatIf', 'start'); h.tap('#whatIf input >> nth=0', 0.4); h.page.keyboard.type('40', delay=300); h.tap('#whatIf >> text=Easy', 1.0); h.tap('#whatIf >> text=Hard', 1.5)
def s3(h): h.smooth('#activityCard', 'end'); h.wait(1.5)
def s4(h): h.wait(1)
run_clip('move', LINES, [s0, s1, s2, s3, s4], 'http://localhost:5757/?demo=alex')
sheet('move', [6, 14, 24, 33, 38])
