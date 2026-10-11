"""Persona 80: Open all / Close all act only on the chosen Filter group and never reveal the content of hidden cards; Show all restores a fully hidden screen."""
import sys, re; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch()
    page = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block').new_page()
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("localStorage.setItem('mh_onboarded','1')"); page.reload(); page.wait_for_timeout(1500)
    ev = page.evaluate
    ev("switchTab('settings'); switchSubTab('settings','manage'); mhTopicApply('manage')"); page.wait_for_timeout(400)
    click = lambda l: (ev("l=>[...document.querySelectorAll('#view-manage .mh-pills-toolbar button')].find(b=>b.innerText===l).click()", l), page.wait_for_timeout(250))
    wrapDisp = lambda k: ev("(k)=>{const e=document.getElementById(GENERIC_SECTION_IDS.manage[k][1]);return e?(e.style.display||getComputedStyle(e).display):'missing'}", k)
    keys = ev("getGenericOrder('manage')")
    # hidden cards stay hidden through Open all
    ev("(k)=>{toggleGenericSectionHidden('manage',k)}", keys[0]); click('Open all')
    if wrapDisp(keys[0]) != 'none': f.add('BUG', 'Open all revealed the content of a hidden card')
    # group scoped: choose first group, Close all only closes that group's cards
    grp = ev("Object.keys(MH_TOPIC_SCOPES.manage.groups)[0]"); gkeys = ev("(g)=>MH_TOPIC_SCOPES.manage.groups[g].keys", grp)
    click('Open all'); ev("(g)=>mhTopicSet('manage', g)", grp); page.wait_for_timeout(200); click('Close all')
    other = [k for k in keys if k not in gkeys and k != keys[0]]
    if not other: f.add('BUG', 'test needs a card outside the group')
    elif any(wrapDisp(k) == 'none' for k in other): f.add('BUG', 'Close all on a filtered group closed cards outside the group')
    # fully hidden screen can be recovered in one tap
    ev("(ks)=>{ks.forEach(k=>{ if(!getGenericHidden('manage').includes(k)) toggleGenericSectionHidden('manage',k)}); mhTopicApply('manage')}", keys)
    if len(ev("getGenericHidden('manage')")) != len(keys): f.add('BUG', 'setup failed')
    ev("showAllGenericHidden('manage')")
    if ev("getGenericHidden('manage').length") != 0: f.add('BUG', 'Show all did not restore hidden cards')
print('findings', len(f)); sys.exit(1 if f else 0)
