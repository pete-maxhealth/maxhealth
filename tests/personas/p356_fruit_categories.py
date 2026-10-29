"""Persona 356 (v3.10.1246): everyday fruit is filed as fruit (it used to fall through to Other), pear and peach are no longer vegetables (they contain "pea"),
spears are not pears, and the neighbours that must NOT change stay as they were (cherry tomatoes, banana bread, peas, peanuts, peanut butter, strawberry jam).
Also: a user's own edit of a word survives, and a new fruit word shows in the shopping-aisle name. Plain function checks on invented library names."""
import sys, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 900}, service_workers='block')
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    p = ctx.new_page(); p.on('pageerror', lambda e: errs.append(str(e)[:200])); ev = p.evaluate
    p.goto('http://localhost:5757/'); p.wait_for_timeout(1500); ev("startDemoMode('doris')"); p.wait_for_timeout(2500)
    cats = lambda n: ev("detectFoodCategory(%r)" % n)
    for n in ['Apple', 'Bananas', 'Green grapes', 'Lemon', 'Limes', 'Plums', 'Cherries', 'Kiwi', 'Mango', 'Pineapple chunks', 'Grapefruit', 'Apricots', 'Pears', 'Pear', 'Peaches', 'Peach slices', 'Nectarines', 'Watermelon', 'Zed lemon juice', 'Apple juice']:
        c = cats(n)
        if 'fruit' not in c or 'vegetable' in c: f.add('BUG', f'{n}: should be fruit, got {c}')
    for n in ['Asparagus spears', 'Broccoli spears']:
        c = cats(n)
        if 'fruit' in c: f.add('BUG', f'{n}: a spear is not a pear: {c}')
    if cats('Broccoli spears') != ['vegetable']: f.add('BUG', f'Broccoli spears should stay a vegetable: {cats("Broccoli spears")}')
    for n, want in [('Cherry tomatoes', ['vegetable', 'salad']), ('Banana bread', ['bread', 'grain']), ('Garden peas', ['vegetable']), ('Peanuts', ['protein', 'fat']),
                    ('Peanut', ['protein', 'fat']), ('Peanut butter', ['nut butter']), ('Strawberry jam', ['fruit', 'sweet']), ('Banana milk', ['dairy']), ('Grapeseed oil', ['protein', 'fat']),
                    ('Chicken', ['meat', 'protein']), ('Orange', ['fruit', 'sweet']), ('Avocado', ['fat', 'fruit'])]:
        c = cats(n)
        if c != want: f.add('BUG', f'{n}: unchanged neighbour should be {want}, got {c}')
    # library items: browse categories come out the same way, and a manual override still wins
    ev("""(()=>{const lib=loadLibrary(); lib.push({name:'Zed pear',portion:'100g',kcal:57,protein:0,fat:0,carbs:15,fibre:3,polyols:0});
      lib.push({name:'Zed banana',portion:'100g',kcal:89,protein:1,fat:0,carbs:23,fibre:2,polyols:0,categories:['sweet']}); saveLibrary(lib);})()""")
    if ev("getItemCategories(loadLibrary().find(x=>x.name==='Zed pear'))") != ['fruit', 'sweet']: f.add('BUG', 'library item Zed pear browse categories')
    if ev("getItemCategories(loadLibrary().find(x=>x.name==='Zed banana'))") != ['sweet']: f.add('BUG', "a person's own category choice must still win")
    # the person's own edit of a built-in word survives (Manage Categories): lemon -> sweet only
    ev("CATEGORY_MAP['lemon']=['sweet']; _categoryCustom['lemon']=['sweet']; refreshCategoryWords(); 0")
    if cats('Lemon') != ['sweet']: f.add('BUG', 'own edit of lemon should apply')
    p.reload(); p.wait_for_timeout(1800)
    if ev("detectFoodCategory('Lemon')") != ['sweet']: f.add('BUG', 'own edit of lemon should survive a reload')
    if ev("detectFoodCategory('Lime')") != ['fruit', 'sweet']: f.add('BUG', 'other fruit words unaffected by that edit')
    # fuzzy library match: the same fruit matches itself, a different food does not
    ev("""(()=>{const lib=loadLibrary(); lib.push({name:'Zed banana bread',portion:'100g',kcal:300,protein:5,fat:10,carbs:45,fibre:1,polyols:0}); saveLibrary(lib);})()""")
    r = ev("(()=>{const m=fuzzyFindInLibrary('Zed banana bread'); return m? (m.name||m.item&&m.item.name||'?') : null})()")
    if r and 'bread' not in r.lower(): f.add('BUG', f'banana bread should not match the plain banana: {r}')
    if errs: f.add('JS-exception', errs[0])
    b.close()
bad = any(s in ('BUG', 'JS-exception') for s, _ in f)
for s, m in f: print(s, m)
print('BUGS' if bad else 'OK', len(f)); sys.exit(1 if bad else 0)
