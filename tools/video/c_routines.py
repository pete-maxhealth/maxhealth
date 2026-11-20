"""Clip: training routines (20 Nov 2026): use an existing one, clone one as a template, or build from scratch. Alex demo persona. Alba."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from clip_lib import run_clip, sheet
LINES = [
 "Training routines. On the Move tab, tap Train and your saved routines are right there. Pick Full Body, and every exercise, with its sets and reps, is ready to go.",
 "Each exercise can start from the template or from what you did last time. Change only what's different, then log the whole session in one go.",
 "To make a new routine, start from one you already have. Tap Routines, then Clone, give it a name, and change whatever you like.",
 "Or build one from scratch. Name it, then tap exercises from your list to add them. Sets and reps are optional.",
 "A free workout can be saved as a routine when you finish it, so next time it's one tap.",
 "Use one, clone one, or build your own. Sample data shown. Not medical advice.",
]
def s0(h):
    h.tap('#maintab-today', 0.8); h.tap('#todaytab-move', 1.2)
    h.page.evaluate("document.getElementById('routineTrainBtn').scrollIntoView({behavior:'smooth',block:'center'})"); h.wait(1.4)
    h.tap('#routineTrainBtn', 1.2); h.tap('#routineListContainer >> text=Full Body', 1.2)
def s1(h):
    h.page.evaluate("document.getElementById('routineListContainer').scrollIntoView({behavior:'smooth',block:'start'})"); h.wait(1.6)
    h.page.evaluate("window.scrollBy({top:420,behavior:'smooth'})"); h.wait(2.0)
def s2(h):
    h.page.evaluate("showRoutineList()"); h.wait(1.0)
    h.page.evaluate("document.getElementById('routineListContainer').scrollIntoView({behavior:'smooth',block:'start'})"); h.wait(1.2)
    h.tap('#routineListContainer >> text=Clone >> nth=0', 1.4)
    h.tap('#appModalConfirm', 1.6)
    h.page.evaluate("document.getElementById('routineListContainer').scrollIntoView({behavior:'smooth',block:'start'})"); h.wait(1.2)
    h.tap('#routineListContainer button:has-text("Save")', 1.4)
def s3(h):
    h.page.evaluate("showRoutineList()"); h.wait(0.8)
    h.page.evaluate("document.getElementById('routineListContainer').scrollIntoView({behavior:'smooth',block:'start'})"); h.wait(1.0)
    h.tap('text=Create another routine', 1.2)
    h.tap('#newRoutineName', 0.4); h.page.keyboard.type('Quick Legs', delay=250); h.wait(0.6)
    h.tap('#routineQuickChips span:text-is("Bench Press")', 0.8); h.tap('#routineQuickChips span:text-is("Rowing")', 0.8); h.tap('#routineQuickChips span:text-is("Press Ups")', 1.2)
def s4(h):
    h.page.evaluate("window.scrollBy({top:300,behavior:'smooth'})"); h.wait(1.0)
    h.tap('text=Save routine', 1.5)
    h.page.evaluate("document.getElementById('routineListContainer').scrollIntoView({behavior:'smooth',block:'start'})"); h.wait(1.5)
def s5(h): h.wait(1.5)
run_clip('routines', LINES, [s0, s1, s2, s3, s4, s5], 'http://localhost:5757/?demo=alex')
sheet('routines', [4, 14, 24, 36, 48, 56])
