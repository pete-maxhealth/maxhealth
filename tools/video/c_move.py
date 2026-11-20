"""Clip: the Move tab (20 Nov 2026 re-cut, Pete's note): steps, exercise, the full exercise list, cardio vs resistance, What if. Alex demo persona. Alba."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from clip_lib import run_clip, sheet
LINES = [
 "This is Alex, and this is the Move tab. Steps, exercise and training all live in one place.",
 "Tick an exercise, type just the minutes, and the calories and effort are worked out for you.",
 "Add another exercise opens a big list. Walking, running, cycling, rowing, badminton, yoga, kayaking and plenty more. Filter by indoor or outdoor, or by type.",
 "Everything you pick is either cardio or resistance. Swimming is cardio, so you log the minutes and how hard it was.",
 "Weights and bodybuilding are resistance. You log the sets and reps in Sessions and routines, and it counts as resistance training.",
 "Not sure what an exercise is worth? What if lets you try it first. Nothing is saved until you tap Log.",
 "Steps, cardio and resistance, in one place. Routines have their own short video. Sample data shown. Not medical advice.",
]
def s0(h): h.tap('#maintab-today', 0.8); h.tap('#todaytab-move', 1.2)
def s1(h):
    h.page.evaluate("document.getElementById('activityCard').scrollIntoView({behavior:'smooth',block:'start'})"); h.wait(1.4)
    h.tap('#activityRows .activity-row >> nth=0 >> input[type=checkbox]', 0.6)
    h.tap('#activityRows .activity-row >> nth=0 >> input.activity-dur', 0.4); h.page.keyboard.type('40', delay=300); h.wait(1.5)
def s2(h):
    h.tap('text=Add another exercise', 1.2)
    h.page.evaluate("document.getElementById('mhPickList').scrollBy({top:650,behavior:'smooth'})"); h.wait(2.2)
    h.tap('#mhPickWhere >> text=Indoor', 0.9); h.tap('#mhPickWhere >> text=Anywhere', 0.6)
    h.tap('#mhPickCats >> text=Racket', 1.2); h.tap('#mhPickCats >> text=Mind', 1.2)
    h.tap('#mhPickCats >> text=Water', 1.0)
def s3(h):
    h.caption('🏊 Cardio: log the minutes')
    h.tap('#mhPickList .mh-card >> text=Swimming (lengths)', 1.4)
    h.page.evaluate("document.getElementById('activityCard').scrollIntoView({behavior:'smooth',block:'start'})"); h.wait(1.2)
    h.tap('#activityRows .activity-row >> nth=1 >> input.activity-dur', 0.4); h.page.keyboard.type('30', delay=300); h.wait(2.0)
def s4(h):
    h.caption('🏋️ Resistance: sets and reps in Sessions')
    h.page.evaluate("document.getElementById('resistanceSimple').scrollIntoView({behavior:'smooth',block:'center'})"); h.wait(2.0)
    h.page.evaluate("document.getElementById('routineTrainBtn').scrollIntoView({behavior:'smooth',block:'center'})"); h.wait(2.0)
def s5(h):
    h.caption(''); h.smooth('#whatIf', 'start'); h.tap('#whatIf input >> nth=0', 0.4); h.page.keyboard.type('40', delay=300); h.tap('#whatIf >> text=Easy', 1.0); h.tap('#whatIf >> text=Hard', 1.5)
def s6(h): h.wait(1)
run_clip('move', LINES, [s0, s1, s2, s3, s4, s5, s6], 'http://localhost:5757/?demo=alex')
sheet('move', [6, 14, 24, 34, 44, 54, 62])
