"""Persona 519: the Move > Steps paragraph when a logged walk's estimated steps reach or pass the watch total (Pete 21 Nov: 11,098 estimated vs 10,958 counted read wrongly as "most of"). Checks the headline and the detail for
walk above the total, walk at 85-99% of it, and the normal cases staying as they were (extra credit, below baseline). NOT covered: translated wording (see p520 if added)."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings(); chk = lambda ok, m: None if ok else f.add('BUG', m)
with fresh_server() as root, sync_playwright() as pw:
    pg = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 844}, service_workers='block').new_page(); ev = pg.evaluate; errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:150]))
    pg.goto('http://localhost:5757/'); pg.wait_for_timeout(1000)
    ev("state.onboarded=true; saveState(); document.getElementById('onboardingOverlay')?.remove()")
    ev("switchTabById('move')"); pg.wait_for_timeout(500)
    def run(total, walk, remainder):
        ev("""([t,w,r])=>{localStorage.setItem('mh_steps_today',String(t)); window.getNonWalkingStepsToday=()=>({walkingSteps:w,remainder:r,total:t});
          window.calcNonWalkingStepsKcal=()=>0; window.getStepsBaseline=()=>5000; renderDailyStepsHeadline();}""", [total, walk, remainder]); pg.wait_for_timeout(600)
        return ev("""()=>{const h=document.getElementById(document.querySelector('[id*=tepsHeadline]')?.id||'stepsHeadline'); const d=document.querySelector('[id*=tepsDetail]'); return [h&&h.innerText, d&&d.innerText]}""")
    h, d = run(10958, 11098, 0)
    chk('accounts for all of your 10,958' in h, f'headline for walk above total: {h}')
    chk('11,098' in d and 'a little more than the 10,958' in d and 'treated as the walk' in d and 'essentially' not in d, f'detail for walk above total: {d}')
    h, d = run(10000, 12000, 0)
    chk('more than the 10,000' in d and 'a little more' not in d, f'big overshoot wording: {d}')
    h, d = run(10000, 9000, 1000)
    chk('accounts for most of your 10,000' in h and 'about 9,000 of today' in d, f'walk at 90%: {h} / {d}')
    h, d = run(10000, 4000, 6000)
    chk('walk' not in h.lower() or 'accounts for' not in h, f'normal day wrongly says the walk accounts for the steps: {h}')
    # the same paragraph in each language (translated by the page's own translator, numbers kept)
    for l, w in [('es', 'Tu paseo registrado'), ('de', 'Dein erfasster Spaziergang'), ('fr', 'Votre marche enregistrée'), ('tr', 'Kaydettiğin yürüyüş'), ('pt', 'A caminhada registada'), ('it', 'La camminata registrata'), ('pl', 'Zapisany spacer'), ('nl', 'Je geregistreerde wandeling')]:
        ev(f"localStorage.setItem('mh_lang','{l}')"); pg.reload(); pg.wait_for_timeout(1500)
        ev("state.onboarded=true; saveState(); document.getElementById('onboardingOverlay')?.remove(); switchTabById('move')"); pg.wait_for_timeout(500)
        h, d = run(10958, 11098, 0)
        chk(w in (d or '') and '11,098' in d and '10,958' in d, f'{l}: detail not translated with its numbers: {(d or "")[:80]}')
        chk('Today' not in (h or '') or l == 'xx', f'{l}: headline still English: {h}')
    for e in errs: f.add('JS-exception', e)
print('findings', len(f))
