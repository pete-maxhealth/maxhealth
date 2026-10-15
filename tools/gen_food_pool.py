#!/usr/bin/env python3
"""Builds the shared starter food + recipe pool (v3.10.1055).
Writes starter_packs/food_pool.json, injects `const MH_FOOD_POOL = {...};` into maxhealth.html (replacing the old demo arrays and
generateDemoLibrary/Recipes), and flags every starter pack file with "foodPool": true. Values are typical reference figures per 100 g
(labelled 'starter' in the app: check against your own labels). Run: python3 tools/gen_food_pool.py"""
import json, glob, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# name, portion g, kcal, protein, carbs, fat  (all per 100 g)
F = [
('Chicken breast, grilled',150,165,31,0,3.6),('Chicken thigh, roasted',120,209,26,0,11),('Turkey mince, lean, cooked',150,150,27,0,4.5),('Lean beef mince, cooked',150,174,26,0,7.7),
('Rump steak, grilled',150,190,28,0,8),('Beef stewing steak, cooked',150,190,30,0,7),('Pork loin chop, grilled',130,195,29,0,8),('Ham, lean',50,107,18,1.5,3.5),
('Salmon fillet, baked',130,208,22,0,13),('Smoked salmon',50,117,18,0,4.5),('Tinned salmon',100,142,20,0,6.3),('Cod fillet, baked',140,105,23,0,1),('Haddock, baked',140,90,20,0,0.6),
('Sea bass, baked',140,97,18,0,2),('Tuna in spring water, drained',110,116,26,0,1),('Sardines in olive oil, drained',90,208,25,0,11.5),('Anchovies, canned',30,210,29,0,10),
('Mackerel, grilled',120,262,24,0,18),('Prawns, cooked',100,99,24,0,0.6),('Egg, boiled',50,155,13,1.1,11),('Egg whites',100,52,11,0.7,0.2),('Tofu, firm',100,144,17,2.8,8.7),
('Tempeh',100,192,20,7.6,11),('Edamame beans',80,121,11,9,5),('Whey protein powder',30,400,80,8,6),('Greek yoghurt, 0% fat',170,59,10,3.6,0.4),('Skyr',150,63,11,4,0.2),
('Kefir',150,41,3.4,4.5,1),('Low-fat yoghurt',125,63,5,7,1.5),('Cottage cheese',100,98,11,3.4,4.3),('Cheddar cheese',30,416,25,0.1,34.9),('Mozzarella',60,280,22,2.2,22),
('Feta cheese',40,264,14,4,21),('Halloumi',50,321,21,2.2,25),('Goat cheese',30,364,22,0.1,30),('Ricotta',60,174,11,3,13),('Brie',30,334,21,0.5,28),('Parmesan',20,431,38,4,29),
('Cream cheese',30,342,6,4,34),('Double cream',30,467,1.7,2.7,50),('Single cream',30,195,3.3,4,19),('Whole milk',200,64,3.4,4.7,3.6),('Skimmed milk',200,34,3.4,5,0.1),
('Soy milk, unsweetened',200,33,3.3,0.6,1.8),('Almond milk, unsweetened',200,15,0.6,0.3,1.2),('Oat milk',200,46,1,6.7,1.5),('Butter',10,717,0.9,0.1,81),('Olive oil',10,884,0,0,100),
('Coconut oil',10,892,0,0,99),('Coconut milk, full fat',100,197,2,2.8,21),('Mayonnaise',15,680,1,1,75),('Bacon, grilled',40,417,30,1,32),('Pork sausages, grilled',100,300,14,3,26),
('Lamb chops, grilled',120,290,25,0,21),('Pork belly, roasted',120,330,24,0,26),('Salami',30,425,22,1,37),('Broccoli, steamed',90,35,2.4,7,0.4),('Cauliflower',100,25,2,5,0.3),
('Cauliflower rice',150,25,2,3,0.3),('Spinach',80,23,2.9,3.6,0.4),('Kale',60,35,2.9,4.4,1.5),('Cabbage',80,25,1.3,5.8,0.1),('Mixed salad leaves',80,17,1.2,2,0.3),
('Cucumber',80,15,0.7,3.6,0.1),('Tomatoes',120,18,0.9,3.9,0.2),('Sun-dried tomatoes',20,258,14,56,3),('Passata',100,29,1.4,5,0.1),('Peppers',100,31,1,6,0.3),
('Courgette',100,17,1.2,3.1,0.3),('Aubergine',100,25,1,6,0.2),('Artichoke hearts',80,47,3,11,0.2),('Asparagus',100,20,2.2,2,0.1),('Green beans',90,31,1.8,7,0.2),
('Mushrooms',80,22,3.1,3.3,0.3),('Onion',80,40,1.1,9,0.1),('Leeks',80,61,1.5,14,0.3),('Garlic',5,149,6.4,33,0.5),('Celery',50,14,0.7,3,0.2),('Carrots',80,41,0.9,10,0.2),
('Beetroot, cooked',80,44,1.7,10,0.2),('Butternut squash, roasted',150,45,1,12,0.1),('Sweet potato, baked',200,90,2,21,0.1),('Potatoes, boiled',200,72,1.8,16,0.1),
('Peas',80,81,5.4,14,0.4),('Sweetcorn',80,86,3.2,19,1.2),('Olives',30,115,0.8,6,11),('Avocado',70,160,2,9,15),('Lemon juice',15,22,0.4,6.9,0.2),
('Porridge oats',40,372,11,60,8),('Muesli, no added sugar',50,340,10,60,6),('Bran flakes',40,320,10,67,2),('Granola',40,450,10,60,18),('White rice, cooked',180,130,2.7,28,0.3),
('Brown rice, cooked',180,112,2.3,23,0.8),('Wholemeal pasta, cooked',180,124,5,25,1),('Noodles, cooked',180,138,4.5,25,2),('Couscous, cooked',150,112,3.8,23,0.2),
('Bulgur wheat, cooked',150,83,3.1,18.6,0.2),('Pearl barley, cooked',150,123,2.3,28,0.4),('Quinoa, cooked',150,120,4.4,21,1.9),('Wholemeal bread',36,247,13,41,3.4),
('Sourdough bread',40,270,9,52,2),('Wholemeal wrap',60,270,9,45,5),('Pitta bread',60,275,9,56,1.2),('Oatcakes',25,430,10,60,17),('Rye crackers',20,330,9,64,3),('Rice cakes',20,387,8,82,3),
('Lentils, cooked',150,116,9,20,0.4),('Chickpeas, cooked',120,164,8.9,27,2.6),('White beans, cooked',130,139,9.7,25,0.5),('Kidney beans, cooked',130,127,8.7,22.8,0.5),
('Black beans, cooked',130,132,8.9,23.7,0.5),('Baked beans',130,75,4.7,12,0.5),('Hummus',50,166,8,14,10),('Tzatziki',50,66,3.6,3.5,4),('Tahini',15,595,17,21,54),
('Banana',120,89,1.1,23,0.3),('Apple',150,52,0.3,14,0.2),('Pear',150,57,0.4,15,0.1),('Orange',130,47,0.9,12,0.1),('Grapes',100,69,0.7,18,0.2),('Figs, fresh',80,74,0.8,19,0.3),
('Kiwi',75,61,1.1,15,0.5),('Mango',100,60,0.8,15,0.4),('Pineapple',100,50,0.5,13,0.1),('Melon',150,34,0.8,8,0.2),('Peach',130,39,0.9,10,0.3),('Strawberries',100,32,0.7,7.7,0.3),
('Raspberries',80,52,1.2,12,0.7),('Blueberries',80,57,0.7,14,0.3),('Dates',24,282,2.5,75,0.4),('Almonds',25,579,21,22,50),('Walnuts',25,654,15,14,65),('Cashews',25,553,18,30,44),
('Pistachios',25,560,20,28,45),('Macadamia nuts',25,718,8,14,76),('Brazil nuts',20,659,14,12,67),('Pecans',25,691,9,14,72),('Pumpkin seeds',20,559,30,11,49),
('Sunflower seeds',20,584,21,20,51),('Flaxseed',10,534,18,29,42),('Chia seeds',15,486,17,42,31),('Peanut butter',20,588,25,20,50),('Almond butter',20,614,21,19,56),
('Dark chocolate, 70%',20,598,7.8,46,43),('Honey',15,304,0.3,82,0),('Soy sauce',15,53,8.1,4.9,0.6),
]
# name, servings, [[ingredient, grams]], styles (all / keto / med / hp / lcal / bal)
R = [
('Chicken salad with avocado',2,[('Chicken breast, grilled',250),('Avocado',140),('Mixed salad leaves',120),('Tomatoes',150),('Olive oil',15)],['all']),
('Tuna and egg salad',2,[('Tuna in spring water, drained',220),('Egg, boiled',150),('Mixed salad leaves',120),('Tomatoes',150),('Olive oil',15)],['all']),
('Cheese and spinach omelette',1,[('Egg, boiled',150),('Cheddar cheese',40),('Spinach',80),('Butter',10)],['all']),
('Steak with green beans and mushrooms',1,[('Rump steak, grilled',180),('Green beans',120),('Mushrooms',100),('Butter',10)],['all']),
('Prawn and avocado salad',2,[('Prawns, cooked',250),('Avocado',140),('Mixed salad leaves',120),('Olive oil',15)],['all']),
('Baked cod with broccoli',2,[('Cod fillet, baked',280),('Broccoli, steamed',200),('Butter',20),('Olive oil',10)],['all']),
('Greek yoghurt power bowl',1,[('Greek yoghurt, 0% fat',200),('Blueberries',80),('Almonds',20),('Walnuts',15)],['all']),
('Egg and avocado breakfast',1,[('Egg, boiled',150),('Avocado',100),('Tomatoes',100),('Olive oil',5)],['all']),
('Turkey meatballs in tomato sauce',3,[('Turkey mince, lean, cooked',450),('Tomatoes',400),('Onion',120),('Egg, boiled',50),('Olive oil',15)],['all']),
('Chicken thigh and pepper traybake',2,[('Chicken thigh, roasted',300),('Peppers',250),('Onion',120),('Olive oil',15)],['all']),
('Cottage cheese and berries',1,[('Cottage cheese',200),('Blueberries',100),('Walnuts',20),('Chia seeds',10)],['all']),
('Steak salad',1,[('Rump steak, grilled',150),('Mixed salad leaves',100),('Tomatoes',100),('Avocado',70),('Olive oil',10)],['all']),
('Mushroom and spinach omelette',1,[('Egg, boiled',150),('Mushrooms',100),('Spinach',60),('Olive oil',5)],['all']),
('Roast chicken with greens',2,[('Chicken thigh, roasted',300),('Broccoli, steamed',200),('Kale',100),('Olive oil',10)],['all']),
('Salmon and asparagus',2,[('Salmon fillet, baked',280),('Asparagus',200),('Lemon juice',15),('Olive oil',10)],['all']),
('Beef in cream sauce with mushrooms',3,[('Rump steak, grilled',600),('Double cream',150),('Mushrooms',250),('Onion',100),('Butter',20)],['keto']),
('Cheesy chicken bake with cauliflower',3,[('Chicken thigh, roasted',500),('Mozzarella',150),('Cream cheese',90),('Cauliflower rice',300),('Olive oil',15)],['keto']),
('Sausage and cheese traybake',2,[('Pork sausages, grilled',300),('Cheddar cheese',80),('Peppers',150),('Courgette',200),('Olive oil',10)],['keto']),
('Salmon with garlic butter spinach',2,[('Salmon fillet, baked',300),('Spinach',200),('Butter',30),('Garlic',5)],['keto']),
('Peanut butter fat bombs',6,[('Peanut butter',120),('Butter',60),('Dark chocolate, 70%',60)],['keto']),
('Vanilla cream custard',2,[('Double cream',150),('Egg, boiled',100)],['keto']),
('Bacon and eggs',1,[('Bacon, grilled',80),('Egg, boiled',150),('Butter',10)],['keto']),
('Lamb chops with courgette',2,[('Lamb chops, grilled',360),('Courgette',250),('Butter',20)],['keto']),
('Mackerel with asparagus',2,[('Mackerel, grilled',300),('Asparagus',250),('Butter',20)],['keto']),
('Cauliflower rice chicken stir-fry',2,[('Chicken breast, grilled',300),('Cauliflower rice',350),('Peppers',150),('Olive oil',20)],['keto']),
('Salami, cheese and olive plate',1,[('Salami',60),('Mozzarella',60),('Olives',50),('Pecans',25)],['keto']),
('Pork belly with green beans',2,[('Pork belly, roasted',300),('Green beans',200),('Mayonnaise',30)],['keto']),
('Halloumi and avocado salad',2,[('Halloumi',150),('Avocado',140),('Mixed salad leaves',100),('Cucumber',100),('Olive oil',20)],['keto']),
('Greek-style chicken with feta and olives',2,[('Chicken thigh, roasted',320),('Feta cheese',80),('Olives',60),('Tomatoes',100),('Olive oil',20)],['keto']),
('Smoked salmon and cream cheese plate',1,[('Smoked salmon',100),('Cream cheese',60),('Cucumber',80),('Avocado',70)],['keto']),
('Bacon and cheese egg muffins',4,[('Egg, boiled',300),('Bacon, grilled',80),('Cheddar cheese',80),('Spinach',60),('Butter',10)],['keto']),
('Beef and broccoli in butter',2,[('Rump steak, grilled',300),('Broccoli, steamed',250),('Butter',30)],['keto']),
('Coconut chicken curry',3,[('Chicken thigh, roasted',450),('Coconut milk, full fat',300),('Spinach',150),('Onion',100),('Coconut oil',15)],['keto']),
('Pork chops with buttered cabbage',2,[('Pork loin chop, grilled',300),('Cabbage',250),('Butter',30)],['keto']),
('Courgette bolognese with parmesan',3,[('Lean beef mince, cooked',450),('Passata',300),('Courgette',500),('Parmesan',30),('Olive oil',20)],['keto']),
('Chicken and rice bowl',2,[('Chicken breast, grilled',300),('White rice, cooked',360),('Broccoli, steamed',180),('Peppers',100),('Olive oil',10)],['hp','bal']),
('Protein porridge',1,[('Porridge oats',50),('Whey protein powder',30),('Whole milk',200),('Banana',100)],['hp']),
('Salmon, sweet potato and greens',2,[('Salmon fillet, baked',260),('Sweet potato, baked',400),('Spinach',150),('Olive oil',10)],['med','bal']),
('Turkey and lentil chilli',4,[('Turkey mince, lean, cooked',500),('Lentils, cooked',300),('Tomatoes',400),('Onion',150),('Peppers',200),('Olive oil',15)],['hp','lcal','bal']),
('Tuna and chickpea salad',2,[('Tuna in spring water, drained',220),('Chickpeas, cooked',240),('Tomatoes',200),('Mixed salad leaves',100),('Olive oil',15)],['med','lcal']),
('Lean bolognese with wholemeal pasta',4,[('Lean beef mince, cooked',500),('Wholemeal pasta, cooked',720),('Tomatoes',400),('Onion',150),('Mushrooms',200),('Carrots',100)],['bal','hp']),
('Tofu and vegetable stir-fry with rice',2,[('Tofu, firm',300),('White rice, cooked',360),('Broccoli, steamed',180),('Carrots',100),('Green beans',120),('Olive oil',10)],['lcal','bal']),
('Overnight oats with berries',1,[('Porridge oats',50),('Low-fat yoghurt',125),('Skimmed milk',100),('Blueberries',80),('Chia seeds',10),('Honey',10)],['bal','lcal']),
('Chicken and salad wrap',1,[('Wholemeal wrap',60),('Chicken breast, grilled',120),('Mixed salad leaves',60),('Tomatoes',60),('Hummus',30)],['bal','lcal']),
('Jacket potato with beans and cheese',1,[('Potatoes, boiled',300),('Baked beans',200),('Cheddar cheese',30)],['bal','lcal']),
('Banana oat pancakes',2,[('Banana',240),('Egg, boiled',100),('Porridge oats',60),('Blueberries',80)],['bal']),
('Prawn noodle stir-fry',2,[('Prawns, cooked',250),('Noodles, cooked',360),('Peppers',150),('Peas',100),('Carrots',100),('Olive oil',10)],['bal','lcal']),
('Greek salad with feta',2,[('Cucumber',200),('Tomatoes',250),('Feta cheese',80),('Olives',60),('Olive oil',20),('Sourdough bread',80)],['med']),
('Sardines on wholemeal toast',1,[('Sardines in olive oil, drained',90),('Wholemeal bread',72),('Tomatoes',100),('Lemon juice',10)],['med']),
('Bean and vegetable stew',4,[('White beans, cooked',520),('Tomatoes',400),('Carrots',160),('Celery',100),('Onion',160),('Kale',120),('Olive oil',30)],['med','lcal']),
('Chicken souvlaki bowl with bulgur',2,[('Chicken breast, grilled',300),('Bulgur wheat, cooked',300),('Tzatziki',100),('Cucumber',150),('Tomatoes',150),('Olive oil',15)],['med','hp']),
('Baked sea bass with tomatoes and olives',2,[('Sea bass, baked',280),('Tomatoes',300),('Olives',50),('Olive oil',20),('Lemon juice',20)],['med','lcal']),
('Hummus and vegetable plate',1,[('Hummus',100),('Carrots',100),('Cucumber',100),('Peppers',100),('Wholemeal pitta bread',0)] if False else [('Hummus',100),('Carrots',100),('Cucumber',100),('Peppers',100),('Pitta bread',60)],['med']),
('Lentil and spinach soup',4,[('Lentils, cooked',450),('Spinach',200),('Onion',160),('Carrots',160),('Tomatoes',200),('Olive oil',30)],['med','lcal']),
('Aubergine and chickpea bake',3,[('Aubergine',400),('Chickpeas, cooked',360),('Tomatoes',400),('Onion',120),('Olive oil',30)],['med']),
('Prawn and white bean salad',2,[('Prawns, cooked',250),('White beans, cooked',260),('Tomatoes',200),('Mixed salad leaves',80),('Olive oil',20),('Lemon juice',20)],['med','hp']),
('Shakshuka-style eggs',2,[('Egg, boiled',200),('Tomatoes',400),('Peppers',150),('Onion',100),('Feta cheese',60),('Olive oil',20)],['med']),
('Barley and roast vegetable bowl',2,[('Pearl barley, cooked',300),('Butternut squash, roasted',300),('Courgette',200),('Feta cheese',60),('Olive oil',20)],['med']),
('Chicken burrito bowl',2,[('Chicken breast, grilled',300),('Black beans, cooked',260),('Brown rice, cooked',360),('Tomatoes',200),('Avocado',100)],['hp']),
('Egg white omelette with ham and veg',1,[('Egg whites',200),('Ham, lean',50),('Peppers',80),('Mushrooms',80),('Olive oil',5)],['hp','lcal']),
('Skyr bowl with berries and almonds',1,[('Skyr',250),('Raspberries',80),('Strawberries',80),('Almonds',20)],['hp']),
('Turkey and quinoa stuffed peppers',2,[('Peppers',300),('Turkey mince, lean, cooked',300),('Quinoa, cooked',200),('Tomatoes',150),('Olive oil',10)],['hp']),
('Beef stir-fry with broccoli and rice',2,[('Beef stewing steak, cooked',300),('Broccoli, steamed',250),('Brown rice, cooked',360),('Soy sauce',30)],['hp']),
('Cottage cheese pancakes',2,[('Cottage cheese',200),('Egg, boiled',100),('Porridge oats',60),('Blueberries',80)],['hp']),
('Salmon and edamame rice bowl',2,[('Salmon fillet, baked',260),('Edamame beans',160),('Brown rice, cooked',360),('Cucumber',100),('Soy sauce',20)],['hp']),
('Pork chop with sweet potato and greens',2,[('Pork loin chop, grilled',260),('Sweet potato, baked',400),('Green beans',180),('Butter',10)],['hp','bal']),
('Vegetable and bean soup',4,[('Kidney beans, cooked',390),('Carrots',160),('Celery',100),('Leeks',160),('Tomatoes',300),('Cabbage',160)],['lcal']),
('Cod with roasted vegetables',2,[('Cod fillet, baked',280),('Courgette',200),('Peppers',200),('Tomatoes',200),('Olive oil',15)],['lcal']),
('Prawn and cucumber salad',2,[('Prawns, cooked',250),('Cucumber',200),('Mixed salad leaves',100),('Lemon juice',20),('Olive oil',10)],['lcal']),
('Turkey lettuce wraps',2,[('Turkey mince, lean, cooked',300),('Mixed salad leaves',120),('Peppers',120),('Carrots',80),('Soy sauce',20)],['lcal']),
('Lentil and tomato soup',4,[('Lentils, cooked',450),('Passata',400),('Onion',160),('Carrots',160),('Celery',100)],['lcal']),
]
fd = {x[0]: x for x in F}
def per(g, v): return round(v * g / 100, 1)
foods = [{'n': x[0], 'g': x[1], 'k': x[2], 'p': x[3], 'c': x[4], 'f': x[5]} for x in F]
recs = []
for name, sv, ings, st in R:
    tot = {'kcal': 0, 'protein': 0, 'carbs': 0, 'fat': 0}; out = []
    for n, g in ings:
        x = fd[n]; o = {'name': n, 'amount': g, 'kcal': per(g, x[2]), 'protein': per(g, x[3]), 'carbs': per(g, x[4]), 'fat': per(g, x[5])}
        out.append(o)
        for a, b in (('kcal', 'kcal'), ('protein', 'protein'), ('carbs', 'carbs'), ('fat', 'fat')): tot[a] += o[b]
    recs.append({'n': name, 's': sv, 'i': [[n, g] for n, g in ings], 't': st})
pool = {'v': 1, 'note': 'Typical reference values per 100 g for starting a library. Check against your own labels.', 'foods': foods, 'recipes': recs}
os.makedirs(os.path.join(ROOT, 'starter_packs', 'data'), exist_ok=True)
json.dump(pool, open(os.path.join(ROOT, 'starter_packs', 'data', 'food_pool.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
# flag packs
n = 0
for fp in glob.glob(os.path.join(ROOT, 'starter_packs', '*.json')):
    if fp.endswith(('index.json', 'food_pool.json')): continue
    d = json.load(open(fp)); d['foodPool'] = True
    json.dump(d, open(fp, 'w'), ensure_ascii=False, indent=2); n += 1
# inject into the app
html = os.path.join(ROOT, 'maxhealth.html'); s = open(html, encoding='utf8').read()
const = 'const MH_FOOD_POOL = ' + json.dumps(pool, ensure_ascii=False, separators=(',', ':')) + ';\n'
rt = open(os.path.join(ROOT, 'tools', 'food_pool_runtime.js'), encoding='utf8').read()
if 'const MH_FOOD_POOL = ' in s: i = s.index('const MH_FOOD_POOL = ')
else: i = s.index('const _DEMO_FOODS_BASE = ')
j = s.index('function generateDemoRoutines()')
s = s[:i] + const + rt + '\n' + s[j:]
open(html, 'w', encoding='utf8').write(s)
print(len(foods), 'foods', len(recs), 'recipes', n, 'packs flagged')
