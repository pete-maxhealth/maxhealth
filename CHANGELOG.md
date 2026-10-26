# MaxedHealth Changelog — Phase 23 (v3.10.744 – v3.10.844, HEAD v3.10.844)

**Version numbering note:** two separate work sessions bumped versions independently and both landed on **v3.10.779** — one for the Nutrition History button-layout fix, one for the AI-recipe-card read-aloud button. Both sets of changes are genuinely in the file (confirmed directly, nothing was lost), it's purely that one version number was used twice in git history. Left as-is rather than rewriting already-pushed commits. v3.10.784's fix (the meat/fish combo-label bug) is also included despite being an earlier commit than 780 — the two sessions' version numbers don't stay in strict chronological order relative to each other, only within each session.

## v3.10.1215
- **Shopping complete dialog tidied.** "Keep list" is gone (Saved lists already do that) and the cancel button now reads Back like every other dialog.
- **PDF receipts are accepted** in the receipt import (PDF.js 3.11.174, Apache-2.0, bundled under lib/). Text-based PDFs only; scanned ones still need a photo.
- **Pack-size wording clarified** so it is clear whether a figure is the size of one pack, a portion or what is left.
- **Reports date range applies straight away** to the Exercise and Sleep cards instead of waiting until you leave and come back.
- **GBM monthly summary and Ask AI now know your age, sex, height and weight** (one profile line in the AI context).
- **Your Journey has a Fat chip** for the fuller picture.
- **History edit: occasion tags are live.** The picker was a frozen list; it now also shows every tag in use on any day (custom ones, renames and merges from Manage tags) and drops deleted ones, matching the Log tab.
- **Ask AI keeps the answer area on screen while it thinks**, so the page no longer jumps to the top.

## v3.10.1214
- **A planned meal can no longer vanish.** With "Trust my plan: log it automatically at the time" ticked (or tapping Ate it), an overdue plan from an earlier day is logged into that day in History. If that day was not in History the plan was removed and nothing was logged, so the meal and its figures disappeared. Now the plan stays, says why, and is left for you to answer (Changed it / Skipped); auto-log skips it.

## v3.10.1213
- **Add foods: "Needs details" and "No amount yet" were the same list, so "No amount yet" is gone.** "Needs details" covers a food with no amount, reorder level or serving. Foods you have not put in My cupboards yet stay under "Not in my cupboards" and are no longer repeated under a second name.
- **Herbs, spices and other never-run-out foods are left out of "Not in my cupboards" and "Needs details".** It uses your Stock rules > Never runs out list. A small line says how many are hidden, with a Show them button (and Hide them once shown). Count one yourself and it is treated like any other food.

## v3.10.1212
- **Today's tiles say how much of the day is logged for later.** A meal already in today's log but timed for later (a bar logged for 19:00) is counted in the tile straight away; the small line under Calories, Protein, Carbs and Fat now adds "includes 162 kcal logged for 19:00". It sits beside the existing "+N planned" line when you have both. Same wording style, only for today.

## v3.10.1211
- **"On your shelf" (Add to the list, Non-nutritional) now only shows what is NOT already on your list.** Items already on the list (and any in Filtered) no longer appear there with an ON LIST tag; if everything is already on the list it says so.

## v3.10.1210
- **Putting several Filtered foods back now walks you through them.** Tick as many as you like and press Put back on shelf: any that still need details open one at a time ("Food 2 of 8 to complete"), same form each time, with Next food / Finish and Stop here. It will not move on while the food is missing something. Foods already complete go straight back. The result names every food put back and says which are low and now on your shopping list.

## v3.10.1209
- **History's ate-out button now looks exactly like Today's.** It used a different version of the plate emoji (solid and colourful) from the outline plate on Today's log. Same character now.

## v3.10.1208
- **Mark an earlier day's meal as eaten out.** The 🍽️ "ate out" button from Today's log is now on every entry in History too (when cupboards & stock is on). Tap it on a takeaway or restaurant meal and what it took off your stock is put back (only stock counted before that meal, as always); tap again to take it off after all.

## v3.10.1207
- **New foods are checked against My cupboards the moment they reach the Library.** Whenever a save adds a food that My cupboards does not know (Add Food, logging a new food, a recipe's new ingredients, imports, voice batches), you are asked once for the whole batch: complete the stock details now, or later. Later (and now, until you finish) puts them in Filtered with 0 stock, so they cannot reach your shopping list. In Filtered each shows what it still needs (how it is counted, reorder level, shop) with a Complete button, and Put back on shelf only releases a food once those are filled in (where it lives is Cupboard unless you change it, so it can never be missing). Never triggered by starter foods, a restore, a rename, a demo, or more than 50 at once (use Library Tools: Library foods → cupboards).

## v3.10.1206
- **One-off: put every Library food that has no stock entry into My cupboards as filtered, with 0 stock.** New Library Tools button "📦 Library foods → cupboards (filtered)". It asks first with the count, adds them with 0 stock held back from your shopping list (they show under Filtered, grouped by aisle), and has an Undo. Foods whose Library portion has no g or ml are left out, because how they are counted is never guessed. Shop, reorder level and where it lives stay empty for you to fill in as you release each one.

## v3.10.1205
- **Library Tools: "+ Add Food" is now "+ Add Food Manually".** Same button, clearer name next to the voice and import tools.

## v3.10.1204
- **The fasting "taken with meds" food is now recognised by its words, not its exact spelling.** With "MCT oil" set, an entry called "MCT C8 Oil (15g)" still restarted the fast, because the whole phrase "mct oil" has to appear in a row. Now every word of what you typed must appear in the entry, in any order, and the usual-amount limit still applies. So "MCT C8 Oil" no longer breaks your fast.

## v3.10.1203
- **Typing in Add to the list no longer opens every shut aisle.** The "Search ingredients" box (and the other add boxes) were opening all of your closed aisles on the list while you typed. Now only searching the list itself ("Search your list") opens them; your open and shut aisles stay as you left them.

## v3.10.1202
- **Aisles keep their open/shut state when another shop's items appear.** Open aisles were shutting by themselves the moment a second shop had something on the list, because the remembered state was filed under a different name once there was more than one shop. Aisles are now always remembered per shop, and what you had open before is kept.

## v3.10.1201
- **Non-food shelf rows line up.** On the "On your shelf" list, the Regular and Add buttons no longer stretch over the item name. Every row has the same layout: name, Regular, then either ON LIST or ＋ Add in a fixed-width spot.

## v3.10.1200
- **Removing a food from My cupboards can be undone.** Both remove buttons now keep a copy of the food with its counts: an Undo on the message for 10 seconds, and a "Recently removed" line under the shop chips in My cupboards (the last 30). Tap a food there to put it back exactly as it was.

## v3.10.1199
- **One set of scroll arrows on Library.** Library was showing its own ↑ ↓ buttons on top of the app-wide pair. Its old pair is switched off, so it has the same single pair as every other screen.

## v3.10.1198
- **Choose your default shop.** Once you have more than one shop, a "Default shop" dropdown under the shop chips lets you pick which one new things go to. Any shop can be the default, and if you delete the default shop the next one takes over (you can change it again at any time). Before this the first shop in the list was the default and could never be deleted.
- Fixed: "Put back" in Why are these on my list? after a shop was deleted could create doubled entries; those items now go to the default shop.
- Filtered shows a small "review before you shop" hint while collapsed.

## v3.10.1197
- **Filtered: ✕ on a running-low item means "not this week".** The item leaves the list but stays on your shelves and keeps counting; the list stops adding it, so it will not come back while you shop. A collapsed "Filtered (n)" section under the list count shows them grouped by aisle, with Select all / Deselect all, tick individual foods, and "Put back on shelf". A put-back food that is still low goes on the list as normal. Adding a filtered food by hand also releases it. Works for non-food items. My cupboards shows "filtered" instead of LOW on those rows. Other items (typed, usuals, added by hand) still just come off the list.

## v3.10.1196
- **A shop's ✕ means the same thing in all three places.** On the shopping list, My cupboards and Add foods it now hides the shop for now (same ✕, same confirmation, same "Hidden shops (n)" line to bring it back). Before, the ✕ in My cupboards and Add foods deleted the shop for good while the one on the list only hid it. Deleting a shop for good is now only under "Hidden shops" ("delete for good", with its confirmation), out of the way. A hidden shop disappears from the chips in all three places and comes back everywhere together. Tests p279, p284 and p296 updated; p297 added.

## v3.10.1195
- **The red "running low" tag on the list now only shows on entries that really came from running low.** Entries that were added by hand from Add foods or My cupboards said "running low" too, so foods with plenty in stock (jam at 200 g against a reorder of 100 g) looked low. They now carry no tag (the "Why are these on my list?" line says how they got there).
- **A shop can be hidden even when it has items on the list** (✕ beside any shop). It asks first, its items come off the list (nothing is deleted from your cupboards, and Put back works), and while it is hidden its low foods are not added. Bring it back from "Hidden shops" and anything low there returns to the list. Tests p289, p284 and p291 updated; p296 added.

## v3.10.1194
- **Shopping complete has a way out that leaves your cupboards alone.** With stock on, the box now offers "Just clear them: leave my cupboards alone", which empties the ticked items from the list without the add-to-cupboards review and without putting anything on the shelf. "Empty the basket" now says what it does: "then I choose what to add to my cupboards" (it never changed a count by itself; the review is where you confirm amounts, and you can skip all). Test p295 added.

## v3.10.1193
- **A "running low" entry now comes off the list when the food is no longer low.** Before, a food that went on the list while its count was 0 (or wrong) stayed there after you corrected the count, so foods well above their reorder level looked "low" on the list. Entries that are already stuck on your list are cleared the next time the shopping screen draws. Anything you ticked into the basket is left alone, and a food that drops low again comes back by itself. Test p294 added.

## v3.10.1192
- **Taking a group off the list can no longer lose something you need.** A food that is genuinely low (at or under its reorder level) comes straight back as "running low" after its group is taken off; only the ones that are not low go. The message says how many were kept.

## v3.10.1191
- **"Why are these on my list?" says when each group was added** (e.g. "added 23 Oct 14:02 to 14:09"), so a batch added in one go shows up as one batch, and the group formerly called "Chosen as Shopping list / Both in Add foods" is now "Added from Add foods or My cupboards".

## v3.10.1190
- **Foods bought at Heylo (or any shop) no longer sit on the list under Asda.** A food that moved from "no shop" to a shop kept its list entry under the old default shop, so the shop looked empty (and could be hidden) while its items were still on the list under Asda. List entries that came from your cupboards now follow the food's shop, for existing entries as well as new ones. A shop that gets its items back shows again by itself. Test p291 added.

## v3.10.1189
- **Shopping and My cupboards now use the app's own controls instead of their own.** (1) All the filter and shop chips (All / Fridge / Freezer / Cupboard / Low / Use soon, the shop chips, ＋ Shop, the Shopping list / My cupboards switch, the Add foods filters) are the same rounded pills as This Week / Month / All, with the same selected look. (2) The ▲ ▼ 👁 ▾ hide controls on the My list, Add to the list and My cupboards cards sit on the title row like every other card. (3) The Import / My usuals / Quick list tiles are the standard button size and centred. (5) The shop ✕ is the same pill, tucked against its chip and no longer red. The aisle bars were left as they are (nothing else in the app groups the same way).
- **On a Needs details row, how a food is counted stays a dropdown (g / ml / each) after you type an amount.** Before, it turned into plain "counted in g" and could only be changed in the full edit form. Changing it asks first, because that clears the food's amounts. Test p290 added.
- Old tests p210, p211, p216, p239 and p274 set to the old single-page layout (they predate the separate panes).

## v3.10.1188
- **The clear ✕ on every Shopping and My cupboards search/type box now matches the Log box**: the same bordered 22px square with a thin ✕, always shown, at the left inside the box, with the text indented. Before, mine sat on the right, only appeared once you typed, and the list search had a second one beside it. The phone's own built-in clear mark on search boxes is hidden so there is only one. Test p285 updated.

## v3.10.1187
- **On the shopping list the ✕ beside a shop now means "not shopping here this week", not delete.** It only shows on a shop with nothing on the list, and hides that shop from the list screen. The shop, its usuals, its history and the cupboard foods bought there are untouched. Hidden shops sit under "Hidden shops (n)": tap one to bring it back, or use its ✕ there to delete it for good (with the usual confirmation). A hidden shop comes back by itself if something is added to it. Permanent delete is also on My cupboards and Add foods, as in 1181. Test p289 added.

## v3.10.1186
- **On a food that needs details, the "Where does it go?" button that said "Cupboards" now says "Shelves"**, so it no longer reads like the "Kept in: Cupboard" box above it. Nothing else changed.

## v3.10.1185
- **Removed the pinned Shopping list / My cupboards switch (v3.10.1183).** It floated over the content and hid the top of the search box and the Use soon bar, which is not how any other screen works. The switch is back to being part of the page; the standard ↑ button takes you to the top where it is. Test p287 removed.

## v3.10.1184
- **The four Today tiles (Calories, Protein, Carbs, Fat) show what your planned meals would add**, as a small line under each, e.g. "+162 kcal planned · 2,022 kcal total". It uses the same planned meals as the Meal plan card (today's and overdue ones), the figures stored with each planned food (nothing estimated), and net carbs if that setting is on. No planned meals, no line. Test p288 added.

## v3.10.1183
- **The Shopping list / My cupboards switch stays pinned at the top of the Shop tab.** Once you were down a long list or cupboard there was no way back to it without scrolling to the top. Test p287 added.

## v3.10.1182
- **Fixed the search box spilling over the Add button.** The clear ✕ wrapper (v3.10.1179) stopped the box filling its row, so it ran over the Add button and the ✕ was hidden. The box now fits its row and the ✕ appears inside it as soon as you type. Test p285 added.

## v3.10.1181
- **Add a non-nutritional item from the shopping list and it is also put in My cupboards** (if it is not there already; the message says "and to your cupboards" or "already in your cupboards"). Plain foods are not copied. Adding from the cupboards behaves as before.
- **Shops can be created and removed from the shopping list, My cupboards and Add foods.** Every shop except the first has a visible ✕ in all three places. Removing one asks first, names the list items that come off and the cupboard foods that lose that shop (the foods stay in the cupboards, with no shop).
- Test p284 added.

## v3.10.1180
- **A food you add or edit in My cupboards is shown to you afterwards.** With aisles closed by default, a food added from "＋ Add a food" (including "as non-nutritional", e.g. washing-up liquid) went into the cupboards but sat inside a closed aisle, so it looked as if nothing had happened. Back and Add to my cupboards now return to My cupboards with that food's aisle open, scrolled to it and flashed. The other aisles you had open stay as they were. Test p283.

## v3.10.1179
- **An ✕ to clear every typing and search box** on the Shopping tab (Add to the list, search your list, Add foods search, cupboard search, ingredient search, usuals). It appears once there is text in the box and empties it.
- **An ✕ on every cupboard row** removes the food from My cupboards (asks first, your shopping list is not touched). The 🗑 stays and still means "used up or binned".
- **＋ Shop in the cupboards pane** (next to "Show what is bought at"), so a shop can be added from there too. Test p282.

## v3.10.1178
- **Adding something to the list now shows you where it went.** Since aisles start closed (1172), "Added" gave no sign that the item was there, and adding it again said "Already on the list" with nothing to see. Now the message names the item and the shop list it is on ("Added Washing up liquid to your Asda list", or "... is already on your Asda list (ticked, in the basket)"), its aisle opens, and the page scrolls to the row and flashes it. Searching your list also opens aisles that match. Test p281.

## v3.10.1177
- **The Shopping tab is two separate panes: 🛒 Shopping list and 🏠 My cupboards.** A two-button switch at the top shows one at a time (the list pane has My list and Add to the list; the cupboards pane has My cupboards), so nothing stacks into one long page. The one you were on is remembered after a reload and when you come back. Each pane keeps its own ▲ ▼ 👁 ▾ controls. Test p280. (Tests that look at both sections together set a test-only "both" mode.)

## v3.10.1176
- **＋ Shop on the Add foods screen.** A new shop can be added right where you pick the shop (next to Asda and Heylo); it is added and chosen at once, so what you add next goes to it. Test p279.

## v3.10.1175
- **An X on every food in the Add foods lists removes it from My cupboards.** For foods you do not want tracked (a typo, something you no longer keep): ✕ on the row, then Remove to confirm. The row goes, the counts update, and your shopping list is not touched. Test p278.

## v3.10.1174
- **"Needs details" and "No amount yet" are to-do lists with no ticking and no pop-up.** Each food's own row already holds Have now, Reorder at, One serving, Bought at and Kept in, so the tick boxes, Tick all shown and the bottom bar are gone from those two views.
- **Each food asks "Where does it go?" on its own row, and it is required.** Three buttons, **Cupboards**, **Shopping list** and **Both**, none pre-selected. Pressing one applies it to that food at once (Cupboards starts counting it, Shopping list puts it on that shop's list, Both does each). A food leaves the list when its amounts are filled in and one is chosen; until then the row says "choose one to finish this food". If a food has no unit yet it asks how it is counted first.
- **The tick bar (other views) names the foods ticked** on its first line, and is a single short strip. After "Add to my cupboards" the screen jumps to Needs details to fill in amounts, and ticks clear. Tests p278, p251, p273, p276.

## v3.10.1173
- **A food leaves "Needs details" (and "No amount yet") the moment it is complete.** Fill in how much you have, when to reorder and one serving and the row fades off the list; the "N shown" and "Needs details (N)" counts update without redrawing the page, so you can work straight down the list. Test p278.
- **The tick bar stays small.** Ticking foods now shows one slim strip (count, Untick all, and the three buttons Add to my cupboards / Put on the list / Both) instead of a panel that covers the list, so Tick all shown and ticking several foods is usable. The explanation, the shop and where-kept pickers, and the single-food amounts sit under a "More" line, closed by default. The buttons wrap rather than overflow on a large-text phone. Tests p278, p272, p273, p251.

## v3.10.1172
- **My list and My cupboards open with every aisle closed.** Aisle sections (Fruit & veg, Meat & fish, Dairy & eggs, Cupboard and so on) start shut, so you see the headings and counts and open only the one you want; what you open is remembered (and Close all / Open all still work). Searching the cupboards shows its matches as before, "Use soon" stays open, and tapping a Use soon food opens just its aisle. A tap on a closed aisle now opens it (it would have closed it again on first tap, which the new test caught). Tests p277, and p197 and p225 now open the aisles they look inside.

## v3.10.1171
- **Add foods bar slimmed down for a phone.** The bar now shows the count, the three actions side by side (**Add to my cupboards**, **Put on the list** and a new **Both**), and tucks *Bought at* and *Kept in* behind a "change the shop or where it is kept" line. Have now / Reorder at appear only when exactly one food is ticked, because an amount cannot mean the same for several foods (the others get their amounts on their own rows via Needs details). Ticks now stay after an action so a second action can follow; Untick all clears them. The buttons keep clear of the floating scroll arrows. Tests p276, p273, p272, p251.
- **Use by can be cleared.** A "Clear the date" button appears under the Use by date, and picking the same date again after clearing it now saves. Test p276.

## v3.10.1170
- **Add foods no longer lists the same product twice.** If you already hold "Cauliflower Rice", the library's "Cauliflower Rice (Asda)" is the same food under a shop's name, so it is hidden from the Add foods list (the same comparison the log matching already uses: brackets and the word Asda ignored). A line says how many are hidden and why, with a **Show them** button; typing the exact name still finds it, and Tick all shown never ticks a hidden food. Two variants where you hold neither are both shown. Test p275.

## v3.10.1169
- **My cupboards: see what is in each shop.** A "Show what is bought at" row (All shops, Asda, Heylo, No shop, each with a count) filters the cupboards by shop, together with Fridge / Freezer / Cupboard / Low / Use soon, so you can check every food is under the right shop and tap one to adjust its stock. It is remembered. Test p274.

## v3.10.1168
- **Add foods bar: set Have now and Reorder at for everything ticked.** Two optional boxes in the bar, in each food's own unit (g, ml or each); blank keeps what each food already has. Nothing is guessed. Test p273.

## v3.10.1167
- **The Add foods bar says what it will do.** It now states how many are ticked and which shop they are for, with a **Bought at** picker right in the bar (so you can switch to Heylo without scrolling up), and a plain line explaining the two buttons: Add to my cupboards starts counting their stock; Put on the list only adds them to that shop's shopping list. Test p272.

## v3.10.1166
- **The shopping list and My cupboards now keep their folds.** Closed aisle groups, Close all / Open all, the Use soon fold and its Show all, and closed groups on the shopping list were held only in memory, so a reload or the app restarting put everything back. They are now remembered on the phone. Test p271.

## v3.10.1165
- **Untick all now really unticks, and the bar can be closed.** On the Add foods screen, Untick all only cleared the rows currently shown, so a ticked food hidden by the search (or a filter) stayed ticked and the bar never went away. It now clears every tick, and the bar has a ✕ that does the same. Test p255 covers a tick hidden by the search.

## v3.10.1164
- **My cupboards: Add foods is at the top, and Close all / Open all.** Pete only found Add foods after collapsing every aisle group. There is now a big **➕ Add foods** button at the top of the card, above the search box. **Close all / Open all** shut or open every aisle group and the Use soon list in one tap. The Use soon list shows five rows with **Show all (15)** / **Show fewer**, and folds from its heading. Test p270.

## v3.10.1163
- **No more Termux for starting or updating.** Pete had to open Termux and type `mhstart`. A web page can't type into Termux (Android doesn't allow it), so the app now uses what can work. The offline notice, the server badge and the failed-sync message offer **Start the server**: it shows a "Server restarting" box with an OK button and opens the MaxedHealth Sync launcher (which already starts the server and brings you back), while watching for the server to answer. The update banner and "Check for updates" now offer **Update now**: the app asks its own server to run the update script (new `POST /update-now`), shows "Updating", waits for the server to restart on the new code and reloads. If the server isn't running, Update now starts it first. The old Termux command stays tucked away under "Still stuck?". The box only says what is really happening (it says "up to date" if nothing needed installing, and says so if the server doesn't come back).
- Needs a real-phone check of the launcher hand-off (it can't be tried here). p269 covers the rest; p74 updated.

## v3.10.1162
- **The Add foods screen no longer buries you.** The big "Tick all shown / Add to my cupboards / Put on the list" bar sat over the rows all the time, even with nothing ticked. It now only appears once something is ticked (with Untick all), and "Tick all shown" lives beside the "shown" count above the list. The search box is pinned at the top of the screen, so wherever you have scrolled in a long list you can type "heylo flat" without scrolling back up.
- p255 updated for both.

## v3.10.1161
- **A typed daily step total no longer disappears.** Pete typed 10k and it wasn't kept. The most likely cause: the next sync of watch data for today wiped the typed figure even when the watch had counted fewer steps, though the box promises "used until your devices report the same or more". It is now only retired once the devices report the same or more. Test p268 (could not reproduce a plain loss locally, so a sync clash is the suspect).

## v3.10.1160
- **The Add box on the shopping list is now the search.** Pete couldn't find where to search for Heylo Flatbread: the box said "Type an item" and just added his words as plain text, with the real search tucked away on a small button. Now it says "Search or type a food", and as you type, matching foods from your cupboards and library appear right under it. One tap puts the food on the shop you have selected. A library food not yet in your cupboards also opens the stock form with that shop already filled in, and returns you to the list. A name that matches nothing offers "New food" on the same shop. With stock off the food simply goes on the list.
- **Removing a mistake is one tap.** Every list row now has a ✕ (no Edit mode needed) and a 6-second Undo.
- Test p267 locks both in; p197 updated for the new wording.

## v3.10.1159
- **Logging now understands spoons on millilitre foods and ounces/pounds on gram foods.** 1 tsp = 5 ml, 1 tbsp = 15 ml (as cooking already did), 1 oz = 28.35 g, 1 lb = 453.6 g. Spoons on a gram food, cups, slices and anything on a counted food are still left alone, since they would need a density or size you haven't given. Locked in by p264.

## v3.10.1158
- **More stock tests (p262–p266) found four real faults, now fixed.**
  - **With stock counting off, some things still moved counts.** Cooking a batch, binning/adding stock and deleting or editing a logged entry changed counts even when counting was off. Now nothing counts while it is off, and switching it back on picks up exactly where the counts were left.
  - **Tapping Shopping complete twice stacked two questions.** A second tap now does nothing while the first question is open (same for any identical confirm box).
  - **Moving a food to another shop left it on the old shop's list.** Changing "Bought at" (cupboard row or edit form) now takes the food's place on the list with it, once; count, reorder, pack and history stay as they were.
  - Tests also lock in: a whole simulated week with expected counts worked out independently; unit traps (kg, l, counts convert exactly; spoons, cups, ounces, slices and weights on a counted food change nothing); double taps never count twice; phone-to-tablet transfer and a mid-shop backup restore arrive exactly; foods with no amount yet count as available for recipes and ideas (only the strict setting excludes them).

## v3.10.1157
- **Scenario tests found three real gaps, now fixed.** Pete asked for end-to-end scenarios (a recipe with everything in, a recipe with substitutes, stock going down for a recorded item, stock going up, every way in and out). Each step is checked against arithmetic done in the test (new test p261). It found:
  - **Logging from a barcode or Open Food Facts result never took stock off.** The food was saved as "Name 30g" with the amount baked into the name, so it could never match the cupboard item "Name". The name is now bare and the amount sits in the amount field (the History line reads the same).
  - **Cooking a batch ignored millilitre foods even when you had given a density.** It now takes them off using that density (grams to millilitres only with a figure you gave; never guessed). Eggs and other counted foods, where grams cannot become a count, are still left alone and named.
  - **Cooking a batch ignored substitutes.** If an ingredient is out or short and a like-for-like swap is in your cupboards, it now asks "Whole Milk is out or short, and you have Oat Milk. Take that off stock instead?" Yes takes the swap off; No leaves it alone. Nothing is asked when the original is in.

## v3.10.1156
- **Shopping works the same whether stock counting is on or off.** Pete: on/off only decides whether amounts are tracked; the list, regulars and saved lists are for everyone. **Shopping complete** now asks how to finish: **Empty the basket** (with stock on, the bought food goes to the stock review and non-nutritional items to the shelf, as before) or **Keep the whole list for next shop** (everything unticked and still on the list, back to how it was before checkout). With stock switched **off** there is no reorder level to bring a food back, so every regular stays on the list, food or not; with stock on, food regulars come back through their reorder level and non-nutritional regulars stay. **Fixed a leak:** with stock switched off but items still on the shelf, finishing a shop could still open the stock review. Saved lists do not depend on stock (checked, tested with it off). **Three more browser pop-ups replaced** with the app's own box, since a browser can swallow them and leave a button doing nothing: Add a shop, Name this saved list, Rename a saved list. Tests p260 (new), p205, p212, p214 updated.

## v3.10.1155
- **One way to add a food to your cupboards, from wherever you are, and back again.** Pete's tweaks: the cupboard search, a library entry and a barcode / Open Food Facts product now all open the same stock form with everything known already filled in, and bring you back to where you were afterwards (the search as you left it, the Library, or the Log). **From the cupboard** the shop is already known: it is the one highlighted. **From the library** (new **📦** button on each ingredient) the shop is taken from the title if it names one ("Asda Double Cream"); otherwise the form asks **Which shop?**, with your existing shops and **＋ New shop…**. It will not add until a shop is chosen. The serving comes from the library portion or the product's own data, the pack size from the product's quantity, and the form asks for anything missing; nothing is guessed. A barcode or search product now opens this form rather than being created silently. **With stock switched off** the food is simply put on that shop's list. Tests p259 (new), p258 (updated).

## v3.10.1154
- **A product found by barcode or Open Food Facts can go straight into your cupboards.** On the amount screen (after a scan or a name search) there is now **📦 Also keep this in my cupboards** (ticked after a barcode scan, because you are holding the product; unticked after a name search). Whichever way you finish, Log or Save to library, it creates the cupboard item under the same name, so logging takes food off it. The pack size comes from the product's own quantity text (400 g, 1.5 L, 75 cl and so on) and the serving from the product's serving size; if the text is anything else ("6 x 60g") nothing is guessed. How much you have and the reorder level stay empty and show as Needs details. An item you already keep is never overwritten, and the tick is hidden with stock switched off. Test p258.

## v3.10.1153
- **Non-nutritional regulars stay on the list; the rest go back on the shelf.** Pete: toilet roll is a weekly regular, hairspray is once a month. On the Non-nutritional shelf (Add → Non-nutritional) every item now has a **☆ Regular** button. A regular is put on the list straight away and, after **Shopping complete**, stays there unticked in the collapsed Non-nutritional block, ready to open at the checkout next time. Anything not marked as a regular leaves the list and lives on the shelf, to come back when you flag it low. Switch ⭐ off and it behaves like the rest. Removing it from the list does not change whether it is a regular. Food is unchanged: it leaves the list when bought and returns when stock reaches its reorder level. Test p257.

## v3.10.1152
- **No food reaches the shopping system half-filled without saying so.** Pete's point: adding a food to a shop only helps if the app also knows how much you have, when to reorder and what one serving is, whichever way the food got there (library, receipt, CSV, list, by hand). Until it has an amount and a reorder level a food can never show as running low. Every food with something missing now says **Still to add: how much you have, when to reorder, one serving** on its row, there is a **Needs details (n)** filter at the top of Add foods, and the cupboards card reads "Check the cupboards (n need details)" and opens straight to that filter. After **Add to my cupboards** the screen switches to those foods at once and says how many. Hand-marked non-nutritional items are exempt. Nothing is filled in for you. Test p256.

## v3.10.1151
- **One "Add foods" screen: pick the shop, search, tick, one bar.** Pete found the cupboard and shop screens hard to use: search boxes that did not look in the library, buttons above the list and more below it, and two Import buttons worded differently. Check the cupboards is now **Add foods**. At the top are **all your shops**, whether or not they are on this trip's list; the highlighted one is where everything goes (picking a shop here does not change the list you are shopping). Search takes words in any order ("flatbread heylo"), and when nothing fits every word it shows the closest names and says so. **＋ Add "x" as a new food to Heylo** sits right under the search box. The **bar at the bottom stays on screen while you scroll**: count ticked, Tick all shown, Untick all, Kept in, **Add to my cupboards** and **Put on the list**. Below the results is **More ways to add** (Import, usuals, quick list, recipe, saved lists). Find foods and More ways each have show/hide and reorder, remembered. The cupboards card's receipt button is now simply **📥 Import**, worded like the Add box one; the import screen itself still asks what the import is for. Tests p255 (new), p251, p226, p244 updated.

## v3.10.1150
- **Foods saved as "1 serving" now show up in the cupboard search and shop pickers.** Pete's Heylo Flatbread was in his library but the search said nothing matched. Any library entry saved with the portion "1 serving" was treated as a meal, and for a meal the app offers only the ingredients inside it; a single product has none, so it vanished. A saved entry with no ingredients inside is now counted as a food in its own right. Real meals still offer their ingredients as before. Test p254.

## v3.10.1149
- **Add a brand-new food straight from the cupboard search.** Pete wanted "Heylo flatbread" in his Heylo shop. The obvious route, typing it into the search on Check the cupboards, found nothing and stopped there, because that screen only lists foods the app already knows. When what you typed matches nothing, a button now appears: **＋ Add "Heylo flatbread" as a new food**. It opens the new-food form with the name filled in, and if a shop's name is in the text (Heylo) that shop is already chosen. Say how it is counted (g, ml or each) and add it. Nothing is guessed. Test p253.

## v3.10.1148
- **The Logged card now says what is left in your cupboards.** Pete asked where the stock figure was after logging Asda double cream: the app took it off quietly and only a brief toast said so. Under the totals the card now shows, for each food that really came off stock, a line like "📦 Stock left: Double Cream (Asda) 350 g", with "(running low)" at or below the reorder level and "(all used)" at zero. Nothing is shown with stock switched off, for foods not in your cupboards, or where the amount could not be read (those still get the existing message). Test p252.

## v3.10.1147
- **Pick several foods at once and send them to a shop (the "Heylo" flow).** Pete wanted to filter his foods by a word, tick them all or one by one, put them in a shop and say where they are kept. Shopping → Check the cupboards (also reached from the Add box with **🔍 Search my foods and pick several**) now has a tick on every row, **Tick all shown**, and a bar with **Bought at** and **Kept in** (cupboard, fridge, freezer, or leave as is). **Apply** sets them for every ticked food; **Put ticked on the list** adds them to the chosen shop's list. Each row also has its own Kept in. Only foods the app already knows are listed. A food with no known way of being counted (g, ml or each) is skipped and the count is shown, never guessed; give it a unit on its own row first.
- **With cupboards and stock switched off, none of this appears or acts.** Checking this I found three places that would have ignored the switch: Shopping complete putting non-nutritional items back on the shelf (which quietly switched stock on again), the stock note on shopping list rows, and the new search button. All three now respect the switch. Test p251 covers both on and off.

## v3.10.1146
- **💡 Ideas on a Use soon line opens Next meal idea with the food filled in.** Pete: pressing Ideas dropped him on the Today dashboard, where nothing showed. It now goes to the Log chat and opens Next meal idea with a new **Use up** box at the top, already holding that food (edit it, or press Ideas on other lines and they are added to the same box). **💡 Ideas using these** asks for suggestions built around what is in the box (your library and recipes, limited to what your cupboards can make; it says so plainly if nothing can use them), and choosing categories or Snack ideas uses the box too. Nothing is sent until you choose, nothing carries over between flows, and a plain Next meal idea or a typed request has no focus. The wrong-tab bug was mine: the old code switched to a tab name the app does not have, so it fell back to Today.

## v3.10.1145
- **Cupboard item screen: saves as you go, with an Undo that stays on screen.** Pete asked whether Save/Cancel are justified: the app mixes about 30 differently worded save buttons and 39 Cancels with roughly 215 fields that save the moment they change, and overwriting a figure and then wondering what it was is the real problem. This is the pilot for one rule: *changing something that exists saves as you change it; making something new has one clearly marked button.* On an existing item there is no Save and no Cancel. Each change is saved when you leave the box or pick a choice and a bar shows exactly what changed ("Saved: Stock now: 800 g → 500 g") with an **↩ Undo** button that stays until you go Back; Undo again steps back further, restoring stock, reorder level, pack and serving sizes, shop, where it is kept, how long it lasts and the use-by date. A value the app cannot read is refused with the reason and nothing is overwritten. **Back** replaces Cancel and never asks anything because nothing is pending. A new item still has one button, now worded "Add to my cupboards", and nothing exists until you press it. Remove (with its confirm) and Add to shopping list are unchanged. Other screens still use Save/Cancel; they will be moved to the same rule one at a time.

## v3.10.1144
- **Shopping complete no longer needs a browser pop-up.** Pete pressed "Shopping complete: empty the basket" and nothing happened. The button asked its question with the browser's own pop-up, and a browser can swallow those silently (it answers "no"), so the button did nothing and said nothing. It now uses the app's own confirm box ("Empty the basket" / "Not yet"), which cannot be suppressed.
- **A non-nutritional item you bought is not sent to the "how much did you buy" step and is not re-listed.** Non-nutritional things are flagged low by hand (the 🛒 button), never by a reorder number, so the automatic running-low list ignores them; they stay on the shelf when you complete a shop.
- **Use soon: the food's name takes you to it in the cupboard list.** Pete audits his pantry, fridge and freezer from that list. Tapping the (dotted-underlined) name opens My cupboards on the All tab with no search and every aisle open, scrolls to that food and flashes it.
- **List rows:** the stock note no longer repeats "running low" (the red tag already says it; the note now reads "1 left"), long names wrap, and the basket's "Put everything back on the list" button is styled like the other buttons.

## v3.10.1143
- **Use soon is one food per line, with a 💡 Ideas button.** Pete: the run-on paragraph "could be a lot better". Each food that needs eating now has its own line showing when and how much is left (for example "tomorrow · 400 g"), and a **💡 Ideas** button. Tap it and you land in the Log chat with the normal meal-idea suggestion (your library and recipes, limited to what your cupboards can make) asked to build around that food; if nothing in your lists can use it, it says so. Meal ideas still lead with the use-soon foods anyway.
- **The shopping list shows the stock behind each item.** A row that is on the list because it ran low reads "running low: 100 g (reorder at 200 g)"; one that is on the list for another reason and is in your cupboards reads "in stock: ...". Nothing is shown for foods you do not track, or for a food with no count, so nothing is guessed.

## v3.10.1142
- **Weight logged against a cupboard item counted in ml (or the reverse) is converted, using a figure you give once.** Pete logged 500 g of Asda double cream (the library holds it per 100 g) and got "could not read the amount": the receipt counted the cream in ml (2 x 600 ml) and the app would not turn grams into millilitres without a density. Now it asks once: "How many grams is 1 ml of it? (Water is 1...)". Your number is remembered for that item, 500 g then comes off as ml and every later weight converts by itself. Nothing is assumed: no answer, a non-number or an impossible one (25 g or more per ml) leaves stock alone. Same the other way for ml logged against a gram item.

## v3.10.1141
- **A logged food is linked to its cupboard item, and the link is remembered.** Pete: "the whole purpose of this is that it will match". When a logged food's name matches no cupboard item (even ignoring the shop brand, v3.10.1140), the app now looks for the one item whose name shares all its words ("Double Cream" and "ASDA Fresh Double Cream"). If there is exactly one, it asks once: "Is that the ... in your cupboards?". Yes takes the amount off now and remembers the pairing, so that food comes off the same item every time without asking. No leaves stock alone and is never asked again for that pair. Two or more candidates are never guessed between. Nothing is taken without your yes the first time.

## v3.10.1140
- **Logging a food takes stock off when the name differs only by the shop's brand.** Pete logged 1000 ml of Asda double cream and the cupboard stayed at 2000 ml: the logged food was "Double Cream" (or "Asda Double Cream") and the stock item "Double Cream (Asda)", so the names did not match and the app skipped it without saying. Names now match with any bracketed text and the word "asda" ignored, but only when exactly one stock item fits; two or more (say an Asda and a Tesco double cream) are left alone and a note says so. Anything else, such as "Single Cream", still does not match. Earlier logs are not re-applied.

## v3.10.1139
- **Non-nutritional things you buy now land on the shelf.** Pete imported cola, Irn-Bru, Vimto and sugar as a list marked non-nutritional; after Shopping complete they were nowhere, because only items already tracked in My cupboards were carried over and a list import never touches the cupboards. Now any non-nutritional item in the basket is put on the shelf (flagged non-food, no count invented) when you press Shopping complete, so it shows under Add > Non-nutritional and gets the 🛒 button. Foods are unchanged. Items already completed before this version are gone from the list and must be added again.

## v3.10.1138
- **Add > Non-nutritional shows what is on your shelf.** Pete: he had to type the name of a non-nutritional item without knowing what he already held. Choosing Non-nutritional on the Add card now lists every non-nutritional item in My cupboards, each with "＋ Add to list" (or ON LIST if it is already there); typing a new one is still below.
- **My cupboards always shows the Non-nutritional tab,** even when empty, with a line saying how to fill it. Typing a name in the cupboards search now also offers "Add as non-nutritional" next to "Add as a new food", so you can put one on the shelf from there.

## v3.10.1137
- **Non-nutritional stock you flag as running low yourself.** Pete: there is no way to police a reorder level for toilet roll, so he says when it is low. Each non-nutritional row in My cupboards has a 🛒 button: tap it and the item goes on your shopping list under its shop (the row then shows ON LIST). Tick it into the basket, Shopping complete clears it, and it stays on the shelf. No numbers are guessed or needed.
- **The Non-nutritional group on the shopping list starts folded.** Tap its header to open it; a fold you set yourself is remembered.

## v3.10.1136
- **Basket button renamed** so it cannot be mistaken for the import screen's Untick all: in "In basket" it now reads "Put everything back on the list". Same action.

## v3.10.1135
- **Untick all in the shopping basket.** Pete could not find one: Untick all lived only on the import review screen. Open "In basket" and the first button, "Untick all (put everything back on the list)", puts every ticked item back on the list. Nothing is deleted.

## v3.10.1134
- **Lines you switch to Non-nutritional on a receipt import are no longer left behind.** Pete marked about 20 lines non-nutritional and none reached the cupboards: a line the importer could not read kept an empty amount and stayed unticked, and Tick all skips lines without an amount. Switching a line to Non-nutritional now counts it in items (the receipt quantity, or 1; a weight or volume becomes a count, flagged "check how many"), ticks it, and files it as non-food. New button "Tick non-nutritional only" next to Tick all / Untick all. List imports keep free-text amounts like "2 bottles". Cause inferred from reproducing the steps; Pete's own phone data could not be seen.

## v3.10.1133
- **Add a non-nutritional item to the cupboards by hand.** Pete could not find non-food stock: it only came from receipts, and the Add a food screen had no way to add one. Type a name there and a second choice, "Add as non-nutritional (toilet roll, cleaning, pet food)", counts it in each, flags it non-food and keeps it out of the food library. The Non-nutritional chip then shows in My cupboards.

## v3.10.1132
- **Fridge life rules can use a whole section.** Pete wanted "fruit and veg 14". The rule form has a section picker (Fruit and veg, Fruit, Vegetables, Salad, Meat, Fish, Dairy, Bread) as well as words. Sections follow how the app already sorts each food; apples, bananas, grapes and lemons are filed as Other by the app's sorter, so those need their words typed in a rule. (Backlog: teach the sorter common fruit.)

## v3.10.1131
- **Fridge life by type of food, set by you.** Pete: cheese keeps much longer than the blanket 3 days, so every cheese showed "use soon". Stock rules > Fridge life by type of food: type words from the food's name ("cheese, cheddar") and the days it keeps; any fridge food with one of those words uses your number. A food's own length still wins, and nothing is built in or guessed. Dates the app worked out move by the difference (the bought date is kept); a date you typed is never moved; deleting a rule puts it back.

## v3.10.1130
- **Non-food stock is easy to find in Check the cupboards.** Pete asked where toilet roll and bin bags are. In the My cupboards card they are under the Non-nutritional chip (and All); in Check the cupboards they were mixed in with foods, and toilet roll was labelled "Oils & fats". They now say Non-nutritional, and a Non-nutritional filter chip shows only them (it appears only when you have some).

## v3.10.1129
- **Fix: a list import put 0 items on the list.** Pete added items to Asda and saw 0. In "A list to shop for" a food with no amount started unticked and Tick all would not tick it (the rule that a stock count needs an amount was applied to a shopping list too), so the button read "Put 0 items on my list". Every listed line now starts ticked and Tick all ticks them; stock imports still need an amount.

## v3.10.1128
- **✨ Ask AI on an import row that is not matched yet.** Pete: "AI comparison needed before manual maybe?" A row with no match, or only a closest guess, has an **Ask AI** button. It sends the receipt line and the names of foods you already have (library and cupboards, never your numbers or health data) and the AI must answer with exactly one of those names or NONE. Anything else is thrown away, so it cannot invent a food. A good answer is shown with **Use this**; nothing links until you press it, and then the row turns green Matched. If the AI is unavailable it says so and you match by hand.

## v3.10.1127
- **"✓ Add this one now" on every import row.** Pete wanted the import to save as he goes. A ticked row with an amount can be put into the cupboards straight away; it then locks as "✓ Added to your cupboards" and the bottom button adds only what is left, so nothing is counted twice (also after a reload). The import is logged once for the duplicate warning. Untick/undo is not offered: fix a count in Check the cupboards.
- **CSV import rows show the same match state as the receipt import.** Each food row says "✓ Matched", "⚠ Check this" (a suggestion you have not confirmed yet) or "＋ New food". A row you have answered now stays on screen and turns green instead of disappearing, and the "need a quick look" count is only what is still open.

## v3.10.1126
- **An import in progress is saved as you go.** Pete: "we need it to be saving as we're going along". Every change on the import review (ticks, amounts, names, a Match pick, the shop, the date) is saved on the phone straight away. Leave the screen, take a call or reload, press Import again and the same list is back. "Start again" throws it away; adding it to the cupboards clears the saved copy. (Only the review step is kept, not the which-column-is-which step.) "Cancel" became "Leave it for now (saved)".
- **Fix: the ↑ button now appears on Shopping, including Check the cupboards.** The Shopping scroll area was the one view not reporting its scrolling to the shared ↑/↓ buttons, so ↓ showed but ↑ never did.
- **Edit entry is easier to close.** Pete needed several presses of Cancel in Today's log. I could not reproduce a hard fault, so this makes it forgiving: Cancel is a full finger-sized button, there is a second "✕ Close" at the top of both edit forms (single and per-ingredient), and the form scrolls to the middle of the screen when it opens, away from the screen edge and the floating arrows.

## v3.10.1125
- **Import rows show one clear match state.** Pete asked what actually tells him a line is matched: before, only a small grey caption changed. Each row now shows a green "✓ Matched" (picked by you, remembered, or a sure library match), an amber "⚠ Check this" when it is only the closest guess, or "＋ New food" when nothing matched, and a long matched name is shown in full under the box (test p230).
- **Fix: Cook Mode is readable on the light theme.** The Cook Mode screen had a fixed dark background but used the theme's text colour, so on a light theme the steps were dark on dark. It now follows the theme. Test p229. Found while recording the tour.
- **Recipe to shopping list now leaves off what is in your cupboards.** With the cupboards on, a counted food with some left (not low, not past its use-by) is not put on the list from a recipe or a meal plan, the checklist labels it "in your cupboards", and the message says how many were left off. Low, out, expired and uncounted foods still go on. Test p228.
- **Fix: ingredients land on the food of the same name.** An AI-suggested ingredient such as "Olive oil" could be matched to a longer, earlier library entry ("Sardines in olive oil, drained") because both scored 100%. An exact name (ignoring case and spacing) now always wins, and on a tie the closest name (fewest extra words) wins. Test p227. Found while recording the short tour.

## v3.10.1124 – A Shopping page that flows: sections, a compact cupboards view, one Import button
- Pete Spence, after trying the cupboards on his real phone: the Shopping page "looks haphazard", is "too fragmented", with "no collapse, no hide, no reorder", two import buttons that did different things, and a worry that a list of every food would be endless.
- **Three sections in one flow** (My list, Add to the list, My cupboards), each with the same title, ? help and ▲ ▼ 👁 ▾ controls; fold, hide and reorder any of them, remembered. The old two-area layout is upgraded, not lost. The buttons are an even two-column grid; Copy list moved into My list; Shopping complete only appears once something is ticked; Send / Receive stock and Turn off are small links.
- **My cupboards view.** Only the foods you hold (never the library); tabs All, Fridge, Freezer, Cupboard, Non-nutritional, Low and Use soon with counts (an empty tab hides itself); aisle headings that fold; tap a food to open it (amount, reorder, shop, storage, use-by) with **Add to shopping list** and **Remove from my cupboards**; a search that also finds foods you do not hold and adds them. "Tracked" is now "in my cupboards" everywhere.
- **One 📥 Import button** (Add to the list and My cupboards). It asks *What is this?* — I have just bought this (adds to the cupboards), Starting my cupboards (sets counts), A list to shop for (shopping list only, cupboards untouched) — and shows a *What can I import?* hint. A shop column and a food-or-not column in a table are understood. **The same receipt pasted twice is noticed** (fingerprint kept with the stock, newest 30) and nothing is counted again unless you tick *Add it again anyway*.
- **Non-nutritional** replaces "Not food" on every screen. Pete's example "COOK by ASDA Cook by Mediterranean Veg Mix 500g" now offers *Same as Asda Mediterranean Frozen Vegetables* (library match, tick off by default; a loose match is never linked for you), and everyday groceries (coffee, squash, bread, veg) no longer ask whether they are food; tea towels, toilet roll and the like still ask.
- Tests: new p223 (CSV library match), p224 (sections), p225 (cupboards view with a 300-food library), p226 (import purposes, shop and type columns, duplicate guard); p201, p207, p213, p218 updated. All mutation-checked.
- Known and left alone: the suggested 3-day fridge life makes every fridge food "use soon" until its own length is set (the Use soon tab shows this); the old CSV screen is no longer reachable from the UI (code and tests kept, see BACKLOG).

## v3.10.1123 – Meal ideas only use what you can make (stock-aware suggestions)
- Pete Spence: Next meal idea and Balance my macros "should only use ingredient suggestions containing items we have in stock or could substitute for a known valid substitution", so the menu never offers anything you cannot actually make.
- **One filter in one place.** Next meal idea, Balance my macros and the category picker all go through `suggestMealFromLibrary`, which now filters foods and recipes by stock *before the AI sees them*, so it cannot suggest what it was never shown. A footer on the result says so ("Only suggesting what you can make (N hidden…)") with a **Show everything** link, and if nothing in the cupboards makes a meal it says that and offers "Suggest from everything instead".
- **Three settings** (Stock control card): **Hide what I am out of** (default; foods you have not counted are assumed to be in the cupboard), **Only what I have counted**, **Off**. Stored in `mh_shopping_suggest_v1`, so it travels in backups. Nothing tracked at all means nothing changes.
- **Recipes** are offered only when every ingredient has its figures (calories, protein, carbs known) and is in stock, can be swapped, or the recipe is already cooked and waiting (leftovers count, and the AI is told).
- **Swaps are strict, never guessed:** a curated like-for-like list (hard cheeses, creams, milks, butters, oils, chicken cuts, white fish, nuts, leafy greens, onions) plus the existing word-overlap finder for brand and size variants; the swap must be a food you have counted and in stock, carbs no more than 2 g higher for the same amount and calories within 35%. Herbs and spices swap for each other. A missing swap beats a wrong one.
- **Herbs and spices** you have not counted always count as in the cupboard (a made-up default pack would drain on its own, which would be a guess). Count one and it is checked like any other food.
- **Stock rules** (Shopping > Stock control > ⚙ Stock rules, collapsed by default), suggested defaults that are all yours to change:
  - **Never runs out** (the magic porridge pot): the herbs and spices category plus salt and cream of tartar by name. Add or remove categories and foods. They are never counted and never go low, but they are still ingredients in recipes. A food you count yourself is checked like any other.
  - **Usual portion when none is set**, by category: herbs and spices 5 g (a teaspoon), oils and fats 15 g (a tablespoon), everything else falls back to 100 g (editable). Type g, ml, tsp or tbsp. A food's own portion or serving always wins. These only decide whether you have enough for a meal idea; they are never used for calories or nutrition. "Back to the suggested defaults" resets them. Stored in `mh_shopping_rules_v1` (in backups).
- **Portions left and pace in the Stock rows:** 600 g reads "600 g (≈ 6 × 100 g)", and with 3+ uses over 3+ days in the last 14 it adds "about 6 days at your usual pace", worked from what you logged and cooked, nothing guessed.
- **Swaps you have made before come first, and they are your call.** Every swap in the recipe builder, Cook Mode or a suggested combo is remembered (`mh_shopping_swaps_v1`, in backups). Meal ideas use a remembered swap even when it fails the like-for-like and macro checks (steak with lemon jam is allowed), as long as you have it in the cupboard, and say "you have swapped this before". The swap picker gets a row above its list: **Your usual swaps for this** and **In your cupboards now** (like-for-likes you have counted).
- **When a recipe card says the stock is short of something, it links to "🔁 Review and swap"**, the existing one-off review (the same screen as Log 1 serving), where any ingredient can be swapped for this cook only without touching the saved recipe. Swaps made there are remembered like any other.
- **Recipe cards say how many batches the stock covers** ("Stock covers 2 batches (limited by Beef mince)").
- The separate "try something new" generator still invents food on purpose (it may need things you do not have); in the real-life pass below it was given a soft steer toward your cupboards.
- Test `p216` (reads the exact prompt sent to the AI; mutation-checked four ways).
- **Real-life pass (same version).** Pete Spence asked for a walk through a real week of shopping and cooking; the gaps it found are built:
  - **Use-by dates.** Optional date on any stock item (edit form), plus an automatic eat-by date on every cooked batch (today + "In the fridge" days in Stock rules, suggested 2, adjustable; a cautious default, not food-safety advice). Past the date a food or batch stops being suggested. Buying more or running an item out clears its old date; a stock-take does not. A **Use soon** strip heads the Stock card and meal ideas are told to use those first.
  - **Leftovers panel** in the Stock card: eat-by date, ❄ Freeze (moves the date out by "Frozen" days, suggested 90), ☀ Thawed it (back to the fridge time), 🗑 Bin. The recipe card note shows the eat-by date too. Transfer files carry the dates.
  - **Used up or binned.** 🗑 on every stock row takes an amount (or all) off stock and remembers it for 30 days; the card shows what was binned. Past-use-by items offer "bin it".
  - **Ate out.** A meal described as a takeaway, restaurant, pub, café or a named chain never touches stock (and a toast says so). Every log row also has a 🍽 button to mark or unmark it after the fact: it puts the stock back, and editing an ate-out entry never takes stock off.
  - **Planned meals reserve stock.** What a planned meal will use is treated as already spoken for: suggestions allow for it, the Stock row shows "500 g planned", and an item that will be low after your plans joins the shopping list now.
  - **Servings are capped to what stock covers.** Each recipe line tells the AI "STOCK COVERS: up to N servings" and a suggestion for more is cut to N with a note (what is logged is the cut figure).
  - **Fixes.** Red, green, bell, stuffed and mixed peppers (and chillies) are vegetables, not spices, so they are no longer treated as never-runs-out; black pepper, peppercorns and flakes stay spices. The "most used / rarely used" hints sent to the AI no longer name foods that are out of stock. "Suggest a recipe from what is in my library" uses only what you can make, and "Try something new" is told what is in the cupboards (a soft steer: it may still need extras).
  - Test: `p217_stock_realife.py` (mutation-checked).
- **Start stock from an order** (Stock control card > 🧾). Pete Spence: auditing every cupboard and the freezer is hard work, so start from a recent order instead. Paste an order (lines like `2 x ASDA British Mature Cheddar 400g`, the way a supermarket order page copies) or choose a CSV (item, qty, size), and stock starts from it:
  - The amount is only ever quantity × the pack size in the name (2 × 400 g = 800 g; `4 x 410g` = 1640 g; litres and kg convert). A count read from a name (`6 Bananas`, `12 Eggs`, `4 Pack`) is shown but marked **check**; a line with no size or count is left blank for you. Nothing is guessed, and reorder levels are never invented.
  - Order-page noise (dates, addresses, prices, totals, "Write a review") is ignored; where a line was substituted, what was sent is used, not what was ordered.
  - Each line is linked to your library name where it can be ("British Mature Cheddar" → Cheddar; a food in another category, such as nut butter for butter, is never suggested) and shown in an editable "Track as" box. A name you change is remembered, so next week's order links itself.
  - Not-food lines and never-runs-out foods (garlic paste, salt) arrive unticked. Foods already tracked default to "leave it as it is", with "add on top" or "replace" per line. A unit clash is refused, a bad amount is skipped with a message, and nothing is saved until you press the button.
  - Test: `p218_stock_order.py` (invented order; mutation-checked five ways).
- **Fridge, freezer or cupboard.** Pete Spence: nothing in a name says sliced onions or mushrooms are frozen, so each food has a **kept in** switch (🗄 cupboard, 🧊 fridge, ❄ freezer), tapped on its Stock row or set in the edit form. A kept food gets a use-by date when you buy it (and when it first gets a count): the food's **own length** if you have set one, else the suggested length from Stock rules (fridge 3 days, freezer 90, both adjustable and limited to sensible numbers). Cooked leftovers keep their own two numbers (2 and 90).
  - **Your own length is remembered** per food and per place ("Lasts (days)": milk 5 days in your fridge), and used every time you buy it again. Saving the form unchanged never resets a countdown.
  - Moving a food between places restarts the clock from today (freezer to fridge counts as thawed today); back to the cupboard clears only dates it worked out. **A date you type yourself always wins.**
  - **Order import:** every line has a kept-in choice. A line under a "Frozen ..." heading on the order page is marked freezer (the only clue it trusts); anything else stays in the cupboard until you say. Dates count from the **order's own date** (read from the page, editable as "Bought on"), so milk delivered on the 17th with 5 days is due on the 22nd. A food already kept somewhere is remembered for the next order.
  - Test: `p219_stock_storage.py` (mutation-checked six ways).
- **Receipts into stock (Shopping > Stock control > 🧾 Add a receipt to stock).** Pete Spence: a Costco trip with unexpected purchases, "the receipt, be it physical or electronic, should be able to be added to the stock". It follows the *update stock* route: counts are added **on top** of what is there and nothing makes a new shopping list. The same screen still does "Start stock from an order" (set the counts); a switch at the top chooses which.
  - **Reads many shapes:** till receipts (item codes, tax letters, `2 @ 3.50`, weight lines `1.234 kg @ £8.00/kg`, `x2`, `Qty: 3`, `24CT`, `12RL`, lb and oz, abbreviations like KS ORG EGGS, BNLS CHKN BRST), e-mailed receipts with the price on its own line, order pages, plain lists, and tables (CSV, tab, `|`, `;`). Totals, tax, card, loyalty, member and discount lines are ignored. Name plus pack size (or a count) is what stock needs; anything missing stays blank and is never guessed.
  - **"What is where":** a table's columns are found from the headings or the values; when it cannot be sure it shows the first rows with a selector over each column (Name, Quantity, Pack size, Price, Item code, Skip) and a "first row is headings" box.
  - **Photo of a paper receipt:** shrunk and sent to the AI already set up in the app only to copy the text out (told not to add or guess), then it goes through the same reader and the same check screen.
  - **Bought at:** the shop is read from the text when named (Asda, Tesco, Costco...), confirmed on the screen, and "Another shop..." adds one. **New names get the shop on the end** ("Baked Beans (Asda)"), the way shop variants are already named; foods already in the library keep their name. One tick turns it off.
  - **Match by hand or create:** every line has **Match...** (library and tracked foods that share a word, with a search) and unmatched lines have **Create new**, which opens Add Food with the name filled and no nutrition guessed. It saves to the library only (nothing is logged) and you land straight back on the import list with that line pointing at the new food.
  - **Non-food is tracked** (toilet roll, bin bags, washing-up liquid): counted as items (rolls, bags, bottles), flagged non-food, and when it falls to its reorder level it goes on the list as non-food. A Food / Not food switch is on every line.
  - **Takes what you bought off your shopping list** (tick box, on for receipts). Existing counts default to "Add this on top" on a receipt, "Leave it" on a first order.
- **Cupboards & stock can be switched off.** Pete Spence: the module assumes the more you supply the better it gets, so people who want the old way need a real off switch. **⏻ Turn off** on the Stock control card (asks first) puts the app back as it was: logging never touches stock, nothing is added to the list, meal ideas are not filtered, no reservations, no stock steer in prompts, no 🍽 button, and the card shrinks to one line with **Turn cupboards & stock on**. Counts are kept, it survives a reload and backups (`enabled` inside `mh_shopping_stock_v1`), and tracking a food on purpose turns it back on. It **starts off** for anyone who has not counted anything (anyone with counted foods keeps it on), and the off card says what switching it on does, including that used-up foods will not be offered. Test p221, p222.
- **Surprise sweet / Surprise savoury now give two ideas.** One is made from what you have (the library, filtered by stock when it is on) and one is a new idea that searches the web for a real recipe for inspiration and writes its own version with an "Inspired by" line. If the web search cannot be done it falls back to a plain idea; a typed request is unchanged. Test p222.

## v3.10.1122 – Fasting now handles planned meals (the timer no longer vanishes)
- Pete Spence: "if you enter a planned meal, the fasting timer disappears and you only get a line."
- **Found and fixed the cause:** a planned meal ticked "Ate it" *before* its planned time was logged at the planned (future) time, and a meal stamped later than now made the live timer give up ("—"). Now ticking a plan before its time logs it at the real time, so the timer restarts from it; a plan already due keeps its planned time. Separately, any meal stamped later than now is ignored by the fast (it has not happened), so a typo like 22:00 at 14:00 can no longer blank the timer.
- **The Fasting card now shows what your plan does to the fast:** "🗓 Planned 18:00 (Steak): your fast would end at 7h, short of your 12h goal (12h is 23:00)", or "goal reached ✓", with tomorrow's plans labelled, plans under your fasting threshold ignored, and "It starts your next fast when you eat it" when nothing has been eaten. It updates whenever the plan changes. Nothing is ever changed for you.
- Test `p215` (fixed clock, mutation-checked).

## v3.10.1121 – Stock control: 📋 Check the cupboards (set up by walking the list)
- Pete Spence: tracking one ingredient at a time is too slow; "someone just goes down the list and checks in the cupboards", a couple a minute, filterable, no submit or save.
- **Stock card → 📋 Check the cupboards** lists every ingredient the app knows. Each row has boxes: **Have now**, **Reorder at**, **One serving** (pre-filled from your library portion where it has one) and **Bought at**. Every box saves the moment you leave it ("✓ saved", or "low" in red); the list is never rebuilt under you, so you keep your place.
- An ingredient starts being tracked when you give it an amount. It needs to know how it is counted (g, ml or each): from the unit box, or the unit you type ("500 g", "4 servings"). A bare number with no unit is refused with the reason, never guessed. Anything wrong shows under that row and saves nothing.
- **Filter:** a text box plus All / Not tracked / Tracked / No amount yet / Low. Long lists show 60 at a time with Show more.
- Test `p214` (mutation-checked).

## v3.10.1120 – Shopping: CSV import with the food / not-food sort, and shop-variant matching
- Pete Spence: four shops' worth of double cream, each with its own nutrition. **Add items → 📄 Import a CSV** reads a file (quotes, commas inside quotes, Windows line endings, headed or not: item, qty, shop, type) and sorts each line.
- **Food or not food:** remembered answers first, then anything already in your library counts as food, obvious cleaning / pet / toiletry words are spotted as not-food, and anything it cannot tell asks. Spotted ones still need your tap.
- **Matching a name to what you already have, in three passes, then it hands back to you:** 1) exact (case and punctuation ignored); 2) ingredient + shop ("Double Cream 300ml (Tesco)" is the Tesco double cream; pack size is not part of the identity; the CSV's shop column counts too); 3) near match (word order, plurals, a typo) which is only ever a pre-ticked suggestion for you to confirm. Two equally good candidates are never chosen for you (you get up to three to pick from, or "none of these"). A match only borrows the name, so the nutrition stored under it comes with it and nothing is invented: an import never creates or changes a food entry.
- Answers are remembered (`mh_shopping_match_v1`, in every backup), so the same file asks nothing the second time. Shops in the file are created; repeats are counted, not duplicated; non-food keeps its amount ("24 pack").
- Test `p213` (mutation-checked).

## v3.10.1119 – Stock control, stage 2: logging and cooking take stock off by themselves
- Pete Spence: "cooking writes the shopping list". Food you log now comes off stock automatically for tracked ingredients, through every doorway that records an amount: chat, library, recipes (Log 1 serving, Other, suggested recipe), paste-a-meal, and past days from History. Planned meals never take stock. The manual calorie form has no amount, so it takes nothing (nothing is guessed).
- Reads the amount you logged: g, kg, ml, l, a count, or servings/portions when the ingredient has a serving size. An amount it cannot read (for example "a scoop") leaves stock alone and a note says so.
- Putting it back: deleting an entry, clearing today, or deleting from History returns exactly what was taken; editing an entry returns the old amount and takes the new. Food eaten before your last stock-take is already in that count and is not taken again.
- **🍲 Cooked a batch** on recipe cards takes the whole recipe off stock once (grams only; ml and counts are left alone and named). Servings you log from that batch afterwards take nothing more; logging more than you cooked takes only the extra share; deleting the entry gives the cooked serving back. Recipe cards also say "stock covers a batch" or "short of X".
- **🛒 Shopping complete now asks what you bought** for tracked items: the usual pack size is prefilled where your stock is known (change it: "2 packs", "500 g"), empty a box to skip, and where it didn't know how much you had it asks rather than guessing. A bad entry stops everything (nothing half-applied). Restocking clears "running low" so it can trigger again. A review you leave is still reachable from the stock card. Test `p210`.
- **📤 Send / 📥 Receive stock** moves your counts from one device (the master) to another: the receiving device must have a backup (it makes one if it can, and refuses if it cannot), then it asks "file from X → this device, replaces", with a warning if the file is older than what is there. After a backup restore the stock card says counts may be stale. Test `p211`.
- Journey test `p212` walks the whole "worst shopping trip": running low while logging, wrong shop first, forgotten cream, cooking a batch, deleting a wrong entry, restoring from backup.
- Stock card help text updated. Tests `p208` (includes a source scan that fails if a new place creates log entries without taking stock) and `p209`, both mutation-checked.

## v3.10.1118 – Stock control, stage 1: track what you run out of, in whatever units you think in
- Pete Spence: "cooking writes the shopping list". This is the first of four stages. **It is manual for now: nothing comes off stock by itself yet** (cooking and logging come next, then Shopping complete adding what you bought, then the master-to-servant transfer between phones).
- **📦 Stock control** sits under the shopping list, with the same ? help and ▲ ▼ 👁 ▾ hide controls as every other card (fold remembers, hide leaves a "Show stock control" link, ▲ ▼ swap it with the list and remember).
- **Opt-in per ingredient.** ＋ Track an ingredient, or ⚡ The ones I use most (choose how each is counted and it starts tracking; no amounts are guessed). Each is counted in g, ml or each, with an optional pack size and serving size, which shop it comes from, how much you have, and a reorder level.
- **Either unit works everywhere.** With whey as a 750 g tub of 30 servings of 25 g, "2 servings", "2 portions" and "50 g" are the same, and "reorder at 5 servings" is 125 g. Amounts show both ways ("125 g (5 servings)"). Also kg, l, packs and each. Nothing is guessed: a bare number needs a unit (except for "each" items), servings need a serving size you gave, packs need a pack size, and grams and ml are never converted into each other. If your library already has a portion for the ingredient, the form mentions it but never fills it in.
- **Running low.** At or under its reorder level an item goes on your list under its shop, tagged "running low", once per time it runs low: take it off yourself and it stays off until you restock and it runs low again. An item whose shop is not on this trip waits and arrives when that shop does (nothing is put under the wrong shop); one already on the list is not duplicated.
- **Safe with history (used by the next stage).** Using stock is recorded so deleting or editing a logged entry can put exactly that amount back, even if it was clamped at zero. Setting the amount yourself is a stock-take: it freezes everything before it, so tidying old history never changes your cupboard.
- Stored as `mh_shopping_stock_v1` (the `mh_shopping` prefix gives it the big-key backup ceiling); in every backup and restored with it. Tests `p206` (checked it fails if the freeze is broken) and `p207`.

## v3.10.1117 – Fixed: big shopping lists and saved lists could silently drop out of the backup
- Pete Spence: his shopping lists are often over 200 items, so nothing here may be limited by size. I measured instead of assuming: 260 items is about 64,000 characters (fine, and it renders in 7 ms), but ten saved lists of that size came to about 293,000, and the backup leaves out any single stored key over 200,000 characters. So heavy use of saved lists would have dropped them from every backup with no sign. **My v3.10.1116 note that saved lists needed no backup changes was only true for small lists; that was wrong.**
- Shopping keys (`mh_shopping*`) now have a 3,000,000-character ceiling in the backup. Restore already took everything it was given.
- Anything still left out for size is now recorded in the backup (`skippedKeys`) instead of vanishing silently.
- `p205` extended: 260 items and ten saved lists must be in the backup and come back through a real restore; an oversized unrelated key must be reported, not lost quietly.

## v3.10.1116 – Shopping: saved lists, with a merge-or-replace choice
- Pete Spence asked for saved, named shopping lists so a shop's list can be brought back after a gap ("a merge-vs-replace prompt when pulling a shop's list back in"). **Add items > 📁 Saved lists.**
- **Save** this shop's items, or the whole list across every shop, under a name you choose. What you wanted is saved, not how far through the trip you were: ticks are not saved, hidden items are left out, and a non-food item keeps its amount ("24 pack"). Saving under a name that already exists (any capitalisation) asks before replacing it.
- **Use** a saved list. If nothing of yours is at that list's shops right now (for example you removed the shop), it simply comes in, and a removed shop is added back. If you already have items at those shops, an inline choice names how many and offers **Add what is missing** (keeps everything you have, ticks included, and adds only what is not there; nothing is ever duplicated) or **Replace** (takes the items at those shops off first, then brings the saved list in; other shops are never touched) or Cancel.
- Rename (a name another list already has is refused) and delete (asks first; your shopping list is never touched).
- Stored in its own key, `mh_shopping_lists_v1`, separate from the list itself. Backups collect every `mh_*` key, so saved lists are in every backup and come back on restore; the new test proves it with a real restore. Nothing new needed in the backup code.
- New test `p205_shop_saved_lists.py`. Checked it can fail: with Replace deliberately broken to wipe every shop it flagged it.

## v3.10.1115 – Shopping: removing a shop now drops its items, doesn't reassign them
- Pete Spence, answering the open question from the shop-rewrite: "if a store is removed from a particular week, it's still going to sell the items, it's just that you didn't need them... they'd just be removed from the shopping list." Removing a shop from this list now drops its items from the list entirely rather than silently moving them onto another shop — the shop itself, its usuals and its purchase history are untouched, ready for whenever it's needed again (the forthcoming saved-list merge/replace feature is what brings a shop like that back).
- Now asks for confirmation first whenever the shop being removed actually has items on the list, naming the shop and how many items will come off — removing an empty shop still needs no confirmation. Previously this reassigned silently with no way to tell it had happened.
- New test `p204_shop_delete_drops_items.py`.

## v3.10.1114 – Fibre audit: one-tap bulk clear for meat, fish, dairy, fat, herbs & spices
- Pete Spence asked whether dried basil's fibre figure could just be looked up rather than typed each time. Checked real USDA-sourced figures (myfooddata.com) rather than go from memory: even the highest-fibre dried spices (oregano, basil) only contribute about 0.3-0.4g per teaspoon at the serving sizes anyone actually uses — below the 0.5g he'd already judged not worth tracking. So rather than a table of per-100g numbers (which also varies by source and risks locking in a wrong figure), the fix is simpler: meat, fish, dairy (eggs included, by the app's existing tagging), fat/oils and herbs & spices are either structurally fibre-free or round away to nothing regardless of amount.
- The fibre audit (`mhNutrientAudit`) now shows a single "Mark these N as no fibre" button covering every outstanding item in those categories at once, instead of tapping "No fibre" on each one individually. A meal entry is never swept up even if it carries one of those category tags, since a composite dish can still carry real fibre from other components; anything already checked, or outside those categories, is untouched. Everything else about the per-item audit flow is unchanged.
- New test `p203_fibre_bulk_negligible.py`.

## v3.10.1113 – Fixed: 7 Today cards were missing their fold control, and "hide" was shouting on one card
- Pete Spence (three screenshots): "A show/hide missing… Uppercase HIDE and lowercase hide? What happened to consistency?" No revert happened (checked `git log`/`git status` — clean, matches this version) — these were pre-existing gaps, not a regression from recent work.
- Audited every card with move (▲▼) and hide (👁) controls and found 7 that had never gotten the 4th "▾ hide" fold-to-bar control that Water, Fibre and Fasting have: **Day mode, Ketosis, Macros (the 4 progress tiles), Macro Ratio, Goal check banner, Meal plan and Weather**. Meal plan looked done (it was already half-wired into the fold list) but had no matching body element, so toggling it silently did nothing — an earlier "meal plan's show/hide is fixed" from me was wrong; I'd only checked move/hide, not fold. All 7 now fold and remember it the same way as every other card.
- Fixed **Today's Log** showing "▾ HIDE" in capitals while every other card says "▾ hide" — `.log-title`'s `text-transform: uppercase` was cascading onto the label inside it. Now stays lowercase everywhere.
- New test `p202_card_fold_consistency.py` checks all 7 cards' fold control exists, works, survives a reload, and that Today's Log's label is lowercase.

## v3.10.1112 – Shopping: non-food items (first part of the shopping list overhaul)
- **Food / Not food** toggle on ＋ Add items > type an item. Not food shows an amount box (free text — "24 pack", "2 bottles") since there's no nutrition to size a portion against. Tested: the toggle resets to Food each time the add panel opens, and picking Food back never carries over an amount or a non-food category.
- Non-food items sit in their own **Not food** section, always last, with the same fold and ☑ all as every real aisle — never mixed in with "Other" (unmatched but real) food.
- Never touch the food library: invisible to My foods, Quick list, recipe search, "recently added" and every nutrition stat, search or report, by construction — nothing to separately hide. The amount shows on the row and carries into Copy list ("Toilet roll (24 pack)").
- First part of the wider shopping overhaul Pete's asked for (CSV import, saved list templates, multi-store nutrition variants) — the rest follows in later versions.

## v3.10.1111 – Fixed: a strength session could silently stop crediting calories/protein at all
- Pete Spence (screenshot): a strength session logged its sets fine, but showed no calories burned and no change to any target. Root cause: both crediting paths (a routine session and the manual "Log a workout") look up the Resistance row on the Activities card by `acts.findIndex(a => a.type === 'resistance')` and only act `if (resIdx > -1)` — with no else. That row is an ordinary activity, removable like any other from the Activities card's edit mode, and nothing ever re-created it once gone. Once removed, every future strength session or routine would credit nothing at all, silently, forever — no toast, no error, nothing to notice beyond the numbers just never moving. Fixed: both paths now re-create the Resistance row on the fly if it's missing, the same shape a fresh profile would have, rather than ever dropping the credit. Covered by two new checks in p169.

## v3.10.1110 – Quick list: Show is 5/10/15/20, not a free 1-10
- Pete Spence: the Quick list's "Show" count was a 1-10 picker. Changed to the four sizes people actually want — 5, 10, 15 or 20 — same behaviour otherwise (never includes usuals or what's already on your list).

## v3.10.1109 – Fixed: ketosis message shown twice; a strength routine now survives a screen timeout
- Pete Spence (screenshot): on a deep-ketosis day the main **DEEP KETOSIS** badge at the top of Today and a second "Deep ketosis ratio... Optimal for your therapeutic protocol" box under Macro ratio were both saying the same thing. The second box's dismiss didn't persist either, so it came back every reload. That branch is removed — the box still shows its two genuinely different warnings (low fat + low carbs = low energy; carbs fine but fat % still short of the therapeutic floor), it just no longer repeats the badge's own "you're on track" message.
- Pete Spence: a strength routine session didn't survive a screen timeout — reps, weights and notes typed in between sets could vanish if the phone's screen went to sleep mid-workout and Android reclaimed the backgrounded page. Two fixes: the screen now stays on for as long as a routine session is open (same mechanism Cook Mode already uses), and the whole in-progress session is also saved to the phone as you go, so even an explicit phone lock (which a screen-on lock can't prevent) doesn't lose it — reopening that routine offers to resume exactly where you left off, or start fresh.

## v3.10.1108 – Fixed: "No fibre" silently rejected on foods with no saved portion
- Pete Spence (screenshot): tapping **No fibre** on Black Pepper in Nutrient Figures in Your Library did nothing — it stayed on the outstanding list. Root cause: `mhAuditSave` checked for a saved portion before doing anything at all, even for "No fibre", so a food with no portion saved bounced with a toast and nothing was recorded. A portion matters for a fibre *amount* (it's per-portion), but "No fibre" is zero at any size and never needed one. "No fibre" now saves immediately regardless of portion; typing a fibre amount still asks for the portion first, as before.

## v3.10.1107 – My usuals: search your ingredients
- On My usuals, typing now searches your saved ingredients. Tap one and it becomes a usual and goes on your list. Already bought it? Tap it again in the usuals list to take it off. You can still type something new and tap Add.

## v3.10.1106 – Shopping: pick straight into My usuals
- On Add from my foods, choose **Add to: This list / My usuals (shop)**. In My usuals mode a tap makes it a usual for the shop you are in (tap again to remove) and does not touch your list.

## v3.10.1105 – Shopping: shops, and a quick list with sources
- **Shops:** tap a shop chip (Asda to start with) to choose where new items go; ＋ Shop adds another, such as Butchers. With more than one shop in use the list is grouped by shop, then by aisle.
- **Shopping complete** clears only the ticked items of the shop you are in. Other shops stay as they are.
- **My usuals are per shop** (butchers usuals are separate from Asda).
- **Quick list sources:** Most eaten, or Recently added (the last things you put on any list), still 1 to 10 and still leaving out usuals and anything already on the list.
- Existing lists carry on as Asda.

## v3.10.1104 – Shopping: a live quick list, one-tap recipes, aisle folds
- **⚡ Quick list** (under ＋ Add items): a live shortlist of the ingredients you eat most, up to the number you choose (1 to 10). It leaves out anything in My usuals or already on your list. Tap one to put it on your list; ⭐ keeps it in My usuals; ✕ means not this time (it comes back after Shopping complete); 🚫 means never show it again (undo under Hidden suggestions). Another item takes its place each time. It is grouped by aisle, each aisle folds, and ＋ all adds a whole aisle.
- **Recipes in one tap:** tap a recipe and all its ingredients go on your list. Take any you do not need off with ✎ Edit.
- **Aisle headings on the list fold** (▾/▸) and have ☑ all to tick the whole aisle into the basket.

## v3.10.1103 – Tap a progress bar to see the history behind it
- **Water:** tapping the bar opens the water chart.
- **Fasting:** tapping the bar opens your fasting history (Insights > Reports). Until you have 7 measured fasts it tells you how many you have instead.
- **Fibre:** tapping the bar opens a 14-day view of fibre by day against your target, with a button to add missing fibre figures to your foods. A day with no fibre figures shows "none", never a made-up zero.

## v3.10.1102 – Shopping list rethought for the shop floor
- **Built to use in the aisles:** big rows, tap anywhere on a row to tick it, and the list is grouped the way you walk a supermarket: Fruit & veg, Bread, Meat & fish, Dairy & eggs, Cupboard, Drinks, Other. Ticked items drop into a collapsed ✓ In basket group so what is left stays on top.
- **Nothing fills itself any more.** Refresh, the top-N setting, Always have, the hide eye, the reorder arrows and the aisle chips are gone. You add things three ways, under ＋ Add items: type it, ⭐ My usuals (a short list you build once and tap each week), or 🍲 Recipe. 🗓 From my plan appears when you have planned meals.
- **Recipes you saved on the Recipes screen now appear** in Add a recipe, alongside meals saved in your food library.
- ✎ Edit shows ⭐ (add to My usuals) and ✕ (remove) on each row; the search box and Copy list stay.

## v3.10.1101 – My statistics tile removed from the Dashboard
- **The My statistics tile is gone from the Dashboard.** Your statistics still live under Insights; the pin-to-Today switch went with it. Saved layouts keep their order.

## v3.10.1100 – Dashboard decluttered: Shopping and Move live on their tabs
- **The Shopping and Move tiles are gone from the Dashboard.** Shopping is under Log, Move is under Today. Saved layouts keep their order; the two old slots simply drop out.

## v3.10.1099 – Quieter cards, scroll buttons on Shopping and Library
- **Meal plan and Fasting:** the explanatory text (what to type, Trust my plan, the fasting status line and guidance) now sits behind each card's ? so the cards stay clean.
- **Shopping search:** the filter box has a 🔍 and a Search key on the phone keyboard; it still filters as you type.
- **Scroll buttons:** the round ↑ ↓ buttons now work on the Shopping and Library screens, the same as everywhere else.

## v3.10.1098 – Same controls on every Today and Move card
- **One control layout everywhere:** every card now shows ▲ ▼ 👁 (move up, move down, hide) in the same order, size and right-hand position, with the fold label (▾ hide) last where a card folds. Log, Guides, Treatment, How are you today, Daily steps and Today's activity were rebuilt to match; the Fasting, Fibre, Water, Shopping and Move cards line up with the rest. Saved layouts and fold states are untouched.

## v3.10.1097 – A Move tab: exercise gets its own place under Today
- **New Move tab** on Today (Dashboard | **Move** | Supplements). Daily steps and Today's activity (activities, plan ahead, add exercise, resistance, routines, treatments of effort) now live there, so the exercise third of nutrition / exercise / sleep is no longer scattered down a long Dashboard.
- **Dashboard keeps a slim Move card:** today's steps and what you have logged, with an Open Move button. It has the same ? help, show/hide, reorder and fold controls as the other cards. Nothing is estimated; with no steps it says so.
- **Move cards have their own show/hide and reorder,** with a Hidden strip to bring one back. Default on the Move screen resets only Move, never the Dashboard.
- **Shopping list: ticked items fold away.** Tick something and it drops out of the to-buy list into a collapsed **✓ In basket (n)** group at the bottom (tap to show or hide it), so what is left to buy stays on top. Untick to bring it back; the arrows move items among what is shown; All, None and the search work across both.
- **Nothing is lost:** a saved Dashboard order keeps its shape (the old steps slot becomes the Move card, activity moves to the Move tab) and a card you had hidden stays hidden. Typed commands ("hide the steps card", "hide the move card") and app search still find everything; links that used to scroll to the activity card now open the Move tab.

## v3.10.1096 – Shopping list: filter by name or brand
- A **filter box** above the list (shows once the list has more than a few items). Type any part of a name or brand, such as "Asda" or "cream", and only matching items show, with a "Showing 3 of 12" line. All and None apply to what you can see, so you can untick or tick every double cream in one go. The ✕ clears it. It combines with the category chips.

- **Shopping list is now its own tab under Log** (Log, History, Library, **Shopping**), laid out like Library: search box at the top (always there, not just once the list is long), then the list, with Add your own, All, None, By aisle, Copy and Shopping complete underneath. It is no longer a pop-up, so a long list scrolls naturally. The Today card button jumps straight to it, and the app search finds it.
- **Shopping list layout fix:** the buttons (Refresh, My foods, Recipe, All, None, By aisle, Copy) each stretched the full width of the screen and squashed the "Add your own item" box to a sliver, pushing the list itself down the page. They now sit in a tidy wrapped row and the add box is full size.
- **Card controls made identical (Fasting, Fibre, Water, Shopping list):** the same round **?** help button as the rest of the app (Fibre and Shopping had a different ⓘ, Fasting had a "details" word), the arrows / eye / hide on their own row, and the big number underneath instead of squeezed beside the controls. Fasting's long guidance now sits behind the one ? button.

## v3.10.1095 – One Language button on the first screen; the fibre audit never assumes a portion
- **First screen:** the nine language flags across the top are now one **🌐 Language** button (showing the flag of the language in use). Tap it and the list opens; tap again to close. Nothing else about choosing a language changed, and Settings still shows all nine.
- **Fibre audit, no assumed portion:** a food with no saved portion now says "Portion not set" instead of quietly showing 100g, and asks what portion its figures are for. Neither a fibre amount nor "No fibre" is saved until the portion is confirmed, and the confirmed portion is stored on the food. Foods that already have a portion show it as before ("One portion = 80g").

## v3.10.1094 – Shopping list
- **🛒 Shopping list** (new Today card with show/hide and reorder, and a full list behind it). **Refresh** builds it from what you actually eat: the top N most-used, most-recent ingredients (10 by default; pick 5 to 50 on the list; a saved meal counts for each of its ingredients), plus the ingredients of anything on your meal plan. Refresh only ever adds: it never removes, unticks or un-hides anything, so the list stays exactly as you left it until you press **Shopping complete**, which empties the ticked items from the basket and keeps the rest.
- Tick or untick items, **All** / **None** (applies to what you are looking at, so "all the meat" works), hide and show hidden, reorder with the arrows, filter by category (just the butcher, say), and **By aisle** to sort the whole list in shopping order. **Copy** puts the unticked items on the clipboard as a plain list.
- **My foods picker:** every ingredient you have saved, including those inside your meals, with search, so you can add things Refresh would not pick up. Your own free-text items too.
- **Recipes:** pick a saved meal and untick any ingredient you do not need to buy; the choice is remembered per recipe, and the meal plan feed honours it.
- **I always have this** (🏠): staples such as salt or olive oil come off the list and are never suggested or added from a recipe again; manage them under "Always have".
- **Quieter cards:** Fibre, Water, Fasting and Shopping now have a visible **▾ hide / ▸ show** on the card (folds it to its title; remembered), and the explanatory text under the progress bar (Fibre's 14-day note and audit link, Fasting's last-meal and window lines, the shopping blurb) sits behind a small **ⓘ / details** toggle, closed by default. The fasting caution is never hidden.
- **Fibre audit fix:** each food now says which portion the figure is for ("One portion = 100g"), and the fibre box is wide enough to type in (it was squashed to a sliver on a phone).
- Stored in one key (`mh_shopping_v1`), so it is in every backup. Test p197; p36 now expects the new card in a migrated order.

## v3.10.1093 – Premium register-interest moved to a Tally form
- Every "register your interest" link (app, landing page, guides, public README) now points at the Tally form, because the GoDaddy website-builder plan cannot run PHP or take sign-ups. The licence service address is unchanged and still needs PHP hosting later.

## v3.10.1092 – Fibre target, and a check on missing nutrient figures
- **🌾 Fibre card on Today** (show/hide and reorder like every card): today's fibre against a target (30g by default, the UK adult guideline, editable in Settings > Fibre Target) and a 14-day average. A day counts only when at least one food carries a fibre figure; unknown is never read as zero, and under 5 such days the average says "not enough days" instead of showing a number. Existing saved layouts keep their order; the card slots in after Macro ratio.
- **Nutrient audit** (Settings, and a link on the card): how many library foods carry fibre, saturated fat, sugars, salt, iron, potassium, magnesium, vitamin D and omega-3, plus a most-used-first list of foods with no fibre figure, each with Save or No fibre. Nothing is estimated or filled in; marking "No fibre" sets a confirmed zero that later edits keep.
- **Finding:** the built-in starter foods carry no fibre values at all, so fibre totals depend on foods you or the AI have entered with a label.
- About 40 new entries per language. Test p196.

## v3.10.1091 – The whole app in your own language
- **Every screen, not just Today.** A whole-app Spanish scan (Today, Log, History, Library, Trends, Statistics, Reports, Settings) found English left on Statistics (titles, "Top 10 foods", weekday names, buttons), Reports (sleep, exercise, fasting, outcomes, weight, carb adherence), Trends (the Premium example cards, "Your routine", usual meal times, usual sleep, HRV baseline), body composition verdicts ("Gaining fat, losing muscle" and the rest), the Patterns and outcomes sentences, exercise categories, and Settings > Data. About 280 new entries per language across all eight non-English packs, rerun-safe via `tools/lang_add_sweep.py`.
- **Pattern matching widened.** Short patterns now accept a number with a unit (`50g`, `2200 kcal`, `1h01`), and text of 5+ characters is matched (`10 days`, `All (3)`), so counts and sums translate as well as sentences.
- **Fixed:** the bedtime finding could show `22:31.72413793103442`; the clock time is now rounded.
- Left alone on purpose: food names and other things you typed, units, file names, commands, theme names.
- Test p195 (Spanish whole-app scan).

## v3.10.1090 – Today in your own language, and one merge rule everywhere
- **Today screen in Spanish (and the other eight languages).** A Spanish demo showed English all over Today: the ketosis badge, food-in / exercise-out strip, Plan ahead, exercise and resistance headings, fasting lines and cautions, symptom names, the Premium card, supplement names and times of day. About 100 phrases added to every language file (`tools/lang_add_today.py` adds only what is missing). The translator now also matches sentences with a name or no digits in them (it only took digit sentences before).
- **One de-duplicate rule for everything that comes in or goes out.** Starter foods used a weaker name match than setup packs; both now use `mhDedupeKey` (normalised name for foods, name/label otherwise). Shared packs and CSV exports drop repeats before they leave. After a merge into the food library the existing duplicate finder is offered for near-matches (typos, different wording). The Settings text, onboarding and the pack list now say plainly that an existing library is merged, never replaced.
- Test p193 (Spanish Today scan, merge and export).
- **README restored.** `README.md` had been blank since v1048 (an earlier blanking, v1043, was a disk-full commit). Restored from the last good copy, updated to v1090, and the personal calorie/protein table replaced by a generic Nutrition targets note. Test p194 fails if README, the docs, the guide or any language file is ever empty or tiny again.
- Docs brought up to date: user guide (bedtime and morning-weight findings, ✨ explain, micronutrients, chart colours, merge rule, bad-value blanking), story page, changelog page, TECHNICAL.

## v3.10.1089 – Explain it to me
- **✨ What does this mean for me?** on What seems to move what, and **✨ Explain** on every statistic: a plain-English read of what matters most, which findings are strong or thin, and a few small things to try. Same AI route as the other reports (starter allowance or your own key); cached against the exact figures so it only costs a call when something changes.
- A legend for the markers (▲ looks helpful, ▼ looks unhelpful, ● just notable).
- Findings now need at least 10 days on each side (was 6): a real phone screenshot showed two resting on 9 days.
- Tests p192 (new), p36 and p111 updated for the stats card and the app's own language copy.

## v3.10.1088 – Readable in every theme
- New test p191 measures text contrast on the Statistics tab and the Sleep and outcomes reports in all four colour themes crossed with the three visual themes. Small secondary text was 2.4 to 2.9:1 in every theme, and the bright label colours on the sleep tiles fell to 1.7:1 in the light theme. Secondary text on those surfaces is now one step stronger, and the light theme uses deeper shades of the same hues. All 16 combinations now pass 3:1. (The app-wide secondary text colour elsewhere was not changed.)

## v3.10.1087 – Impossible device values are blanked at import
- Found by the new import test: a glitchy row in a wearable file (99,999,999 steps, a 5,000 kg weight, a negative night, a heart rate of 300) went into History as real and skewed every chart and statistic. Each column now has a plausible range; a value outside it is blanked and the rest of the row is kept. New test p190 also covers exported PDFs, every language file (valid, placeholders intact, loads from the app's own copy), and the reminder self-test.

## v3.10.1086 – Micronutrients in Statistics
- Fibre, iron, potassium, magnesium, vitamin D and omega-3 are now statistics you can build: by food, by day, by week. Foods carry them from Open Food Facts or your own entry (Library edit gained vitamin D and omega-3 boxes). A day with no figure is left out, never counted as zero. Four ready-made ones in the library. Test p189.

## v3.10.1083 – 1085 – Drag reorder, chart colours, more "what moves what"
- **v1083:** drag a statistic card by its ⠿ handle to reorder (arrows still work).
- **v1084:** a colour swatch on each Trends chart's style row recolours its main line (double-tap to reset).
- **v1085:** What seems to move what now also looks at bedtime (nights later than usual against that night's sleep), next-morning weight change, and the day of a treatment session plus the two days after. The sleep report states how steady your bedtime is. Demo nights carry bedtimes.
- Housekeeping: BACKLOG items found already built (Strength CSV merges, main-log voice logging, recipe-aware suggestions, magnesium/iron/potassium, Worker allowance and caps).

## v3.10.1082 – Colour and chart type, one tap away on every statistic
- **🎨 on each statistics card** opens a small strip: change how it is shown (ranked list, bars, line, table, donut, whatever suits that statistic) and its colour, without opening Edit. Nine ready colours plus a colour wheel for any shade; the builder gets the wheel too.
- Colours are checked as plain `#rrggbb` everywhere (card, builder, imported files), so a shared statistic cannot carry anything else. Test p185.

## v3.10.1081 (addendum) – Demo personas now carry sleep stages
- Demo history gets a deterministic night for every day: duration, deep/REM/light/awake, efficiency and sleeping heart rate, a little longer and deeper after harder exercise days. Reports > Sleep and "What seems to move what" now have something real to show in the demo. Tour videos re-recorded with Sleep and Statistics chapters.

## v3.10.1081 – Statistics on Today and in reports, speed-based energy, net of resting
- **My statistics on Today.** Pin up to four statistics (📌 on a card, or a switch in the builder) and they appear as a compact card on the Today screen after Weather, with the usual ▲▼ and 👁 controls. It stays out of the way until something is pinned.
- **Statistics in summaries and the AI.** A switch per statistic includes it in the weekly summary (screen, print and copy), the clinician view and the AI context, each stating its own period. Hidden statistics are never shared; shared files never carry pin or share flags.
- **Speed-based MET.** A walk, run or ride with both a distance and a time is now costed from its real speed using the 2011 Compendium of Physical Activities (level ground; cycling joined at band mid-points). A hand-chosen effort still overrides it, and implausible speeds (typos) are ignored.
- **Net of resting energy.** Exercise energy is now counted as MET minus 1 for estimates with no watch calibration behind them, because the daily target already contains resting energy. Once a kind of exercise has watch calibration, the measured factor applies on its own (no double correction). Settings > Formulas has a Net / Gross switch.

## v3.10.1080 – Sleep everywhere, what moves what, compare periods, weather follows you
- **Sleep is now a full citizen.** History days show a sleep panel (duration, stage bar, efficiency, sleeping heart rate). Reports gain a Sleep section (average, 7h+ nights, consistency, stages, each night, weekday vs weekend, change on the period before). Sleep flows into the AI context, the weekly summary, the clinician view and the carer page.
- **What seems to move what (Early Stage).** One engine compares days with a habit against days without it: exercise by kind and by activity, resistance, hard effort, a late last meal, an over-ceiling carb day, a very active day, or a logged treatment session. It looks at the next night's sleep, deep sleep, efficiency and sleeping heart rate, next-day HRV and symptoms, and the other way round: what a short night does to the same day's eating and movement. Only differences that are large and clearly beyond normal day-to-day wobble are shown, always as associations, never as cause.
- **Compare with the period before** inside any statistic about foods, exercises, lifts or weekdays: percentage change, new entries marked, a Before column in tables.
- **Weather location follows you.** A place set with "Use my location" is re-read on Refresh and when you open the app (at most every 30 minutes) and moves if you are more than about 3 km from the saved spot. A town you typed is never overridden.

## v3.10.1079 – Sleep in Statistics
- Statistics can now measure deep, REM and light sleep, time awake, sleep efficiency and sleeping heart rate, as well as total sleep. Three sleep statistics added to the Library.

## v3.10.1078 – Statistics tab
- New **Statistics** tab under Insights (Trends / Statistics / Reports). The Top Foods and Weekday cards moved out of Trends, with their section and filter plumbing.
- Build your own statistics: pick what to look at (foods, days, weeks, months, weekdays, exercises, kinds of exercise, resistance lifts), what to measure, total/average/highest/lowest, top 5 to all, any period or custom dates, and how to show it (ranked list, bar, line, donut, table). Live preview as you build.
- Sections (Food, Over time, Body, Exercise, My own) with search, section filter, reorder, hide/show, edit, delete.
- Library of 18 ready-made statistics; Copy as text, download CSV, and Share/Import as a small file that carries the questions, never the data.
- Pick a colour per statistic. Saved in `mh_stats_defs`, included in every backup.

## v3.10.1077
- **Clinician view** (and its copied text) now includes an Exercise block for the chosen period: active days, minutes, share at hard effort, mix by category, resistance sets and volume, with a note that energy figures are self-logged estimates.
- Verified and tested (no code change needed): a full backup carries dated exercise history, resistance sets and notes, the planned exercise, routines with template sets, the activity list, per-category calibration, remembered effort, activity level and steps baseline, and a restore brings all of it back.

## v3.10.1076
- **AI and reports know your exercise.** Prompts and generated reports now carry a LOGGED EXERCISE summary for the period (active days, minutes, kcal, effort mix, mix by category, resistance volume, recent days by name and effort), with a standing instruction to treat any link to sleep, weight, symptoms or ketosis as an association rather than a cause.
- **What your own days suggest (Early Stage).** Reports → Exercise compares next-night sleep and next-day HRV after each kind of exercise day against rest days. It only speaks with 5+ days in each group, a difference big enough to matter and a clear signal over noise; otherwise it says nothing stands out yet. Always labelled as an association, never cause. The same findings go into the AI context.
- **Sharing.** The weekly summary shows each day's exercise (activities, minutes, resistance sets and volume) in both the on-screen and copied text. The carer link carries minutes per active day, and each week card on the carer page adds "N active days, M minutes of exercise".
- The performance report picks up the new Exercise minutes and Resistance volume metrics automatically through Compare Metrics.

## v3.10.1075
- **Exercise now has its own memory.** One per-day summary (minutes, sessions, kcal, effort mix, kcal and minutes by category, resistance sets and volume) is derived from what is already saved, so every past day counts and nothing needs migrating.
- **History days** show an Exercise panel: each activity with minutes, effort and kcal, plus Resistance exercises with their sets ("2 × 12 @ 20kg, 1 × 8 @ 25kg") and total volume.
- **Compare Metrics / trend chart:** two new lines, Exercise minutes and Resistance volume, alongside logged exercise kcal and the watch's active calories.
- **Reports → Exercise:** active days, total minutes, kcal from exercise, share of minutes at Hard, minutes per week (Hard highlighted), what you did by category, resistance totals and personal bests (a star when a best was set inside the range). Rolling ranges compare against the previous period, but only when that period is properly covered.
- Demo personas now have a weekly exercise rhythm (Alex: walks, badminton, resistance, running, hiking; Doris: walks, water aerobics, yoga, gardening; Maria: walks, pilates, cycling), so the new views have something real to show.

## v3.10.1074
- **Calibration per kind of exercise.** Your watch gives one active-calorie figure per day, so on days when only one kind of exercise was logged (walking, racket sports, gym...) that day's comparison is now filed under that kind. After 4 such days that category gets its own correction, blended toward your overall factor so a few odd days can't swing it (clamped between 0.6 and 1.5). The Activity detail line says when a category's own figure is being used and why. Categories with too few days keep using the overall factor, exactly as before.
- Activities remember the effort you last chose for them, so a re-added kayak starts at the effort you usually pick instead of Moderate.

## v3.10.1073
- **Fixed (important):** v3.10.1071's exercise planner reused three function names from the planned-meals module (`mhPlanSave`, `mhPlanAdd`, `mhPlanRemove`), which broke planning meals. The exercise planner is renamed (`mhXPlan*`); planned meals work again. A new test fails the build if two `mh*` functions ever share a name.
- **Fixed:** the page no longer jumps while you type or leave a field in Activities, Resistance or Plan ahead. Logging exercise changes sections above the card; the card is now held where it was on screen.
- **Fixed:** live kcal updates in the Activities list could land on the wrong row after the Resistance split (rows now matched by index, not position).

## v3.10.1072
- **Exercise catalogue**: "＋ Add exercise" now opens a picker of 55+ known activities (walk & hike, running, cycling, water, racket & court, team & ball, gym & fitness, mind & body, outdoors & home, ice & snow) with search, an Anywhere / Indoor / Outdoor filter and category chips. Each card shows an indicative kcal for a Moderate 30 minutes at your weight.
- Each activity carries its own MET (Compendium of Physical Activities, rounded), so badminton, squash, kayaking or kettlebells are no longer all costed as a generic 5 MET. Padel, pickleball, e-bike and paddleboard are marked "est.".
- Activity rows show an indoor / outdoor tag and plain-words effort levels per activity (for example Badminton: Social knock-about / Rallies, good pace / Competitive match). Distance boxes appear only where distance matters, with the right pace bands, so no more "does it need distance?" question.
- One manual line remains ("Something else"); typed names such as "Padel with the lads" are recognised and use the real energy cost, and the History editor recognises them too.
- Plan ahead can use any catalogue activity (＋ More), and Done adds it to your activities automatically.

## v3.10.1071
- **Plan ahead** (Activity card): pick Steps, Walk, Run, Cycle or Resistance, an amount and an effort, and see what it would earn before you do it: kcal from the same MET and steps-above-baseline formulas the day uses (at your activity level), plus the +15g protein on a resistance day, and the room left it would give. Planned items show on Today's In/Out strip and only count when marked Done ✓.
- Planned steps are a target: your real count, typed or live from Health Connect, takes over, the plan shrinks as you walk and clears itself once you pass it.

## v3.10.1070
- **Food in, exercise out.** Calories & macros on Today now has a strip under the four tiles: 🍽 IN (eaten), 🔥 OUT (exercise, plus steps above your baseline) and ⚖ ROOM LEFT (target + exercise − eaten, or OVER). Exercise now sits beside the food as the other half of the day, and tapping OUT jumps to the activity card.
- New test p170.

## v3.10.1069
- Demo: Alex now has four routines (Full Body, Upper Push and Pull, Legs and Glutes, Core and Mobility) with different reps and weights per set, bodyweight and loaded sets, and notes such as "seated, slow negative", so Train, Clone and the effort suggestion have something real to show. Sample data only.

## v3.10.1068
- **Resistance, rethought.** "Strength Training" is now **Resistance**, a collapsible section under Activities that starts closed (a logged session takes a lot of room, and it is still fully editable when open). Activities keeps walking, running and the rest. The Resistance minutes-and-effort row moved into the Resistance section as the simple route.
- **One totals line** (exercises, sets, kg lifted, minutes, effort) now heads the Resistance section, shows live while you train, and summarises each routine.
- **Train and routines are separate.** "▶ Train" starts a session (from a routine, a free workout, or one exercise) under a green TRAINING TODAY banner. "🗂 Routines" is for templates only, under an EDITING TEMPLATE banner. Apply is no longer in the routine manager.
- **Clone asks for a name.** Cloning a routine asks for its new name straight away, creates it, and opens it to edit. The original is never touched.
- **Effort fills itself in.** Finishing a routine session suggests Easy, Moderate or Hard from the day's volume against your last sessions of the same routine, says why, and stops once you choose yourself.
- **Changed a routine while training?** At the end it asks once: Just for today, Update the routine, or Save as a new routine. A free workout offers to save itself as a routine.
- **Steps note under Activities** says in plain words how a logged walk and the day's steps fit together (the walk's steps are taken out so nothing counts twice, and only steps above your baseline add anything).
- New test p169.

## v3.10.1067
- Fixed: the tag lists in Reports, Compare Metrics and the before/during/after chips had one chip per exercise duration ("Exercise: 135min Cardio", "Exercise: 150min Resistance", "Exercise: 180min Walking" ...), hundreds of them on a long history. "Exercise: <minutes>min <type>" now counts as one tag per type ("Exercise: Walking", "Exercise: Resistance"), and renaming or deleting that tag changes every day that had it. Each day still keeps its own duration.
- New test p168.

## v3.10.1066
- Fixed (found in your own backups): your confirmed TDEE (3400) and standard carb ceiling (50g) were in the 11 Oct backup and gone by 15 Oct. Cause: a demo left running by an older app version saves a backup without those two fields; the next load restored from it and treated "field missing" as "delete". Cleanup now leaves any field the backup does not carry alone. Only an explicit "the real account had none" removes a value.
- New test p167 (old-format backup keeps TDEE and carb ceiling; fails on v1065, passes now). p166 also run against the app: passes.

## v3.10.1065
- Changed: the TDEE estimate in Suggested Targets now follows your Activity Level (Sedentary 1.2, Lightly active 1.375, Moderately active 1.55, Very active 1.725 times BMR), so it can no longer disagree with the level the steps check set. Before, the level used your last two weeks of steps but the estimate used the last 30 days, which could drop it a whole tier. With no level set it still uses the 30-day step average. The card names the level beside the step average. A confirmed TDEE you have entered still overrides the formula.
- New test p166 (all four levels, the fallback, the card wording). The function was also checked on its own in Node.

## v3.10.1064
- Changed: pull-down-to-refresh is blocked only while a demo is running. Outside a demo it works as before, so you can still pull down to check for updates.

## v3.10.1063
- Fixed: choosing a language with no internet changed the flag but left the text in English. The translations were only fetched from GitHub. The phone's own server now serves them (`/lang/<code>.json`), so a language works in airplane mode on the first try. GitHub is only the fallback. (Needs the server to restart once after the update.)
- New test p165: German, French and Spanish with every outside address blocked and no saved copy. It fails on v1062 and passes now.

## v3.10.1062
- Fixed (demo): the "Default" button (and any layout change that reloads the page) ended the demo AND permanently changed your real card layout. A demo now restarts itself after any reload, and your real layout, hidden cards and filters are put back exactly when you exit, or on the next load if the tab was closed.
- Fixed (demo): a downward drag at the top of the screen (pull-to-refresh) reloaded the page and threw you out of the demo. Pull-to-refresh is switched off in the app, and a reload resumes the demo anyway.
- Fixed: tapping the target banner on Today opened a carb-zones panel that listed "Strict Ketogenic", "This Protocol 35-50g" and "Holiday ceiling 60-75g" for everyone. People who are not on keto now see only their own carb target and the plain low-carb and standard ranges. Keto users are unchanged.
- Fixed: "Generate full summary" and the GBM summary now grey out offline like the other AI buttons, with the same "needs internet" explanation when tapped.
- New: building a routine, and Log a workout, now offer tap-to-add exercise chips (your own logged exercises first, then common ones) and name suggestions. Tapping an exercise you have done before fills in its last sets. The routine editor adds the exercise to the first empty row instead of leaving blank rows.
- New test p164 (carb-zones wording on 4 non-keto and 2 keto personas, Default and reload in a demo, exit and abandoned-demo restore, offline greying, exercise chips).

## v3.10.1061
- Fixed (demo): past days in History looked empty when opened, because the demo's meals had a name but no description and History hides entries without one. You could not edit or delete a past demo meal. Demo meals now carry a description.
- Fixed (demo): tapping the demo routine crashed (its exercises were plain names, the app expects name and sets), and a routine you created said "saved" but was not kept. Demo routines now go through the same normaliser as real ones and edits last for the demo. `getLastLoggedSets` also copes with a missing name.
- New test p163: Alex offline through editing and deleting today's entries, History (edit, delete entry, edit totals, delete a day, calendar), routines (create, apply, delete), fasting numbers, symptoms and treatments.

## v3.10.1060
- Fixed: in a demo, typing a meal gets its sample answer through a network call answered on the phone. The offline check counted that as a working internet connection and flipped the app to "Back online" in airplane mode, after which barcode, food search and the AI buttons stopped giving their clean "needs internet" message. A demo's own answers no longer count; the 15-second check and the browser's online event still do.
- Fixed: in a demo, "Add food" and "Save recipe" said "Added" but nothing was kept. Edits to the library and recipes now last for the rest of that demo (memory only, never written to storage, reset when you start another demo or exit).
- New test p162: Alex end to end with no internet (49 checks across Today, Log, History, Library, Insights, Reports, Settings and Exit demo).

## Tests (no app change)
- Added p161: core food flows with no internet on demo personas (typed meal preview, logging a library recipe, barcode and food search messages, recipe builder picker, "what fits" suggestions and their ingredient picker). Offline click-through of every main screen also run on Alex, Raj, Maria and John: no JS errors, stuck spinners or broken text.

## v3.10.1059
- Fixed: the ingredient swap picker (recipe builder, Cook Mode and the suggested-meal cards) is pre-filled with the old ingredient's full name, so it matched only itself and left nothing to swap with, which offline is a dead end. It now always lists the rest of your library underneath ("Other options in your library"), with the most similar foods first (most shared categories, then A-Z). Test p160 covers both the in-library and no-match cases, for an everyday and a low-carb persona, offline.

## v3.10.1058
- Fixed: swapping a recipe ingredient (recipe builder and Cook Mode) dead-ended when nothing in the library matched the old ingredient's name, which is common offline because the only way out was an online search. The picker now lists the whole library A-Z underneath, and says plainly that online search needs internet when you are offline. New test p160 (demo personas, offline).

## v3.10.1057
- Fixed: onboarding only adds the starter foods and the chosen lifestyle if the person actually reached the "How do you like to eat?" step. Before this, finishing setup by any other route (including automated tests) could add 147 foods silently. Found by the full test run (p09 expects an empty library).
- Changed: the pool data now lives at `starter_packs/data/food_pool.json`, out of the pack folder, so it is not mistaken for a starter pack (test p99 caught it). `tools/gen_food_pool.py` writes it there.
- Full persona suite run end to end: everything passes in the real repo.

## v3.10.1056
- Fixed (keto wording for non-keto profiles, second sweep): the "Sleep & Ketosis" search entry now reads "Sleep & carb adherence"; the default "Ketosis check" saved prompt reads "Carb check"; the protein drill-down no longer says "during therapeutic ketosis"; a settings help line no longer mentions ketosis streaks; and the AI Full Summary prompt no longer asks for a ketosis section, a ketogenic fat-ratio flag, a GKI line (unless readings exist) or ketone wording. Non-keto profiles get a "Carb & plan adherence" section that also names their lifestyle.
- Test p156 now also opens every card on every main screen, reads help text, tooltips and placeholders, opens every metric drill-down, checks search labels and saved prompts, and records the Full Summary and brief prompts. Left alone on purpose: the fasting help line "On a ketogenic diet?" (it is advice for people who fast, not an assumption), the GKI drill-down (only reachable by someone logging blood ketones) and the net-carb explainer's mention of keto products.

## v3.10.1055
- New: **starter foods and recipes**, one shared pool of 147 generic foods and 71 simple recipes (typical reference values per 100 g, no brands), embedded in the app so it works offline and generated from one source (`tools/gen_food_pool.py`, data in `starter_packs/food_pool.json`).
  - **Onboarding** has a new step, "How do you like to eat?": pick Balanced, Mediterranean, Higher protein or Lower calorie (or none), and tick "Add starter foods and recipes" (on by default, skippable). Keto profiles are not asked to choose and get the low-carb set.
  - **Starter packs**: all 27 pack files carry `foodPool`, so every pack preview offers a "Starter foods and recipes" tick, matched to your way of eating.
  - **Settings** (under the condition): "Add starter foods and recipes" / "Remove starter foods and recipes". Starter items are marked source "starter", so removing takes out only those.
  - Keto gets the low-carb recipes and leaves out foods over 15 g carbs per 100 g (unless a chosen recipe needs them); everyone else gets every non-keto recipe, or the ones matching the chosen lifestyle.
  - **Demos** read the same pool, so a visitor sees the same foods a new user would get (low-carb personas the keto set).
- Tests p158 (pool), p159 (onboarding step), p152 updated (150 kcal floor for light soups and salads).

## v3.10.1054
- New: **Set my own ratio** in How I eat (carbs / protein / fat percentages, must add to about 100, 5-point margin either side).
- New: **plan adherence** for anyone with a non-keto lifestyle: a stat in the weight-journey panel and a card in the report showing the share of logged days whose split sat inside the lifestyle's ranges. Keto users keep ketosis adherence. Test p157 extended.

## v3.10.1053
- New: **How I eat** (Settings, under the condition). Conditions and goals set the requirements; a lifestyle works inside them. Pick Balanced, Mediterranean, Higher protein or Lower calorie: your condition, goal and carb ceilings are not changed. The Macro ratio card on Today then judges the day against that lifestyle's ranges ("In your range / Nearly there / Off your plan") instead of a fat floor, and the AI recipe and meal-idea prompts are told your way of eating. Ranges are typical starting points, not medical advice. Keto stays its own opt-in (Go Keto!) with its disclaimer, and wins if both are set. Not offered to keto profiles. The choice is in the demo's private keys, so it never leaks into or out of a real account. Test p157 (a thyroid persona on Mediterranean).

## v3.10.1052
- Fixed: the AI recipe, "new recipe idea" and next-meal prompts told the AI the user was on a strict ketogenic diet, and the recipe prompt told it to keep every recipe low-carb/ketogenic, whatever the profile. They now say that only for keto profiles; everyone else is told to follow their own targets and not assume any particular diet (`mhDietWho()`).
- Fixed: keto wording in the recipe-idea placeholder, the treatment-day comparison text, the onboarding carb hint, the treatment report prompt and the chat prompt for non-keto profiles.
- Test p156 now also records every AI request in the next-meal, balance, recipe-idea and chat flows for non-keto personas and fails if any mentions keto.

## v3.10.1051
- Fixed: three places showed keto wording to people who are not on a keto profile: the Insights intro to the weight journey ("coloured by ketosis"), a "Ketogenic ratio" card in the reports, and "ketosis targets" in the weather help. They now say carb target, or only appear for keto users. New test p156 opens every main screen as four non-keto personas and fails on any visible keto, ketone or ketosis wording (the Go Keto! row is exempt), and checks a keto persona still sees it.

## v3.10.1050
- New: **Go Keto!** for anyone whose profile is not already ketogenic (Settings, next to the condition). It shows a disclaimer (check with your doctor, dietitian or other qualified health professional first, and who should be especially careful) and needs a tick before it switches on. It then turns on the keto cards and wording (ketosis zones, carb ceilings, ketone prompts) and sets a 50g ceiling, without changing your profile. Stop keto mode puts your old ceilings back. Works in demos too and never leaks into or out of a real account. Test p155.

## v3.10.1049
- Changed: the demo library is now much bigger and depends on the persona. Everyone gets 33 everyday foods plus either 27 moderate-carb foods or 17 keto foods (60 or 50 in all) and 24 recipes. Low-carb personas get keto recipes (beef in cream sauce, cheesy chicken bake, salmon with garlic butter spinach, fat bombs, bacon and eggs and more); everyone else gets muscle-gain and general-health meals (chicken and rice bowl, protein porridge, turkey chilli, overnight oats and more). All generic and brand-free, with full macros. Tests p152 (thresholds raised) and p154 (keto vs everyday sets).

## v3.10.1048
- Fixed: a boiled egg (or anything with "boiled" in its name) was treated as an oil by the meal-preview fat check, because "oil" sits inside "boiled". Typing "2 boiled eggs and butter" showed a red "fat looks far too low for 100g (expect roughly 90g)" warning on the egg. The oil, butter, cream, lard, ghee and dripping checks now match whole words, and "boiled onion" no longer counts as "oil added". Test p153 (fails without the fix).

## v3.10.1047
- Changed: the demo food library and recipes are now generic. The old demo library was a copy of the app owner's own food diary (supermarket brands, beers, a wine, takeaway meals) and was low-carb for every persona. It is replaced by 48 everyday foods (chicken, salmon, eggs, oats, rice, pasta, sweet potato, fruit, vegetables, nuts, dairy, whey) and 8 recipes (chicken and rice bowl, protein porridge, salmon with sweet potato, turkey and lentil chilli, tuna and chickpea salad, lean bolognese, yoghurt power bowl, tofu stir-fry), all with full macros and no brand names.
- Changed: Alex (the muscle-gain demo persona) is no longer on a low-carb style: carb target 320 g instead of 120 g, moderate meal pool.
- Fixed: Library > Log 1 serving on a recipe whose ingredient amounts were stored as text ("300g") showed NaN kcal in the review. The review now reads the amount as a number. This also hardens real recipes saved with text amounts.
- Fixed: in a demo on the default 'Local only' setting, typing a meal gave "Couldn't reach the AI" (the demo's on-device sample answer was never reached), and with no internet it said "No internet". A demo now always uses the on-device sample answer and skips the connectivity check.
- Changed: a meal typed in the demo is matched against the demo library first (so "2 eggs and 2 slices of toast with butter" returns egg, bread and butter with their real macros); only an unmatched meal gets the generic sample.
- Test p152 (demo library: no brands, full macros, every recipe logs without NaN, typed meal matches, Alex carbs 320).

## v3.10.1046
- Changed: the demo shows Premium again, as COMING SOON. The banner link reads "Premium, coming soon", the Today card and the Trends sample chart say "Coming soon", and the preview is headed "Premium: coming soon". It was switched off in v3.10.1041 to 1045 while the demo videos were being made. The preview now gives the reasons Premium is paid for: automatic wearable sync, external data imports (Withings, RingConn, Amazfit and Zepp, Garmin, Health Connect, with new devices addable), device ranking, self-checks, "Your routine", AI included with no key to set up, and support, updates and setup help, for Android. "Register interest" still opens the register-interest page (`MH_PREMIUM_URL`). Test p132 updated.

## v3.10.1045
- Fixed: 'Edit this day by hand' on Trends sent you to Settings > Data. It now opens that day's totals (Log > History, with 'Edit day totals' already open and scrolled into view). A day with no food logged has no History entry, so it still goes to Manual Entry, and that card is now shown again if you had hidden it (the Data tab said 'Filter · 5 hidden' and the jump silently stopped at the top). Opening any section by name from search does the same.

## v3.10.1044
- Changed: the Settings row 'Condition / Protocol' is now 'Diet protocol', which is what it actually sets (the carb target and report framing). All eight language packs updated.
- Fixed: README.md had been emptied by the previous commit (the disk filled up mid-write). Restored in full.

## v3.10.1043
- Fixed: opening Settings (or starting or leaving a demo) popped up 'Carb counting: Total ✓' and 'Exercise offset disabled ✓' toasts as if you had just changed those settings. They now only appear when you actually tap them.
- Demo: the persona's calorie target now counts as confirmed for the maintain and gain phases, so Suggested Targets no longer shows a red 'carried over from a different phase' warning for sample people.

## v3.10.1042
- Fixed: 'Next meal idea' and 'Balance my macros' failed in demo mode with a JSON error. The demo's stand-in AI now returns sample combinations built from the demo person's own library (sensible picks for the categories chosen), so the flow shows a real result and 'Log this meal' works.
- Fixed: the new-user welcome card and the 'back up your data' nag no longer appear in a demo (including right after a language-change restart), since neither applies to sample data.

## v3.10.1041
- Fixed: after a language change inside a demo the page flashed your own theme and figures for about a second before the demo restarted. The page is now held back until the demo is back.
- Fixed: the app's background sync of the real server CSV files (master and combined) could run while a demo was active (and during the restart after a language change), which could mix real days into the demo and showed a 'Data loaded' toast. Those syncs are now skipped for the whole demo.
- The demo no longer shows the Premium card, the Trends sample chart or the 'See Premium' banner link (Premium is not delivered yet). One switch, MH_DEMO_SHOW_PREMIUM, brings them back.

## v3.10.1040
- Meal plan on Today is now its own card with the same move up / move down / hide controls and fold bar as every other Today card (it used to be a plain box inside Calories & macros with no controls). Saved layouts gain it just after Calories & macros. Test p149; p36 updated for the new key.

## v3.10.1039
- Changing language while in demo mode no longer drops you out of the demo (the reload used to end it and show your real account). The same persona restarts straight after the reload, in this tab only; your real data is still restored when you exit. Test p148.

## v3.10.1038
- Treatment Sessions results show whole numbers for calories, steps, millilitres and grams (2381 kcal, not 2380.8). Weight and other metrics keep one decimal.

## v3.10.1037
- Barry (neutral PEMF demo persona) now eats close to his own targets: calories about 93-105% of target, protein over target, carbs under his ceiling on most days, so his Summary reads as a good month. Opt-in via persona.calibrate; every other persona is unchanged. Test p147.

## v3.10.1036
- Fixed: folded Settings sections re-opened themselves after every reload (body shown, label still saying 'show'). The section-ordering code un-hid every section it was not hiding, which also re-opened folded bodies. It now only un-hides what it hid itself, and keeps a folded section folded when you hide then restore it. Test p146; p136 adjusted because the mover correctly skips cards with no data.

## v3.10.1035
- New demo persona Barry: the same PEMF back-pain story as Bill (weekly sessions, improving pain scores, Treatment Sessions before/after) with the app's normal header and no company branding, so it is safe for public screenshots and video. Bill is unchanged for the PEMFiT pitch. Test p145.

## v3.10.1034
- Reports > Treatment Sessions: the 'Compare against' wall of about 45 chips is now grouped (Body, Nutrition, Activity and sleep, Fasting) and shows only metrics that have data, with blood-test markers behind one expander and a 'Show all metrics' link. Selected metrics always stay visible. Test p144.

## v3.10.1033
- Demo-mode leak audit: 26 more personal-account settings (conditions, condition history, activity level, carer email, today notes, tableware, saved prompts/queries, research digests, journey overlays, steps baselines, notification prefs and more) are blanked while a demo persona is active and restored on exit or after an abandoned session. Exit also puts back any other mh_ key demo changed. p143 extended.

## v3.10.1032
- Fixed: after exiting demo mode the Settings form still held the demo persona's name, age and height, and the next profile save wrote them into the real account. Settings fields now refresh on entering and leaving demo. p143 extended.

## v3.10.1031
- Fixed: demo mode also leaked the real fat, water and per-phase calorie targets (a 1750 kcal persona showed 281 g fat). Persona fat now fills its remaining calories; real values saved and restored. p143 extended.

## v3.10.1030
- Fixed: demo mode no longer shows the real account's confirmed TDEE or carb ceiling (a 27-year-old demo persona was showing 3400 kcal). Each persona gets a formula TDEE and its own carb ceiling; real values are saved and restored on exit and after an abandoned session. Test p143.

## Docs refresh (12 Oct, no app change)

README has a "Newest" block for v3.10.981-998, the How It Works guide gained "More than one condition? Tags? Before and after.", and the premium comparison table lists starter packs and the five languages. BACKLOG holds the written launcher plan (backup incl. `debug.keystore`, step-doubling fix, moving the APK off public GitHub).

## v3.10.1029 — Nine Protocols, 27 Packs

Settings > Condition / Protocol lists nine because it only sets the carb target and report framing. It looked as if it should list all 27 starter packs, so a short line under it now says what it does and links to Change my focus, where the packs live. Test p142.

## v3.10.1028 — Hide Stays Lowercase

The fold hint on Wellness Balance and the Import-tab labels showed as capitals ("HIDE"). It now reads "▾ hide" like every other section.

## v3.10.1027 — Your Routine Matches Patterns

Your routine is now a proper Trends section, the same kind as Patterns and Your Journey: same title style, "▾ hide" fold, and the "3/8 👁 ▼ ▲" controls. It leaves the metric-card order (a saved order that still lists it is tidied automatically) and defaults to straight before Patterns; it's now moved with the other sections. Tests p136, p140.

## v3.10.1026 — Routine And Patterns Together

Patterns now always sits directly under Your routine, wherever you move the routine card: the usual first, then what goes with what. Test p140.

## v3.10.1025 — Your Routine Folds, Reads Better

Found on the real phone. Your routine now has the same "▾ hide / ▸ show" fold as Patterns. The sleep line no longer says "Last 3 nights: last 3 nights shorter". A meal window wider than four hours (a lunch of 09:27-20:50 is not a routine) now reads "varies a lot, often about 14:00". Test p140.

## v3.10.1024 — Language Gets Its Own Section

Language was tucked inside Profile. It is now its own Settings section, folds like the others, appears in the Manage filter chips and in settings search. Nothing about the nine languages changed. Test p139.

## v3.10.1023 — Dismiss, And Say So

System health gets a "Dismiss pipeline warnings" link. The warnings come from the last seven days of the pipeline log, so they used to stay for a week even after the cause was fixed. Dismissing hides what was logged so far; the same problem found again on a later sync shows again, so nothing real is hidden. "Resolve sleep conflict" now tells you when there is no open conflict (the warning is then just old log text) and when the local server cannot be reached or needs updating, instead of doing nothing. Needs the new server.py on the phone, which the normal update brings. Test p138.

## v3.10.1022 — System Health You Can Tap

Settings → Manage → Data → System health squeezed long pipeline messages into a narrow right-hand column, which pushed "Mark app errors as fixed" out of reach. The row now stacks with full-width text, the action links sit directly under the headline, each long message is cut to one line with a "Details ▾" toggle for the whole text, and a sleep-conflict warning gets a "Resolve sleep conflict" link. Test p137.

## v3.10.1021 — Routine Card Joins The Layout

"Your routine" is now a proper Trends card: it has the ▲ ▼ reorder and 👁 hide buttons, folds with Close all, belongs to the Patterns filter, restores from the Hidden strip, and is cleared by Default. It sits at the top of the saved order (existing saved orders are migrated), and shows in the 7 Days, 30 Days, All and Custom views. Test p136 covers each control.

## v3.10.1020 — Your Routine

`pattern_detector.py` was rewritten: everything is compared with your own baseline (no Excellent/Good/Low scales, no "regular exercise" label), meal times come from the whole logged history, restored-from-backup placeholders are ignored, midnight bedtimes average correctly, and each signal says how many days it still needs. Trends gets a "Your routine" card (Premium reads it from the phone's server; the demo shows a labelled sample; nothing shows on the free web app). Tests p135 and p136.

## v3.10.1019 — Premium Page, Sharper

The Premium page and in-app preview now lead with what Premium does every day: sync that feeds the early-warning checks, missing-day and source tagging, dated backups with restore, and AI included with no key to set up. The comparison table gained an AI row. Android-only and the iPhone route were added earlier (v3.10.1016).

## v3.10.1018 — Ko-fi Is Live (JustGiving button removed)

`MH_DONATE_URL` now points at ko-fi.com/maxedhealth, so the "Help keep it free" card shows in Settings → AI Provider (never in the demo). The why-free page has a matching Ko-fi button, and the old JustGiving button is gone (Headcase Cancer Trust stays).

## v3.10.1017 — Ko-fi Card, Switched Off

A "Help keep it free" card is wired into Settings → AI Provider, hidden until `MH_DONATE_URL` is set to the Ko-fi page. It is never shown in the demo or in the logging flow. Nothing visible changes until the URL is added.

## v3.10.1016 — Why Not iPhone

The Premium page has a "What about iPhone?" section: why Premium is Android only, what an iPhone user still gets from the free app, how the manual route works, and why regular backups matter. The in-app Premium preview carries a short version of the same note. Test p132 checks it.

## v3.10.1015 — Premium On Trends Too

Demo mode now also puts a locked, clearly labelled "ring vs watch, 7 days" sample chart at the top of Trends. Tapping it opens the same synced-day example. It disappears on exit. Test p132 covers it.

## v3.10.1014 — Trial Button Held Back

The "Start 14-day trial" button is hidden for now, because a trial only raises AI limits until the phone-side Premium download exists. The function and the licence service are unchanged; un-hide `#licenceTrialBtn` when that download ships (home checklist, section C).

## v3.10.1013 — Four More Languages

Portuguese (Brazil), Italian, Polish and Dutch join English, Spanish, German, French and Turkish, each with its flag, in the onboarding and Settings pickers. They cover about 1,370 to 1,390 of the app's strings, keep every {n} placeholder, and use the right speech language for voice entry. They are machine translations and need review by native speakers, which is on the home checklist. Test p133 checks files, placeholders, the nine-language picker and switching.

## v3.10.1012 — Show The Sync

The demo now has a Premium card at the top of Today and a "See a day of synced data" example: a clearly labelled, static day showing Health Connect snapshots, ring and watch end-of-day figures, the device-ranking decision with the sleep difference flagged, and the daily self-check. Removed on exit. Test p132.

## v3.10.1011 — Free Starter Allowance

The shared AI proxy now gives each device a free starter allowance (60 answers), then a small daily top-up (5), with a visible "Free AI answers left" line in Settings, AI Provider and a gentle toast at 10 and 3 left. A valid signed licence token gets a higher daily limit. The Worker also now only accepts approved models, caps response size, and allows only the web-search tool, so a stranger cannot point it at an expensive model. The app only sends the new headers once the Worker has proved it understands them, so an older deployed Worker keeps working. **Deploy `worker.js` in the Cloudflare dashboard to switch the allowance on; add a `LICENCE_SECRET` secret when the licence service goes live.** Docs rewritten to the Free web app vs Premium model (guide, story, index, legal); the full DIY guide moved to `premium/`. Also new: a licence service (`premium-site/licence.php`: device-bound keys, 14-day trial, revoke, licensed download) with a licence card in Settings, and `tools/split_premium.py` to build the public free tree and the private Premium payload (see `premium/MIGRATION.md`). Tests p126 to p131.

## v3.10.1010 — Demo Without Live AI

Demo mode can no longer reach any AI provider or the shared proxy. Every AI request made during a demo is answered on the device with a clearly labelled "Sample answer" in the right shape (meal estimate, recipe, multi-check, chat, insight), so a demo cannot spend real tokens. A "See Premium" link in the demo banner opens a locked preview of what Premium adds, with the register-interest link. Tests p125.

## v3.10.1009 — A Demo For Every Pack

Eleven new demo personas so every one of the 27 starter packs has someone to try: type 3c diabetes, heart health, Crohn's and colitis, arthritis, fibromyalgia, long COVID, PCOS, thyroid, cancer treatment, anxiety and low mood, and sleep problems. 28 personas in all. Test p124 checks pack coverage.

## v3.10.1008 — Fair Tap Size

- Every button is now at least 34px tall (the small chips, Open all / Close all, Edit, On, delete and similar were about 29px at large text). The sweep at 1.5x text size on two demo personas now finds no small buttons, no clipped text and no unlabelled buttons. The chat-bar buttons keep their theme styling by design.

## v3.10.1007 — mhstart Comes Back By Itself

- Pete's phone had lost the `mhstart` command (probably a Termux package upgrade), so the "Local server not running" box told him to type something that did not exist. On startup (Termux only) the server now writes `mhstart` again if it is missing; it never overwrites an existing one. Until the server is up once, start it with `bash ~/mh_watchdog.sh`. Tests: `p123`; also `p74` and `p107` were updated (a hard-coded old version, and a step-count tag that no longer counts as a tag).

## v3.10.1006 — No More Fake "000 steps" Tags

- The Treatment Sessions picker (and Manage tags, Compare, reports) offered dozens of junk tags such as "000 steps", "001 steps", "000 steps|active day". Cause: older device imports wrote a day's note as "12,345 steps, 7.1h sleep, HRV 40", the note is comma-separated, so "12,345" split into the fake tags "12" and "345 steps". Fixed three ways: new imports write plain digits ("12345 steps"); a one-time repair rewrites the stored notes; and device read-outs (steps, sleep hours, HRV, SpO2, bare numbers, and a typed "Exercise: 6.3k steps") are never offered as tags at all. Real tags such as "Treatment: Massage" are untouched. Test: `p122`.
- Also fixed: the new steps log line (v3.10.1005) never appeared because the merge changes rows in place; it now snapshots the old value first. Caught by `p87`.

## v3.10.1005 — The Log Now Says What Happened To Steps

- First real look at the new log viewer (Pete's phone): the logs live in `app/logs/` and are fresh (the July file was a stale old copy in a different folder), but a search for "steps" found nothing, because the pipeline only logged a generic "merge ok" line. Now, whenever a run changes the steps of any of the last 10 days, it logs one line: the date, old value, new value, which source was chosen and what every source offered (for example `steps 2026-10-12: 6000 -> 9185 (chosen: health_connect; offered: manual=6000 health_connect=9185)`). The "Steps only" filter in the viewer now answers "who replaced my typed total, and when".

## v3.10.1004 — Pipeline & Health Connect Log

- New card in Settings → Advanced: **🧾 Pipeline & Health Connect Log**. Reads every log the server keeps (`pipeline.log`, `cron_pipeline.log`, the watchdog and auto-update logs, plus the other places a pipeline log could have ended up), shows where each lives and when it was last written, flags one that has been silent for 2+ days as STALE, and can show only the Health Connect lines or only the steps lines. Has Select all and Copy. Server: `GET /logs?n=150&q=text`. Added after Pete's `pipeline.log` turned out to end in July while data was still arriving: a silent log is now visible instead of misleading. Test: `p121`.
- The Select all / Copy bar now also appears for an output that becomes visible after it was filled (opened section, switched topic).

## v3.10.1003 — Typed Steps Survive the Night

- Pete's rule for steps: during the day Health Connect gives the snapshot, the typed total is the fallback when Health Connect is not reporting, and at the end of the day RingConn / Zepp supply the true figure. The old code did not match: today the typed total beat Health Connect, and from midnight the (double-counted) Health Connect figure replaced the typed one, so typed entries seemed to vanish. Now: **today** a typed total is a floor (it shows while it is above what the devices report; Health Connect and ring/watch figures at or above it take over). **After the day ends** Health Connect can no longer replace a typed total, only a real device (RingConn, Zepp, Garmin, Withings) can, and a typed total also replaces a Health Connect figure already stored for that day. Entries from the Manual Entry screen are unchanged (always absolute). Test: `p87` (merge rules).
- Reminder: Health Connect still double-counts steps until the launcher fix in BACKLOG, so on today it can read high.

## v3.10.1002 — Consistency Sweep

- **Meal plan card:** the "+ Plan a meal" button, the plan rows and the Yes / Changed it / Skipped buttons wrapped badly or clipped at large text ("YES, ATE IT" lost its end). They now wrap, each plan row is a padded rounded box (yellow outline when it is due), and the three buttons drop to a new line when the screen is narrow.
- **Rounder, clearer buttons:** every rectangular button (copy, run, modal, neutral, settings, zoom, and the small inline ones, in every colour theme) shares a 12px corner and a heavier outline. Pills, tabs and the theme-styled chat bar are left as they were.
- **Select all + Copy** under every output area (AI answers, reports, import results, logs, diagnostics, commands). One shared bar, added next to the output so the copy is exactly the output text; hidden on empty placeholders. Falls back to selecting the text if the phone blocks clipboard access.
- **Sweep fixes:** card titles with ▲▼👁 wrapped instead of clipping at large text (22 clipped on Trends, Reports, Settings); the ▲▼ arrows are a proper tap size (they were 16 by 17px); toasts wrap instead of running off the screen (the new Share messages are long); photo, gallery and send buttons gained labels for screen readers; buttons have a minimum height. Test: `p120`.

## v3.10.1001 — Reorder Works Inside a Topic

- ▲ ▼ on Settings, Reports and Import cards could appear dead when a topic chip (for example About & setup) was selected: the card swapped places with a neighbour that belongs to another topic and so was out of sight. It now jumps over cards you cannot currently see, to the next visible one. Test: `p119` (fails on the old code, passes now).

## v3.10.1000 — Share Tries Harder

- On Pete's phone the share menu still answered "not allowed" even with a fresh tap, so the zip itself is probably not on that browser's list of shareable file types (inference). The Share… button now tries three ways in turn: the zip, then the files separately (CSV and JSON are usually allowed), then plain text for small data, and says which one worked. Only if all three are refused does it save to Downloads, with the reason. Test: `p118`.

## v3.10.999 — Share Really Shares

- Pete noticed Share seemed identical to Export. Cause (inferred from the code, confirmed by the new behaviour): Share always builds a zip, and the phone's share menu only opens if the tap is still "fresh". After the zip is built that can have expired, and the old code then silently saved a download, so it looked like Export. Now a refused share opens a small "Ready to share" box with a fresh **Share…** button (plus Cancel and "Save to Downloads instead"). If the browser has no share menu at all, the toast says so plainly instead of pretending.
- Buttons relabelled **💾 Save to Downloads** and **📤 Share…**, with a hint saying what each does (Share always makes one zip). Five-language strings added. Test: `p118`.

## v3.10.998 — Score a Past Day

- **＋ Score a past day** under the "How are you today?" card: pick any of the last 14 days, tap 1-5 for each symptom (tap a score again to clear it), Save. It goes into that day's history entry (a small food-less one is created, in date order, if the day has none; food data is never touched). Good for a day you forgot to score, or one you want filled in after a clinic visit. Appears in Compare Metrics, before/after, reports and the analyst like any other score. Test: `p117`.

## v3.10.997 — Header Fit and Translated Language Settings

- The top bar no longer squashes the LOCAL badge or the date when a language is on: the badge and date stay on one line and the controls wrap instead of clipping at large text sizes. The date follows the language (for example "12 EKİ PZT").
- The Settings > Language card's explanation and the LOCAL badge are now translated (only the language buttons stay in their own language).

## v3.10.996 — "How are you today?" Feeds Analysis Properly

- **Fixed: days with no food were losing their scores and tags.** A "How are you today?" score, a tag (e.g. "Treatment: Massage") or a per-tag note recorded on a day when no food was logged vanished at midnight, because the daily history entry was only written when there was a food log. Those days are now kept (merged into an existing wearable-only entry if there is one, otherwise a small food-less entry). Food averages and counts ignore them (0 kcal), and a day with nothing recorded is not invented. Test: `p115`.
- **Ask the analyst now sees your scores, tags and treatment days** (last 120 days) alongside the daily numbers, so a question like "did exercise, HRV or nutrition affect my headache days?" can be answered from your data. Only added when you have any. Test: `p116`.
- The language box's close button now says **Cancel** (in your language) instead of a bare ✕, and its other labels are translated too.
- Already working, checked: scores appear as Compare Metrics pills, in the before/after around a treatment or tag, in report profiles (symptoms) and in Patterns on food days.

## v3.10.995 — Translate This Screen (AI)

- When a language other than English is on, a **✨ Translate this screen with AI** button sits next to the flag in the top bar and inside the language box. It collects the English text still showing on the screen that the language pack does not cover, tells you how many phrases and where they go (your own AI provider), and only sends after you tap Translate. Notes: it can include your own notes or food names if they are on screen.
- The answers are kept on your phone (`mh_lang_user_<code>`), so each phrase is only translated once and works offline afterwards. The shipped pack always wins over an AI translation. **Forget my AI translations** in the language box clears them. Failure or a bad answer changes nothing.
- The AI is told to keep numbers, units, names and quotes, never soften medical meaning, and leave a medical term in English if unsure. Machine translation: check anything important in English. Test `p114`.

## v3.10.994 — Flags You Can See, More of the App Translated

- **Flags are now drawn pictures**, not emoji (some phones do not draw flag emoji). One sits in the top bar next to search: tap it to change language. Settings > Profile and the first onboarding screen show a row of flag buttons; the corner button when a language is on shows the flag too. English is always in the list.
- **Numbered sentences are translated.** The engine now handles dictionary entries with `{1}`, `{2}` slots, so the weather card, the "walk would close the gap" line, fasting and trends sentences, report headings, and "x/y taken" style text switch language (parts such as an effort label are translated too).
- About 240 more strings per language (Today, Trends, Reports, Settings, weather). Still English on purpose: the long Formulas and Technical Reference text and device import hints, some partial sentence fragments, and anything you typed yourself (food names, notes). Machine-assisted, not clinician-reviewed.
- Test `p111` also checks a numbered sentence and that very short patterns never hijack ordinary text.

## v3.10.993 — Meal Plan Card Tidy

- The plan card's buttons are now three equal, labelled buttons in a row (✓ Ate it, ✎ Time, ✕ Remove; when due: ✓ Yes, ate it, ✎ Changed it, ✕ Skipped), so the lone ✕ no longer looks lost. Long food names wrap instead of pushing the card wider than the screen.
- The eaten + planned totals now show your daily **fat goal** (Settings target) next to Fat, like the other macros. Test: `p105`.
- Full persona suite re-run at v3.10.992: everything passes; the two failures (p113 rounding, p14 poking the language selector) were test issues, fixed.

## v3.10.992 — Flags, Report Profiles on Tags, Planner Fasting Heads-up

- **Flags** 🇬🇧 🇪🇸 🇩🇪 🇫🇷 🇹🇷 on the language pickers, the 🌐 recovery box and the corner button. Medical terms with no safe translation stay in English (nothing is guessed); Settings says so.
- **Report profiles can be about a tag** (for example "Swim", or "Any Exercise") as well as a treatment, and the wizard shows the condition chips so a clinician can narrow the list to one condition. The saved profile, the report text, PDF and CSV use the tag name. Test: `p112`.
- **Planner fasting heads-up:** if you track fasting (a goal set, or 3+ fasts in the last 30 days) and a plan would end a fast early, the confirmation says how long after your last meal it is and when your goal would be reached. Information only, nothing changes. Silent otherwise. Test: `p113`.
- Decided not to build: demo personas applying a pack's screen layout (it would need its own restore on exit, for a cosmetic gain).

## v3.10.991 — Language Packs

- **Languages:** English (default), Spanish, German, French and Turkish. Pick one in onboarding (first screen) or Settings > Profile. Screens, buttons, hints and most toasts and cards switch over; anything not yet translated simply stays English.
- **Always a way back:** when a non-English language is on, a 🌐 button is on every screen and opens a box with **Back to English**. `?lang=en` in the address also resets it.
- Voice input and read-aloud follow the chosen language, and the AI explanations are asked to answer in it.
- Packs live in `lang/<code>.json`, are fetched once and cached for offline use. **Machine-assisted translations, not clinician-reviewed; native-speaker and clinician review welcome.** Dates, numbers and units are unchanged. Test: `p111`.

## v3.10.990 — Six More Demo Personas

- **New demo personas** for the newer cohorts: Frank (high blood pressure), Linda (asthma), Ben (multiple sclerosis), Arthur (Parkinson's), Helen (menopause), Nadia (IBS). Each has the pack's symptoms, treatments where it fits, today's scores and **day tags** on the sample history (for example Treatment: Physiotherapy, Exercise: Swim), so the new before/after and Compare Metrics tag features have something to show. Sample data only, nothing saved, and every persona says it is not advice. Persona count 17 in all.
- Demo does not yet apply each pack's screen layout or condition labels (they would need their own restore on exit). Test: `p110`.

## v3.10.989 — Tag Manager

- **Manage tags** (link under the occasion picker on Today): every tag with how many days it was used; ✎ renames it on every day (renaming onto an existing name merges them, ignoring capitals), 🗑 removes it from every day. Activity summaries and your per-tag notes are kept. This keeps "massage", "Massage" and "Massage session" from splitting the before/after and Compare Metrics numbers. Test: `p109`.

## v3.10.988 — Condition Labels, Condition Filter, Add Another Focus

- **Condition labels.** When a pack adds symptoms or treatments it stamps its condition on them (`conds`). If another pack shares a symptom, it carries both labels. Things you already had or typed yourself carry no label and so always show.
- **Condition filter** (chips at the top of Compare Metrics and the Treatment Sessions picker, shown once you have two or more conditions): tick one or several, none means everything. It filters the symptom and treatment pills and anchors.
- **Add as another focus** in Change my focus: keeps your lists, adds the pack's symptoms and treatments with its label, and combines the two layouts so a card stays tucked away or folded only if both focuses do. Switch still replaces. Test: `p108`.

## v3.10.987 — Tags As Before/During/After Anchors And Compare Metrics Pills

- **Treatment Sessions analysis** (before / day of / after) can now be anchored on a **day tag**, not just a logged treatment: pick a tag such as "Treatment: Acupuncture" or "Exercise: 10k steps", or "Any Treatment" / "Any Exercise" for every tag in that category. Same window, same 3-day minimum, CSV, share and saved queries. Tags are listed after your treatments and are never selected by default.
- **Compare Metrics** gets a Tags group: any tag used on 3+ days becomes a 0/1 "did this tag apply today" pill that can sit on a chart with HRV, carbs, headache scores and so on.
- Still to come: condition labels on symptoms/treatments/tags with a condition filter on the pickers, "Add another focus" in Change my focus, and the tag manager. Test: `p107`.

## v3.10.986 — Treatment Tags From Your Own List, No Duplicate Tag Strip

- **Occasion picker** now shows a chip per treatment on your own treatment list (any condition: Massage, Chemo, Insulin, Physio…), tapping one adds the tag **Treatment: <name>**; you can still type your own, e.g. "Treatment: Acupuncture". Works for every pack because it reads your list, not a fixed one.
- **No duplicate**: while the picker's Active tags list is on screen, the pinned 📌 strip no longer repeats the same tags (the activity nudge still shows). Test `p106`.

## v3.10.985 — Meal Planner ("I'm planning on eating this at …")

- **Plan a meal for later.** Type "I'm planning on eating 2 eggs and toast at 1pm" (needs a plan word and a time; "I had…" is never a plan), or tap **🗓 Plan for later** on any meal preview. The food goes through the normal preview (library or your own numbers, nothing estimated) and lands in a separate planned list (`mh_planned_v1`), not the log.
- **Today shows the plan** under the macro bars: each planned meal with ✓ Ate it now / ✎ Time / ✕, and totals as **eaten + planned = combined / target** for calories, protein, carbs (net-aware) and fat, with a warning if the plan would go over your carb ceiling or calorie target, or what is still to go.
- **At the planned time** the row asks "Did you eat this?": Yes (moves into the real log at the planned time), Changed it (removes the plan and pre-fills chat), Skipped. Unanswered plans never count as eaten; plans over 3 days old drop quietly. Optional "Trust my plan" switch logs automatically.
- Ambiguous hours pick the next upcoming time, with breakfast/lunch/dinner words as hints; the preview shows the time so it can be changed. Test: `p105`. Fasting-window warnings are not included (the app has no eating-window setting).

## v3.10.984 — Seventeen More Condition Packs, Disclaimer On Every Pack Screen

- **17 new starter packs** (27 in all, listed A-Z): High blood pressure, Heart health, Asthma & COPD, IBS & gut health, Crohn's & colitis, Arthritis & joint pain, Fibromyalgia & chronic pain, Long COVID & ME/CFS, Multiple sclerosis, Parkinson's, PCOS, Menopause, Thyroid, Cancer treatment, Anxiety & low mood, Weight loss (keeps the fasting card), Sleep problems. Each is symptoms (and common treatment names) plus a screen layout; they are generic starting lists, not clinical guidance.
- **Disclaimer on every pack screen**: the Starter packs list, the pack preview, and Change my focus (list and preview) all say these are starting lists of things people commonly track, not medical advice, and do not replace your own clinician. Every pack description also ends "nothing here is advice". Tests: `p99` (all packs), `p104` (disclaimer shown).

## v3.10.983 — Type 3c (Pancreatic) Diabetes Pack

- **New pack: Type 3c (pancreatic) diabetes tracking**: symptoms (thirst, urination, fatigue, unplanned weight loss, loose or greasy stools, abdominal pain, bloating, low-sugar signs), treatments (Insulin dose, Pancreatic enzymes with a meal), weight kept in front, ketosis and fasting tucked away. Ten packs in total. Covered by `p99`.

## v3.10.982 — Change My Focus, Muscle Growth Pack

- **Settings > Manage > Setup > "🎯 Change my focus (what are you tracking now?)"**: pick Everything or any starter pack (Everything / eight condition packs / Muscle growth). The preview names the Today cards that will tuck away or fold and the Trends cards that hide, and how many symptoms/treatments will be added. Switch replaces your screen arrangement with the pack's (hidden cards stay reachable under Filter) and adds the pack's lists without removing any of yours; nothing logged is touched. "Show me everything" returns to the standard layout. Works offline for Brain tumour and Keep it simple (embedded copies); the rest need the GitHub list.
- **New pack: Muscle growth tracking** (soreness, joint ache, fatigue, sleep, appetite, motivation, cramps; ketosis and fasting tucked away, weight/calories/protein/body composition kept in front). Nine packs in total. Test: `p104_change_focus`.

## v3.10.981 — Topic Chips Always Visible, Library Chip Icons, Food Category Filter

- **The topic chips (All / Body / Heart & sleep / Food / Patterns, Manage, Reports, Import, Library) are visible again, always, under the toolbar** (Pete Spence: "I can't see any sub categories anywhere"). Since v3.10.973 they sat inside the closed Filter panel and tapping one closed it again, so they kept vanishing. Only the "Hidden:" lists stay behind Filter now. The Filter button appears only on screens that have a Hidden list. History goes back to its own This Week / Month / All row with no toolbar. Tests p71 and p98 updated to match.

- **Library chips carry icons** (🍳 Recipes, 🔤 A–Z, 🥦 Food Library, 🛠️ Tools, 📋 Ingredients).
- **Food Library category dropdown**: under All items / sort, "All categories" plus the categories really in use (with their emoji). Picking one narrows the list, shows the "Showing meat only — nothing else is missing" banner with Show everything, and updates the match count. Deliberately not remembered across a reload (a narrowed list that survives a restart looks like lost data). Test: `p103_library_category_icons`.

## v3.10.980 — Close All Now Folds The Trends Metric Cards

- **Close all on Trends said "closed 7" but Weight, Heart rate, Steps etc. stayed open** (Pete Spence's screenshot): those metric cards had no collapse of their own, only the section headings did. Each metric card now folds to a one-line bar (icon, name, latest value); tap the bar to open just that card. Close all / Open all handle them and respect the chosen group (Body, Heart & sleep ...); hidden or empty cards are left alone and not counted. Remembered per card (`mh_collapse_tc_<id>`), cleared by Default. Test: `p102_trends_cards_fold`.

## v3.10.979 — 👁 Hide On Every Library Section

- **Every Library section has the 👁** (as on Today, Reports and Settings). Hidden sections wait under Filter in a "Hidden:" list (counted on the Filter button, tap to bring back, Show all). Choosing a section's chip still shows it; Open all skips hidden sections; Default clears them. State in `mh_library_hidden` (layout key). Test: `p101_library_hide_eye`.

## v3.10.978 — Clear The System Health App-Error Note

- **"Mark app errors as fixed"** under System health (Settings > About): clears the reported-errors list so the amber note goes away (it used to clear only on its own after 7 days without a repeat). Confirms first; a repeat of the same error is recorded again as New. Server: `POST /clear-client-errors`. Test: `p100_clear_app_errors`.

## v3.10.977 — Filter Toolbar On More Screens, Three New Packs, Test Plan

- **Same toolbar on History, Library and Customise** (first item, same order as every other page). History's This Week / Month / All now sit inside the Filter panel. Library gets section chips (All, Recipes, A-Z, Food Library, Tools, Ingredients) that persist and are cleared by Default (`mh_topic_library`). Customise has nothing to filter, so it shows Open all / Close all / Default with no Filter button (a screen with no chips never gets a dead Filter button). Supplements and Log (chat) have nothing to fold or filter and deliberately get no toolbar.
- **Three more starter packs**: strict keto, type 1 diabetes, cluster headache (index now lists eight). Symptoms and layout only, no advice.
- **Test plan**: `tests/TEST_PLAN.md` (automatic suite, per-feature checks, Pete's 10-minute phone checklist, release gate). Two older tests were stale rather than the app (p08 now chooses 'Show me everything' like p01; p47 follows the renamed `descForAI`). New tests: `p98_filter_rows_more_screens`, `p99_all_shipped_packs` (every shipped pack validated and applied in the app).

## v3.10.976 — AI Check No Longer Sends Guessed Grams, Layout By Voice, Half-Written Page Guard

- **The 3-AI comparison on a logged meal sent the first AI's guessed grams to all three checkers** (Pete Spence's screenshot: clotted cream 90g, raspberries 35g... then every AI "independently" guessed ~160g, the exact total). An amount is now sent only if it appears in the person's own words; guessed amounts are left out, so each AI judges the portion itself. Because their macros are then for their own portion, they are scaled to the logged amount before comparing and averaging (raw figures stay on the card, and the card says no amounts were sent). Library, History and Recipe edit forms still send the amount you entered. Test: `p95`.
- **"JS ERROR ... reading 'style'" (08:22) and the older "Invalid or unexpected token / missing )" entries**: the auto-update rewrites `maxhealth.html` in place, and a page load landing mid-write received half a file. The server now only serves a file that ends with `</html>`, retrying briefly and falling back to the last complete copy. The metric drill-down also no longer throws if its overlay is missing; it asks for a refresh. Test: `p96`.
- **Layout by voice or typing**: "Hide the fasting card", "Show the ketosis card", "Close all cards", "Open all cards", "Reset my layout" (confirms first). Only short phrases ending in card/cards/section are matched, so ordinary questions are never hijacked. Listed under "What can I ask". Test: `p97`.
- **Nudge card has Read aloud (🔊)**.
- **Documentation**: user guide gained "Make it yours" (Filter row, fold, Default, starter packs, nudges, voice); in-app Guides gained "Layout, Filter & Starter Packs" and the "Verify across 3 AIs" note now describes when amounts are sent.

## v3.10.975 — Gentle Nudges, And Three More Starter Packs

- **Optional nudges on Today.** If a starter pack tucked a card away (hidden, or folded into a bar), then a week after the pack was applied the app offers it back once: *Show it / Not now / Don't ask again*. One at a time, a week apart; "Not now" asks again in a week; cards you hid yourself are never offered; nothing appears without a tap. "Show it" also updates your pack layout so Default keeps it. Offered in order: Macro ratio, Goal check, Day mode, Fasting, Ketosis.
- **New starter packs** (symptom list and layout only, nothing here is advice): Epilepsy tracking, Type 2 diabetes tracking, Migraine & headache tracking. Available from Settings → Data → Starter packs.
- Tests: `p94_nudges.py`.

## v3.10.974 — Toolbar Always First, Meal Picker Fix, Pill Sweep

- **Filter toolbar fix on Trends**: the panel change in v973 made Trends pile up hundreds of hidden duplicate toolbars and left the real one far down the page, so the category chips looked like they had vanished. Fixed, with a test that counts toolbars per screen.
- **Same controls, same order, same place on every page**: Filter / Open all / Close all / Default is now always the first thing on Today, Trends, Reports, Settings → Manage and Settings → Data (it used to land wherever the first chip was created).
- **Next meal idea**: each picker now keeps its own selection. Opening the picker a second time retires the old one (their buttons shared ids, so taps could highlight the wrong copy). Selected categories show a tick as well as the colour, stay at full strength after Send, and **Snack** is now a clearly separate action ("Snack ideas →", dashed) rather than looking permanently selected.
- **Pill sizing swept across the remaining pill-style buttons**: Log quick buttons, History range pills, Reports ranges, provider pills, drill-down periods, tableware chip. Icons are unchanged.
- Test: `p93_toolbar_order_meal_picker.py`.

## v3.10.973 — One Filter Panel, One Pill Size

- **Hidden lists now sit inside the Filter.** Opening Filter shows one panel under the toolbar holding the topic chips and the "Hidden:" pills together (divided by a dotted line), instead of loose rows below. Works on Today, Trends, Reports and every Settings screen.
- **One pill size across the main pages**: toolbar buttons, topic chips, Hidden pills, Trends period pills (Today / 7 Days / 30 Days / All / Custom) and day-mode tags all use a single size variable (`--mh-pill-fs`), a notch smaller than before and in the same font.

## v3.10.972 — First Run: "What Would You Like To Start With?"

- New wizard step after Health Context with three choices: **Brain tumour tracking**, **Keep it simple**, **Show me everything**. The first two add their starter-pack lists and apply their screen layout (Default buttons then return to it); the third applies nothing. The choice is pre-selected from the condition picked (GBM suggests Brain tumour, anything else Keep it simple) and can be changed.
- The packs are embedded in the app so the first run works offline; a test fails if they drift from `starter_packs/*.json`. Preview mode applies nothing.
- Tests: `p92_first_run_choice.py`; `p01_new_user.py` now chooses "everything" before finishing.

## v3.10.971 — Starter Packs Carry A Screen Layout

- **Setup packs can now include a "Screen layout"**: which cards start open, folded or hidden. Shown in the pack preview as its own tick-box; importing never touches logged data.
- **Only layout settings are accepted** from a pack (anything else, including settings and keys, is refused). "Add what's missing" never overrides a screen you have arranged; "Replace" does.
- **Default buttons return to the pack's layout** once one has been applied (the confirm says so).
- **Both starter packs now ship a layout**: General wellbeing hides the advanced metabolic cards; Brain tumour tracking folds them into one-line bars and keeps symptoms/treatment open.
- Settings: **Redo setup wizard** moved into an "Advanced" fold so it can't be hit by accident.
- Export/share: "Screen layout" is a tick-box alongside the other setup items.
- Test: `p91_pack_layout.py`.

## v3.10.970 — Library Reset Link Removed

- Removed the "Reset section order to default" link at the top of the Library; the toolbar's **↺ Default** (and Settings → Reset layout on every screen) already restore Library order.

## v3.10.969 — Filter Count Fix, Themed Toolbar, Quieter Pills

- **"1 hidden" with nothing to restore fixed.** Hidden-card lists could keep keys for cards that no longer exist; they were counted in the Filter badge but never listed. `mhPruneHidden` now drops them on read (generic, dashboard, trend cards).
- **Toolbar buttons (Filter, Open all, Close all, Default) use the chosen theme accent.**
- **All chips quieter** (smaller, transparent) so the toolbar leads.
- **Chips and Hidden strips now sit nested under the open Filter** on an accent rule.
- Test: `p90_stale_hidden.py`.

## v3.10.968 — Reset Layout, And Live Values On Folded Cards

- **↺ Default** button on every screen's toolbar (beside Open all / Close all): puts that screen back to its standard layout (open/closed cards, hidden cards, their order, the topic filter) after a confirmation. **Settings → Setup → Reset layout on every screen** does the same everywhere. Only layout is touched, never anything logged; the page reloads and comes back to the same screen.
- **Folded Today cards show a live value** on the right of their bar: Weight (92.6kg), Day mode (the occasion), Ketosis (status), Calories & macros (kcal, protein, carbs so far), Macro ratio (P/F/C %), Fasting (time fasted so far) and Water (250 / 2000ml). So a fully folded Today still works as a dashboard.
Tests: p89 (new), p88, p71, p72, p73, p78, p80, p81. Full suite green at v3.10.967 (88 personas).

## v3.10.967 — Close All On Today Now Closes The Big Cards

Close all on Today said "8 closed" but most of the page stayed put: only a handful of small inner sections had a collapse control (and half of those were already hidden), while the big cards could only be hidden or reordered. Weight, Day mode, Ketosis, Calories & macros, Macro ratio today, Goal check, Symptoms, Treatment, Local weather, Fasting and Water now shrink to a one-line bar with their name; Close all does it for every card that is showing, tapping a bar opens just that card, Open all restores them, and each card remembers its state (kept through refreshes and day changes). Empty cards get no bar. The "Closed N" message now counts only what really changed on screen. Tests: p88 (new), p71, p78, p80.

## v3.10.966 — Typed Steps Are A Same-Day Catch-Up, Not An Override

The Today **Daily Steps** box says "your real total" but only fed the calorie estimate; nothing typed there reached the pipeline, so Trends kept showing the watch's stale figure (Zepp 4277 all afternoon while Health Connect, RingConn and Zepp had not synced). Typing or changing the total now also saves it as today's manual steps, marked **provisional**, with these rules (`merge_with_precedence`):
- **Today:** it is a floor. It shows while it is greater than what Zepp, RingConn, Withings or Garmin report; a device figure equal to or above it takes over (source flips from "typed in" to the device).
- **Health Connect can never beat it** (it double-counts phone + watch).
- **After midnight** the devices win outright; the typed figure only fills a day no device reported.
- **Manual Entry screen** values (and CSV template uploads) are not provisional and stay absolute.
The page re-reads a few seconds after saving. Local server only. Test: p87 (end to end plus the merge rules).

## v3.10.965 — Tableware Chip Shares The Saved-Prompts Row

The "Tableware: <set> · back to Home on <date> change" banner took a whole line above the Log buttons. It is now a short pill (🍽 set name · dd/mm) on the same row as "Browse saved prompts"; the name shortens with "…" if space is tight, and tapping it still opens the tableware settings (the full wording is its tooltip). Test: p44.

## v3.10.964 — The Phone Now Uses The Repo's RingConn And Withings Readers

The pipeline preferred an older RingConn and Withings reader kept in the phone's own `app/extractors/` folder (outside git), so the RingConn night-grouping fix and the Withings no-longer-claims-RingConn fix of v3.10.962-963 never ran there: a RingConn nap still replaced Zepp's night and Withings still read RingConn's zip. Both now come from the repo like Health Connect and manual do. A reader of your own in `data/extractors/` still wins over both.

## v3.10.963 — RingConn Nights Joined And Filed By Wake Date; Source On Every Row

- **RingConn sleep.** One night recorded as several sessions (for example 22:18-04:25, then 05:30-08:18) was filed by each session's own start date, so a night was split across two days and its second half, alone on the wake day, replaced Zepp's real sleep (2h07 instead of 8h25). Sessions are now sorted and any starting less than 2 hours after the previous one ended are joined (durations and stages added); a night is filed under the day you **woke**, like every other source; a short daytime session (08:00-18:59, under 3 h) is a nap in `sleep_nap_min`. Your real 10-11 Oct file now gives 7h42 on 11 Oct. Re-importing an export corrects the days it covers; older RingConn nights outside it keep their old (bedtime) date. This supersedes the v3.10.962 nap rule. Tests p58 (two separate nights now each keep their own date), p86 (real pattern).
- **Source on every row.** The one-line "Source:" per card was ambiguous because a card can mix devices. Each Activity, Vitals, Sleep and Weight row now carries its own small device name (Zepp, Health Connect, RingConn, Withings, Garmin, typed in). Test: p85.

## v3.10.962 — RingConn Nap No Longer Replaces The Night

A RingConn nap (11:00, 2h07) was the only session filed under today, so it became today's whole "night" and, because RingConn outranks Zepp for sleep, it replaced Zepp's real 8h25m. Two fixes: (1) a short RingConn session that starts in daytime (08:00-18:59, under 3 h) is now a nap and goes to `sleep_nap_min`, never the night; a day with only a nap has no night from RingConn, so Zepp's stands. (2) The Withings reader also claimed RingConn's "Data Export-<name>-<dates>.zip" through its "any other zip" fallback and filled the gaps RingConn had left; it now leaves those to RingConn. Re-upload the same export after updating to correct the day. Because a value already attributed to RingConn can't be overridden by Zepp, a new helper `clear_day_sleep.py [YYYY-MM-DD]` blanks one day's sleep figures and their attribution (with backups) so the right exports can refill them. Test: p86.

## v3.10.961 — Day Cards Say Where Their Figures Came From; Off-Phone Backup Advice

- Each Trends → Today / day-view card now ends with a small **Source:** line (for example "Source: Zepp (Amazfit) + Health Connect (phone)"), built from the pipeline's per-field attribution. New server endpoint `GET /field-sources` serves it. A figure that falls back to yesterday's sleep is marked as such. The app re-renders when the source changes after a sync (so a RingConn upload that outranks Zepp shows up).
- User guide gains a monthly **Keep a copy off your phone** step, and Settings → Storage shows a one-line hint. Test: p85.

## v3.10.960 — Today's Sleep Is Today's Night

Trends → Today showed sleep from **yesterday's** row (3h) over today's own (8h25m). The pipeline files a night under the day you woke (bedtime 22:35 → wake 08:18 sits on the wake date), so today's own sleep figures are last night's. Today's row now wins, and yesterday's only fills in when today has none yet. Test: p84.

## v3.10.959 — Open App Re-Reads Fresh Sync Data

The app only re-read combined.csv when it first found the server. A screen left open, or a phone app resumed, after a sync or Zepp merge finished kept showing the older figures (for example Sleep 3h after the pipeline had written 8h25m) until a full reload. It now re-checks whenever it comes back to the front and every 2 minutes while on screen; when nothing changed the check is silent. Test: p83.

## v3.10.958 — Up/Down Arrows In Chat; Up Arrow Reaches The Menu

The Log chat screen had no ↑/↓ arrows (they were left out because they sat on top of the send button). With large text the docked composer is tall and the tabs scroll out of reach, so chat now gets the arrows too, placed up the right-hand side clear of the send button. ↑ now also scrolls every outer container back up, so it brings the top menu back into view, not just the inner list. Test: p81.

## v3.10.957 — One Period Comparison, Big-Text Overflow

- **Two period comparisons are now one.** Seasonal Compare (Reports) is gone. **Compare Two Periods** (Insights → Trends) now also shows average weight, sleep, HRV and SpO2 alongside logged days, kcal, protein, carbs, steps and the weight-trend verdict. Old saved order or hidden entries for Seasonal Compare are simply ignored.
- **Large text**: with Android's large text setting, date boxes in side-by-side columns pushed past the card edge. Grid columns can now shrink and date, time and number boxes never exceed their container.
- Tests p82 (merged comparison); p50 updated.

## v3.10.956 — Top-Left Back Button

Every other back button in the app sits top-left, but the main screens had none, so once you had scrolled past the tabs there was no obvious way back. The app now remembers the screen you came from, and a round ← appears top-left once you scroll down; it takes you back one screen (press again to return). It is hidden on screens that already have their own ← (such as the metric detail pages) and sits below the offline banner when that shows. Test: p81.

## v3.10.955 — Back To The Top After Filter Change Or Close All

Choosing a Filter group or pressing Close all shortens the screen, which could leave you scrolled past the tabs and Filter bar with nothing to tap to get back. Both now return you to the top of the screen automatically (the ↑ button also appears sooner since v3.10.954).

## v3.10.954 — Back-To-Top Button Appears Sooner

The ↑ button on Settings, Insights and other long screens only appeared after scrolling 300 px, so on a filtered, short screen you could be scrolled away from the tabs with only ↓ showing and no way back. It now appears after 90 px, and ↓ appears while more than 200 px remains.

## v3.10.953 — Open all Never Reveals Hidden Cards; Show All

Found from Pete's screenshots: with cards hidden, **Open all** re-opened their content (the title stayed hidden, so a card body such as Profile appeared with no heading, and filtering looked like it had closed or hidden everything). Open all / Close all now skip hidden cards completely and only act on the chosen Filter group. The Hidden strip also gets a **Show all** button when more than one card is hidden, so a fully hidden screen can be recovered in one tap. Test: p80.

## v3.10.952 — Weekly Summary Fix, Targets Tidied, Meds Don't Break A Fast, Device File Patterns You Can Test

- **Weekly summary notification** said "over your undefined carb limit". It now reads your real Standard ceiling, uses the latest seven logged days (newest by date), and says so plainly if no ceiling is set.
- **Settings → targets**: the daily calorie, protein and fat boxes duplicated the Suggested Targets card. They now sit behind "Set my own numbers instead (advanced, e.g. from a dietitian)", with a one-line "Your targets now: …" summary above. Nothing was removed.
- **Fasting**: new "Taken with meds" setting (for example MCT oil, which helps some tablets absorb) plus your usual amount. A matching entry no larger than about 20% over that amount no longer breaks a fast, and a live line under the threshold explains exactly what is ignored. Never delay a dose to protect a fast.
- **Supplements**: removed a half-screen blank spacer under the list.
- **Manage devices**: each device shows its built-in file-name rules; 🔍 tests your saved patterns against what is in Downloads right now; adding a pattern first shows which files it would pick up (read-only, nothing is moved, file names escaped). Every pattern change keeps a restore point (last 8) and the list shows "Earlier file patterns (tap to restore)". Server: new `GET /devices/preview`.
- Added a regression test for hide-then-reorder on every screen (could not reproduce the reported problem; Pete to say which screen).

## v3.10.951 — Filter Is Set Once: Tucked Away, and Open/Close All Leave It Alone

The "Filters & hidden" button is now just **Filter**. It names the filter you have chosen and the number of hidden cards, for example "☰ Filter: Backup & restore · 2 hidden ▸", so you can see the state without opening anything. Because a filter is set once and rarely changed, **choosing a filter chip now closes the panel by itself**. **Open all and Close all no longer touch hidden cards**: they only expand or collapse sections. Restoring a hidden card is done from the Filter panel, where the Hidden strip lives. This reverses v3.10.941, where Open all also restored hidden cards; the new rule is that hidden and filtered-out cards are a decision made once and never undone by an unrelated button. Evidence label: not applicable (app plumbing). Persona p71 updated.

## v3.10.950 — Steps Baseline Automatic, Activity Level Reads Real Weekly Steps

**Incidental Steps Baseline** now has an **Automatic** switch. Automatic means the baseline follows your Activity Level using the same three presets as before (sedentary and lightly active 5,000, moderate 7,500, very active 9,500), and the card says which value it is using and why. Anyone who had typed their own baseline keeps it (manual) until they switch Automatic on; a new user starts on Automatic. Switching Automatic off keeps the current value rather than jumping. **The Activity Level itself now reads real weekly steps.** The old check needed about 44 days of step history. It now compares the average of each of the last 2 to 4 whole weeks (your auto-switch days divided by 7, so 14 days means 2 weeks) with the same tier thresholds the TDEE multiplier uses. A week counts only with 5 or more days of steps. If every week points to the same different tier, the level moves and, if the baseline is automatic, the baseline moves with it; otherwise the card says why nothing changed (for example "needs 5 or more days of steps in each of the last 2 weeks, so far 3, 7"). Someone on Light with the old default baseline of 7,500 will now see 5,000 under Automatic, so a few more step calories are credited. Evidence label: Proven for step counts as an activity measure, Speculative as an exact calorie figure (a heuristic). New test: `p77_steps_baseline_auto.py`.

## v3.10.949 — Data Tab Simplified: One Export/Import Card, Restore Apart

The Data tab had grown several cards doing overlapping jobs (two Export All buttons, a "Data Management" picker, a "Nutrition History — Import & Backup" card, a "Data Preview & Validator" and a Manual Pipeline card). It is now: **Export, import & backup** (one card), **Restore from backup** (its own card), **Sync Wearable Data** (with the Manual Pipeline as a hideable "Run a device by hand" section inside it), Wearable History, Add device, Manual Entry, and **Missing Data & Coverage**. In the export card every exportable thing is a tick box with **Select all / Unselect all**; choose **One zip** or **Separate files**, then Export or Share. "Everything" is spelled out: meals (master.csv), wearable history (combined.csv), library, recipes, routines, supplements, strength log, the symptom / treatment / report-profile / tableware / device setup, and a full app backup .json. It does not include the raw files in the device inbox folder. Import takes any file made there: CSVs, a setup pack, a full backup, or a zip of them, each routed by what it is (meals and wearable CSVs go through their existing importers; lists go through the preview; a full backup asks before replacing). Restore now also works **from a backup file** (.json or the zip), with a confirmation that names the backup date. The old **Data Preview & Validator** was never about files: it summarises how much of your history has meals, steps, sleep, heart rate, HRV, SpO2 and weight, and where the gaps are, so it now sits inside Missing Data & Coverage. "Clear today's log" moved behind a small "More" fold. Evidence label: not applicable (app plumbing). New test: `p76_data_tab.py`; p50 and p75 updated.

## v3.10.948 — Setup Packs Finished: Safer, Wider, With Starter Packs

Four additions to v3.10.947. **Safety:** a pack can come from anyone and some lists show names without escaping them, so every imported text value now has angle brackets stripped and is length-capped, and the preview escapes the pack's own header; a test feeds in a script-bearing pack and checks nothing runs. **Wearable devices** joined the pack (device names, file patterns and source order, never data); importing pushes them to the server's device list. **The old CSV import** (Food Library, Supplements, Recipes, Routines) now opens the same preview instead of silently replacing: Add-what's-missing by default, Replace behind a confirmation, and a "these are my own foods: keep their locks" tick so restoring your own library doesn't lose its locks. The Strength Log keeps its replace behaviour but now asks first. **Starter packs:** a 🌱 button (Import mode) fetches ready-made lists from `starter_packs/` on GitHub and opens them in the same preview. Two to begin with: "Brain tumour tracking" (symptoms and treatments people commonly track) and "General wellbeing" (six everyday symptoms). Guide: the ARISTOCRAT Phase I wording now states the 27-patient size and wide uncertainty instead of calling the signal "remarkable". **Also fixed (found by the full test run at 2 am):** a snack logged just after midnight (before 04:00) in "Today" was treated as the late end of the previous evening, which put it in the future and blanked the live fasting timer. Before 04:00 still counts as the late end of that day when it is on a past day's log, but an entry that would land in the future now keeps its real clock time. Persona p63 gained a time-travelling check for both cases. Evidence label: not applicable (app plumbing). Persona p75 extended.

## v3.10.947 — Setup Packs: Share What You've Built

Setting up plates, supplements, symptoms and report profiles from scratch is what puts new people off. The Data Management card (Import tab → Data) already exported single datasets, but as separate CSV files and with no preview on the way back in. It now also handles **setup packs**: one small `.json` file holding only the setup you tick, with no entries, history, labs, keys or your name. New ticks in the picker: **Symptom list, Treatment list, Report profiles, Tableware sizes** (alongside Food Library, Supplements, Recipes, Routines). New button **📦 Share setup as one file** hands it to the phone's share sheet (falls back to a download). Choosing a pack on the Import side opens a **preview** listing each section with "N new, N already there"; the default is **Add what's missing** (nothing of yours is changed or removed), with **Replace** behind a confirmation. Details that matter: shared foods always arrive **unlocked and marked "from pack"** (a locked value is a promise the receiver made themselves, so it can't be inherited, and the receiver's own locked foods stay locked); report profiles never carry "last sent" dates; ids are remapped so a profile still points at the right symptom and treatment; tableware merge only fills your Home sizes where they're empty and adds sets and items you don't have. The Strength Log and Full App State are deliberately left out of packs. The old CSV import is unchanged (it still replaces). Evidence label: not applicable (app plumbing). New test: `p75_setup_pack.py` (it also caught my own first-draft bug where a merge unlocked the receiver's locked foods).

## v3.10.946 — "Your Phone Is Behind" Warning

Jill's phone sat on v3.10.739 for a month while the app cheerfully said "latest version": the existing update banner only notices a newer copy from the phone's *own* server, and that server had stopped pulling from GitHub (Android had killed Termux's cron). The app now also reads the published README's Version line from GitHub (at most every 6 hours, quietly skipped when offline) and compares it with its own version numerically. If GitHub is ahead, a small banner at the top says which version the phone is on and which is out, shows the Termux command (`bash ~/mh_autoupdate.sh`) with a Copy button, and can be dismissed; a dismissal holds until a still newer version appears. Settings → About shows the same warning line, and the CHECK FOR UPDATES button now answers "behind" truthfully instead of "latest". Nothing is changed or downloaded by the check. Evidence label: not applicable (app plumbing). New test: `p74_behind_github.py`.

## v3.10.945 — Troubleshooting Tools Join Advanced; Collapsed Rows Obey Filters Again

Pete Spence: the troubleshooting tools "should definitely be in advanced". The "⚠ Advanced — Troubleshooting Tools" block used to sit wherever it happened to fall in the page, which put it mid-list between Device Precedence and Formulas. It now belongs to the Advanced section of Settings, Manage: shown under **All** and under the **Advanced** chip, hidden under the other chips, and always kept last, including after a card is reordered. The Advanced chip's note mentions it. **Bug fix for v3.10.944:** the one-line collapsed rows forced `display:flex !important`, which overrode both the chip filter and the eye (hide) button, so a collapsed screen would have shown every card regardless of chip or hidden state. The flex rule is no longer forced, so filters and hide win again; a stray wrapper margin that left a blank gap in a collapsed list is also removed. Personas p72 (troubleshooting placement under every chip, last place, survives reorder) and p73 (collapsed rows obey the chip filter and the eye button) cover both; the full suite (p01 to p73) passes.

## v3.10.944 — A Collapsed Card Shrinks To One List Row

Pete Spence, with a screenshot of Settings after Close all: "Should these not shrink to the list?" Collapsed cards kept their full-size headers: titles wrapped, the position number, eye and arrows scattered over several lines, and Add / Clear all / Log Panel / New buttons sat under a closed card. A collapsed card's header is now flagged (`mh-collapsed`, set by tapping the header, Open all / Close all, and the saved state at load) and CSS turns it into one line: title on the left (truncated with an ellipsis if long), position number, eye, ▼ and ▲ lined up on the right, action buttons tucked away until the card is expanded. Headers that held bare title text are wrapped once so truncation works. It applies on every screen. Persona p73 checks every collapsed row is a single line, the badge sits inside its row, no buttons show while collapsed, they return on expand, and the state persists across a reload. The full persona suite (p01 to p73) passes.

## v3.10.943 — Open All / Close All Act On What You Are Looking At; Advanced Is A Section

Pete Spence: Open all appeared to do nothing when cards were hidden, and it should act on everything only when All is selected, otherwise only on the chosen set. **Scope:** the toolbar now follows the chip row. With All selected it acts on every card on the screen; with a chip selected (Me & targets, Food, and so on) it acts only on that group. **Open all** now also restores cards hidden with the eye button, within that scope, and the toast says how many sections it opened and how many it restored. **Close all** only collapses; it never hides or un-hides anything, because hiding is a deliberate choice. **Advanced** is now an ordinary section chip in Settings, Manage holding the six technical cards (Formulas & Technical Reference, Device precedence, Exercise offset, Incidental steps baseline, Report profiles, Idle timeout), with a plain-English note when selected. All still shows everything, and the other chips no longer contain those cards. The on/off Advanced switch is gone. Personas p71 (scoped Open all, restore, Close all leaves hidden state alone) and p72 (Advanced as a section) updated; the full suite (p01 to p72) passes.

## v3.10.942 — One Button For The Pills, Open All / Close All, A Clearer Advanced

Pete Spence, with a screenshot: the "Hidden:" strip listed every card and took half the screen, "Advanced on" explained nothing, and the v940 on/off switch "didn't land". Three changes. **One button per screen:** each screen with chip rows or "Hidden:" strips (Today, Trends, Reports, Settings Manage and Import, multi-metric sections) now starts with **☰ Filters & hidden (N)**. Everything behind it (topic chips, the Advanced chip, every Hidden: pill) is collapsed by default; tapping it shows or hides them all, and the choice is remembered. The pills themselves are unchanged. The v940 Settings switch is removed. **Open all / Close all:** two buttons beside it expand or collapse every collapsible card on that screen and remember the state. **Advanced redefined:** it now holds only the technical settings a newcomer would not understand, namely Formulas & Technical Reference, Device precedence, Exercise offset, Incidental steps baseline, Report profiles and Idle timeout. Carer & Clinician and Tableware move back to everyday. The chip reads "⚙ Advanced ▸/▾" with a plain-English line saying what is inside. Persona p71 was rewritten for the toolbar (default collapsed, one global state, count, Open/Close all, persistence, restoring a card still works), p72 for the new Advanced list; the full persona suite (p01 to p72) passes.

## v3.10.941 — Simple And Advanced Settings

Pete Spence: offer everything needed for most tasks under Settings, and the rest under Advanced. Settings, Manage now opens with the everyday cards (Profile, Carb targets, Water, Fasting, Notifications, AI provider, Supplements, Symptoms, Treatments, Lab results, Premium, About, Setup). Eight rarely-touched cards sit behind a new **Advanced** chip beside the topic chips: Formulas, Device precision, Exercise offset, Tableware, Steps baseline, Report profiles, Carer and Idle timeout. Nothing is removed or switched off: an advanced setting keeps working and keeps its value while hidden, a settings search always reveals the card it found, and the on/off choice is remembered. It defaults to off. Persona p72 checks hidden, shown, reload, toggle back and search reveal; the full persona suite (p01 to p72) passes.

## v3.10.940 — One Switch For The "Hidden:" Restore Buttons

Pete Spence: "a single hide and show on the hidden pills for all appropriate screens". There are five separate "Hidden:" strips (Dashboard, Trends, the generic Reports/Settings/Import screens, the multi-metric sections and the multi-metric legend), each showing a button per hidden card. Settings, in the Setup card, now has **Show the "Hidden:" restore buttons**: one switch that hides or shows all of them together (a body class, so no screen needed changing). It defaults to on, so nothing changes until you turn it off. Turning it off hides only the buttons; hidden cards stay hidden and come back with the switch. The choice survives a reload. Persona p71 checks default, off, on, reload, and that hiding the strip never un-hides a card.

## v3.10.939 — Fasting Exports Record The Calorie Limit Used

Pete Spence asked whether a 100 kcal fasting limit would be acceptable instead of 50. It is already a setting (0 to 500), but changing it silently rewrites every past fast, so an export could not say which limit it was measured with. The Every fast list now states the limit in use, and the CSV gains a `meal_counts_from_kcal` column on every row. The clinician report already carried the limit in its footnote. Persona p70 now checks the column at the default and after the limit is changed to 100.

## v3.10.938 — Every Fast, Kept And Listed

Pete Spence asked whether there was a fasting history report and whether fasting should be kept for the full history rather than 30 days. Checked first: nothing was ever discarded, because fasts are recalculated from the whole meal log each time, and the Fasting report already had an All-time tile beside the 30-day one. What was missing was any way to see the individual fasts. The Fasting report (Insights, Reports) now ends with **Every fast**: one row per measured fast since logging began, newest first, showing the last meal, the next meal and the length, with a tick when it met your goal and an *extended* tag for multi-day fasts tagged Fasting. Chips filter All, Extended, At goal and Under goal; the first 20 show, with Show all. Days that cannot be measured (no logged meal time the evening before) are counted in a note, never estimated. **Download all fasts (CSV)** saves the full history. The printable clinician report now adds an all-time line under the last-30-days fasting figures. It sits inside the existing Fasting card, so the card's show/hide and reorder already apply. Persona p70 builds 60 days of meals with a known gap and a known 36h extended fast and checks durations, order, filters, the unmeasured note and the CSV row count.

## v3.10.937 — TDEE Recheck Nudge Offers A Suggested Figure (Review And Confirm)

The recheck nudge (v3.10.820) said your confirmed TDEE might be out of date but left you to work out a new one. It now adds a **Review a suggested TDEE** button. The suggestion is rough on purpose: the gap between the weight change you expected on your current goal and what actually happened, turned into kcal a day with the 7,700 kcal per kg rule of thumb, moved at most 300 either way, rounded to the nearest 10, and no button at all if the change would be under 50. Tapping it shows the old and new figures with a plain caveat (weigh-ins are noisy; treat it as a starting point; re-check in a couple of weeks). **Nothing changes until you confirm**; Cancel keeps the old figure. Confirming goes through the normal save, so the confirmed date is re-stamped and the nudge cycle restarts. Evidence label: Speculative as a number (a heuristic), Proven as a prompt to re-check. New test: `p69_tdee_suggestion.py`.

## v3.10.936 — Portion Edits Measure Against What The Entry Shows Now

Follow-up to v3.10.935, where the grams box was found to measure against the amount an entry was first logged with ("logged as 15g") while the form's numbers are for the amount it shows now (8g). Three fixes in the portion edit: (1) the grams box now measures against the amount shown now and says so ("now 8g"), so typing the current amount is 100% and typing half is 50%; (2) repeated edits compound correctly (8g halved is 4g, with the badge going 53% to 27%, where before the amount was recalculated from the first-logged 15g and came out as 8g again); (3) a save that changes nothing, such as only correcting the meal time, no longer wipes the portion badge. New test: `p68_portion_baseline.py`.

## v3.10.935 — The Portion Box Accepts "8g"

Pete Spence, with screenshots of the edit form: "It won't let you enter a g in the new portion size box." The "or type the new portion" box was a numbers-only field, so a unit typed after the amount was refused, and on a phone the number keyboard has no letters. It is now a text box with the decimal keypad: "8", "8g", "8 g", "8G" and "8,5" all work, and the multi-ingredient form's "scale entire entry to" box got the same fix. Test `p54_portion_grams.py` now types units in both forms (it fails on the old code, where the browser refuses the text). Not changed, flagged: the box works out the percentage from the amount the entry was first logged with (the "logged as 15g" beside it), not from the amount it shows now, so for an entry already trimmed once the two can differ. Typing 8 on that MCT entry gives 53% of the 15g figures.

## v3.10.934 — The Wearable Placeholder No Longer Leaks Into Meal Features

Pete Spence asked whether the personas had been updated to cover the Meals-card bug. They had not, because no persona used a day with wearable data and no food, so a sweep of everything that reads meals was done. The placeholder entry (23:59, 0 kcal, date as its id) was leaking into three more places: **Top foods** counted "4,093 steps, 3.6h sleep..." as a food, the **"usual first meal" nudge** treated 23:59 as a first-meal time on those days (pulling the usual time later), and the **AI's list of what you ate yesterday** included it as a meal. All three now use one shared check, `mhIsDeviceStub()`, as the Meals card does. Fasting was already safe (0 kcal is under the threshold). Left as it is on purpose: the History list still shows the wearable summary line for such a day, since it is index-based and doubles as that day's device summary. A real meal logged at 23:59 with calories still counts everywhere. New test: `p67_wearable_stub_leaks.py`.

## v3.10.933 — No Meals Card On A Day With No Meals

Pete Spence, with a screenshot of Trends: "Meals by calorie contribution? Nothing displaying. Should there be?" No, there should not. A day with only wearable data (steps, sleep, HRV) is stored with a placeholder entry timed 23:59 and 0 kcal so the day exists in history, and the Meals card was listing that placeholder as if it were a meal ("4,093 steps, 3.6h sleep, HRV 25.6, SpO2 94.7%", 0 kcal, 0%). The placeholder is now left out, and with no real meals the card does not appear at all. Days with real meals are unchanged. New test: `p66_wearable_only_day.py` (fails on the old code, passes on the new).

## v3.10.932 — Meal Time Can Be Corrected When You Edit An Entry

Pete Spence: "Updating portion sizes would adjust the mealtime, so we'd need an update timestamp or change switch." Checked first: editing a portion (or any value) has never touched the time a meal was eaten, so fasts are not disturbed by portion changes (proved in the new test). The gap was the other way round: a time could never be corrected, and meals logged to a past day without a time stayed "approximate" and were ignored for fasting for ever. Both edit forms (single item and multi-ingredient) now have a **Meal time** field. It is blank for approximate entries, saving without choosing a time leaves them as they were, and choosing one sets the time and clears the approximate flag. Cancel discards it. New test: `p65_edit_meal_time.py`.

## v3.10.931 — Pete Spence, In Full

Pete Spence: "it's about time to change all references in the app and documentation of Pete to Pete Spence". Every reference in the app (Settings "Developed by", comments, messages), the landing page, README, TECHNICAL.md, the user guide, story and why-free pages, the GBM patient guide, CODEOWNERS, the server and the update scripts now uses the full name. Left alone on purpose: real export file names such as `Activity-Pete-*.csv` and `Data Export-Pete-*.zip` (the parsers match the names the devices actually produce), the test personas' typed-in name, and the Android launcher source (outside this repository). New test: `p64_full_name.py`.

## v3.10.930 — Fasting, Built Into The Whole App

Pete Spence: fasting has to be "fully embodied into the system, not just a bolt on", for everyone with or without a condition, and a help tip is needed because "a lot of people think longer is better". Every logged meal already carries a time, so fasting is **measured from the existing log with no new entry**, and past days count retroactively. Overnight fast for a day = its first meal minus the previous logged day's last meal; eating window = last meal minus first. A meal is any entry at or above a kcal threshold (default 50, Settings), so a black coffee or a supplement never breaks a fast. Times before 04:00 count as the late end of that day. Entries logged to a past day without choosing a time are now marked `timeApprox` (their stored time is when they were logged) and are ignored. A multi-day fast counts only when every day between the two meals is tagged Fasting. **Today:** new Fasting card (live time since last meal, goal bar, last completed fast, last eating window, condition note), with show/hide, reorder and an order migration for saved layouts. **Settings > Manage:** Fasting card (your own overnight goal, default 12 h, and the threshold); both are `mh_` keys so they travel in backups. **Trends:** Overnight Fast card (bars against a goal line, longest, % at goal, average eating window) with hide/reorder and order migration. **Compare Metrics:** Overnight fast and Eating window in the Nutrition group. **Reports:** Fasting section (last 30 days and all time, plus days after a fast at or above your goal against the rest on ketosis/on-target adherence, sleep and GKI, labelled as an association) with collapse/reorder; also a Fasting block in the printable report and a FASTING line in the AI context (the goal is the person's own, no medical target, association only). **Conditions:** diabetes gets a plain caution about glucose-lowering medicine, epilepsy about anti-seizure medicine, migraine a note on meal gaps as a trigger, GBM/keto a Proven / Early stage note linking fasts to ketones and GKI. **Help tip:** longer is not better; ketogenic eating already sits close to a fasting state; fat or protein taken with medicine barely moves insulin or glucose and never means skipping a dose. Persona `p63_fasting.py`.

## v3.10.929 — A Silent Connection No Longer Holds The App Up (Service Worker 2.4)

Pete Spence tested the web version in airplane mode (a VPN icon still showing), pressed Home and the page that came back was the landing page, and it was slow to appear. Three causes, all fixed. (1) A connection that is on but silent makes the browser wait its own long timeout before using the saved copy. The service worker now shows the saved copy if the server has not started answering within 3 seconds (time to first response only, so a slow download is never cut off) and refreshes it in the background. (2) The landing page (`/maxhealth/`, `index.html`) was not covered by the saved-copy fallback; it is now. (3) The landing page's Google Fonts stylesheet blocked rendering; it now loads without blocking, as the app already did. Also found by the new test: the bundled Chart.js / jsPDF / JSZip `<script>` tags block the page while loading, so with a silent connection the app never finished starting. They are now saved at install and served from the saved copy, refreshed in the background. Wording: the welcome screen no longer says "no subscriptions"; the landing page's "0 subscriptions" tile became "Free web version", and its wearable-sync line points to Premium first with the Termux DIY route second. The step-by-step Termux setup guide moved off the public landing page to an unlisted `premium-site/setup.html` (branded, `noindex`) for Premium customers; the landing page now has a Premium section with the register-interest link in its place. Persona `p62_silent_network.py` stops the server mid-test so connections are accepted but never answered; it hangs on the old worker and passes on the new one.

## v3.10.928 — Premium (Local Version) Card And A Register-Interest Page

Pete Spence's plan: keep the web version free, offer the local Android version as a paid Premium, and until payment is set up send interested people to a register-interest page on pspence.co.uk. New **Premium (local version)** card in Settings > Manage (show/hide, reorder, site search). A cloud visitor sees what local adds (automatic Health Connect wearable sync, data on your own phone, works with no signal, setup help and updates) and a **Register interest** link that opens `MH_PREMIUM_URL` in a new tab (`noopener`); the app itself sends nothing. A local user sees a thank-you instead. New `premium-site/` folder: `index.html` (page with an unticked consent box and a plain privacy note) and `register.php` (validates email, requires consent, honeypot, 30 s rate limit, saves to a private CSV above the web root, guards spreadsheet formulas, emails a notice) plus a GoDaddy cPanel README. The repo already carries an all-rights-reserved LICENSE. Persona `p61_premium_card.py`. The page is dark to match the app, carries the MaxedHealth icon (favicon, header, footer, link preview), shows the four Premium benefits as cards and is checked at phone and desktop width. Second pass: brighter secondary text, seven benefit cards (adds full offline mode, device extractors including adding new ones, device precedence with sleep-conflict flagging, self-checks and auto-update) and a Free web vs Premium table. The in-app card lists the same benefits.

## v3.10.927 — One-Tap "Share Backup" For Cloud Users

Pete Spence: "Anything that doesn't involve Android Studio is good to work on." A browser app on a phone cannot back itself up in the background, but it can hand a file to the phone's share sheet in one tap. New **📤 Share backup to Files / Drive / iCloud** button in Settings > Data & Backup and in the Today backup reminder. It builds the same zip as Export All Data and passes it to the share sheet, so you can send it to Files, Google Drive, iCloud, email or a message. The button only appears on browsers that can share files (phones, mostly); elsewhere it stays hidden and Export All Data still downloads as before. A cancelled share is not counted as a backup, so the reminder keeps nagging; a completed one is. If the share fails for any other reason it falls back to the normal download. p59 extended (button shown/hidden by capability, cancelled share not recorded, completed share hands over a zip and is recorded).

## v3.10.926 — Cooking Fat: Say So Instead Of Silently Counting Zero

Pete Spence: "Say go" on the hidden-fat idea, after the research showed photo apps miss roughly 30 g of fat per meal (oil and butter that soaked in). The AI prompt already itemised visible oil, sauce and butter and already refused to add ingredients you did not mention. The gap was the case in between: food that was clearly fried, roasted or pan-cooked with no fat visible or stated. New **cooking fat note** rule: the AI still adds nothing and invents no amount (your "never add unlisted ingredients" rule stands), but ends the message with one line: "No cooking oil or butter counted - tell me what you used and how much and I'll add it." It stays quiet when you already gave the fat, when fat is visible and itemised, or when nothing was cooked in fat (raw, boiled, steamed, microwaved, ready meals, labelled packaged foods). Prompt-only change; new p60 guards the rule wording so a later edit cannot quietly drop it.

## v3.10.925 — Protecting Cloud Users' Data From Being Lost

Pete Spence: "Is there any way to stop MaxHealth from having the cache cleared or to either highlight any data outstanding that would be lost or fire a warning?" The honest limit first: the browser, not the app, decides when a website's data is deleted, and no web page can force it to keep it. (Clearing "cached images and files" does not touch the app's data; clearing "cookies and site data" does.) So three layers:
- **Ask the browser to protect it.** The app now requests persistent storage (`navigator.storage.persist()`) shortly after start. If granted, the browser will not delete the data to free space. It can be refused, so Settings > Data & Backup shows which one you have ("🛡️ granted" or "⚠ not promised").
- **Say what would be lost.** For cloud users the backup banner on Today now appears after 7 days (was 14) or as soon as 5 days of entries are unsaved, and says how many days of entries (food and readings) have been added since the last backup, instead of a generic "it's been a while". Local (Termux) users are unchanged because the server backs up for them.
- **iPhone:** in a normal Safari tab (not installed) the banner and the Settings line explain that Safari can delete a website's data after 7 days without a visit (Apple's WebKit policy), and that adding MaxedHealth to the Home Screen avoids that.
- Not done: automatic backup for cloud users (a browser cannot write files in the background on a phone). A "share backup to Files/Drive" one-tap option could come later.
- Test: p59 extended (storage requested, both Settings states, banner names the unsaved days and clears after a backup, iPhone Safari tab recognised).

## v3.10.924 — Hide "Push To Local Server" For Cloud Users

Pete Spence: "Yes please" (the leftover found by the cloud persona). The Import tab's "🔄 Push this app's data to the local server" button is hidden when there is no local server, and shown again as soon as one is found. p59 now checks it.

## v3.10.923 — Cloud-User Persona (Daily Watch)

Pete Spence: "We probably need to do a full test as a cloud user. Could this be simulated and added as persona so we can keep a daily watch?" New `tests/personas/p59_cloud_user.py`, picked up automatically by the nightly run (it runs every `p[0-9]*.py`). It simulates a web-only visitor (iPhone or browser, no local server) by serving the page from a non-localhost host with every other request refused, then: onboards; confirms the app knows there is no server; walks all 10 screens checking for page errors and for Termux / `mhstart` wording outside the Import tab; checks the Sync card explains cloud mode, the Sync button is off and no background-sync banner shows; imports a CSV, checks Missing Data lists the right days, fills one gap and a brand-new day with Manual Entry; reloads the page and checks the hand-entered values and imported rows survived. No app change in this release.
- Found while building it, not changed (flagging rather than expanding scope): the Import tab still shows "Push this app's data to the local server" to cloud users. It does nothing useful for them.

## v3.10.922 — Wearable Sync Card Says Plainly It Is Not For Cloud Mode

Pete Spence: "How is the wearable sync card dealt with for these users? Is it hidden or carry a message saying that it's not for cloud use?" Checked: it was shown, with the Sync button greyed out, but the text said "Local server not running" and the panel under it told people to open Termux and type `mhstart`, which an iPhone or browser-only user cannot do. Now, on the web (cloud) version the card says "Wearable sync is not available in cloud mode. It needs the local version of MaxedHealth, which runs on an Android phone." and points to Manual Entry, the importers below it and Data Backup; the Termux panel is not shown. On the Android local version the old "server not running" help is unchanged. Test: p57 extended (page served from a non-localhost host with every other request blocked).

## v3.10.921 — Manual Entry And Missing Data Now Work In Cloud Mode; Bolder Log-Confirm Buttons

Pete Spence: "Yes to the cloud fix" (and a screenshot of the log-confirmation buttons asking for bolder text).
- **Cloud / GitHub Pages / iPhone users can now use Manual Entry.** With no local server, the same screen saves into this browser's own data (the same place a combined.csv import fills): the day is merged into the in-app history, and the browser's cached combined.csv is updated so it survives a reload. Only the typed fields are written, other days are untouched, and a day you open shows what the browser already holds for it. Local (Termux) behaviour is unchanged and still goes through the server.
- **Missing Data card** now works in cloud mode too: it works out the same gaps (no steps, heart rate or sleep on a finished day in the last 14) from the browser's data. The "Edit this day by hand" link on Trends is back for everyone (the v3.10.919 hiding is removed because it is no longer needed).
- **Bolder buttons:** "Log it ✓", "Save only", "Cancel" and "Verify across 3 AIs" in the log-confirmation panel now use bold text.
- Honest limit: in cloud mode there is no wearable sync, so data in the browser only exists from imports you do by hand, and clearing the browser's site data clears it (use Data Backup). Test: p57 extended with a cloud phase (server blocked: gaps, save, cache, shrinking list).

## v3.10.920 — RingConn Second Sleep Session: Broken Nights Joined, Naps Kept Separately

Pete Spence: "Yes to Ringconn second period." RingConn can record several sleep sessions under one date, and until now only the longest was kept; the rest were silently dropped (73 dates in the old export had this). Rule, per date: the longest session is the night. A short extra session (under 3 hours) that starts or ends within 2 hours of the night is a broken night (woke, got up, slept again), so its minutes and stages are **added to the night**. A short extra session further away than that is a **nap**, stored in a new field `sleep_nap_min` and shown as "Nap (separate)" in the day's Sleep card; it does not change the night's total. A long second session (3 hours or more) is a different night under the same date label and is ignored as before.
- Applies to RingConn exports imported from now on. Dates already in combined.csv are not rewritten (the merge never overwrites a source with itself), so nothing already settled changes.
- New column `sleep_nap_min` in combined.csv (old files simply gain an empty column). Not offered in Manual Entry.
- Test: new p58 (plain night, joined broken night incl. stages, nap, long second session ignored).
- Judgment call, flagged: the 3-hour and 2-hour limits are my defaults; they sit at the top of `extractors/ringconn.py` (`NAP_MAX_MIN`, `NAP_JOIN_GAP_MIN`) if they need tuning.

## v3.10.919 — New Day-Fix Links Respect Cloud Mode

Pete Spence: "How will all these new features affect cloud and Apple users?" Checked: Manual Entry saves through the local server, which cloud (GitHub Pages) and iPhone users do not have. The sync banner already stays hidden without a server, but the new "Edit this day by hand" link would have led to a form that cannot save, and the Missing Data card would have said only "could not check". Now the link is hidden without a local server, and the card explains it is a local-server feature. Everything else from 907-918 (photo ruler, tableware, grams, notifications card) runs in the page and works the same in cloud mode. p57 extended.

## v3.10.918 — Missing Data: Gap Finder With One-Tap Fix

Pete Spence: "Plough away" on the gap finder. A stalled sync leaves whole days without steps, heart rate or sleep, and they are easy to miss. New card **Settings > Import > Missing Data** lists the finished days in the last 14 days that lack any of those three (today is left out, it is still in progress; days before your first recorded day are not counted). Each row shows what is missing and a "Fill in" tap that opens Manual Entry on that day.
- Server: new `GET /data-gaps?days=N` (1-60, default 14) reads combined.csv; a day with no row at all counts as missing everything.
- The card has show/hide and reorder like the other Import cards, sits in the "History & entry" chip group and is findable by site search ("missing", "gaps").
- Test: new p57 (gap rules incl. empty rows, today excluded, pre-history ignored; row opens the right day; hide/reorder controls present).

## v3.10.917 — "Edit This Day By Hand" On Every Day

Pete Spence: "Could it not be a simple link on each previous days, so as you navigate, the option is there per day?" The Trends day navigator (← →) now shows a small "✏️ Edit this day by hand" link under the date. It opens Manual Entry on exactly the day you are looking at (today, yesterday, any day back), so a gap you spot while browsing is one tap from fixing. The sync-warning sheet's date box stays for when you already know which day. p56 extended.

## v3.10.916 — Pick Which Day To Fill In

Pete Spence: "What if it's not yesterday?" The Manual Entry link in the sync help sheet was fixed on yesterday. The sheet now has a date box (defaults to yesterday, cannot pick the future); the button opens Manual Entry on whichever day you chose. The Settings "fill a missed day by hand" link still goes to yesterday, and you can change the date in Manual Entry itself. p56 updated.

## v3.10.915 — Sync Warning Now Links Straight To Manual Entry

Pete Spence (8 Oct): "A link to manual adjustments from here maybe? It would make sense." Since a day the background sync missed is not recovered automatically, the warning now offers the fix.
- The sync help sheet has a "Fill in yesterday by hand (Manual Entry)" button: it closes the sheet, opens Settings > Import > Manual Entry, expands it and sets the date to yesterday (existing values for that day load so you only fill the gaps).
- Settings > Sync age warning also has a "fill a missed day by hand" link.
- Test: p56 extended (sheet closes, date is yesterday, section is visible).

## v3.10.914 — The App Now Tells You When The Phone's Background Sync Has Stopped

Pete Spence (8 Oct): the launcher's 30-minute sync had silently stopped (battery rules, found with the launcher's diary), and "users are going to need to be aware of all these. Either a script to check and fix, or to report if changed."
- **Fixing is not possible from the app or a script:** Android deliberately stops an app from lifting its own battery limits, so nothing can switch "No restrictions" on for you. What the app can do is notice the symptom and tell you, so that is what this does.
- **How it notices:** the launcher writes a line to its own diary each time the sync service starts (every 30 minutes when healthy). The server reads the age of the last one (`/sync-status` now returns `launcher_age_minutes`). Under 3 hours is fine.
- **Today banner:** after 3 hours with no run, an amber banner appears at the top of Today: "Background sync has not run for N hours". Tap it for a short sheet of the settings that cause it (battery No restrictions, Alarms & reminders, Autostart where the phone has it, lock the app / turn off "Pause app activity if unused", then open the launcher once), and a note that missed days may need Manual Entry. The ✕ hides it for the rest of the day; it disappears by itself when the sync recovers.
- **Settings > Sync age** now also shows how long ago the background service last started, with the same tap-for-help link, and warns at 3 hours instead of only after 6.
- **Self-check** (the Nothing to worry about / One to know / One to watch line) now includes a line when the background sync is late: amber after 3 hours, red after a day.
- Nothing is shown when there is no launcher diary at all (for example before the launcher is installed).
- Test: new p56 (diary age read correctly, unknown when missing, banner shows/hides/dismisses and returns when recovered, help sheet content, self-check both ways).

## v3.10.913 — A Sleep Night You Already Settled Is Not Asked Again

Pete Spence (8 Oct, 15:42): the "Sleep sources disagree" card for 8 Oct appeared again, although he had already chosen Zepp for that night at 09:33.
- **Cause (read from the code):** the launcher cannot see what was decided, so it re-queues the same overlap every time it syncs. The server then served it again, and the card re-asked an already-answered question. (The earlier comment in the code that a re-detected overlap "will show up again" was meant for "Decide later", not for a settled night.)
- **Fix (server only, no APK):** when you choose Use ringconn / Use zepp / add both / type your own figure, the server remembers that night together with a fingerprint of the sessions you were shown (source, start and end to the minute). If the launcher re-queues the identical sessions, they are dropped quietly. If the night genuinely changes (a different end time, a new session), you are asked again. **Decide later** is not remembered, so it still comes back.
- Test: p52 extended (settled night with identical sessions does not return, a changed night does, Decide later does).

## v3.10.912 — Tableware Boxes Follow What The Item Is

Pete Spence (8 Oct, screenshot of a custom item called "Test" showing Across/Holds/Empty): "How did Test know what it was? If a bowl or cutlery, the dimensions wouldn't work."
- **It didn't know.** Every custom item got the same three generic boxes. Now each item has a **kind**, chosen from a list when you add it (Plate, Bowl, Cup/mug/glass, Spoon, Knife or fork, Something else), and the boxes follow it:
  - Plate: Across, Food area, Empty weight
  - Bowl: Across, Holds (ml), Empty weight
  - Cup, mug, glass: Holds (ml), Empty weight (no width box)
  - Spoon: Length, Holds (ml)
  - Knife or fork: Length only
  - Something else (and every item you added before this): the original three boxes
- Spoons and cutlery say **Length (cm)**, the photo ruler says "Measure length" and "tap both ends", and the AI line says "cm long" instead of "cm across". Plates still get the food area.
- A box that already holds a value always stays visible, so nothing you entered can vanish. "Copy as new" keeps the source's kind. The built-in items were given their kinds.
- Test: p44 extended (box counts per kind, Length wording, food area on custom plates only, fork "cm long" in the AI line, filled boxes stay visible); p53 now expects 📏 on the 6 width/length items.

## v3.10.911 — Notifications Card Showed "Enable" Even When Already On

Pete Spence (8 Oct): "Settings/Manage/Notifications. Even if notifications are set, the button still says enable notifications."
- **Cause (reproduced):** the card was only brought up to date when the Reports tab opened or its header was tapped. The Settings page itself only had the page's fixed "🔔 ENABLE NOTIFICATIONS" button, so with permission already granted it still showed Enable until you happened to do one of those. Denied showed it too.
- **Fix:** the card now refreshes at load, when the app returns to the front (for example after changing the setting in Android), and whenever the browser's answer changes while the card is on screen.
- If the browser has not been asked yet, the status line now says so ("the browser reports 'not asked'"). If you tap Enable and no prompt appears, a message explains to allow notifications in the browser's site settings, instead of a misleading "Permission denied".
- Test: new p55 (granted hides the button, not-asked shows it, denied hides it, and a permission change while open is followed). It fails on the old code.

## v3.10.910 — Type A Portion In Grams, And A Real Accuracy Tip For Crockery

Pete Spence (8 Oct): the food-log edit has a way to change a portion by percentage, but needs "or enter a new portion size manually". And: is there a help tip explaining what actually matters for accuracy under crockery and cutlery?
- **Today > edit an entry (single item):** under PORTION % there is now "or type the new portion [__] g", showing what it was logged as. It works out the percentage from the logged amount, fills the % box, and the macros follow exactly as if that % had been typed. If the entry has no gram size it says so and points to the % box.
- **Multi-ingredient entries:** a matching "or set the whole portion to [__] g" under "Scale entire entry to %". Every ingredient is scaled by the same factor from its ORIGINAL amount (applying twice never compounds). If any ingredient has no gram size (for example "1 bowl") it refuses and changes nothing.
- **Crockery and cutlery help tip rewritten** to say what actually matters, in order: the plate's food area, the ml you measure with water for bowls/mugs/glasses, width to about 1 cm being plenty, a typed food weight always beating these sizes, and the photo-ruler rules (straight down, card at rim height or stand back and zoom, check the points).
- Test: new p54 (single-entry grams to %, multi-entry factor and no-compounding, refusal when a size is missing, tip wording).

## v3.10.909 — Plates: Food Area, Measured With A Third Point

Pete Spence (8 Oct): his plate is 29.1 cm across, but the food sits on a much smaller circle inside the rim. "Definitely needs the actual food area, and it might be sensible for a third measuring point."
- **New "Food area (cm)" box on plates** (dinner plate, side plate and copies of plates). Optional and blank by default, because rims vary far too much to guess.
- **Photo ruler, step 3 of 3 (plates only):** after the width, a "Food area ›" button asks for ONE tap on the inner edge of the rim. The plate centre is the midpoint of your width points, so the distance from the centre to that tap gives the food diameter. A dashed ring shows what it measured so you can see it follows the rim, and the point can be nudged or snapped like the others. "Use it" still saves the width only; "Use both" saves width and food area. A food area at least as big as the plate is refused. Mugs, bowls and cutlery still use the 2-step version.
- **AI portion line** now includes "food area (inside the rim) about N cm across", with an instruction to judge how much of that inner circle is covered rather than the full rim.
- "Copy as new" carries the food area for plates and does not add one to bowls.
- Test: p53 (3-step flow, ~10.0 cm food area from a known image, both values saved, oversize refused, Back returns, mug has no food step), p44 (plates only, AI line wording, copies).

## v3.10.908 — Tableware: Copy As New

Pete Spence (8 Oct): the place he is staying has several plate sizes (his measured dinner plate came out at 29.1 cm), plus different cutlery and bowls, so he needs more than one of each. "A copy from and forced rename should do it."
- **"copy as new"** link on every tableware item (plates, bowls, mug, glass, spoons, and your own). It makes a new item that starts with the source's sizes, then you adjust it (📏 for width, type the ml and weight).
- **Different name required:** an empty name or one already used is refused, so two similar plates can never be confused.
- Copy from Home: Home gets the copied sizes. Copy while viewing another set (Holiday etc.): that set gets the copied sizes and Home keeps Home's own.
- A copied spoon keeps the "level spoon" wording sent to the AI.
- Copies are ordinary custom items (remove on Home, up to 20), and they appear in the AI's tableware line like the built-in ones.
- Test: p44 extended (empty and duplicate names refused, starts from Home's override, spoon wording, copy inside another set, copy link on every item).

## v3.10.907 — Photo Ruler: Edge Snap

Pete Spence (8 Oct): "Wouldn't a snap to object make this process fool proof?"
- **Snap to edge:** when a point is placed (or moved), it slides to the strongest light/dark edge within about a thumb-width, searched along the line joining the two points, so rough taps land on the card edge or rim. Flat areas with no clear edge are left exactly where you tapped.
- **Snap button** (zoom row) turns it off, remembered in `mh_ruler_snap`. Nudge arrows still work on top.
- Test: p53 extended (tap off the edge lands on it, flat area untouched, toggle works); nudge test runs with snap off.

## v3.10.906 — Photo Ruler: Pick Up A Point And Nudge It

Pete Spence (8 Oct, screenshot): very difficult to place a point exactly, and a mistake means starting again.
- **Pick up and nudge:** the newest point is picked automatically (shown with an extra ring). Arrows ◀ ▲ ▼ ▶ appear under the photo and move it one screen pixel at a time, so zooming in makes the steps finer. Hold an arrow to keep moving.
- **Tap a point to pick it up** (within about a thumb-width) instead of replacing it, then nudge. Tapping elsewhere with both points placed still moves the nearer one there.
- Undo and Clear keep the picked-point marker in step.
- Test: p53 extended (nudge moves the picked point by the expected amount; tapping a point picks it up without moving it; the measurement follows).

## v3.10.905 — Photo Ruler: Pinch To Zoom, Drag To Move, No More Stray Points

Pete Spence (8 Oct, screenshots): trying to zoom put points in and Clear did nothing. The header was shifted off the left edge: pinching had zoomed the whole page, not the photo.
- **Gestures rebuilt:** two fingers pinch-zoom the photo (up to 8×, anchored on your fingers), one finger drags it around, a quick tap places a point. The screen behind can no longer be pinch-zoomed.
- **Taps and zooms only repaint the photo**, they no longer rebuild the screen, so the buttons stay put and your place in the photo is kept.
- **Buttons:** Fit / 3× / 6× (centred), **Undo** (last point) and **Clear** (this step's points). Marks stay the same size on screen at any zoom.
- Test: p53 extended (pinch zooms the photo and not the page, drag pans without placing a point, taps at zoom, Undo, Clear).

## v3.10.904 — Photo Ruler: Choose An Existing Photo

Pete Spence (8 Oct): no way to choose a photo. The single button used the camera directly, which skips Android's photo picker.
- Two buttons now: "Take a photo now" (camera) and "Choose a photo I already took" (gallery).
- Test: p53 extended.

## v3.10.903 — Photo Ruler: Readable Next Step

Pete Spence (8 Oct): the line at the bottom of the screen was barely readable.
- It was a faded-out "Next" button, disabled until both ends of the reference were tapped. Now the bottom bar always says what to do ("Step 1 of 2: tap both ends of the reference (2 to go)", then "Step 2 of 2: tap both edges of the item"), and the Next / Use it buttons only appear when they work, at full strength.
- Test: p53 extended.

## v3.10.902 — Photo Ruler: Clearer Reference Choices, Remembered

Pete Spence (8 Oct, screenshot): the reference list said "Bank card" but cards he has measure around 64 x 40 mm.
- Options renamed "Debit/credit card" with a note that those are the standard 85.6 x 54 mm; smaller loyalty or key-fob cards need the last option ("Smaller card or other object") with their length typed in mm.
- The chosen reference and any typed length are remembered, so it is set once.
- Test: p53 extended.

## v3.10.901 — Photo Ruler For Measuring Plates, Bowls And Spoons

Pete Spence (8 Oct): could we build a simple AR ruler for crockery and cutlery?
- **Settings > Tableware:** a 📏 beside every "Across (cm)" box. Take or choose a photo from straight above with a bank card lying flat beside the item, tap the two ends of the card's long edge (85.6 mm), then tap across the item. The size is worked out from the ratio and goes straight into that box.
- **Other references:** card short edge, A4 paper, or any object whose length you type in mm.
- **Accuracy:** zoom 1×/2×/3× to place points precisely; tapping again nudges the nearest point. Expect within a few mm if the photo is taken straight down; a tilted phone gives a wrong answer, and the screen says so. A result under 1 cm or over 60 cm is refused as an obvious mis-tap.
- **Why not real AR:** WebXR depends on ARCore being installed and supported on the phone, which cannot be checked from here. This works on any phone with a camera. If you want real AR later it can be added as an option on phones that support it.
- The photo is processed on the phone and never saved or sent.
- Test: p53 (new): known card and bowl sizes measured back to within 0.4 cm; plate value saved; absurd result refused.

## v3.10.900 — Sleep Card Spots Time-In-Bed Figures, Type Your Own; One-Tap Bug Report

Pete Spence (8 Oct, three screenshots): the sleep-conflict card offered RingConn 8.7h (23:16-08:01) against Zepp 5.0h. RingConn's own app says 6h55 asleep over that span; Zepp's says 4:25 plus a 0:43 nap (about 5h08), so Zepp's figure was right and RingConn's was the whole time in bed.
- **Flag on the card:** when a source's duration equals its whole start-to-end span (it sent no sleep stages), the card now says so: that figure is time in bed, not time asleep, so check the device's own app first.
- **Type your own:** a box on the card ("Or type your own, hours") saves your figure for that night through the same manual-entry path as the other choices. The server accepts 0.5-20 hours.
- **Not fixed (needs the launcher):** RingConn's Health Connect record carries no sleep stages, so the launcher can only see the whole span. Fixing that properly means a launcher change; until then the flag and the typed figure cover it.
- **Report a bug:** Settings → About → "Send feedback / report a bug" now opens a GitHub issue already filled in with app version, device, screen, connection and the server health check, with a prompt to drag in a screenshot. Under it, "Copy the report text instead" for anyone without GitHub. No food or health data is included.
- Test: p52 (new).

## v3.10.899 — One Cancel Is Enough

Pete Spence (8 Oct): editing one ingredient's portion on a photo-added meal and then cancelling needed a Cancel press per ingredient. I could not reproduce it in the plain pre-log edit (one Cancel works there), so this closes the two places where Cancel could repeat:
- **Item edit form:** Cancel now closes every open edit form at once (and clears its scaling baseline), and opening an edit closes any other first.
- **Save ingredients batch:** Cancel / "Back to edit" / dismissing the "can't physically fit" warning now ends the whole batch with a toast saying how many were skipped, instead of leaving each remaining ingredient to ask again (or leaving a half-finished batch stuck).
- Still not fixed if you see it elsewhere: a screenshot of the screen where it happens will pin it down.
- Test: p51 extended.

## v3.10.898 — Compare Two Periods: Expected Trend, Travel Day Included, Shorter Spans

Pete Spence (7 Oct, screenshot): baseline now correctly counts 20 days, but the recent period (3-6 Oct, 4 weigh-ins over 3 days) showed no weight trend, so no verdict.
- **Expected trend if logging is accurate:** new row. Your baseline burn (from the baseline weight trend) plus the steps difference, set against the kcal logged recently, predicts a weight trend per week. Compare it with what the scales show: a much bigger loss than predicted points to over-counting in the photos, flat or gaining to under-counting. Works even when the recent period is too short to measure its own trend.
- **Default recent period** now extends back over adjacent travel/Occasion days (e.g. a travel day before the first Holiday-mode day), so the trip starts where the trip started.
- A weight trend now needs weigh-ins over 3+ days (was 4+); the verdict still shows its margin of error.
- Test: p51 extended.

## v3.10.897 — Compare Two Periods Shows What It Counted, And Reads Scale-File Weights

Pete Spence (7 Oct): still showing 2 days after the window fix.
- **"What was counted"** under the card lists, for each period, the exact dates with food logged, the dates with a weight, and the dates with neither, plus the app version. If something is missing, it is now visible which day.
- **Weights from the scale file:** days that only exist in the imported scale (Withings) file, with no food logged, now count as weigh-ins too (they previously did not, because the card read only the app's own day records).
- Test: p51 extended.

## v3.10.896 — Compare Two Periods (And Your Story) Were Limited By The Trends Window

Pete Spence (7 Oct, screenshot): the new card showed 1 logged day and 1 weigh-in for the baseline even though every date had weights.
- **Cause:** `getTrendsData(true)` ("always full history") only skipped the Today view; with Trends set to a numbered window (e.g. 7 days) or a custom range it still cut the data to that window. So the Compare Two Periods card, Your Journey and the drill-downs could silently see only the last week or so.
- **Fix:** full-history callers now ignore the numbered and custom Trends windows.
- Test: p51 extended (windowed vs full counts, baseline days counted).

## v3.10.895 — Compare Two Periods (Photo-Estimate Check)

Pete Spence (7 Oct, home from holiday where meals were photo-logged): wants a comparison with the previous few weeks, since weight is drifting down slightly while logged intake is no higher than usual.
- **New Trends card "Compare Two Periods"** (Patterns chip; has show/hide and reorder like every card). Defaults: Recent = your latest run of Holiday-mode days, Baseline = the 3 weeks before. Dates are editable and remembered.
- Shows logged days, avg kcal, protein, carbs, steps, weight trend per week and weigh-ins for each period.
- **Verdict:** logged kcal minus 7700 x daily weight change = the burn the logging implies. If real burn was similar in both periods (adjusted ~40 kcal per extra 1,000 steps), the gap between the two implied burns is how far the recent logging was off. Always shown with a margin of error; when the gap is inside the noise it says so rather than claiming a bias. Needs 3+ logged days and 3+ weigh-ins over 4+ days per period.
- Honest limit: a ~6 day holiday gives a wide margin (several hundred kcal/day). Weigh-ins on the days the scales missed (the new backdate/edit weight options) tighten it.
- Test: p51 extended.

## v3.10.894 — Weight In The History Day Editor

Pete Spence (7 Oct, screenshot of History → Edit day totals): that screen has water, steps and exercise but no weight, so a missed day could not be fixed there.
- **Edit day totals** now has a WEIGHT box (in your chosen unit, stones + pounds in st mode). Blank means no reading for that day. A corrected weight is also what that day's exercise calories are costed with, and your current weight follows the newest weigh-in. The "Changed:" summary after saving lists a weight change.
- Test: p51 extended.

## v3.10.893 — Add Or Fix A Day's Weight From The Charts Too

Pete Spence (7 Oct): "Wouldn't it have been a good idea to update weight for previous days from here too?" (Fair point: the date box only existed behind the dashboard UPDATE button.)
- **Trends weight card:** new "＋ Add or fix a day's weight" link, opening on the most recent day with no reading.
- **Your story graph:** tapping a gap marker offers "＋ Add a weight for a missed day" (opens on the first missing date); tapping any weigh-in offers "✏️ Edit this day's weight".
- **Weight drill-down:** same "＋ Add or fix a day's weight" link.
- The popup opens on the chosen date, pre-filled with that day's reading if there is one (empty if not).
- Test: p51 extended.

## v3.10.892 — Faint "Last Known" Weight Line Across Gaps

Pete Spence (7 Oct): liked the idea of a faint carried-forward line for days with no weigh-in.
- **Your story graph and the Trends weight chart** now draw a faint dotted flat line from your last real weigh-in across any gap to the next reading, so a gap reads as "no new data, last known was X" rather than a slide between two points. Display only: nothing is saved, and averages, rates and exports ignore it. A "last known (carried, not saved)" note appears in the legend when a gap exists.
- Test: p51 extended (flat across the gap, helper, legend).

## v3.10.891 — Copy Previous Set, Backdate A Weight, Honest Gaps On Your Story

Pete Spence (7 Oct, on holiday with only gym scales): "Manual weight for days not provided by Withings... a 2 week gap would mean what on the charts?" and "creating a routine set, copy previous line would be useful."
- **Copy previous set:** in the routine editor each set line has a ⧉ button (copies reps, weight and note into a new line below it), and each exercise has a "⧉ copy previous set" link. The same link is on the Apply (workout) screen. One typed line plus taps gives 3 x 10 @ 40 kg.
- **Backdate a weight:** the Update Weight popup now has a Date box (defaults to today, can't pick the future). Choosing an earlier day saves that day's reading without changing your current weight unless it is your newest one.
- **Your story graph shows gaps:** a break of more than 7 days between weigh-ins now stops the line and shows a "⋯ 18d" marker, instead of joining the two ends with a straight line. Also fixed: treatment markers were converted twice in lb/st (v3.10.890).
- Not done on purpose: carrying a previous day's weight forward as stored data (it would flatten trends and distort the weekly rate).
- Test: p51 extended (gap marker, backdate, future date, copy sets).

## v3.10.890 — Charts Follow Your Weight Unit, And Food/Water/Exercise Lines On Your Story

Pete Spence (7 Oct): "Today has exercise, food and water... can these be merged into the multiple metrics area? Best added to the Your story graphic. Charts in kg only."
- **Charts in your unit:** the Your Journey chart, the weight / bone mass / hydration drill-down (hero number, stats, chart, day panel), the full-screen chart and Compare Metrics now show lb (or lb for st+lb, same as the Trends weight chart) when that is your unit. Stored data stays kg.
- **Your Journey overlays:** seven chips above the chart (Calories, Protein, Carbs, Water, Logged exercise, Active calories, Steps). Each draws as a dashed line scaled to its own maximum, so they sit together on one chart; tap a day to see the real figures. Shown on the days you weighed (that is what the chart is built from). Your choice is remembered.
- **Compare Metrics:** new "Logged exercise" (sum of the exercise you logged that day) and "Active calories (wearable)", both under Exercise. Fat (g) had been missing from every group so you could never pick it; it is now under Nutrition.
- Test: new p51 (converters, series, groups, chips persist, day panel); p45/p46/p49 still pass.

## v3.10.889 — st + lb Entry, And The Compare-AI Chat Bubble Pulses

Pete Spence (7 Oct, real phone): (1) with the unit set to st + lb the Update Weight popup still asked for pounds; (2) the "Asking Claude, Gemini, and ChatGPT independently about..." chat bubble did not pulse.
- **st + lb entry:** the Update Weight popup and the weight target boxes now take stones and pounds in one box, e.g. "14 st 2". It also understands "14st 2lb", "14 stone 2", a lone "198" (40 or more is read as pounds) and a lone "12" (under 40 is read as whole stones). Voice entry keeps both numbers ("fourteen stone two" becomes 14 st 2). The boxes switch back to plain numbers in kg or lbs. Stored value is still kg.
- **Compare-AI bubble in the Log chat** is now a pulsing "thinking" bubble (the earlier wait-box change covered the edit screens, not this chat bubble). It is removed when the answers arrive, as before.
- Test: p45 extended (st popup, parsing variants, st targets, back to kg), p47 extended.

## v3.10.888 — Topic Chips On Settings → Data (Import)

Pete Spence's Data screenshot showed seven sections tucked behind a "Hidden:" strip. Same view-filter chips, so the page needs far less hiding: All · Connect devices (sync wearable data, add new device, advanced/manual pipeline) · History & entry (wearable history, nutrition history, manual entry) · Backup & checks (data & backup, data management, preview & validator). Nothing is moved or un-hidden; search resets the chips to All. Test: p50 extended.

## v3.10.887 — Topic Chips On Reports And Settings → Manage

Pete Spence (7 Oct): continue the de-cluttering. Reports had 13 flat sections and Settings → Manage had 19.
- **Reports chips:** All · Ask & share (Ask AI, Query Builder, Export) · Summaries (Summary, Insights, GBM, Research) · Analysis (activity credit, seasonal, sleep & ketosis, weight vs protocol) · Treatment (analysis, sessions).
- **Settings → Manage chips:** All · Me & targets (profile, carb ceilings, water, tableware, steps, exercise offset, device precision, formulas) · AI & alerts (AI provider, notifications, idle timeout, carer) · Health tracking (supplements, symptoms, treatments, lab results, report profiles) · About & setup.
- **View filter only:** nothing is moved, deleted or un-hidden; your own ▲ ▼ 👁 order and hidden cards keep working, and All looks as before. The topic is remembered per screen.
- **Search is safe:** searching for any setting or report resets the chips to All first, so a chip can never hide the thing you just searched for.
- Test: p50.

## v3.10.886 — Trends "Today" View: Look-Alike Sections Merged, Chips Apply

Pete Spence (7 Oct): continue de-cluttering. Trends opens on the single-day "Today" view, which had its own look-alike cards.
- **Weight and Body Composition are now one section** ("Weight & Body Composition": weight, fat %, muscle %, bone, hydration). Rows only appear when there is a reading. The weight row opens the weight chart. Bone and hydration now follow your chosen weight unit (they were stuck on kg).
- **Sleep and Sleep Detail are now one "Sleep" section** (stages, then bedtime, wake time, efficiency and snoring when recorded).
- **The topic chips now sit above both views** and filter the single-day sections too (Body = weight & body composition; Heart & sleep = activity & vitals and sleep; Food = meal breakdown). Patterns says there is nothing to compare in a single day.
- Old saved hide/order settings for the retired Body Composition and Sleep Detail sections are simply ignored; your other choices are kept.
- Test: p49 extended.

## v3.10.885 — Trends: Topic Chips And "What Question Does This Answer" Captions

Pete Spence (7 Oct): the app is so feature-rich that similar-looking cards confuse and overwhelm. First step, on Trends (the worst overlap).
- **Topic chips** across the top of Trends: All · Body · Heart & sleep · Food · Patterns. Tap one and only that topic's cards show (Body = Body Composition, Journey, weight, fat %, muscle %, bone, hydration; Heart & sleep = HR, SpO2, HRV, sleep, steps, distance; Food = calories, protein, carbs, water, GKI, top foods, day of week; Patterns = wellness balance and patterns). Remembered between visits.
- **It is only a view filter.** Nothing is moved, deleted or un-hidden, so your own ▲ ▼ 👁 order and hidden cards keep working, and All looks exactly as before.
- **One-line captions** on Journey, Body Composition, Patterns, Top Foods and Day of Week saying which question each answers, so look-alike cards are told apart at a glance.
- Not yet done (next passes): the Today/daily view and Reports tab groupings, merging the separate fat/muscle/bone/hydration cards into Body Composition, and a Simple/Full switch for new users.
- Test: p49.

## v3.10.884 — Photo Estimates: Count Small Items, Fresh vs Jarred, Don't Inflate Small Portions

Pete Spence (7 Oct): a bowl with about seven pitted cherries and a dollop of soft cheese came back as "cherries (fresh) 80g, 51kcal, 12.2g carbs", the worst over-estimate yet.
- **Why:** the meal-photo prompt only had plate-sized anchors (a loaded dinner plate is 400-700g) and no way to size small countable items, so a handful of fruit was sized like a serving. It also had nothing to tell fresh fruit from jarred fruit in syrup.
- **Fix (prompt):** (1) count visible pieces and multiply by a per-piece weight, shown in the message ("7 x ~4g = ~28g") - fresh cherry with stone ~8g, pitted/jarred ~4-5g, plus strawberry, blueberry, grape, olive, almond, walnut, prawn, cherry tomato; (2) pitted/glossy fruit in pooled juice is jarred/tinned, not "fresh" - use the drained weight, say so, and flag the syrup sugar; (3) the 400-700g anchor is for a loaded dinner plate only, a small bowl or dollop is typically 30-120g.
- Still visual estimates (about +/-20%); the Edit ingredients button remains the quick correction. Test: p48.

## v3.10.883 — Slow Waits Get The Pulsing Border

Pete Spence (7 Oct): anything that can take a while to populate should show the same flashing box border as the chat's "Analysing photo…" bubble.
- **New shared `.mh-wait-box`** — identical pulsing border (the chat thinking bubble's animation); respects reduced-motion.
- **Compare AI** (library edit, log entry edit, history edit, recipe ingredient add): the "Asking Claude, Gemini and ChatGPT…" placeholder now pulses until the answers replace it.
- **Report and AI buttons** (Ask AI, full summary, GBM review, oncology narrative, missed-day estimate, wearable sync): a pulsing box appears right under the button while it is working and disappears the moment it finishes, errors, or is re-enabled.
- Chat bubbles already pulsed and are unchanged.
- Test: p47.

## v3.10.882 — Body Composition Card (Trends)

Pete Spence (7 Oct): borrowed the best idea from Withings' Body Composition screen. Weight alone hides what changed; flat weight with fat up and muscle down is a different story from fat down and muscle up.
- **New Trends card "Body Composition"** (with ▲ ▼ 👁 like every card). A plain-words verdict: gaining fat / losing muscle / losing fat, gaining muscle / holding steady and so on.
- **How it decides:** this week's smart-scale readings (averaged) vs the week before, with a 0.3 kg threshold, so one noisy bioimpedance reading can't flip it. With too little data it compares the latest weigh-in with the one before (0.5 kg threshold) and says so on the card. A single reading makes no claim. A note appears when weight barely moved but composition did.
- **Stacked share bar** (muscle / fat / bone) from the latest reading, plus **change badges** for weight, muscle and fat (↗ ↙ arrows, change in your chosen weight unit, and change in share as points).
- Reads the same Withings rows as the weight drill-down; hides itself when there are none. Honest caveat shown: scale estimates swing by half a kilo or more.
- Not borrowed: Withings' population "Normal/High" bands (we have no population data) and BMR labels.
- Test: p46 (verdicts for fat-up/muscle-down, recomposition, steady, sparse fallback, single reading, unit-aware, controls present).

## v3.10.881 — Tableware Card Gets Show/Hide And Reorder

Pete Spence (7 Oct): every card needs show/hide and reorder. The Tableware & Portion Sizes card was registered for hiding but missing from the Settings ordering list, so it never got the ▲ ▼ 👁 controls.
- Tableware now has ▲ ▼ 👁 like the other Settings cards (and starts in the same open/closed state handling as its neighbours).
- **Side fix:** adding a card to a list used to throw away the order you had arranged (the saved order was only accepted if it matched the live list exactly). Your order is now kept, and a newly added card slots in after its natural neighbour. This protects every future card too.
- Test: p44 extended (controls present, saved order kept, move works).

## v3.10.880 — One Weight Unit For The Whole App (kg / lbs / st + lb)

Pete Spence (7 Oct): do the kg/lbs choice from onboarding and profile drive every weight card? They did not. The onboarding choice only converted what you typed, was never remembered, and everything displayed in kg.
- **New Settings → Profile → Weight unit** (kg / lbs / st + lb). Display only: data is always stored in kg, so switching never changes or loses anything. In st + lb, fields where you type a weight take pounds (labelled lb); everything displayed reads like "14 st 2 lb".
- **Follows the unit:** dashboard weight card, gap to target and trend rate, target range fields in Settings, the Update Weight popup (and voice entry), Trends weight card/stats/chart, history rows, journey stats, drill-down numbers, weekly report, suggested-targets text, early-warning text, chat weight reply.
- **Real bug fixed:** onboarding in lbs or st stored the typed number as if it were kg (200 lb became "200 kg"), and the same for the target. Height typed in ft+in was also stored raw and dropped. Both are now converted to kg/cm, and the chosen unit is remembered.
- **Not converted (still kg):** the metric drill-down chart and its hero figure, the journey chart, correlation tables, reports/exports and AI prompts (clinical figures stay in kg on purpose).
- Test: p45 (lbs onboarding stores kg, unit persists, dashboard/target/modal/trends follow, st rounding, kg mode untouched).

## v3.10.879 — Tableware & Portion Sizes (Settings)

Pete Spence (7 Oct): a settings list of crockery and cutlery sizes so photo estimates are more accurate, with defaults, overrides, per-item return-to-default, and labelled sets.
- **Settings > Tableware & Portion Sizes:** dinner plate, side plate, bowl, mug, glass, teaspoon, dessertspoon, tablespoon. Each has Across (cm), Holds (ml) and Empty weight (g). Typical sizes are pre-filled; weights are blank by default (never guessed).
- **Sets:** Home is built in and always the starting set. Add or remove your own (holiday, work, parents' house...). Non-Home sets store only what differs and inherit everything else from Home, so a later change to Home flows through.
- **Reset:** a ↺ appears beside any changed value. On Home it restores the typical size; on other sets it means "same as Home".
- **Back to Home on (date):** optional per set; checked on load, focus and every minute.
- **Log chip:** shows the active set when it is not Home.
- **AI:** the photo/meal estimate prompt gets a KNOWN TABLEWARE line (untouched defaults are marked "typical size, not measured"). The compare AIs are text-only (they never see the photo) so they get the same line in their prompt text.
- Test: p44.

## v3.10.878 — The App Opens With No Connection At All (service worker v2.3)

Pete Spence (6 Oct, 20:24): with WiFi OR mobile data on, the app opens normally; with BOTH off (or airplane mode with WiFi off) it shows the old May screen instead. `/last-hits` proved Chrome never contacted the server in that state, so Chrome was showing something stale it had stored. Reproduced in the test browser: with no connection at all the old code fails to open the page (net::ERR_INTERNET_DISCONNECTED).
- **sw.js v2.3:** the service worker now keeps the last good copy of the app page and serves it only when the server cannot be reached. Whenever the server answers, the page always comes fresh from it (network first, no HTTP cache), so nothing can be out of date while you have a connection. A copy is saved when the worker installs, so the first offline open already works. Other requests (data, sync) still go to the network and fail normally offline, as before.
- **maxhealth.html:** the page used to delete ALL service workers on every load and re-register one. That would remove the worker holding the offline copy, so it now removes only workers that are not its own `sw.js`.
- Your saved data is untouched (same address, same storage); offline the app shows what is saved on the phone, and the offline banner/wrapper behaves as before.
- Test: p43 (online fresh, offline serves the last good page, `?tab=` links work offline, one registration after reload, fresh again once back online). It fails on the old code with ERR_INTERNET_DISCONNECTED.

## Server — Clear-Site-Data Header Withdrawn (no app version change)

The `Clear-Site-Data: "cache"` header added earlier on 6 Oct (to drop Chrome's stale cached copy) is removed again: with it, the app sat on its MH splash screen (20:16, WiFi and mobile data on). Chrome holds the page response until a clear finishes. p42 now checks the header is NOT sent. The /last-hits diagnostic stays.

## Server — /last-hits Diagnostic For The Fully-Offline Stale Screen (no app version change)

Pete Spence (6 Oct): with airplane mode on AND WiFi off, the old May screen appears again (with WiFi left on inside airplane mode, the real app opens fine; clearing the launcher's cache did not change the fully-offline case). To tell whether Chrome even reaches the server in that state, the server now remembers its last 15 page loads (time, path, client) in memory and shows them at `localhost:5757/last-hits`. Nothing is written to disk.

## v3.10.877 — Ketosis Banner: Controls No Longer Cover The Text

Pete Spence (6 Oct, screenshot): the 👁 hide button sat on top of the end of the ketosis banner ("92.2G REMAINING"), hiding part of the number, and the ▲ ▼ were nearly invisible on the light theme (white at 50%). The three controls now sit on their own row above the banner, in the same grey as every other card's controls. Test: p41 (fails on the old layout).

## v3.10.876 — Typing A Dish No Longer Gets Mistaken For A Suggestion Request

Pete Spence (6 Oct, same screenshot): he typed "Ceaser salad with beef bacon" to log it, and instead of logging it the app answered "Here's what fits, using real items from your library" with a beef burger in the salad. The short-phrase check for "meat and 2 veg" style requests split the text on "with", saw the category word "salad" and a food word, and decided it was a request for suggestions.
- A bare phrase now only counts as a suggestion request when every word in it is category vocabulary (a category, veg/veggies, a food keyword, a number or a filler word). "Ceaser" is a dish name, so that phrase goes down the normal log path. "meat and 2 veg", "protein and pasta", "chicken and 2 veg" and "meat and veg" work as before.
- Test: p40 (fails on the old code).

## v3.10.875 — Swapping A Suggested Item: Online Search Starts From What You Typed

Pete Spence (6 Oct, screenshot): a "Here's what fits" suggestion had Asda Beef Burgers in a Caesar salad with beef bacon. He tapped swap, typed "beef bacon", then went online, and the search box (and Try AI) came up with the old item, "Asda Beef Burger", instead of "beef bacon".
- The swap picker now hands what you typed to the online search. The old item's name is only the starting point when nothing was typed. Fixed for suggested-meal items, recipe-builder ingredients and flagged-ingredient searches.
- Test: p39 (fails on the old code).

## v3.10.874 — Barcode Scan: QR Codes Ignored, Not-Found Offers To Read The Label

Pete Spence (6 Oct, screenshot of a Luvbiltong beef biltong pack): the scan reported "Barcode 5065015932000 not found" and then "Barcode https://www.instagram.com/luvbiltongsnacks/ not found". The scanner had locked onto the QR code printed on the pack and tried to look the web link up as if it were a product.
- Only real product barcodes (8-14 digits, EAN/UPC) are now looked up. QR codes and other codes are ignored and the scanner keeps looking; a photo with only a QR code falls through to the AI reader.
- When a barcode is not in Open Food Facts (or has no nutrition data), the message now carries a **"Read the label with AI instead"** button. It attaches the picture you just took to the meal box, so the normal photo AI reads the label (the 44g protein / 85g on that pack) rather than leaving you at a dead end.
- Test: p38 (fails on the old code).

## v3.10.873 — Weather Card: Show / Hide / Reorder, Help Tip, And Documented Formulas

Pete Spence: help tip for which environmental factors affect the app; update the Formulas card?; the usual show/hide/reorder.
- **Show / hide / reorder:** the weather card now has the same ▲ ▼ 👁 controls as every other Today card (also on the "Add local weather" prompt), joins the "Hidden:" restore strip as "Weather", and sits just above Water by default. Anyone who had already saved a custom Today order keeps it; the weather card is slotted in above Water rather than resetting their layout.
- **Help tip (?)** on the weather card: what the weather changes (water target, suggested effort, tips), what it does not change (calories, macros, ketosis targets), that your own adjustment wins, and that these are rule-of-thumb guides.
- **Formulas & Technical Reference** has a new "Water Target & Weather" section: base target + 500ml per exercise hour + heat extra (25-29° +250ml, 30-34° +500ml, 35°+ +750ml), the effort-easing bands, and when tips appear. It is also findable through Settings search (weather, heat, hydration, effort).
- **Hourly strip + best time for outdoor exercise:** under the weather summary, a scrolling 06:00-22:00 strip with a weather icon, temperature and rain chance (when 40%+) for each hour. The best window is outlined: the longest remaining run of hours that feel 27° or cooler, with rain under 40% and UV 5 or lower. If none, it names the coolest hour or says indoors is better. Your own temperature adjustment shifts every hour; marking today wet gives no window. Older cached weather refreshes itself to pick up hourly data.
- Tests: p36, p37.

## v3.10.872 — HRV Shows Whole Milliseconds; Weather Search Box Fixed

Pete Spence (6 Oct, two screenshots): the weather card's town search was a tiny oval beside a huge Search button, and the HRV card showed 27.29901960784314 overflowing its tile.
- **HRV:** the Trends card, its Min/Max/status line and the gauge now show whole milliseconds (27ms). The launcher sends averages as long decimals; the Health Connect importer now also keeps one decimal on HRV, heart rate and SpO2 averages (27.3), so new data is stored tidy. Existing stored rows keep their long values, but they now display rounded.
- **Weather card:** the setup search box and Search button, and the "Not right? Adjust" fields, are now sensibly sized (the app's global input styling had been squeezing the box).
- Test: p35 (fails on the old code for both problems).

## v3.10.871 — Tapping A Notification Opens The App On The Right Screen

Pete Spence: reminders showed up on his phone, but tapping them should open the app where the notification was about. The service worker had no click handler at all, so a tap just opened or focused the app wherever it was. Now (sw.js v2.2): tapping closes the notification, focuses the open app and takes it to the screen the reminder belongs to, or, if the app was closed, opens it with `?tab=<screen>` and the page switches itself (and tidies the address). Supplement reminders now go to the Supplements screen (they went to the dashboard); carb alert and end-of-day go to Log; weekly summary goes to Reports. Test: p34 (fails with the old service worker, passes with the new).

Also found while testing: a test run that gets killed can leave its server running on port 5757 and make later runs test stale code; clear leftovers by process id before re-running.

## v3.10.870 — Logging No Longer Crashes When The AI Sends Numbers As Text

Pete Spence, 5 Oct evening, logging "Duck, beef, beef slices, broccoli, carrots": "Something broke processing that response: after.toFixed is not a function." The AI had replied fine, but one or more numbers came back as text (e.g. "72", "12g", "<1") rather than numbers. Text in the totals turns addition into joining ("0" + "650" = "0650"), and the preview then crashed. Reproduced exactly, then fixed: every nutrition number from the AI is now converted to a real number before anything uses it ("12g" -> 12, "<1" -> 0.5, "trace"/blank -> 0). Test: p33.

## v3.10.869 — Portion Guesses Are Now Visible Per AI (And Work For Whole Meals)

Pete Spence pasted a whole-meal check (omelette, poached egg, halloumi, mushrooms) that showed no portion information. The v3.10.864 change was in, but it only showed portions in a summary line at the bottom, and its comparison used just the first weight in the list (200g), which is wrong for a multi-item meal. Now: each AI's row shows "its own portion guess: ~Xg (kcal)" or says it gave none; for several foods the AIs are asked for the combined weight and it is compared against the sum of all stated weights (480g here). Test: p29 now runs a four-item meal.

## v3.10.868 — GBM Reports Can Now Actually Be Hidden

Pete Spence: the GBM cards weren't hiding. The two GBM-only reports on Insights (GBM Monthly Summary, GBM Research Digest) have the 👁 hide button, but a routine that shows them for GBM users ran after every render and forced them back on, undoing the hide. It now respects your hide choice (non-GBM users still never see them). Also re-checked right after each hide/show tap. Test: p32 (fails without the fix, passes with it).

## v3.10.867 — Weather Card Suggests Today's Exercise Effort

The weather card now says "Suggested effort today": normal, ease about 5% (25°+), 10-15% (30°+), 20% or go indoors (35°+), indoors or ease 10% (-5° or colder), always following your override. Rule of thumb, not measured. Test: p31.

## v3.10.866 — Local Weather: Water And Exercise Tips, With Your Override

Pete Spence: environmental factors for exercise: a quick look at location and a reliable weather source, which can be overridden because forecasts are often wrong, affecting water intake and exercise difficulty.
- New card above Water on Today: "Add local weather". Pick a place by typing a town (free Open-Meteo geocoding) or "Use my location". Only the rounded coordinates leave the phone, and only to Open-Meteo (free, no account or key).
- Shows now / high / feels-like max / rain chance / UV, with exercise tips: very hot (35°+), hot (30°+), warm, freezing, cold, wet, high UV. These are rule-of-thumb guidance, not measured.
- **Water target rises on hot days** on top of the exercise allowance: +250ml from 25°, +500ml from 30°, +750ml from 35° (feels-like high). Shown as "+500ml heat".
- **Your override wins:** "Not right? Adjust" lets you set what it actually feels like today and dry/wet; it applies for that day only and "Back to forecast" undoes it. The water target and tips follow your figure.
- Offline: the last forecast for today is kept and used; with none, the card says so and nothing changes. Location and cache are included in backups.
- Not yet wired: exercise "difficulty" scoring in logged workouts and the AI brief reading the weather. Candidates for next.
- Test: p31.

## v3.10.865 — The Server Now Keeps Its Own Scheduler Alive (Why The App Kept Dropping Offline)

Pete Spence's phone logs (5 Oct): `pgrep crond` returned nothing, and the auto-update log stops dead on 2 Oct 14:05. **crond had silently died.** crond runs the watchdog that restarts this server, so when Android later killed the server nothing brought it back: "Site cannot be reached", and the old May screen was whatever else the home-screen icon could open. (The watchdog log also shows the server being found down about hourly for days, so Android is killing it regularly.)
- While the server is alive it now checks every minute that crond is running and restarts it (logged to `~/mh_watchdog.log`), and re-takes the wake-lock at startup.
- The watchdog cron line is now self-installed too if missing (the other two already were).
- Test: p30.
- Still needed on the phone: Android battery setting "Unrestricted" for Termux and Termux:Boot.

## v3.10.864 — The 3-AI Check Now Judges Portion Size Independently

Pete Spence: "Why doesn't each AI try to work out the portion sizes as well as the whole dish? What if the original AI (you) have not guessed the portion sizes correctly in the first place?" Fair: the checkers were handed my guessed amount ("300g") as fact and only asked for macros, so a bad portion guess was simply confirmed three times.
- Each of Claude, Gemini and ChatGPT is now also given your original words and asked for its **own portion estimate** (grams) and the calories for that portion, alongside the macros for the logged amount. Applies to the meal check, the 3-AI estimate and all the edit forms that use it.
- The card shows each AI's portion guess and warns when they disagree by 25%+ (or two of them are well off the logged amount): "Portion size is the shaky part... weigh it if you can". Averaging still uses the logged amount, so nothing changes silently.
- "Browse saved prompts" on the Log tab is now centred.
- Test: p29.

## v3.10.841 — Sleep Conflict Card No Longer Offers To "Add" Two Devices' Sleep Together

Pete Spence: "Looks like the sleeping health connect issue is still apparent" — Trends showed 13h32m total sleep at 11:15am. Screenshots of both apps settled it: RingConn and Zepp each said he'd been asleep **5h17m**, but the raw Health Connect sessions (RingConn 01:23–06:13, RingConn nap 08:03–09:11, Zepp 01:56–09:16) add up to 13h18m — spans include awake time, and two devices were recording the same night.

Web side: the sleep-conflict comparison card had a "Both genuinely happened — add them" button that summed every queued session. That only makes sense for separate periods, which the launcher already sums automatically; the card only ever appears for two devices overlapping in time, where "add them" can only double-count. Removed. The real fix is on the launcher side (v11 — see the launcher's CHANGELOG and TECHNICAL.md's Health Connect section): sleep is now measured in asleep time per source, and two devices that agree within 20 minutes resolve silently without a card at all.

## v3.10.844 — Extractors Ship In The Repo (No Hand-Copy, New Installs Work)

Pete Spence asked whether all of this is smooth for new users. It wasn't: `app/extractors/` sits outside the git repo, the launcher's `provision.sh` only creates it empty, and nothing ever filled or updated it, so a brand-new install had no Health Connect extractor at all ("No extractor found") and Health Connect data would never reach combined.csv. `run_extractor()` now prefers an extractor shipped in the repo's own `extractors/` folder and falls back to `app/extractors/` (still used for the withings/ringconn/amazfit ones that only exist on Pete Spence's phone). `health_connect.py` is in the repo, so `git pull` is the whole upgrade. Tested with a sample export.

## v3.10.863 — The App No Longer Freezes On A Dead Connection (Offline Mode Actually Works)

Pete Spence, abroad: offline mode "obviously doesn't work... the local service seems to want external network access." He was right, and my v3.10.862 test had missed it: it made internet requests fail *instantly*, but a phone with no signal or roaming data makes them *hang*, and the page head loaded four things from the internet as **blocking** resources (Google Fonts, jsPDF, jsPDF-AutoTable, JSZip). The browser waited on them before showing anything, so the app sat there. Reproduced (page never finished loading with hung requests), then fixed:
- **jsPDF, its table plugin and JSZip now ship with the app** in `lib/` (pinned to the versions used before: 2.5.1, 3.8.2, 3.10.1), like Chart.js. PDF reports and the one-file zip backup now work with no internet at all. The CDN is only a non-blocking fallback if a local file is missing.
- **Fonts load without blocking.** The app appears immediately in the system font and swaps to the web fonts if they ever arrive.
- **Hang check before AI calls.** If the connection is on but silent, the first AI use now spots it in 3 seconds (a small request to gstatic.com, result trusted for 60 s) and goes straight to the offline choices, instead of waiting out the long AI timeout. A quick failure is left to the existing handling.
- Page load with a dead connection: never finished, now 0.5 s. Test: p28 (hung requests; onboarding, tabs, common-food logging, offline banner, save-for-later, real PDF and zip from the bundled libraries).
- Also found: logging a common food ("two boiled eggs") works with no internet (local database), as intended.

## v3.10.862 — Offline Mode: Banner, "Needs Internet" Notes, And Save-For-Later Meals

Pete Spence (travelling, 2 Oct): "I desperately need offline mode. We need to show an offline banner throughout time spent there. Non working items such as AI compare need a note... another function similar to manual / health connect that updates via sync when it comes back online."

The app already runs from the phone's own server, so offline here means **no internet**: logging, your library, history and charts keep working; the AI, food database and barcode lookup stop. What's new:
- **Offline banner** across the top of every screen for as long as there's no connection ("Offline — logging, your library and history still work. AI, food search and barcode need internet."), with a count of saved entries. Detection is not just the phone's Wi-Fi flag: when any request to the internet fails, the app checks for real, then re-checks every 15 seconds until it's back.
- **Internet-only features say so.** Verify across 3 AIs (all five places), the 3-AI estimate, AI brief and summaries, Ask AI, barcode scanning, AI ingredient search and AI recipe suggestions go grey with "· needs internet", and tapping one explains itself instead of failing. Food-database search still opens (recent scans and your library work) with a note.
- **Save for later.** A meal the local database can't recognise (common foods like "two boiled eggs" already log offline) offers "Save it for when I'm back online" or "Enter the macros myself now". Saved entries (text, and a photo up to ~900 KB) live in `mh_offline_queue`, so they are included in backups.
- **Sync on reconnect, with you in control.** When the connection returns the banner turns green with a **Review** button. Each saved entry goes through the normal AI preview and is logged only when you confirm it, on the **day and time you saved it** (a past day goes into that day's history). Cancelling logs nothing and leaves nothing behind. Nothing is ever logged unseen, in keeping with the strict-tracking rules.
- Not covered: PDF reports still need the PDF library from the internet the first time (CSV fallback exists), and Google Fonts fall back to the system font offline. A stopped local server is a separate, existing notice.
- Test: p27 (banner on every tab, guards, no AI calls offline, queue survives reload, reconnect, confirm keeps the saved time, past-day logging, cancel leaves no residue).

## v3.10.861 — Backups Carry Settings, An Empty Backup Can No Longer Replace A Good One, Missed-Day Dates Validated

Found by the new backup/restore test (p25) and the screens test (p26).
- **Same-day empty backup overwrote a good one.** After a browser wipe the app saved an empty-state backup over that day's good one, so the restore had nothing to restore. The server now refuses to replace today's backup with one under half its size (`kept-existing`).
- **Settings weren't in the backup.** The full backup now includes your `mh_*` settings (excluding caches, logs, debug and anything key/token/secret/password-like) and a restore applies them.
- **Missed-day logging accepted nonsense dates** (not a real date, future, or today). It now checks format, real calendar date, not future, not today.
- Covered with no bugs found: labs, Insights, chat logging, demo mode, carer.html. Not testable here: PDF output (jsPDF loads from a CDN the sandbox can't reach), camera, voice, iOS, real notifications.

## v3.10.860 — Symptom Scores Reach History, And "Today" No Longer Slips A Day After Midnight In BST

Found by the new symptoms/strength/history test (p23) and clock-change test (p24).
- **Symptom scores never reached history.** They were only copied across while today's entry already sat at the top of history, which is almost never true because history is written at rollover. So Patterns, symptom trends and reports never saw a single score. The rollover now carries the day's scores into that day's history entry (and into an existing entry if there is one).
- **Wrong day between 00:00 and 01:00 in British Summer Time.** 16 places built "today" with `toISOString()`, which is UTC and so gives yesterday for that hour: phase and condition history entries, the export reminder, manual-entry template dates, report date ranges, notification keys, the calendar heatmap. They now use a local-date helper (`localISODate`). p24 checks both clock changes (25/10/26 and 28/03/27) and the BST hour.
- Covered with no bugs found: treatments (log, note, delete), routine → strength log → server CSV → restore, Resistance activity credit, History screen.

## v3.10.859 — Recipes: Hand-Typed Ingredients Log Correctly, Steps Survive A Restore

Found by the new recipes persona test (p22).
- **Logging a recipe inflated oils and fats.** An ingredient typed in by hand has macros for one portion but no weight. Logging invented "100g × your share", and the pure-fat safety check then trusted that made-up weight: 120 kcal of olive oil logged as 450 kcal, 50g fat. Ingredients without a weight now log as "1 portion" (or "0.5 portions"); ingredients with a real weight still log in grams.
- **Recipe steps were never backed up.** `recipes.csv` had no column for them, so after a browser wipe the recipe came back with ingredients and no method. Steps are now saved (new `steps_json` column; older 8-column files still restore). Pipes in ingredient names, notes and steps are escaped rather than replaced with "/".

## v3.10.858 — Fresh Installs Now Get The Update And Merge Jobs Automatically

Pete Spence's phone runs three cron jobs (watchdog every minute, GitHub auto-update at :05/:35, `update_health.py` every 30 minutes). The launcher's `provision.sh` only ever created the watchdog line, so a fresh install never got app updates or the 30-minute merge. On startup, in Termux only, the server now adds whichever of those two lines is missing and installs `mh_autoupdate.sh` (now kept in the repo) if absent. Existing lines are never changed or removed, a commented-out line doesn't count as present, and the check is a no-op outside Termux. No launcher rebuild needed. Test: p21 (fresh, already-complete, watchdog-only and commented-out crontabs).

## v3.10.857 — Server Merges Health Connect Data Itself (No Cron Needed)

The launcher drops `health_connect_export.json` into the inbox every 30 minutes, but merging it into `combined.csv` relied on a separate cron job that a fresh install does not necessarily have (the launcher's `provision.sh` only schedules the server watchdog). The server now checks the inbox every 60 seconds and, when a Health Connect export is new or changed, runs the Health Connect merge itself. It runs that one extractor only, never sweeps the rest of the inbox, waits if a sync is already running, and does nothing if the file hasn't changed. An existing cron job just becomes a harmless second path. Test: p20 (fails without the watcher, passes with it).

## v3.10.856 — Manual Sleep Correction Sticks, SpO2 Rounded, Midnight Rollover While Open

**Manual correction overwritten (Pete Spence: "sleep still stuck, even though I altered via manual").** Two real holes, both found by reproducing it. (1) Every full sync archived `manual_entry.json` into `inbox/old/`, so a correction saved while a sync was already running was moved away before it was applied, and the Health Connect value came back; if the field-attribution file was ever lost, the device value then won outright. The file now stays in the inbox, is re-applied (manual first) on every run, and is included in the 7-day backups and `--restore`. (2) A manual save during a running sync used to say "will be picked up" but nothing picked it up. It is now queued and runs the moment that sync ends. Test: p19 (fails on the old code, passes now).

**SpO2 showed 95.47619047619048%.** The Trends day list and the SpO2 card now round to one decimal (the list's shared formatter, so HR, HRV and calories are covered too).

**App left open past midnight.** The day only rolled over when something redrew the dashboard, so a phone resumed next morning could still show yesterday's meals. It now checks on becoming visible, on focus, and every minute, through the existing single rollover path. Test: p18 (also covers 1/5/40-day gaps, no duplicates, empty days).

## v3.10.855 — Zepp/Amazfit Export Now Opens Without ZArchiver Or pyzipper

Found by replaying Pete Spence's real exports (private test `p16_real_exports.py`).

- Zepp's "Export your data" zip uses WinZip-AES encryption. Python's own zip reader cannot open it ("That compression method is not supported"), so the extractor's `--password` / `ZEPP_PASSWORD` option never worked on a real export, and the in-app password box (`/extract-zepp`) needed the optional `pyzipper` package, which `setup.sh` installs with its errors hidden - a silent failure on any phone where that install fails.
- New `extractors/_winzip_aes.py` reads these zips with the standard library only (uses `cryptography` if present for speed, otherwise a built-in AES). The Zepp extractor uses it, and `/extract-zepp` falls back to it when `pyzipper` is missing. Wrong password -> clear "password is wrong" message; tampered/corrupt data is refused; extraction never writes outside the inbox.
- Verified on the real Zepp export: 202 days (activity, sleep, heart rate, body), both direct and through the in-app password flow.
- New `p17_winzip_aes.py` (public AES test vectors, round trip, wrong password, tamper check) runs everywhere. `p16` also replays real Withings/RingConn (826 days; weight, HRV, SpO2 and body-fat agree 100% with the phone's own result) and, when `MH_ZEPP_PASSWORD` is supplied for a run, the Zepp zip.
- Observation, unchanged: RingConn days with two sleep sessions keep only the longest (by design), so a nap or split night is dropped.

## v3.10.854 — Self-Check And Error Log (Stage One Of Self-Monitoring)

- **Error capture:** the app records uncaught JavaScript errors and unhandled promise rejections, de-duplicated with counts, first/last seen and app version. They are reported to `data/error_log.json` on the phone. Messages are truncated and long digit runs removed, so no health values are kept.
- **`selfcheck.py`** (also `GET /selfcheck`): checks `combined.csv` integrity and freshness, the pipeline log (errors/warnings this week, ignoring normal "no export for a device you don't own" noise), recorded app errors, and backup age. Result is **Nothing to worry about / One to know / One to watch**, written to `data/selfcheck.json`.
- **Settings → About → System health** shows that headline plus the top three items in plain English.
- `error_log.json` joins the backup rotation and `--restore`.
- New persona test `p15_selfcheck.py`. Checked against the real 830-day backup: no false alarms (only "newest data is 5 days old", which was true of that backup).

## v3.10.853 — Supplements Fixed; Reports, Themes, Routines Verified

Found by the new persona tests `p13_reports.py` and `p14_stack_themes_settings.py`.

- **Supplement periods:** the Add/Edit supplement form stored its selected periods in a hidden field whose value was broken by its own quote marks. Adding a supplement and pressing Save without tapping a period button, or opening Edit and pressing Save, stored the period as `[` — the supplement then vanished from every checklist. Fixed (and the name/dose/tablets fields are now quote-safe too).
- **Supplement restore:** the app wrote supplements to the phone with 6 columns (including tablets) but restored them expecting 5, so after a browser wipe every supplement came back in the wrong period and inactive ones came back active. Both sides now agree; old 5-column files still load. A `|` in a name is saved as `/`.
- Removed a leftover hard-coded "target 92-93kg" from an unused assistant helper.
- Verified, no change needed: every Reports range and builder for no-data / 45-day / GBM users (no NaN, no one else's personal text, no GBM-only sections for other conditions), the treatment progress report file, all 5 base × 4 visual themes (readable text), routines and strength log restore after a wipe, and poking every Settings dropdown/toggle.

## v3.10.852 — Manual Entry And CSV Import Tell The Truth

Found by the new manual-entry persona test (`p12_manual_entry.py`).

- **UK dates** (05/10/2026, 5-10-26, 05.10.2026) in an uploaded CSV were reported as "Uploaded" and then silently dropped by the pipeline. They are now converted; a date that can't be read (31/02/2026) is reported by name.
- **Excel-style files** now work: semicolon or tab separators, decimal commas (70,6), quoted thousands ("6,007"), capitalised/padded headers ("Date, Weight").
- **Long histories**: anything over 400 rows was refused outright. The app now uploads in batches, so a year or two of Apple-Health-style daily data goes in one go.
- **Out-of-range values** (a 700 kg weight, a 2031 date) used to be told "Saved" and then quietly discarded by the pipeline. The server now checks at save time and the screen says exactly what was NOT saved and why; valid fields in the same entry are still saved.

## v3.10.851 — Library Restore No Longer Loses Detail

Found by the new library persona test (`p11_library.py`).

- The library copy kept on the phone (`library.csv`) only held 10 columns. After a browser wipe, every restored food lost its fibre, polyols, categories, use count, sat fat, sugars, salt and other extras.
- A food whose name contained a `|` split into extra columns and vanished on restore.
- Names are now escaped, and all other fields travel in an 11th `extra` column. Old files still load.

## v3.10.850 — Device Setup Now Survives A Lost Browser Or Phone

Raised by Pete Spence: where does extra device/extractor setup live, and is it backed up? It was not.

- **Custom devices, the retired list and file patterns** used to live only in browser localStorage. They now live on the server in `data/devices.json` (browser copy is just a cache). Existing browser-only setups are uploaded automatically the first time Settings opens.
- **Device precedence** is restored from `pipeline_prefs.json` when a browser has none stored, so a wiped browser no longer shows defaults (and then overwrites the real order on the next reorder).
- **Backups** now also take `pipeline_prefs.json`, `devices.json` and a zip of any user-written extractors; `update_health.py --restore <file>` restores each.
- **User extractors**: drop `<device>.py` in `data/extractors/` (inside the backed-up data area). It is run for that device, beats a built-in of the same name (logged as a warning and flagged in Settings), and a non-built-in device is added to every precedence list at lowest priority.
- **File patterns** (Settings → Device Precedence → 📁): "file name contains X (and ends .ext)" teaches the Downloads sweep which files belong to a device, e.g. when a maker renames its exports. Built-in rules are unchanged and are checked first.
- New persona test `p10_devices.py`.

## v3.10.849 — Typing A Plain Meal Now Logs It

Found by persona p09 (meal logging, AI stubbed):
- **A bare two-food phrase such as "chicken breast and rice" was hijacked into a meal-SUGGESTION request, not logged.** For a new user with an empty library the app answered "Your library is empty - nothing to check against yet" and the meal never reached the AI. A bare phrase now only counts as a suggestion request when at least one part is a generic category word (protein, meat, veg, carb...). "protein and pasta" and "meat and 2 veg" still work as requests (tested). Behaviour change to be aware of: "chicken and pasta" typed alone now LOGS a meal rather than suggesting one.
- **The AI was told "the user is on a strict low-carb, high-protein protocol" for every condition**, even a general user with a 150 g carb target. Now only for the ketogenic-based conditions; others are told to follow their own targets and not assume low-carb.
- p09 covers 3 conditions x 4 ways of typing a meal through preview, "Log it", Today totals and stored entry.
- Note for distribution: users on the default provider send every AI call through the developer's own Cloudflare Worker (per-device daily cap). Worth a decision before more people use the app.

## v3.10.848 — GBM-Only Content No Longer Shown To Everyone

Found by persona p08 (one user per condition, tapping real tabs):
- **GBM Monthly Summary and GBM Research Digest were visible on Reports for every non-GBM user.** The app hid them correctly, then the Reports layout-reorder code (`applyGenericOrder`) un-hid every section the user hadn't manually hidden, undoing it each time. It never showed for GBM users, which is why it went unnoticed. The condition gating is now re-applied after every reorder pass.
- **"GBM Protocol" patient-guide links** (dashboard guides row, first-run welcome box) now show for GBM only.
- Checked the other conditions: ketosis tiles / "Ketosis check" appear only for the keto-based conditions (GBM, epilepsy, strict keto, migraine, cluster headache); diabetes and recomp users get their own guidance note; no "seizure", "metformin" or developer-name leakage outside Settings.
- Unexplained, not reproducible: the weight tile once showed 69.8/69.9 for a typed 70 kg. Stored value was exactly 70.

## Garmin Extractor (server/pipeline only; UNVERIFIED against a real Garmin export)

- New `extractors/garmin.py`. Reads (a) a Garmin Connect "Export Your Data" zip (recognised by looking inside for `DI_CONNECT/`; hash-named zips are no longer mistaken for Zepp exports) - daily summaries (`UDSFile*.json`: steps, distance, active kcal, resting/min/max HR) and nightly sleep (`*sleepData.json`: deep/light/REM/awake; sleep_duration = time asleep); and (b) `garmin*.json` wellness files in the existing parser's two schemas.
- `server.py` sweep moves those into the inbox; the Garmin check runs before the Zepp numeric-prefix check on purpose.
- `hr_resting` added to the Garmin source fields. The "No Garmin pipeline extractor" info line is gone.
- Written from known schemas, not a real export: every lookup is tolerant (missing/odd keys leave that metric blank, never crash). Drop the first real Garmin export into the personas fixtures and adjust aliases.
- Persona p07 (hash-named zip in Downloads, plain JSON, garbage zip). Real 830-day history re-verified unchanged.

## Pipeline Fixes From Persona Testing (no app version bump; server/pipeline only)

Found by running fake single-device, two-device and messy-data users through a fresh install:
- **Manual entries were silently ignored on any new install.** `manual.py` lived only in `app/extractors/` outside git ("copy it there by hand"). Moved into the repo's `extractors/` and always preferred, so `git pull` is enough and field-list updates (like `hr_resting`) actually reach the phone.
- **Withings, RingConn and Amazfit extractors now ship in the repo** as a fallback. An existing `app/extractors/<device>.py` still wins, so a working install never changes on `git pull`. Health Connect and Manual always use the repo copy.
- **Garmin / Manual no longer log a scary "No extractor found" warning on every sync** (Garmin logs an info line pointing to CSV import; it has no pipeline extractor).
- **Future-dated rows (e.g. year 2999) are rejected** instead of being stored at the end of every chart.
- **A stray null/number inside a Health Connect export crashed the extractor**; non-dict entries are now skipped.
- Verified against the 27 Sep backup (830 days): pipeline output unchanged.
- Known quirk, left as is: clearing a manual value does not release that day back to device data.
- New personas p04 (single-device), p05 (sleep conflict/manual precedence), p06 (messy data, 45-day gap).

## v3.10.847 — Chart.js Ships With The App

- Chart.js 4.4.1 now bundled in `lib/chart.umd.js` and served by a new `/lib/` route in server.py, so charts work offline and on a brand-new install with no internet. CDN kept only as a second chance.
- Route serves only `.js` files that exist in `lib/` (basename only, so path traversal returns 404).
- jsPDF / JSZip still load from CDN; both already degrade gracefully (CSV report, separate-file backup).
- `tests/personas/p03_charts.py`: verifies real Chart.js loads and the lib route is safe.

## v3.10.846 — Feet/Stones Input Fix Found By New-User Testing

- **Fixed:** typing a height as `5.6` (5ft 6in) was read as 5ft **60** inches = 304cm, giving a new user a ~3,570 kcal daily target with no visible error. Digits after the point are now read literally as inches (5.6 = 5.06 = 5ft 6in; 5.10 = 5ft 10in). Same fix for stones: `12.10` was read as 12st 1lb, now 12st 10lb. Label now shows `5.6 = 5ft 6in`.
- New `tests/personas/` harness: fresh server + empty data + headless Chromium. p01 walks the setup wizard across 6 profiles/units/conditions; p02 checks unit parsing. Both pass.

## v3.10.845 — Health Connect Sync-Age Indicator

- New server route `/sync-status` reports when the launcher last delivered a Health Connect export (newest `health_connect_export*.json` in inbox or inbox/old).
- Settings → About now shows "Health Connect sync: ✅ 12 min ago", or a ⚠️ with plain advice if nothing has arrived for over 6 hours. Catches a silently stalled background sync (e.g. 1 Oct, 02:01–12:00) without guessing at battery settings.
- Fixed: server.py was missing `import time`.

## Launcher v1.5.1 (versionCode 15) — Battery Notice Softened

- Banner now reads "Sync may be limited by battery settings" and the dialog says Android reports an app *may* be limited, and that it can be ignored if already allowed in the phone's own battery settings (HyperOS can disagree with Android's exemption list).
- New "Don't remind me again" button (stored in launcher prefs).
- Removed Xiaomi Autostart advice (not every phone has it); generic tip now points to Settings > Apps > Battery usage > Allow background usage.
- Removed the "Battery list / Termux" button (dialog has three button slots).

## Launcher v1.5 (versionCode 14) — Battery / Background-Running Guidance

- New orange banner on the launcher screen when MaxedHealth Sync or Termux is battery-restricted. Tap for a plain explanation, manufacturer-specific tips (Xiaomi/Redmi/POCO, Samsung, other) and buttons to allow background running or open the battery list.
- Auto-open of MaxedHealth is held while the explanation is showing; the check re-runs on return from settings.
- Onboarding battery step now explains what the Android prompt is for.
- Why: on 1 Oct Health Connect returned no data 02:01-12:00 until the launcher was opened, consistent with background killing. Built but not yet tested on-device.

## Launcher v1.4.1 (versionCode 13) — Grant Screen Now Actually Offers The New Permissions

Pete Spence: "Health connect never offered anything." Cause (mine): v1.4 made `hasAllPermissions()` check only the original seven so an upgrade could never stop a working sync, but the "Grant permission & sync now" screen used that same check to decide whether to open Health Connect's permission screen at all. It saw the seven granted, said "already granted", and never asked for the three new ones. Fix: new `hasEveryPermission()` (core + extras) for that screen only; the background service still gates on core. The screen also now syncs as soon as the core seven are granted rather than demanding every optional one. Workaround on v1.4: Android Settings → Apps → Health Connect → App permissions → MaxedHealth Sync.

## v3.10.843 — Launcher v1.4: Far More Health Connect Data, Resting HR Column, Pass-Through Extractor

Pete Spence asked whether we use every metric Health Connect offers ("Health Connect users only would want as much information as possible"). We used seven; this adds the rest that make sense, in one batch.

**Launcher (APK v1.4, versionCode 12):** now also reads distance, resting heart rate, total calories (written as `calories_passive` = total − active), min/max heart rate, min/max HRV and SpO2, and, for the night that resolved to a single sleep figure, deep/light/REM/awake minutes, bedtime, wake time and sleep efficiency. Stage totals use the SAME source choice as the sleep total (one source; or all if devices recorded separate periods; or the preferred device only if two recorded the same night), so deep+light+REM always agrees with `sleep_duration`. Exercise sessions and BMR were deliberately left out: sessions need their own design, and the app already calculates BMR itself.

**Safe upgrade:** the three new permissions are optional. The background sync's gate (`hasAllPermissions`) still requires only the original seven, and each new read is skipped unless granted and wrapped in try/catch, so installing over v1.3 cannot stop a working sync. The new ones appear the next time the Health Connect permission screen is opened ("Grant permission & sync now").

**Phone-side extractor (superseded by v3.10.844 — no copy needed any more):** `extractors/health_connect.py` lives outside the git repo on the phone (`app/extractors/`). As of the 27 Sep backup it hand-listed four fields and dropped everything else, so HRV, SpO2 and active calories added on 30 Sep may never have reached combined.csv. The repo now holds a pass-through version (`extractors/health_connect.py`); copy it over the phone's one. See apk/README or the release note.

**Pipeline:** new `hr_resting` column (ALL_FIELDS, METRIC_FIELDS['hr'], validation 20–200, manual entry list, server FIELD_NAMES); `SOURCE_FIELDS['health_connect']` widened; validation ranges added for `distance_m` and `calories_passive`. Web app: Resting HR row in Activity & Vitals, import/parse and manual-entry registry.

## v3.10.842 — Manual Always Wins; A Source Can Correct Its Own Earlier Value

**Manual is no longer a rankable source.** Pete Spence asked whether manual needs to be position 1 everywhere. It did, and the Settings editor was quietly undermining that: it appended "Manual" to the bottom of every precedence list except weight (where it sat 2nd, under Withings) and sent all lists to `pipeline_prefs.json`, so a saved order would have made a typed-in correction lose to Health Connect. `get_precedence()` now forces `manual` first for every metric regardless of what was saved, and the editor no longer lists Manual (a one-line note says it always wins; it is also gone from "Manage devices").

**Same-source correction.**

The 13h32m for 1 Oct survived every later Health Connect sync, including ones from the fixed v11 launcher. `merge_with_precedence` only overwrote a field when the new source *outranked* whatever set it (`<`), so Health Connect re-reporting its own field was a tie and was ignored. Changed to `<=`: the same source's newer reading wins; lower-priority sources still cannot override higher ones and manual still outranks everything. Checked with four cases (HC corrects HC, HC cannot beat manual, ringconn beats HC, HC cannot beat ringconn). Needs `git pull` on the phone.

## v3.10.840 — Device Precedence Reorder Bug Fixed (Real Root Cause), Manual Update-Check Button, Launcher Distribution Overhaul

Pete Spence: "device precedence won't reorder, it keeps coming back open on screen and in position 1." Took real investigating to find — every reorder mechanism involved (including device precedence's own drag-reorder) turned out to be working correctly. The actual cause: an unguarded top-level `Chart.register(mhTodayHighlightPlugin, mhDataLabelPlugin)` call elsewhere in the file. When the Chart.js CDN load fails (blocked network, offline, flaky connection), the existing fallback swapped in a stub `Chart` object with no `.register` method — so the fallback itself threw, and because it was a top-level throw, it silently killed **all script execution for the rest of that page load**, not just charts. That included the code that reads back saved reorder/precedence state, which is why the section visibly snapped to position 1 and stayed open — it never got the chance to apply the saved order at all. Reproduced directly via a headless test that blocks only the Chart.js CDN request, which alone reproduced the exact symptom with zero reorder-code changes. Fixed by making the `onerror` fallback define a no-op `Chart.register`, and wrapping the real call site in `try/catch` regardless. See TECHNICAL.md's "Generic section reordering" section for the general lesson here — this class of bug (an uncaught top-level exception silently killing everything defined later in this file) can resurface anywhere a third-party script might fail to load.

**Also added, same session, at Pete Spence's explicit request ahead of a release:**
- **Settings → About → 🔄 CHECK FOR UPDATES button** — the PWA already checks for updates automatically via its service worker, but there was no way to check on demand. Button shows "Checking…", then either the existing update banner (if one's available) or a "you're on the latest version" toast, rather than looking like it did nothing.
- **Launcher APK now distributed from this repo's `apk/` folder** (`apk/MaxedHealth-launcher.apk` + `apk/version.json` + `apk/README.md`), replacing "handed to testers directly." The native launcher app itself gained a matching in-app update-check (`checkForNewerApk()` in `MainActivity.kt`, compares `version.json`'s `versionCode` against the installed build, shows a banner linking back to the folder) — see TECHNICAL.md for the full release process this now requires (bump `versionCode` in `build.gradle.kts`, replace the APK, update `version.json`, all three together).
- **Launcher's Health Connect button** (loading screen) changed from a 900ms-timed gear icon to a permanent labelled "Health Connect settings" button, then from 900ms to a 6000ms minimum display time after Pete Spence reported it still vanishing before he could tap it on a warm launch — 900ms genuinely wasn't enough time for a human to see, register, and tap the button, not just a tight margin.

## v3.10.839 — "7 Days" On Trends Was Only Showing 6

Pete Spence: "This is not 7 days of my data" — the Trends screen's 7-day view (and 30-day, and any other fixed window) was actually showing one fewer day than advertised whenever "Include today" was left off (the default, since an in-progress day can skew an average/trend line).

The cutoff date math was already correct — `now - 7 days` genuinely reserves a 7-calendar-day window including today. But today then got silently dropped by the separate today-exclusion filter that runs right after, and nothing compensated for that lost slot — so "7 Days" rendered as 6 (e.g. 23rd–28th, missing both the 29th and effectively one more day of real history than intended).

Fixed `getTrendsData()`: when today is going to be excluded (not `_trendsIncludeToday`, not `forceFullHistory`), the cutoff is pushed back one extra day so the window still shows a genuine 7 (or 30, etc.) days, ending yesterday rather than quietly shrinking by one. Verified directly: with today excluded, a 7-day window now returns 7 real dates ending yesterday; with "Include today" on, it returns 7 real dates ending today, unchanged from before.

(Investigated and ruled out as part of this: whether flat-looking SpO2/heart-rate values on the chart were a demo-persona data leak — confirmed the demo-persona generator never fabricates SpO2/HR/HRV/sleep data at all, only meals and weight, so that's not a route this bug could come from.)

## v3.10.838 — Routine Template kg/lbs Toggle Didn't Visually Update

Pete Spence: "Strength training won't let's me select lbs" — turned out to be specifically the kg/lbs toggle added in v3.10.836 to the routine create/edit template screen. The toggle was actually working correctly underneath the whole time — tapping "lbs" genuinely switched `_routineFormUnit` and converted every displayed weight — but `setRoutineFormUnit()` never updated the two buttons' own styling, unlike the two other kg/lbs toggles in the app (manual-log form, Apply Routine screen), which both explicitly restyle their buttons on switch. So "kg" stayed visually highlighted forever, making it look like the tap did nothing even though it had worked.

Fixed `setRoutineFormUnit()` to restyle both buttons on every switch, matching the pattern `setStrengthUnit()`/`setRoutineUnit()` already use. Verified directly: toggling to lbs moves the highlighted border/background from the kg button to the lbs button, and back again on toggling back.

## v3.10.837 — Portion Wasn't Pre-Filling When Re-Searching a Meal-Preview or Recipe Item

Pete Spence: "Portion not populating for edit" — tapping the 🔍 search icon on an "AI estimate" row in a meal preview (or a flagged recipe ingredient) to pick a proper match, then landing on the amount screen with "Enter grams" blank and "Enter amount above" still showing, even though the item clearly already had an amount (e.g. 470g).

Root cause: the item's existing `.amount` is stored as a display string almost everywhere in the app — `"470g"`, `"150ml"`, etc. — not a bare number, and the amount screen was assigning that string straight into `foodAmountGrams`, a `type="number"` input. Browsers silently reject a non-numeric value on a number input, so it just stayed empty — no error, no console warning, nothing to see wrong except the blank box.

Added `_fixingIngredientGrams()`, which pulls out the leading number regardless of whether `.amount` is already numeric or a unit-suffixed string, and used it in all three places the food-search amount screen tries to pre-fill from a "fixing" ingredient (Open Food Facts result, AI-estimate result, library result). Verified directly: `"470g"` → `470`, `"150ml"` → `150`, `"x1"` → `1`, a bare number passes through unchanged, and a missing/empty amount still correctly leaves the field blank.

## v3.10.836 — kg/lbs Toggle Was Missing From the Routine Template Editor

Pete Spence: "No lbs switch from kg?" — the routine create/edit template form added in v3.10.835 had no unit toggle at all, unlike the two other places weight gets entered (the Apply Routine screen and the manual "Log a workout" form), which both already have one.

Added a kg/lbs toggle to the routine template editor, right under the routine name field. It uses its own independent unit state (`_routineFormUnit`), deliberately separate from the one the Apply Routine screen and manual-log form share (`_strengthUnit`) — so switching units while building a template has no effect on what unit those other forms are showing, and vice versa. As always, weight is stored on the routine as true kg (`weight_kg`) regardless of entry unit; the toggle only changes how the numbers are displayed and typed while the form is open. Switching units converts whatever's currently on screen on the spot (60kg → 132.3lbs), rather than reinterpreting the same digits under a new unit. Reopening a routine to edit or duplicate it always shows kg first, since that's what's actually stored — never whatever unit was last selected.

## v3.10.835 — Routine Templates Can Now Carry Fixed Sets, Reps, Weight & Notes

Pete Spence's own request, with a real example: "Rowing, 40 x 60kg, Purple band 40-80kg / Rowing, 20 x 60kg, Purple band 40-80kg / Rowing, 10 x 60kg, Purple band 40-80kg" saved as part of the routine template itself, auto-populating when applied — not just an exercise name that pulls numbers from whatever was logged last time.

A saved routine's exercises were previously just plain names (`exercises: ['Rowing', 'Squats']`) — sets/reps/weight always came from `getLastLoggedSets()`, whatever was logged most recently for that name. Now each exercise in a routine template can carry its own fixed sets, each with reps, weight, and a free-text note (e.g. "Purple band 40-80kg") — set when creating or editing a routine, in the same per-exercise +/− row editor as before, now with per-set rows underneath each exercise.

**When applying a routine, three cases:**
- Only a template exists (no logged history yet for that exercise) → template pre-fills silently, no interruption.
- Only logged history exists (no template sets) → pre-fills from history, exactly as before.
- **Both exist** → doesn't guess. A small "📋 Template / 🕓 Last session" toggle appears under that exercise, defaulted to the template but switchable any time before logging — every switch re-derives cleanly from the original data, so nothing is lost going back and forth.

Notes carry all the way through: template → the Apply screen's set rows → `state.strengthLog` once logged → the Strength Training card's session summary → `strength.csv` (server backup) and the routines/strength backup-restore CSVs (a `note` column appended at the end of each, so older exported files without it still import correctly). The manual "Log a workout" form (outside routines) also gained a note field per set in the same pass, for consistency.

**Backward compatible:** existing routines saved before this change (plain-string exercise lists) are normalized transparently on load — they behave exactly as before (auto-fill from last session, no template chip) until edited and re-saved, at which point they pick up the new shape. Verified directly: built a routine matching Pete Spence's exact example, applied it with no history (went straight to template), logged it, then re-applied with both template and history now present (correctly offered the choice, switching both ways preserved the data) — and separately confirmed an old plain-string routine still loads and normalizes correctly.

## v3.10.834 — Demo Personas Get Fixed Themes; Bill Gets Real PEMFiT Branding

Second "shop window" request: every demo persona now has its own fixed, distinct look — base theme, accent colour, icon pack — instead of all 11 sharing one hardcoded Vital theme. Reused the app's own existing theme system entirely (Dark/Aurora/Carbon/Slate/Light bases, Vital/Pulse/Forge icon packs, custom accent colours) rather than inventing new CSS; every accent was run through the app's own dark/light contrast-safety check before being assigned, so nothing renders illegibly. Switching persona mid-demo now switches the whole look, not just the data.

Bill specifically gets real PEMFiT branding: exact colours sampled directly from the logo Pete Spence provided (orange `#f37122`, grey `#8b8c8e` tagline — not guessed), used as both his in-app theme accent and his demo report profile's branding colour, with the actual PEMFiT logo embedded so his exported report PDFs carry it too.

**Also fixed along the way, found during this work:** switching theme/accent/icon-pack while in demo mode was writing straight to the real account's localStorage keys (`mh_theme`, `mh_custom_accent`, `mh_icon_pack`, and the org-branding keys `mh_org_logo`/`mh_org_name`) with **none of them captured or restored** by demo mode's snapshot/exit/abandoned-session-recovery safety net — the exact same class of gap that caused the v3.10.830 lab-results leak, just waiting to happen the moment persona theming existed to trigger it. All five fields are now captured in `startDemoMode()`'s snapshot, restored on a clean `exitDemoMode()`, and restored by `healFromAbandonedDemoSession()` on next load if the session was left running uncleanly — verified by direct execution testing (not just code review): entering Bill's demo, then simulating both a clean exit and an abandoned session, confirmed the real account's original theme/accent/org-logo values come back exactly, every time.

**Known limitation, not new:** exported report PDFs render the org logo into a fixed 16×16mm square (`buildProfileReportPDF`) regardless of the source image's aspect ratio — pre-existing behaviour, same as it would be for any real user's uploaded logo, not something this change introduced or attempted to fix. PEMFiT's wide wordmark will appear squashed in that one spot until that's addressed separately.

## v3.10.833 — Alphabetical Sort Now Ignores Leading Icons

Follow-up to v3.10.832: Pete Spence flagged that section titles with a leading emoji — "📐 Formulas & Technical Reference", "🩸 Lab Results + Log Panel" — were sorting by the emoji's Unicode codepoint rather than by the first real letter, landing them in odd spots instead of under F/L where someone scanning alphabetically would look for them. Added a small `_stripLeadingIconForSort()` helper (strips a leading emoji/symbol run and its trailing whitespace, for comparison purposes only) and wired it into both restore-strip sort comparators (`renderGenericRestoreStrip`, `renderDashboardRestoreStrip`). Display is untouched — pills still show their icon — only the sort comparison ignores it now.

## v3.10.832 — Collapsed Section Pills Now Alphabetical, Everywhere

Pete Spence's own request: the "Hidden: X + Y + Z" pill row that appears wherever collapsible sections exist (Settings → Manage/Customise/Data, Trends, Reports, Import, the Today dashboard) was ordering pills purely by "whichever order you happened to tap hide in" — which reads as random and made a longer hidden list (like the Settings → Manage screenshot that prompted this) genuinely hard to scan for the one you wanted back. Both restore-strip renderers (`renderGenericRestoreStrip`, covering Manage/Customise/Data/Trends/Reports/Import, and `renderDashboardRestoreStrip`, covering Today) now sort by the section's resolved label at render time — purely a display change, the underlying hidden-list storage and hide/show mechanics are completely untouched. Also alphabetized while in this area, per the same request ("anywhere they are"): Compare Metrics' group pills (Body Composition, Exercise, Lab Results, Nutrition, Symptoms, Treatment, Vitals & Sleep — was an arbitrary hand-written order) and per-item category chips on library edit forms (was insertion order). Left alone deliberately: Manage Categories' "Words" list already offers an explicit alphabetical sort option alongside its default match-priority order, and reordering that default would risk conflating display order with the real keyword-match priority `detectFoodCategory()` depends on; "Next meal idea"'s category pills were already alphabetical (Snack pinned first by design, as a distinct suggestion type, not a category).

## v3.10.831 — Demo Picker Visual Polish (Shop-Window Pass, Part 1)

First piece of the "make the demo a proper shop window" work, scoped specifically for an in-person pitch (phone screen broadcast to a room, narrated live) rather than a generic redesign — so this deliberately focuses on the very first thing anyone in the room sees: the demo persona picker and the always-visible demo banner. The picker was previously hardcoding a fixed dark palette (`#1c2230`/`#151a23`/etc.) regardless of the active theme, making it look like an unstyled dev screen bolted onto an otherwise polished app; now fully theme-aware via CSS variables, so it matches whatever visual theme is actually selected. Each of the 10 personas now gets its own icon for fast visual scanning on a small screen from across a room, and cards show only the short tagline rather than the full bio paragraph — a wall of text per card was unreadable at a glance on a mirrored phone display; the full bio remains available for anyone exploring solo later. The demo banner (visible throughout the whole live session) got a small legibility bump — slightly bolder, slightly larger — so it reads as a clear, intentional status rather than fine print. Deliberately left the demo entry point's location alone (Settings → Manage → Try Demo Mode) per Pete Spence's own call — navigation speed isn't the actual problem when the demo gets queued up before the meeting starts.

## v3.10.830 — SERIOUS DATA-SAFETY BUG FIXED: Demo Data Could Overwrite Real Lab Results

Found live on Pete Spence's real device: after exploring the Alex demo persona, Alex's two lab panels (Pre-Block/Post-Block Check) were sitting in Pete Spence's actual Lab Results, not demo data. Root cause: `healFromAbandonedDemoSession()` — the safety net that restores real data on next app load if demo mode was left active uncleanly (app closed/backgrounded/killed mid-demo, rather than tapping "Exit Demo") — restores every other captured field (treatment defs/log, symptom defs/log, report profiles, targets, condition, etc.) but was missing the line for `mh_lab_results` entirely. It was never added when Lab Results demo support was built (v3.10.824). `startDemoMode()`'s backup snapshot does capture real lab results correctly, and a **clean** exit (tapping "Exit Demo") already restored them correctly via `exitDemoMode()` — this only affected the abandoned-session recovery path specifically. Fixed by adding the missing `restore('mh_lab_results', backup.labResults)` line. If you were affected: your real lab results may still be recoverable from `mh_demo_backup` in localStorage IF it hasn't already been cleared by a subsequent app load (the healing function deletes it unconditionally after running, whether or not the restore was complete) — check immediately rather than opening the app further. Everyone should treat any Lab Results entered or reviewed shortly after exploring a demo persona as unverified until confirmed against source records.

## v3.10.829 — Real Bug: `updateDashboard()` Was Missing Its Own Closing Brace

The actual root cause behind v3.10.828's "fix" still failing on real-device testing (`_parseDDMMYY is not defined`, reported live from the demo site on Alex). Took a long, thorough investigation to actually pin down — static syntax checks kept passing, and the function genuinely looked top-level by every normal reading. The real story: `updateDashboard()` (the function that refreshes the whole Today dashboard) never had a proper closing brace of its own. Partway through its body, three unrelated things — the streak-milestone system (`checkStreakMilestone`, `STREAK_MILESTONES_KETO/GENERAL`), the shared `_parseDDMMYY()` date parser, and `checkTdeeStillAccurate()` — were sitting *inside* `updateDashboard`'s own scope, not at true top level, before the rest of `updateDashboard`'s own code (the ketosis badge, phase name, etc.) continued on regardless. This went unnoticed because everything that called `_parseDDMMYY`/`checkStreakMilestone` from *inside* `updateDashboard` still worked fine (same accidental scope) — it only broke for code *outside* `updateDashboard` trying to reach them, which is exactly what `getDrillData()`'s lab-marker branch (new in v3.10.823) started doing. Confirmed via direct execution testing (not just static syntax checking) before and after the fix. Fixed by moving the three misplaced declarations out to genuine top-level scope, right after `updateDashboard()`'s real closing brace. No behavioural change for anything that was already working — this was purely a scoping defect that only became reachable once lab-marker Compare Metrics needed to call `_parseDDMMYY` from outside `updateDashboard` for the first time.

## v3.10.828 — Real Bug: Compare Metrics Couldn't Actually Compare Sparse Lab Panels

Found via direct testing: on the demo site, Alex's before/after lab trend looked broken in Compare Metrics — you could see each lab marker individually, but overlaying/comparing them showed nothing useful. Root cause: `openMetricDrill()`'s single-metric Deep Dive view was fixed back in v3.10.823 to default lab markers (and weight) to the "All" period, since real readings are infrequent and a 30-day default shows zero or one point almost always — but Compare Metrics never got the same fix, and Alex's two panels (39 days ago and 6 days ago) don't both fit inside the default 30-day window, so the older panel silently fell outside it. Fixed: selecting a lab marker (or weight) in Compare Metrics now checks whether it actually has data in the current period, and if not — but it does have data across all time — automatically widens to "All" with a toast explaining why, rather than leaving someone staring at what looks like an empty comparison. Only triggers the first time a sparse metric would otherwise show nothing; never overrides a period chosen deliberately for other metrics already on the chart.

## v3.10.827 — 10th Demo Persona: Bill, a PEMFiT Use Case

First of the three "All 3" follow-ups (persona → pitch doc refresh → visual polish, in that order). Added a 10th demo persona, Bill — 54, chronic lower back pain from years of physical work, no other condition being managed, started regular PEMF sessions eight weeks ago and wanted a proper way to see whether they were actually helping rather than going on how a given week felt. His story is carried entirely by Treatment Tracking: 7 PEMF sessions over 6 weeks logged against a self-tracked pain/sleep/mobility symptom trio, showing a genuine, gradual improvement — exactly the shape of evidence a real PEMFiT customer would want to see reflected back at them. Built specifically so the demo has a case that mirrors PEMFiT's own actual use case, not just a generic wellness persona, ahead of refreshing the PEMFiT pitch document next. No new mechanics — `showDemoPersonaPicker()` is fully array-driven, so Bill needed zero additional UI wiring.

## v3.10.826 — Sam Gets the Same Before/After Treatment

Second of the scoped follow-ups: Sam (self-directed strict keto, no medical condition — her whole bio is literally "does this hold up as a useful tracker for someone not managing an illness") upgraded from one static panel to a real baseline-vs-six-weeks-in pair, mirroring Alex's before/after pattern. Genuine early metabolic response shown — triglycerides and fasting glucose down, HDL up — the fast-moving early result that would actually make someone doing this off their own back want to keep checking. Doris and Karen remain single/light-touch panels for now (the "feature exists for ordinary users too" case, not active correlation) — candidates for the same upgrade if wanted later.

## v3.10.825 — Alex Gets a Real Before/After Lab Trend

Reasonable follow-up question: does any non-clinical demo persona show what it looks like for someone who just has their own bloods and wants to see how nutrition and training measure against them — not a monitored condition, just personal curiosity? Alex (recomp/training, no medical condition) was the natural fit — already the most metrics-driven persona (HRV, body composition, training load) — but only had one static panel. Upgraded to two: a pre-training-block check and a post-block check bracketing his three boot camp phases, with values that move plausibly with his known trajectory (HDL up, triglycerides down — a realistic low-carb response; creatinine up slightly from higher training load/muscle mass, not a kidney concern, eGFR stays comfortably normal). Now shows a genuine two-point trend, not a single snapshot, demonstrating the lab-trend features from v3.10.823 for someone with zero medical reason to be tracking bloodwork at all — just wanting to see if it's working.

## v3.10.824 — Demo Personas Get Real Lab Panels, Plus a Genuine Symptom-Tracking Bug Fixed

All 9 demo personas now carry realistic `labPanels`, each written to fit their existing story — John (T2 diabetic) shows HbA1c and lipids genuinely improving across 3 panels as weight comes down; Maria (GBM) shows liver function and CRP tracking her two chemotherapy cycles, with real dips during treatment and recovery between; Grace (T1 diabetic) gets a quieter, realistic quarterly HbA1c check rather than a dramatic arc; Priya (still struggling with adherence) and Tom (strong responder) get deliberately contrasting bloodwork — flat/unremarkable for Priya, comfortably-improving for Tom — matching the outcome contrast their bios already describe; Doris, Alex, Sam, Raj, and Karen each get a panel fitting their own non-dramatic, realistic story rather than padding for its own sake. The point: anyone exploring the demo can now see the trend chips, Compare Metrics overlay, and AI report trend narrative (all new in v3.10.823) actually working on realistic data, not empty for every persona.

Also fixed while in this code: a real, separate bug where every persona's symptom tracker (Priya's migraine log, Tom's cluster headache log, Maria's chemo symptoms, Raj's seizure tracking) silently showed nothing at all in demo mode — `loadSymptomDefs()`'s demo branch called a `generateDemoSymptoms()` function that was never actually written, falling through to an empty default list every time, while `saveSymptomDefs()` had a demo-mode guard that (correctly, in isolation) refused the write that would have populated it. Fixed by removing the guard, matching `saveTreatmentDefs()`'s own already-correct pattern — real account data was never at risk either way, since the snapshot/restore mechanism in `startDemoMode()`/`exitDemoMode()` already protects it independently.

## v3.10.823 — Lab Markers Are Now Real, Chartable Metrics

Follow-up to v3.10.821's Lab Results tracker, after the reasonable question of whether logged bloodwork actually *did* anything beyond sit in a list. It didn't — the AI report saw the latest panel and nothing else, and there was no way to see a marker move over time at all. Fixed properly: all 14 lab markers are now registered in `DRILL_CONFIG` (`lab_<id>` keys) exactly like weight, GKI, or any device metric, which means they're automatically selectable in **Trends → Compare Metrics** — overlayable against weight, treatments, GKI, carbs, anything else tracked — and open the full Deep Dive chart/stats view via a new **📈 View a trend** chip row in the Lab Results section itself (only shown for markers with 2+ real readings; a single value has nothing to trend against yet). Deliberately NOT forward-filled between readings the way body-composition metrics are — a lab value silently implied as "current" every day since the last draw would misrepresent how infrequent real testing is, so the chart shows honest gaps. The AI report context also gained a genuine trend summary (direction, magnitude, current in/out-of-range status per marker across all draws) alongside the existing latest-panel snapshot, so a report can now say a marker is climbing or falling, not just where it sits today.

## v3.10.822 — Non-Medical Side: Electrolytes, a Logging Streak, and Recipes From What You Actually Have

Second competitive-research pass, this time against general nutrition/fitness/habit apps (MyFitnessPal, Cronometer, Lose It, Streaks, Habitify) rather than medical trackers. Worth noting first: on barcode scanning and photo-based meal logging, MaxedHealth already beats the field — both are real (Open Food Facts lookup, AI photo/label parsing) and neither is paywalled, versus MyFitnessPal locking both behind Premium in 2024. Three genuine gaps found and fixed:

**Potassium & magnesium tracking** — extended the existing satFat/sugars/salt/iron field set (library edit form, Open Food Facts barcode/search lookups, `calcTotals()`) to include potassium and magnesium, both pulled automatically from Open Food Facts where available. Specifically relevant for anyone eating low-carb, where electrolyte management is a known real issue. While in this code, also fixed a pre-existing gap where reusing a saved-search library item silently zeroed out its satFat/sugars/salt/iron instead of reading the real stored values.

**General logging streak** — new `calcLoggingStreak()`, deliberately separate from the existing ketosis-adherence streak (which correctly resets the moment a day goes over the carb ceiling, even on a perfectly-logged day). This one counts consecutive days with anything logged at all, rewarding the more basic — and often harder — habit of just showing up, the way dedicated habit-tracker apps do. Shown as a small line under the main dashboard badge, in Your Journey's stats, with its own milestone celebrations (7/14/30/50/100/200/365 days), and now available to the AI report as a distinct figure from carb-ceiling adherence.

**Recipe suggestions from your own library** — new "📦 Suggest a recipe from what's in my library" option (Library → Try Something New). Deliberately not a paste-a-URL importer: this app has no backend fetch/CORS-proxy path, so scraping arbitrary recipe sites client-side would fail on most of them. Instead, the AI is handed real ingredients already in the library (with real macros) and composes a recipe from actual stock, sized to current macro targets — reuses the exact same generate → parse → "Create Recipe" pipeline already built for the general recipe-discovery mode.

## v3.10.821 — Lab Results Tracker: Real Bloodwork Now Has a Home

MaxedHealth previously had no way to log real lab-drawn bloodwork anywhere, despite being comfortable with device-derived biomarkers throughout — a gap found during a competitive-research pass against premium health-tracking apps (several offer PDF lab-report auto-parsing; this ships the underlying data model and manual entry first). New **🩸 Lab Results** section in Settings → Manage: a growing list of dated lab panels (not daily-reset, matching the Treatment Tracking pattern rather than Symptom Tracking's, since a blood draw is a periodic event, not a daily one), each panel logging only the markers it actually reported across 5 groups — Lipids, Liver Function, Glucose & Metabolic, Inflammatory & Blood Count, and Kidney Function (14 markers total, each with its own reference range) — nothing assumed or defaulted for markers left blank. Panels can be edited or deleted, are included in full backup/restore and demo-mode's real-data snapshot/restore, and the single most recent panel (regardless of report period, since draws are sparse) now appears in the AI report's context, with any out-of-range marker flagged for discussion with the treating clinician — the prompt is explicit that this is informational, not a diagnosis.

## v3.10.820 — TDEE-Still-Accurate Nudge

Another competitive-research find: premium trackers prompt a TDEE recheck when real-world weight trend stops matching what the current goal + TDEE predicts. New `checkTdeeStillAccurate()`: once a manually-confirmed TDEE is 14+ days old, with at least 4 real weigh-ins in the trend window, compares actual weight change against what the active goal (Lose/Gain/Maintain) implies — flat when it shouldn't be, or moving the wrong way — and surfaces a one-time-per-14-days nudge bubble. Never auto-changes `mh_tdee` itself; purely a prompt to re-check.

## v3.10.819 — Real GKI (Glucose Ketone Index) Logging

MaxedHealth could only ever infer ketosis compliance from logged food. New **🩸 Log a real reading** flow (from the Carb Zones tooltip) lets an actual blood glucose + blood ketone meter reading be logged directly, computing a real GKI (glucose ÷ ketones × 100) stored per-day alongside the rest of that day's history. Full integration: today's reading shown color-coded (therapeutic ketosis <2.0 green, <3.0 yellow, else red) right where the diet-inferred estimate already lived; a new GKI Trends card and Compare-Metrics entry; and a new AI-report context line explicitly distinguished from the existing diet-inferred figure, so the two are never conflated.

## v3.10.818 — Water Target Celebration Now Fires From Every Logging Path

The "target reached" toast only ever fired from one of three ways to log water (quick-add buttons), not the custom-amount or voice-logging paths — so hitting the day's target via either of those went uncelebrated. Refactored all three into a shared `_addWaterAndCelebrate()`, so the celebration (and its once-per-day guard) now fires consistently regardless of how the water was logged.

## v3.10.804-807 — Wellness Balance Card: From "Wrong" to "Explained" to Actually Fixed

Reported as the Activity/Vitals scores looking wrong against a wearable app's own same-day numbers. Three passes, each one real: v3.10.804 clarified the card's subtitle was a 7-day average, not "today" (a labelling fix, not the underlying issue); v3.10.805 added a **Wellness Score Debug** panel (Settings) so the raw data behind each of the 4 scores could be checked directly instead of guessed at; v3.10.807 (Pete Spence's own follow-up — "the user specified query period should be reflected, be it custom, 30 days or whatever") fixed the actual bug: Sleep/Activity/Nutrition ignored Trends' own Today/7D/30D/All/Custom selector entirely and always averaged a hardcoded last-7-real-days window. Now they average whatever period is currently selected, with a dynamic subtitle stating the real day-count found. Vitals' HRV baseline deliberately stays a fixed last-30-readings window regardless of period (a personal baseline needs real history a short custom range may not have) — documented explicitly so it isn't mistaken for a leftover bug. The Debug panel was updated to mirror the same selected period, so it's checking the same question the live card answers, not a different one.

## v3.10.808-811 — Copy Diagnostics for Claude Extended, Then Two Real Bugs Found In It

Extended the existing combined-diagnostics export to include Wellness Score Debug and the Sync Wearable Data log as new sources (v3.10.808), then moved Wellness Score Debug itself into Advanced Tools with its own icon (💗, v3.10.809) for consistency with the rest of the debug-tools family.

Reported: "Copy diagnostic for Claude isn't maintaining state." First pass (v3.10.810) found and fixed a real but different bug — `renderDiagnosticsList()` was rebuilding its checkbox list from scratch on every expand/collapse, silently discarding the user's own tick/untick choices back to computed defaults. Reported as unresolved. Root cause (v3.10.811) turned out to be the section's own collapsed/expanded state, not its checkboxes: **Copy Diagnostics** was missing from the load-time collapse-state array that runs at app startup, so it silently reverted to open on every app reopen regardless of what was left last time — see v3.10.817 below, where 6 more Advanced Tools sections turned out to have exactly the same gap.

## v3.10.812 — Removed Orphaned Duplicate `#dupeScanBanner`

Leftover from an earlier Library Tools split: two `#dupeScanBanner` elements existed in the DOM (a duplicate ID), one live next to the Find Duplicates button, one an orphaned dead copy above the library search bar with no JS reference anywhere. Removed the dead one. Found via a routine health-check sanity run.

## v3.10.813 — Recipe Drafts Now Autosave

Reported: recipe editing "often loses the screen if it times out" — a screen timeout or Android backgrounding the tab silently discarded an in-progress recipe, since `_recipeIngredients`/`_recipeSteps`/`_editingRecipeId` lived only in memory with zero persistence. New `mh_recipe_draft` localStorage key, written on every totals update, offered back ("Looks like '\<name\>' didn't get saved last time — resume editing it?") on next app open, and cleared on both a successful save and an explicit cancel.

## v3.10.814 — "+ Add Food" De-elevated

Previously sat alone in its own row at the top of Food Library, more prominent than its actual frequency of use justified. Moved into the Library Tools row alongside Batch voice-build/Find Duplicates/Auto-Categorize/Preview Categories.

## v3.10.815 — Library Edit Forms Now Lazy-Built (Real DOM-Weight Fix)

Every library item's full edit form (name, portion, category chips, 6 macro inputs, AI-verify panel, More Info reveal, delete/cancel/save) was being built into the DOM for **every item on every render**, regardless of whether it was ever opened — a genuine, growing performance cost as the library grows, reported as "the page becomes more unmanageable when unhidden." Refactored into `buildLibraryEditFormHtml()`, called lazily only the first time a given item's edit form is actually opened, with the shell emptied again (`innerHTML = ''`) on close so only one form ever carries real weight at a time.

## v3.10.816 — Health Connect Data Not Appearing: Cross-Origin Caching Root Cause Found

Long-running investigation ("still no data from Health Connect for yesterday") that ruled out, in order, with direct verification at each step: the Python extraction pipeline (confirmed correct via `csv.DictReader` and `awk` field-counts directly against the real file), a duplicate/stale `combined.csv` (confirmed only one file exists via `find`), server-side caching (`server.py` reads the file fresh on every request, confirmed via code read and direct `curl`), and service-worker caching (`sw.js` explicitly uses `cache: 'no-store'`, confirmed via direct read).

Actual root cause: `autoImportCombinedIfStale()`'s fetch to the local pipeline server (`http://localhost:5757/combined`) is **cross-origin** relative to the app's own page origin — and a service worker only ever intercepts same-origin requests within its scope, so `sw.js`'s `no-store` handling had never applied to this request at all, despite looking airtight. Left exposed to the browser's own default HTTP cache heuristics, which could silently serve a stale `/combined` response across a PWA suspend/resume cycle. Fixed on both ends: the fetch itself now sets `cache: 'no-store'` explicitly, and `server.py` also sends `Cache-Control: no-store, no-cache, must-revalidate` + `Pragma: no-cache` on `/combined`, so no cache layer anywhere can serve it stale regardless of client-side fetch options.

Separately, and likely the actual original trigger for the missing-data symptom before this fix: `update_health.py` (unversioned, see below) was found to archive the entire inbox — including a genuinely unprocessed Health Connect export — on a single-device run that had nothing to do with Health Connect at all.

## v3.10.817 — 6 More Advanced Tools Sections Missing Their Startup Collapse-State Registration

Same bug class as v3.10.811 (Copy Diagnostics), found by auditing every Advanced Tools section against both collapse-state arrays rather than assuming the earlier fix had caught everything: **Log Mutation Debug, Save Debug Trace, Settings Change Log, JS Error Log, Manual Entry Log,** and **Label Read Log** were all correctly registered in the "full audit sweep" array (runs on every Manage/Customise tab switch) but missing from the separate array that runs once at app startup — so all 6 silently reverted to their HTML-authored default (open) on every fresh app open, regardless of what was left last time. All 11 real Advanced Tools sections are now confirmed present in both arrays.

## Unversioned — `update_health.py`: Single-Device Pipeline Runs No Longer Archive the Whole Inbox

Real incident (28/09/2026): a Manual Entry save triggers `update_health.py --device manual`. No manual extractor exists, so that run yielded nothing — but `archive_inbox()` ran anyway on the way out, and it archives **every** file in the inbox unconditionally, with no concept of which device actually looked at which file. That swept a genuine, unprocessed `health_connect_export.json` straight to `inbox/old/` without it ever being extracted — `combined.csv`'s last real Health Connect row was stuck on the 27th, and nothing in the log called out that an unrelated file had just been archived unread. Fixed: `archive_inbox()` now only runs on a full pipeline run (no `--device` filter) — a single-device run has no business archiving every other device's untouched export.

## v3.10.777 — Scrolling Charts Opened on the Oldest Day, Not the Latest

Journey (weight), single-metric Deep Dive, and Compare Metrics charts all correctly size their scrollable area for long history (90D/All), but none of them ever moved the scroll position afterward — so any chart wide enough to scroll opened at `scrollLeft: 0` (the earliest tracked day) instead of the most recent one. Fixed in all three: after sizing the inner scroll width, `scrollLeft` is now set to the far end whenever the chart is actually wider than its wrap.

## v3.10.778 — Read-Aloud Fixed for Long/Paragraph Output

The shared `toggleSpeakText()` function (used by every 🔊 button in the app — chat replies, saved prompts, Reports → Ask AI, GBM Summary) spoke each answer as a single `SpeechSynthesisUtterance`. Two real, separate browser bugs bite that on genuinely long text:

- Chrome/Android's speech engine silently stops producing audio past ~10–15 seconds into one utterance. A partial workaround already existed (a pause/resume "keep alive" nudge, still in place), but it isn't reliable for something minutes long.
- Android's native TTS engine has a hard character cap per utterance (~4000 chars) — past that, `speak()` can fail to produce any audio at all, not just cut off partway. This is likely why GBM Summary (shorter) worked while longer Reports/saved-prompt answers didn't.

Fixed by splitting text into sentence-sized chunks (~200 chars) and queuing them to play back-to-back, staying safely under both limits regardless of which one was actually the cause on a given phone. Stop/start button behavior unchanged — tapping stop now cleanly halts the whole chunk queue via a cancellation token, not just the currently-playing sentence.

## v3.10.779 — Read-Aloud Added to AI-Suggested Recipe Cards

AI-suggested recipe cards (the "🍽️ Create Recipe from this" bubbles in chat) build their own custom HTML rather than going through the plain-text bubble path other AI replies use, so they never picked up a speak button automatically. Added one (`speakRecipeBubble()` / `_recipeSpeechText()`), reusing the same fixed, chunked `toggleSpeakText()` above — reads title, intro, ingredients, then numbered method steps, in the same order the card displays them. Cook Mode's separate step-by-step voice narration is untouched; each step is short enough that it was never affected by the two bugs above.

## v3.10.780 — Removed Dead Code: `generateDemoData()`

The original single-persona demo dataset generator, fully superseded when the multi-persona system (`generateDemoHistoryForPersona()`) was built, but never removed. Confirmed zero references anywhere (direct calls, string-based lookups) before deleting — ~15KB of a genuinely unreachable function.

## Native Launcher — Compile Fix, Reliable Health Connect Entry Point, Race Condition

Follow-up work on the native Android launcher app (separate from the web app version bumps above — this app doesn't share the same version numbering):

- **Real bug, mine**: `MainActivity.kt` referenced `TermuxBridge.runMhstart()` (added during the earlier server-timeout/retry fix) but the function was never actually written into `TermuxBridge.kt` — a genuine "said I fixed it, didn't" compile error. Added it, following the same `RUN_COMMAND` pattern as `runProvisionScript()`, targeting `~/bin/mhstart` directly (it lives in Termux's own private storage, so — unlike `provision.sh` on shared storage — it's already executable and doesn't need the `bash <path>` wrapper).
- **Second real bug found alongside it**: `MainActivity.kt` called `Intent(...)` in `findInstalledWebApk()` with no `import android.content.Intent` at all — would have been the very next compile error.
- **`shortcuts.xml` build failure**: `shortcutShortLabel`/`shortcutLongLabel` must be `@string/...` references — Android's resource linker rejects a literal string there, unlike almost every other XML attribute. Fixed by moving the labels into a new `res/values/strings.xml`.
- **The long-press shortcut itself turned out to be unreachable**: confirmed on Pete Spence's phone that HyperOS's launcher doesn't invoke static app shortcuts at all — no menu appears on long-press, on any app. Rather than depend on a launcher-specific gesture, added a plain tap-target gear icon directly on the loading screen instead, shown only when `HealthConnectBridge.isAvailable()` says Health Connect is actually usable on the device. The shortcut XML is left in place for launchers that do support it.
- **`isAvailable()` was stricter than the logic actually proven to work**: it required an exact match to `SDK_AVAILABLE`, while `HealthConnectTestActivity` (tested and working) treats anything that isn't explicitly "unavailable" or "needs a provider update" as usable. Loosened to match.
- **Edge-to-edge (Android 15 default) hid the gear behind the status bar**: fixed with a real 56dp top margin instead of small internal padding.
- **A genuine race condition**: tapping the gear opened Health Connect settings, but the coroutine already waiting to auto-open MaxedHealth itself didn't know the user had navigated away — it kept running in the background and fired a moment later regardless, colliding with the screen just opened (this is what "Site cannot be reached" right after tapping the gear actually was). Fixed by cancelling that pending job the moment the gear is tapped.
- **Added a 900ms minimum display time** before auto-opening MaxedHealth, only when the server was already running (the fast path) — without it, the loading screen (and the gear on it) could flash past in well under a fifth of a second, too fast to tap. Nothing added to the slow-start path, which already takes far longer than that.

---

## Native Android Launcher — Built and Working End-to-End

The single biggest onboarding blocker (every early tester hit the same wall — seeing/manually running Termux) is now solved. A native Android app (`com.maxedhealth.launcher`, separate Android Studio project) walks a new install through Termux, Termux:Boot, and Termux:API installation and permission steps automatically via Termux's `RUN_COMMAND` intent, with a single unavoidable manual step (a one-time clipboard paste inside Termux — Termux blocks external apps from writing `allow-external-apps` to its own settings otherwise).

- **Real bug found and fixed**: `RUN_COMMAND` requires its target to be executable, but a file staged on shared storage can never be marked executable — an Android filesystem limit, not a permissions issue. Fixed by having the launcher run Termux's own `bash` with `provision.sh` as an argument, rather than trying to execute the script directly.
- **A second, separate real bug found in `provision.sh` itself**: its crontab-restoring line piped `crontab -l | grep -v "mh_watchdog"` into the new crontab — on a genuinely empty crontab (exactly what a fresh Termux install has), `grep -v` on empty input exits 1, its normal "found nothing" signal, but under this script's `set -e` that silently killed the whole step before the actual watchdog line ever got added, leaving crontab empty with no error shown anywhere. Confirmed live: this is exactly what happened after Pete Spence's own Termux F-Droid migration — `crond` wasn't even running, and the self-healing watchdog had silently done nothing for hours. Fixed with a simple `|| true`.
- **Discovered along the way**: an existing daily-use MaxedHealth icon can be a Chrome-installed WebAPK, which gets its own separate storage from plain Chrome even for the identical URL — the launcher now finds and opens that specific installed app directly, falling back to a plain Chrome tab only if it's missing.
- Custom app icon (heartbeat/MH mark, adaptive icon set for Android 8+).

## Health Connect — Real Integration, Not Just a Plan

Built directly into the launcher (no separate bridge app, unlike an earlier plan documented in TECHNICAL.md — corrected there too). Reads steps, average heart rate, weight, and sleep duration from Android's Health Connect, writes them into the same pipeline inbox every other device uses, and folds into `combined.csv` via a new `extractors/health_connect.py`.

- **Real bug found and fixed**: originally mapped to `hrv` in `update_health.py`'s `SOURCE_FIELDS`/`DEFAULT_PRECEDENCE`, but what's actually read is average heart rate (`HeartRateRecord`), not heart-rate variability (`HeartRateVariabilityRmssdRecord`, a different record type, not currently read at all) — corrected to `hr_avg` before this ever reached real data.
- Health Connect's permission screen needed two non-obvious manifest pieces to appear at all: declaring both possible package names (`com.google.android.healthconnect.controller` on Android 14+, `com.google.android.apps.healthdata` on older versions) in a `<queries>` block, and a mandatory `<activity-alias>` for Android 14+ that Health Connect silently requires — without it, the permission screen never appears, no crash, no error.
- Deliberately last in precedence for every field it can supply — an aggregate of whatever else already writes to Health Connect, never overriding a device's own direct reading.
- A visible on/off switch added (defaults on) — while off, nothing is read and no permission is requested at all, matching this app's stated transparency principle rather than relying on Android's own, much less discoverable, permission-revoke screen.
- Tested end-to-end on a real device: permission granted through Health Connect's own screen, data read, written to the real inbox, picked up by a real `update_health.py` run, confirmed in `combined.csv`.
- Known gap, honestly: still lives on a temporary standalone test icon, not the real onboarding/Settings flow; sync is manual only, no scheduled background sync yet.

## Demo Mode — A Real Persona System, Not One Fixed Dataset

"Try a demo first" previously loaded one generic anonymised dataset. It now opens a picker of genuinely different starting points, each with real, internally-consistent data generated to match their own stated targets and story rather than a single dataset relabelled.

- **Ten personas**: two goal-based (general weight loss; body recomposition, with real training-block-driven wearable data — steps/HR/HRV/body composition merged through the app's own real CSV importer, three boot camps and two recovery massages, fat down and muscle up, HRV dipping under load and trending up overall as fitness improves, plus workout history with escalating load), and one for each of the seven supported medical/therapeutic conditions — including two deliberately paired on the same early-stage evidence base with opposite outcomes (one thriving, one still struggling with inconsistent adherence), and a nutrition/effort-focused "still struggling" persona with no medical condition at all, genuinely generating real overage days and real low-activity days rather than just being labelled inconsistent.
- Real structured Treatment Tracking, condition-appropriate Symptoms, and a ready-made Report Profile wired up for several personas — genuine data behind the "informative clinical report" story, not an empty wizard.
- **A serious real bug found and fixed, twice**: (1) switching personas without exiting first was overwriting the saved real-account snapshot with demo data, so exiting later could restore the wrong thing, or in one confirmed case, restore nothing at all (a setting silently reverted to its app default). (2) The deeper issue behind that: demo cleanup only ever ran on an explicit "Exit demo" tap — closing the tab, switching apps, or the phone locking (all completely normal usage) skipped it entirely, leaving demo data sitting in real storage indistinguishable from real data, with no banner to warn anyone. Fixed properly: entering demo now also writes a durable backup, and every single page load checks for it and self-heals automatically if a previous session was left open, rather than depending on a graceful exit that real usage often skips. (The person's actual logged food history and weight were never at risk either way — `saveState()` already refuses to persist while demo mode is active.)
- A real, separately-caught gap while building this: symptoms and a Report Profile originally required a treatment to exist first, which would have silently given nothing to several conditions (migraine, epilepsy) that have genuine symptom-tracking value with no session-based treatment to log. Decoupled.

## Documentation Corrections

`user-guide.html` updated to describe several already-real features it never documented: library auto-categorisation, the recipe ingredient-review screen, "Refresh from Library," "Next meal idea"/"Balance my macros," and the multi-ingredient per-entry editor.

`TECHNICAL.md`'s entire Health Connect section described a different, abandoned architecture (a separate bridge app, syncing via Android's Downloads folder) that was never actually built — rewritten to match what's real. Also corrected: `mhstart`'s real path (`~/bin/mhstart`, not `$PREFIX/bin` as this doc had said twice), `mh_condition`'s real values (9 real options, not 3), and the Auto-update section, previously stated as "confirmed working," corrected to reflect what's actually been found on the real device more than once: `mh_autoupdate.sh` isn't present, and real crontab has, every time it's been checked, contained only the watchdog line.

`README.md` updated: current version number, the demo mode description rewritten for the real persona system, Health Connect added to the wearables list, and a new section introducing the native launcher as the real answer to the onboarding-friction problem this README had been flagging as unresolved.

---



## Supplements — Tablet Counts and Per-Period Reordering

- Supplement entries now have an optional **Tablets** field, separate from the pharmacological dose (e.g. dose "2400mg", tablets "2 capsules") — shown alongside the dose everywhere a supplement appears (Today's checklist, Manage Supplements).
- The Manage Supplements settings list is now grouped by time-of-day period (matching Today's tab) instead of one flat list, with ▲▼ buttons to reorder within each group. Ordering is stored **per-period**, not as one global position — a supplement in both the morning and evening lists can sit in a different relative position in each, since there's no reason those need to match.

## GBM Monthly Summary — Stuck Read-Aloud Button

- The read-aloud button on the GBM Research Digest/Monthly Summary read `document.getElementById('gbm-summary-text').innerText` at click time. `.innerText` is layout-aware and can silently return an empty string for a hidden or not-yet-laid-out element, unlike `.textContent` — speaking an empty utterance could leave the button stuck showing "stop" without anything actually playing. Fixed with the same `innerText`-with-`textContent`-fallback pattern already used elsewhere (`copyElementText`), plus a general empty-text guard added to `toggleSpeakText()` itself so any future read-aloud button hits the same safety net automatically rather than needing the fix repeated per-caller.

## Gross vs Net Carbs — One More Spot Found

- The Deep Ketosis smart-alert banner ("✓ Deep ketosis ratio — Xg carbs, Y% fat calories") was reading raw `totals.carbs` directly, missed by the earlier systemic gross-vs-net sweep — both the displayed carbs figure and the ceiling comparisons behind it (`carbs < ceiling`, `carbs < 30`) were using gross carbs instead of `getEffectiveCarbs()`. Genuinely misleading on any day with polyol-heavy items logged, since gross and net carbs diverge. Fixed to match the rest of the dashboard.
- Separately, per-item and per-meal "was X, Y after polyols" figures were added in four places that previously showed only the raw carbs number with no indication polyols hadn't been subtracted yet: Today's Log list, the Edit Entry form (live-updating as either carbs or polyols is adjusted), and both the per-item line and the Total line of the chat "LOGGED ✓" confirmation bubble.

## Debug Tools — Retired Two, Added Copy Diagnostics for Claude

- Retired two stale debug traces whose underlying bugs have been fixed and stable for a long time: the polyols pipeline trace (bug fixed in v3.10.684) and the impact box trace (superseded by the broader gross-vs-net carbs sweep). The polyols tracer had 9 call sites threaded through the core logging pipeline — rather than touch each one for no functional gain, the tracer function itself was made a no-op; the impact box trace was a single self-contained block, removed entirely along with both Settings buttons.
- Added a new **📋 Copy Diagnostics for Claude** section at the top of Settings → Manage: lists every remaining diagnostic source (Log Mutation Debug, AI-Assist Apply Trace, Add-Category Trace, Save-Only Categories Trace, Body Comp Debug, Rollover Debug Log) with a live entry count, pre-ticks whichever ones currently have something to contribute, and bundles the selected sources into one combined block — app version, timestamp, then each source's full text — ready to paste into a chat. Each source's text-generation logic was extracted into its own function so the individual "View X trace" buttons keep working exactly as before, with nothing duplicated between the two.
- All debug/troubleshooting sections under Settings → Manage now have a consistent icon in their title and sit together as one group (⚖️ Body Comp Debug → 🌙 Rollover Debug Log → 🔍 Log Mutation Debug → 💾 Save Debug Trace → 📋 Copy Diagnostics for Claude → 🩺 App Health Check → 📝 Settings Change Log → 🐛 JS Error Log → 🏷 Label Read Log).

## Category Data Loss on "Save Only" — Found and Fixed

- **Real, serious data-loss bug**: saving an already-in-library item via the chat meal-preview's "📚 Save only" button (`saveLibraryOnlyFromPreview`) did a full wholesale replace of the library entry (`lib[idx] = entry`) rather than updating it. Since the replacement entry only ever carried `.categories` when something was freshly typed into "Categories for Save only" *that specific time*, leaving the field blank — the normal case when just re-saving updated macros or portion — silently wiped out every category the item already had, with no warning. The identical bug existed in the separate fuzzy-name-match confirm path (`confirmFuzzyLibOverwrite`).
- Found via a real repro reported and re-tested across several rounds: categories added through the working Library edit form vanished the next time the same item was saved via chat. Two rounds of debug-trace instrumentation (`mh_addcat_trace`, `mh_saveonly_cat_trace`, both viewable under Settings → Debug) were added along the way and left in place; a persistent try/catch was also added around `saveLibraryOnlyFromPreview` itself after a report of literally silent failure (no trace, no error) turned out to be worth guarding against regardless of the specific cause.
- **Fixed and centralized on request**: both the "Save only" and fuzzy-confirm paths now update fields on the existing library entry in place and merge any newly-typed categories in via a new shared `mergeCategoriesIntoLibraryItem()` — the same seed-from-auto-detected-if-empty, append-don't-replace logic the Library edit form's `addItemCategory()` already used correctly. `addItemCategory()` itself was refactored to call the same shared helper rather than keeping its own separate copy.
- The chat meal-preview screen now shows a read-only "Already saved as: …" line above the categories input whenever the food matches an existing library entry, so the two screens show consistent state — previously the field was always blank regardless of what the item already had, which read as "the fix didn't work" even after the underlying data bug above was actually resolved.
- **Second, related bug found while testing the first fix**: adding or removing a category chip in the Library edit form called a full `renderLibrary()` — rebuilding the entire library list from scratch on every single tap, which wiped the CSS class keeping that item's edit form expanded. Removing several categories in a row silently bounced back to the collapsed card list after each one, with no way to see the running result without reopening the form each time. Fixed by patching just that item's chip container in place (new shared `renderCategoryChipsHtml()`) instead of a full rebuild — the form now stays open through multiple edits.
- **Two remaining gaps closed**: the ✏️ per-item edit form on the chat meal-preview screen (opened via the pencil icon on an individual item, distinct from the shared "Categories for Save only" field) had no categories field at all — added one, merged in at save time alongside the shared field rather than replacing it. Separately, a brand-new item (no existing library match) saved with no explicit `.categories` at all when both fields were left blank — auto-detection covered what was *displayed*, but nothing was actually stored on the item. New items now always get real, persisted categories from the moment they're created, seeded from auto-detection when nothing was typed, matching how the Library tab itself behaves.

## Gross-vs-Net Carbs — Widespread, Not Cosmetic

- **The single biggest finding of this session.** `getEffectiveCarbs()`/`getEffectiveCarbsForDay()` (net-of-polyols carbs, when Net Carbs mode is on) existed and was correct, but roughly 20 separate places across the app were still reading raw `totals.carbs` directly instead — not just display labels, but the actual adherence percentages and averages themselves. Found while investigating a single "still can't see the real number" report and kept expanding once the pattern became clear.
- Fixed in: the Reports tab's own headline adherence % (`renderReportSummary`), Weekly Summary and the printable clinical report (both their day-*counts*, having previously only had their *labels* fixed), Sleep-vs-Ketosis correlation (cards and narrative), the AI daily-insight prompt (which also had a second, separate bug — a flat always-standard ceiling ignoring Occasion/Holiday days entirely), `generateAIBrief`, the Trends carbs summary card, the actual Ketosis Adherence trend chart, a Period Comparison table, a carb-tier distribution breakdown, the Carb-Overage-Addressed status (feeds the weight chart's colour coding), a day-detail panel, a per-day AI-report breakdown, the weekly push notification's own wording, the caregiver "carer link" export, and the Compare Metrics "Carbs" overlay (a default first-selected metric, so a commonly-seen chart).
- **A specific, recurring failure pattern**: several instances were previously "fixed" only at the label level — the displayed word changed from "ketosis" to something condition-neutral, while the underlying number feeding that label was still computed from gross carbs. Four separate places had this exact shape (Sleep-Ketosis, the AI daily-insight, Reports summary, `generateAIBrief`) — each one had its adherence-% sibling already correct, with an "avg carbs" figure sitting right next to it in the same function still wrong, until a full re-check caught all four.
- Confirmed two related instances are correctly gross by design and left untouched: a calorie-macro-split pie chart (about total caloric contribution, not ketosis adherence) and a day-rollover deduplication check (raw-to-raw equality for data integrity, where display preference is irrelevant).

## Condition-Generalization — The Ketosis-Wording Bug Class

- **~20 fixes.** "Ketosis"/"in ketosis"/"GBM protocol" language was appearing unconditionally throughout the app regardless of the actual selected condition — accurate for GBM/Epilepsy/Strict Keto/Migraine/Cluster Headache (genuinely ketogenic protocols), meaningless or actively misleading for Diabetes/Body Recomposition/General Health, where "under your carb target" isn't a claim about ketosis at all.
- New shared `isKetogenicCondition()` (reuses `CONDITION_META`'s own protocol text rather than a second hardcoded list that could drift out of sync) — replaces several ad-hoc, inconsistent `isGBMorEpilepsy` checks found along the way, at least one of which only covered 2 of the 5 genuinely ketogenic conditions.
- Fixed: the main Today-tab badge (the single most-visible instance in the app — "KETOSIS ZONE"/"DEEP KETOSIS" → "ON TARGET"/"WELL UNDER TARGET"), its tap-through "Daily Carb Zones" tooltip (previously only checked GBM specifically, not the full ketogenic set — a non-keto user still saw GKI targets and "ketogenic protocol" framing; GKI now hides entirely rather than showing generic-but-still-irrelevant wording), the "Ketosis check" quick-prompt chip and its actual response text (`getKetosisStatus()` — only one line of it checked condition before this, every message branch talked about ketosis unconditionally), the 7/14/30/50/100/200/365-day streak-milestone celebrations (two full parallel message sets, not word-patched), the "What can I ask?" help response, four Trends chart labels/headings, Settings' Carb Ceilings heading, the macro-advice panel's "Fat % here is a ketosis requirement" claim (an unused `id` hint suggested this was meant to be dynamic but was never wired up), and the dashboard's fat-ratio "smart alert" (hidden entirely for non-keto conditions rather than reframed with still-irrelevant advice, since the concept itself — a 65% fat floor — doesn't apply outside a ketogenic protocol).
- Settings' fat-target advice (three hand-duplicated copies, all with the same unconditional ketosis wording) centralized into one shared `updateFatTargetAdvice()`.

## New: Balance My Macros

- New Log-tab chip, the deliberate opposite of Next Meal Idea: that one starts from what you fancy (pick categories yourself), this one starts from what today's macros still need — no picker, just tap it. Reuses the same library-only suggestion engine, so results are always real, loggable items, never invented.
- If there's genuinely too little budget left (<15% remaining) or it's past a reasonable hour, says so plainly first, then offers smaller snack-sized ideas instead of quietly padding out a "meal" that doesn't fit — this is by design specifically for this flow: unlike Next Meal Idea's category picker, there's no explicit composition being overridden, so a chocolate/sweet suggestion here is a legitimate need-driven answer, not the wrong-flow bug the same wording caused elsewhere.

## Saved Prompts — Scope Tagging, and Reports Now Genuinely Includes Today

- Every saved prompt can now be tagged **Today**, **History**, or **Both** — the Log tab and Reports tab each have their own "Browse saved prompts" list, filtered by tag, so a history-needing question can no longer be run through the tab that only ever sees today's data (the exact confusion that prompted this work: a saved ketosis-adherence question run from the Log tab correctly, if unhelpfully, said it couldn't see history).
- Live keyword-based scope suggestion as the question is typed ("today"/"remaining" → Today; "recent"/"trend"/"compare"/"week" → History; both → Both) — plain matching, not an AI call, since it needs to be instant and a wrong guess costs nothing (correcting it is the same single tap getting it right first would have been). Backs off permanently the moment a toggle is tapped manually.
- One-tap **🪄 Auto-classify** batch action for prompts saved before this feature existed, using the same keyword logic — appears automatically wherever unclassified prompts exist, disappears once none remain.
- Root cause of the "why couldn't the Log tab ever answer this" problem: `state.history` only ever contains *completed* days — today gets added at midnight rollover, never before. New shared `_historyIncludingToday()` merges today's live totals into Reports' full-history context, so "History" is now a genuine superset covering pure-historical, pure-today, and spans-both questions correctly. Wired into Ask AI/Full Summary and the oncology narrative; the GBM Summary (which shares a separate, date-range-respecting history function with the Trends charts) gets today merged in conditionally instead, only when it actually falls inside whatever range is currently selected.

## Library & Portion Parsing

- **Root cause of a library item silently failing to scale**: portion-parsing required an explicit unit suffix ("15g") everywhere — a bare numeric portion ("15", no unit) always failed silently, falling back to a 100g guess and never actually scaling regardless of the amount entered. Found via a specific repro (15g and 100g of the same item producing identical macros). The exact same broken pattern had been independently hand-copied across **8 separate call sites** (both Library LOG flows, the final log-confirm step, recipe import matching, both voice-add flows, the shared recipe-substitute/combo helper, and Refresh from Library) — centralized into one shared `_parsePortionGrams()` so the bug class can't reappear by being copied a 9th time.
- **Category comma-splitting**: adding a category to a library item never actually split on commas — typing "Baking, Sweet" produced one literal category containing a comma instead of two separate ones. Fixed, with the existing typo-detection ("did you mean 'dairy' not 'diary'?") generalized to work across a whole comma-separated batch at once. The same bug, independently duplicated, was also found and fixed in the Manage Categories keyword-to-category dictionary editor.
- Library search/filter/sort persistence (added this session) had a real side effect: a restored "Recipes only" filter hid the Ingredients/A-Z/Food sections entirely with no visual indication anything was filtered, looking exactly like data loss. The filter no longer persists across reloads (search and sort still do); a visible warning banner now appears whenever the filter is narrowed mid-session, placed specifically outside the sections it toggles so it can't hide itself.
- `buildMealImpactHtml`'s Carbs row was comparing gross-before against net-after (an apples-to-oranges mismatch that could show a carb total decreasing after adding a carb-containing item) — the root cause of "carbs have always been around 8 or 9, what's changed."
- "Verify across 3 AIs" extended to the Library edit form, Today/History simple edit forms, and the recipe manual-add form (previously only available on the initial preview).

## Supplements

- `_fuzzyMatchSupplement()` (voice check-off) compared two incompatible units directly against each other — a name's character length for an exact match, vs a small word-hit count for a fuzzy match — meaning one early exact match could permanently block a later, genuinely better fuzzy match from ever winning. Fixed with a proper two-tier comparison (exact always beats fuzzy, each tier compared using its own consistent unit).
- `toggleSupplementActive()` and `saveSupplementEdit()` only refreshed the Settings management list, not Today's checklist — toggling a supplement off, or editing its name/dose/periods, left Today showing stale info until something else happened to trigger a refresh. (Delete already did this correctly.)

## Wearable Import Pipeline

- **Silent data loss found**: the CSV import (`processCombinedText`) never mapped a `fat_g` column at all, despite the app's own export schema elsewhere explicitly including one — kcal/protein/carbs all had proper lookups, fat simply never did. Any imported nutrition data including dietary fat was dropped on every single import.
- `advRun`'s status-poll loop had no error handling at all, unlike the sibling `doSync()` poll — a dropped connection mid-run could throw uncaught inside the interval, silently skip that tick, and never call `clearInterval`, leaving it stuck polling indefinitely with no visible error. Now matches `doSync()`'s pattern.

## Trends

- The Steps summary card's status text, its colour, the "days over" count, and the bar chart's own colour-coding were all hardcoded to 10,000/7,000 steps, while the gauge on the same card already used the personalized Activity Level baseline from Settings — now consistent throughout the card. A separate, similar-looking instance in the Deep Dive drill panel was checked and confirmed to be a deliberate, already-reasoned design choice (universal 10k/5k benchmarks shown *alongside* a separately-labeled personal baseline, not replaced by it) and left alone.

---

# MaxedHealth Changelog — Phase 21 (v3.10.628 – v3.10.658)

## Compare Metrics — Real Root-Cause Bugs, Not Symptoms

- **The actual reason metrics randomly went missing or showed only one point**: `getTrendsData()` (shared by Trends and Compare Metrics) has a branch controlled by `trendsWindow`, a variable belonging entirely to the Trends page's own Today/multi-day toggle — defaulting to `'today'` on every fresh app load. Left there, it silently returned a single day regardless of whatever period Compare Metrics itself had selected. Explains exactly why "it works if Trends' own period was already changed first, breaks if changed only within Compare Metrics" — found via a precise repro (Body Fat % always worked because it never touches this function; everything routing through it was at the mercy of unrelated page state). Added a `forceFullHistory` bypass; Compare Metrics and the single-metric Deep Dive view now always use it, since both manage their own independent period filtering.
- **A second real bug found alongside it**: the earlier "merge today's totals into the existing row" fix was mutating `state.history`'s actual object directly (a shallow-copied array's elements are still the same references) — silently overwriting real saved data on every single render. Now clones before mutating.
- **Five color-collision groups** across the 16 metric pills — HRV/Sleep/Distance all shared purple, Protein/Ketosis Adherence/Muscle% all shared green, Calories/Steps shared blue, Weight/Carbs shared yellow, Hydration/Water shared light blue. All 16 now genuinely distinct.
- Added a render-generation guard (skips a stale/redundant re-render if a newer one has started) and a try/catch around the core render logic that logs any real failure to the JS Error Log instead of a silent blank canvas — both defensive improvements found worth keeping even after the real root cause was identified.
- `multiMetricScroll` was missing from the shared scroll-nav registry every other major view uses — Compare Metrics now has the same ▲▼ jump buttons as everywhere else.

## Compare Metrics — New Capabilities

- **Custom date range** added alongside 7D/30D/All (90D removed per request across all three standardized period selectors — see below). One shared date-range check per screen rather than scattering the logic across every place a period was already being filtered.
- **Pills grouped into categories** — Treatment, Exercise, Vitals & Sleep, Nutrition, Body Composition, Symptoms — top-level pills that expand/collapse to show their members, with a count shown when a group has active selections. Was a single flat list of 16+ pills before.
- **📦 Full Report Package** — bundles the chart image, a CSV of the underlying data, the text summary, and the most recent AI interpretation (if one's been asked for) into a single share action via the Web Share API where supported (native share sheet, pick WhatsApp/email/Drive/etc.), falling back honestly to a downloaded image + mailto with everything else inline in the body if multi-file sharing isn't supported on the device.

## Treatment Tracking — Substantial Extensions

- **Log a session for a PAST day** directly from History's Occasion Tags section — didn't exist before at all; sessions could only ever be logged for today.
- **Session-level notes** (optional, prompted at logging time) and **general per-tag day-level notes** (a 📝 icon on any active Occasion Tag, History and Today both) — two deliberately separate mechanisms, since a day can have several sessions each needing their own note, while a tag like "Illness" needs one note for the whole day. Stored in dedicated fields (`day.tagNotes`/session `.note`), never inside the comma-split `day.notes` tag list, which is parsed as discrete tags in over 20 places elsewhere.
- **Today dashboard card** — Treatment Tracking previously existed only in Settings and Reports; logging a session gave no visible confirmation anywhere you'd actually look afterward. New card matches the "How are you today?" card's style, with its own reorder/hide (▲▼, 📝) matching every other dashboard section — the same fix applied to the Symptoms card, which had the identical gap.
- **Reports → Treatment Sessions rebuilt for multi-select**: both treatments and comparison metrics are now pill-based (were single-select dropdowns), producing a treatment × metric cross-product of before/during/after blocks. New 📄 CSV export and 🤖 Send to AI for interpretation (drops a real summary into the chat input, ready to send or edit).
- **Custom tags now support a parent category** — "Resistance bands"/"Walking" auto-select "Exercise" (fixed mapping); a new custom tag prompts once for an optional parent and remembers the choice permanently. The parent is never auto-removed when the child tag is removed — it may still genuinely apply on its own.
- Occasion Tags' "Treatment" chip now shows the *specific* treatment name(s) logged that day, not just a generic checkmark — someone can have more than one treatment the same day, same as multiple exercises.

## Voice Input — Three Real, Separate Bugs

- **"done" required a manual tap that never actually happened.** The mic flow was built for multi-item food logging; saying "done" only showed a toast with a "Log it" action — nothing was ever auto-sent. Now auto-sends immediately.
- **A trailing "done" on a longer utterance was still missed.** The done-phrase detector required the *whole* utterance to be 5 words or fewer — fine for short ingredient names, not for full-sentence questions. If speech recognition merges a request and "done" into one long transcript (no long enough pause), it now still detects and strips a trailing done-phrase instead of failing the word-count check outright.
- **The deeper "arrow does nothing" cause**: nothing was ever written to the *visible* input box during voice capture — spoken words sat in an invisible variable with only a passing toast as feedback, so `sendChat()` correctly refused to send an empty box. The input box now fills in live as you speak, giving a real, editable, always-available manual fallback regardless of whether spoken "done" gets detected.

## Meal Logging — Real Bugs Found, Not Guessed

- **Numbered-suggestion selection losing context** — replying "1" or "yes, the X one" to a numbered list was either searched as literal text or re-opened a "recipe or quick log?" clarification, losing the specific suggestion entirely. Fixed by tracking any assistant message containing a real numbered list and replaying it as context with an explicit instruction on the next reply — later strengthened to also explicitly forbid the AI from calling a library-search tool instead of just logging the selected option, after a report showed a numbered reply hijacking into an unrelated "checking your library" flow with different suggestions entirely.
- **The actual root cause of "keto custard shows 0 uses" wasn't about recipes at all** — a deterministic keyword shortcut hijacks any short message containing "keto"/"ketosis" into a ketosis status readout instead of ever reaching food logging. A prior session had partially fixed this for one case (a photo + short product name) but left the plain-text case — an extremely common product-naming pattern (keto bread, keto custard, keto bar) — still broken. Now requires an actual status/question indicator (check, status, am i, how's, doing) alongside the word, not just the bare word under a length limit.
- **Recipe `useCount` moved to one real choke point.** Three separately-patched logging paths (direct Log button, custom-servings prompt, suggested-combo) all had their own explicit increment, but a recipe logged by describing it in a message never touched any of them — going straight into `logFoods()`, which had no matching logic at all. Moved the increment into `logFoods()` itself, matched by name against the logged text (exact, starts-with for the "(N servings)" suffix, or a gated fuzzy contains-match for free text) — covers every path, including ones added later, without needing to find and patch each one individually. Added a real diagnostic to the existing call-trace debug tool (Settings → Manage → Log Mutation Debug) showing exactly what text a match was attempted against and what it found.
- **The Most Used saga, resolved through three further rounds of real debug-trace data** (not guessing): (1) the name-match only ever checked whether the *logged* text contained/started with the *recipe* name — never the reverse, so a shortened version of a longer recipe name ("keto spaghetti" for a saved "Keto Spaghetti Bolognese") never matched in either direction; fixed with the missing reverse check. (2) The real, deeper cause turned out to live in `logSuggestedCombo`, which has two branches: one references a saved recipe directly (already worked), the other builds its combo from individual library items with no recipe reference anywhere in that code path at all — even when the AI's suggestion exactly matches a saved recipe's composition, there's no name to match against, just a join of separately-looked-up ingredient names. Added a genuinely different comparison as a fallback once name-matching has failed: the *set* of logged ingredient names against each saved recipe's own ingredient list, 75%+ overlap required (gated to recipes with 3+ ingredients to avoid coincidental matches). The debug trace now shows which method actually matched, name or ingredient overlap, with the real percentage.
- Recipe cards now show the real `useCount` ("used N×") when sorted by Most Used, so the sort can be verified directly against real data rather than guessed at.

## Period Selectors — Standardized

- Trends, Reports, and Compare Metrics now all use the same 7 days/30 days/All time/Custom set (90 days removed from all three per request). Trends alone keeps "Today" as an addition on top, since it's a genuinely different single-day view, not just a shorter period.

## Settings Reorganized

- **Data & Backup moved from Manage into the Import sub-tab**, which is renamed **"Data"** — covers import/export/sync/restore/onboarding under one sensible label. A real 📦 Export All Data button was also added directly to this section (previously only referenced by a tooltip pointing elsewhere).
- **Full site-search audit**: cross-checked every real collapsible section in the app (65 total) against the search index by script — found the *entire* Reports tab was unindexed (not just one button), plus 17 sections across Today/Library/Trends/Log. Then ran a second automated check comparing every entry's assumed scroll-target element against the real one — found and fixed 7 wrap-id mismatches, including 3 pre-existing ones unrelated to this session's work. Final state verified by script: 62 indexed sections, zero gaps, zero mismatches.
- **Query Builder** gained "Occasion Tag" as a queryable field — categorical match against real tag presence (with autocomplete), not forced into the existing numeric gt/lt/between controls built for metrics.

## PWA / Update Detection

- **New "a new version is ready" banner.** There was previously no way to know a new version had deployed while the app was open, and no active check when returning to it — a real report surfaced a device stuck three versions behind, silently, with several shipped fixes invisible the whole time. Detects a waiting service-worker update and prompts to reload; also explicitly checks for updates on load and whenever the tab regains focus.



## Notification & Data-Integrity Bugs — Real Causes Found, Not Guessed

- **Supplement/EOD/weekly/carb-alert notifications marked themselves "fired" the moment a send was attempted, not once it actually succeeded.** `sendLocalNotif` now returns a real success/failure result; all four notification types only mark themselves done on confirmed delivery, so a genuine failure (permission not truly granted, service worker not ready) correctly retries on the next check instead of going silent for the rest of the day. Added a live diagnostic (Settings → Notifications → "Test supplement reminder now") that reports each decision point instead of returning silently.
- **Fat sanitization was overwriting a deliberately-entered 0** — the "fill in missing fat" heuristics treated a stored `0` the same as "AI never filled this in," so a real correction (e.g. Tennent's Lager, genuinely 0g fat) kept reverting. Added `_fatUserEdited` tracking at all 4 places fat can actually be hand-edited. Separately found the *specific* Tennent's bug: alcohol's real calories (~7kcal/g) aren't captured by protein/carb/fat, and the "200+kcal with 0g fat is probably wrong" heuristic didn't know that — moved the existing `isAlcohol` exception (already used elsewhere) to also cover this block.
- **Device-precedence imports were silently permanently blocked** — every device-sourced field (steps, sleep, HRV, SpO2, HR, weight, body comp) used a "fill only if blank, never overwrite" rule, meaning a manual entry or an earlier import blocked every future import from updating that date's data, for that field, forever — regardless of configured device precedence. Now updates on every fresh import ("last import wins" for device data — true per-field precedence would need `combined.csv` to carry per-row source-device attribution, which the pipeline doesn't write).
- **The export button appeared to hang forever** — wasn't actually stuck; `exportAll()` returns almost instantly (it just schedules staggered downloads), but nothing ever reset the button text. Both the dashboard banner and the chat-bubble version now correctly revert/dismiss after the export window.
- **"Redo setup wizard" did nothing** — `checkOnboarding()` reads `.onboarded` from inside the `maxhealth_v1` state blob; the button only ever cleared two unrelated top-level keys. Fixed, plus a one-time force-flag so the "already has real data" escape hatch (which exists to stop nagging an established user) doesn't immediately undo the reset before the wizard even shows — exactly the situation anyone tapping that button is already in.

## Chart Style Picker, Zepp-Inspired Polish, Donut/Heatmap Views

- Line/bar/point style picker on all 15 Trends cards and per-metric in Compare Metrics (true mixed chart — one metric can show as bars while another shows as a line, simultaneously), remembered per tile.
- Two Chart.js plugins registered globally (today-highlight band, last-point data labels) — every chart gets them automatically. Threshold-aware amber coloring on HRV/SpO2. New horizontal gauge component (the one genuinely new element, not a restyle) on HR/HRV/SpO2/Steps/Sleep/Ketosis Adherence and the deep-dive screen.
- 🍩 donut added to Ketosis Adherence (days in/out of ceiling) and Calories (macro split); 📆 calendar heatmap added to Ketosis Adherence. Sleep's donut was attempted twice and never worked reliably despite real debugging effort — removed rather than keep chasing it; the same information is already visible via the existing sleep-timeline bar.
- A genuine regression during this work — a delegated click-listener fix for one broken icon accidentally disabled *every* chart-style icon on every tile (registered on the wrong event phase, which a `stopPropagation()` elsewhere silently defeated) — caught and fixed same-session via capture-phase registration.

## Body Composition Units, Patterns Overhaul

- Bone Mass/Hydration investigated properly (Settings → Body Comp Debug, real cache data, not guesswork) after appearing to show an alarming decline — resolved as correct data, misleading presentation: both are genuinely *improving* as % of body weight, but a ~24kg total weight change over the tracked period means the same % of a lighter body is fewer absolute kilograms. Both cards now show kg and % simultaneously, toggle for which drives the chart, defaults to %.
- **Patterns gained a second, genuinely different detection shape**: SPC-style early-warning checks (`checkSPCBreach`) using real individuals-control-chart methodology (Western Electric/Nelson rules — 2-of-3 beyond 2SD, 4-of-5 beyond 1SD, 8-in-a-row, baseline mean+SD from 20+ historical days excluding the test window) for Calories and Weight, on top of the existing group-comparison findings. Calories checked net of logged exercise credit, not raw intake — eating more on a day with more exercise logged isn't over-eating. Weight is direction-aware against the real configured target range.
- 6 new cross-metric group-comparison findings: fat vs ketosis adherence, HRV vs ketosis adherence (both directions), protein adherence vs muscle % trend (first-half/second-half, not a daily split — body composition doesn't move day to day), hydration vs HRV, same-night SpO2 vs sleep. Empty state now reports real day-counts per check instead of one generic "not enough data" message.

## Library: Auto-Categorize, Exercise Duplicates

- New 🏷️ Auto-Categorize button replaces the old copy-a-prompt-to-a-separate-Claude-session workflow. Auto-assigns only 'fat' and 'protein' directly, and only where the real macro ratio (Atwater calorie-split) genuinely supports it — everything else queues into a one-at-a-time review modal (same pattern as Find Duplicates) with a macro-based suggestion pre-selected, and picking meat/fish auto-checks protein alongside it (matching the hierarchy `DEFAULT_CATEGORY_MAP` already applies automatically to keyword matches).
- New exercise-name duplicate finder (Settings → Treatment Tracking) for Strength Log — same fuzzy-match-and-review pattern as Library's own Find Duplicates, relative edit-distance threshold so short names aren't wrongly merged. Merging renames across both logged history and any saved routines referencing the old name.

# MaxedHealth Changelog — Phase 20 (v3.10.599 – v3.10.627)

## Treatment Tracking — New System

- New user-extensible treatment definitions (name + optional explanation, e.g. PEMF) with real timestamped session logging — deliberately built on the Symptom Tracking pattern, not Exercise (checked first: Exercise/`state.strengthLog` is genuinely free-text with no structured definitions at all, so it wasn't the right model despite being the one initially suggested). Kept entirely separate from the pre-existing GBM "Treatment Analysis" (chemo/radiation, keyword-matched from notes) to avoid confusing two different systems with the same name — the new one is "Treatment Sessions."
- Treatment sessions now selectable as Compare Metrics pills (0/1 per day, same shape as Ketosis Adherence), with reorder/hide/chart-style all confirmed already working generically (traced directly: `isSymptom`/`isTreatment` are checked in exactly one place in the whole file, everywhere else is metric-agnostic).
- New "Treatment Sessions" report (Reports tab): pick a treatment and a comparison metric, see day-before/day-of/day-after averages, minimum 3 logged session days required.
- New Compare Metrics chart export (real PNG download, theme-aware background) and data-summary copy. New audience-agnostic "🎯 Custom" export mode — deliberately not locked to any one use-case (a PT-reporting example was raised during scoping but corrected mid-build to not become another hardcoded audience alongside the existing oncology-specific Clinical mode) — just writes up whatever's currently selected in Compare Metrics.

## Also Fixed Along the Way

- Global scroll-nav ↑/↓ buttons were obscuring the Log/Chat send button — `chatScroll` was in the same watch-list as every plain dashboard view, but it's the one view with its own docked compose bar in the same corner. Two separate places set the active-container state; the first fix only caught one of them.
- Sleep donut and one other feature hit the same inline-`onclick`-with-embedded-string parse-error bug class that had already bitten this app twice — the underlying pattern (data-attributes + delegated listener, immune regardless of what characters end up in the value) is now used for chart-style buttons and the library-picker replacement-search link specifically.
- Recipes are now sortable (A-Z / Most Used / Kcal/Protein/Fat/Carbs-per-serving / Recent) — checked first and confirmed they genuinely had no sort at all. "Most Used" needed real usage tracking added (recipes never had a `useCount`), incremented at both of the two independently-written logging code paths.
- Compare Metrics gained a kg/% toggle for Bone Mass/Hydration matching the Trends cards, sharing the same stored preference so the two screens never disagree.


# MaxedHealth Changelog — Phase 19 (v3.10.585 – v3.10.594)

**v3.10.564–584 not individually documented here** — same gap this file already flags for earlier phases (472–499, 13–14), now extended; this session picked up mid-testing at 585 with no summary of what landed in between.

## Compare Metrics — Multi-Line Overlay, Built and Then Actually Fixed

- **Single-metric drill chart and Your Journey both lost horizontal scroll** after 586's `touch-action:pan-x pan-y` fix — because the real blocker on both wasn't touch-action at all. The single-metric chart had a `touchmove` handler calling `preventDefault()` on every move to drive a floating tooltip/scrubber, which overrides touch-action CSS outright; Your Journey never had a scroll wrapper in the first place. Fixed both: floating tooltips replaced with tap-to-open info panels (✕ to dismiss) on both charts, same pattern the compare-metrics chart already used, which also removed the JS-level `preventDefault` that was the actual cause.
- **Selected metrics disappearing from the compare-metrics overlay** — not a selection bug (the array-based toggle was already correct), but `pointRadius` being computed once from the *combined* date range across every selected metric rather than per-dataset. Combined with `spanGaps:false`, any metric with its own gaps (sleep only synced some days, ketosis only computed on logged days) lost both its connecting line and its points on 90D/All views, leaving only continuously-synced metrics (Hydration) visible. Radius now decided per-dataset from that metric's own real data coverage.
- **Reorder + hide added at three levels**: individual legend cards, the three compare-metrics sections (Chart / Day-Period Info / Legend — reordered so Day/Period sits between Chart and Legend), and separately the 15 individual Trends metric cards — all using the same persisted-order-array pattern as the dashboard's own `moveDashboardSection`.
- **Real lockout bug shipped and then fixed same-session**: the ▲▼👁 controls lived inside each section/card's own header, so hiding a section also hid its own restore control — no way back in the UI. Fixed with a persistent restore strip, independent of any single section, applied to both the compare-metrics sections and the Trends cards from the start once the bug was found.
- **Reset button** added next to the metric picker — clears pill selection to empty (deliberately not back to the original 3-metric default; a genuine reset shouldn't reintroduce metrics that weren't asked for).
- **Day/period drill-down panel** — tapping a point shows real values for that day, or (toggle) an average over the currently-selected top period ending on that date. Confirmed this doesn't duplicate the top 7D/30D/90D/All selector: the top selector controls what the chart displays, the panel toggle is a rolling window of the same length ending wherever you tapped, independent of the chart's own visible range.

## Full Charts Section Removed, Then Substantially Rebuilt Inline

- **The old "Full Charts" collapsible (14 duplicate mini-charts at the foot of Trends) removed** as redundant now that Compare Metrics covers the same ground with proper scrolling — but this also silently deleted the only chart some metrics had, which wasn't the intent.
- **Restored properly**: all 9 metrics that already had a summary card (Weight, HR\*, SpO2, HRV, Steps, Sleep, Calories, Protein, Carbs) got their detailed chart moved back inline into their existing card, appearing with the rest of that metric's stats instead of behind a separate link. Ketosis Adherence (no card of its own) folded into the Carbs card, where its data was already being computed.
  - \*Heart Rate never had a detailed chart in the first place, before or after — nothing was removed there, there was never a `chartHR`.
- **6 metrics that only ever lived in the old Full Charts section got real cards built for them**: Water, Fat %, Muscle %, Bone Mass, Hydration, Distance — simpler than the other 9 (no sparkline, no multi-stat grid, since none of that machinery existed for them before) but same chart-in-card treatment, and now included in the same reorder/hide system as everything else.
- **`water` added to `DRILL_CONFIG`** — it had a card and a chart but no drill-down entry, so tapping it did nothing and it was invisible to Compare Metrics' own metric list. Consistent with the other 5 added in an earlier phase for the same reason (a real tappable UI element with no backing config entry).
- 9 direct `new Chart(document.getElementById(...))` calls (one per always-rendered metric) were guarded with an existence check before the HTML was fully restored — defensive, kept in place since it costs nothing and protects against the same class of bug if a canvas is ever conditionally absent again.

## Trends Page Reordered

- **Analysis period filter (Today/30/60/All) moved to the very top of the page and deliberately excluded from the hide system** — every chart and card on the page reads through this filter, so hiding it would strand everything else with no way to change what's showing.
- **Today's Wellness, Your Journey, and Patterns grouped together** immediately below the period filter, ahead of Compare Metrics and the metric card grid — previously interleaved with the filter and the Compare Metrics button in a less coherent order.

## Known Outstanding Items

- Health Connect bridge (Android) — still parked, not started.
- GitHub Releases page cleanup — not actioned this session.
- RingConn sleep backfill still only covers 19 Aug 2025 onward — older history not yet corrected.
- AI photo-reading occasional polyols misreads on certain label layouts — unchanged; needs a real failed example to fix safely rather than a blind prompt edit.
- Documentation (this file, README.md, TECHNICAL.md, user-guide.html, changelog.html) had drifted again — README was at v3.10.577, changelog.html and this file at v3.10.563, user-guide.html's footer at v3.10.471, while the app had reached v3.10.594. Caught up in this pass.

# MaxedHealth Changelog — Phase 18 (v3.10.510 – v3.10.563)

A long session spanning a full structural bug audit, a category system built from scratch, retiring Meals in favour of Recipes, and a real feature built twice — once wrong, once right — after testing against real data and real phrasing caught what isolated testing had missed both times.

## Category System — Built From Scratch

- **Real food-group categories replace ingredient-name-as-category.** Every library item now auto-categorizes into genuine groups (meat, fish, dairy, vegetable, fruit, fat, protein, grain, breakfast cereal, bread, sweet, savoury, herbs and spices, alcohol, salad) via `DEFAULT_CATEGORY_MAP`, a keyword→categories dictionary, with `getItemCategories()` as the single resolver (per-item manual override first, auto-detection fallback).
- **Split "cereal" into two genuinely different categories** — "grain" (pasta, rice, bread, oats) and "breakfast cereal" (cornflakes, weetabix, muesli, granola, cheerios), which had been conflated under one label. Real product-name detection added for the latter; none of those products were being auto-detected at all before, since their names never happened to contain the literal word "cereal."
- **Fully in-app editable** via a new Manage Categories modal — add/remove/edit any word→category mapping, per-item category overrides, a rename tool for fixing existing data in bulk (e.g. a stray "diary" → "dairy" typo across every affected item), typo protection using Damerau-Levenshtein distance (catches transpositions like diary/dairy that a standard Levenshtein implementation would miss), and scroll-to-top/bottom navigation matching Library's existing pattern.
- **Kept deliberately separate from `MEAT_TYPE_WORDS`**, the strict list `fuzzyFindInLibrary` uses to stop "Chicken Mince" fuzzy-matching "Beef Mince" — the browse-category system correctly groups both under meat/protein, but that's a different purpose from match-safety disqualification, and merging the two would have broken the safety property silently.
- **"Snack"/"snacks" — blocked as a category, then correctly reversed.** Originally blocked from per-item tagging on the reasoning that it would duplicate the picker's own pinned Snack button. That redundancy concern turned out to only actually apply *inside* the meal-suggestion picker itself — per-item tagging, the general browse view, and all four save-to-library paths had no such collision, so blocking it there was simply wrong. Reversed in all four places after being caught directly (a real Caramac bar wouldn't tag).
- **The snack-sizing instruction itself had a real semantic error, also since fixed**: "a small combo of separate savoury items" is tapas, not a snack. Rewritten using concrete real examples (crisps, chocolate, sweets, peperami, pork scratchings) instead of the wrong abstraction — peperami and pork scratchings turned out to be genuinely uncategorized in the map too, now fixed.
- **Bulk-tested against a real 219-item library export** — 93.6% auto-categorized correctly out of the box; fixed real gaps found in the process (bare "fish"/"meat"/"salad" weren't keys at all, only specific types like salmon/chicken were; rosemary, thyme, vodka, avocado, caramel, toffee, and baking powder were missing entirely). Coverage now 98.2%.

## Structured Meal Requests — "Meat and 3 Veg"

- **Built, shipped broken, then actually fixed.** The first version only ever reached `parseMultiCategoryRequest` from inside a gate requiring "idea"/"suggestion" to also be present in the message — a bare phrase like "protein and pasta" fell through to the AI's food-logging parser instead, which (correctly, from its own perspective) asked for clarifying detail rather than suggesting anything. The bug shipped because testing exercised the parser in isolation and the pinned button (which calls the suggestion function directly, bypassing the gate) — never the real path a bare typed phrase actually takes. Fixed with an independent check, guarded against genuine logging attempts (logging verbs, weight/volume quantities) via real counter-examples, not just the target phrase — "I had chicken and pasta for dinner" and "200g chicken and 100g pasta" both still correctly log rather than being misread as suggestion requests.
- **Also generalized beyond category names to real keywords** — "protein and pasta" now resolves "pasta" to the grain category via `CATEGORY_MAP`'s own keywords, not just formal category names, keeping the specific word for extra AI precision (prefer genuinely pasta, not just anything else grain-shaped).
- **Rebuilt entirely as a multi-select pill UI**, replacing the original single-tap-per-pill picker: tap-to-select category pills with an editable per-category count (hidden/0 until tapped, then 1 and editable), a Send button submitting the full selection as a composition array. The earlier pinned "Meat + 3 Veg" button is now redundant and removed — the general picker covers it directly, alongside anything else (protein + grain + salad, fish + 2 veg + a fat, etc).
- **Deterministic partial-match threshold**, not left entirely to the AI to notice: a 2+-category request needs at least 2 of those categories to have a real matching library item before it's worth sending to the AI at all — one matching category out of three requested isn't a genuine partial match. Verified against every example given, including the single-category exemption (no partial-match concept applies when only one category was ever requested).
- **AI-level partial-match instruction strengthened** to explicitly name which category came up short and why, rather than a vague general caveat, for the case where the threshold passes but individual counts still can't be fully met.

## Meals Retired in Favour of Recipes

- **"Save as meal" now creates a genuine recipe** with real per-item ingredients (available at save-time), not a flattened single-entry blob.
- **Existing meals convertible via an explicit, confirmed migration** — preserves exact total macros (individual item macros were never stored for meals in the first place, only the combined total, so a single-ingredient recipe carrying the real total, with the original component list kept as a note, is the honest ceiling of what's recoverable). Button since archived after Pete Spence confirmed the one-time migration was complete.
- **Logging a saved recipe now opens a real review step** — add, remove, or swap any ingredient (reusing the existing swap-search/scale/add/remove system already built for AI-suggested meals) before it hits the log, instead of logging directly with zero chance to check it.
- **"Refresh from Library"** added to the recipe builder — updates a recipe's ingredients if the underlying library item has since been corrected, rather than the recipe silently drifting out of sync forever. Confirmed via code inspection that this genuinely never happened automatically before, and that History being the same way (frozen snapshots, no retroactive rewrite) is correct, deliberate behaviour, not a related bug.
- **Meals section removed from the Library UI entirely.** A real regression was caught and fixed before shipping: `renderLibrary()` had an early-exit guard depending on the now-deleted Meals element, which would have blanked the entire Library tab, Ingredients included.

## Save-to-Library — Four Separate Paths, Same Category Gap

- **A comprehensive audit, not a single-instance fix.** The first report (the "Save only" button after a multi-AI verify) led to auditing every `lib.push()` call site in the codebase rather than patching just the one hit. Found a genuinely separate fourth save path (`saveFoodToLibraryFromPanel`, the database/barcode search results screen) that bypassed the shared save infrastructure entirely, with no category option at all. Voice Add and CSV wearable import confirmed unrelated or already-correct.
- **All four now support setting categories at save time**: the Add Food modal, the post-AI-log "Save to Library" modal, the "Save only" meal-preview bubble (shared across however many foods are in that batch), and the database-search amount panel. Left blank, every path still auto-detects normally.
- **Category browse view had no way to add a new item to it at all** — only LOG/EDIT on what already existed. Added an "+ Add [category] item" flow offering a real choice (Search online or Enter manually, matching the existing pattern used for unmatched recipe ingredients) rather than jumping straight to a blank form, with the category carried through automatically to whichever path is used.

## Fibre & Polyols — Editable At Last

- **Root cause of a real reported miss (Heylo Caramel Granola) wasn't the AI mis-reading a label** — it was that neither the Add Food form nor the library item edit form had a fibre/polyols field at all. Once an item was saved without them, there was no way to add them afterward short of deleting and re-adding the whole entry. Fixed on both forms.

## Site-Wide Search — Real Coverage Gaps

- **Recipes were never actually searched at all**, despite the section being labelled "Library & Recipes" — they live in a separate store from the library array and were silently excluded. Fixed and verified.
- Twelve settings entries had no search keywords whatsoever (only findable by typing the exact label) — Target Formulas covers BMR/TDEE/MET/walking pace/macro ratio and had none of it indexed. Fixed all twelve, plus one section (Data Preview & Validator) that was completely absent from the index despite existing in the UI.

## Past-Day Logging — Sticky-Flag Bug

- `window._logTargetDate`, set by History's "+ Add food" button, was a sticky mode only ever cleared by an explicit "Back to today" tap — nothing else reset it. If that banner went unnoticed, a later logging action genuinely meant for today would silently also land on the past day. Now auto-clears after every successful past-day log, making each entry a deliberate one-shot action.

## Smaller, Confirmed Fixes

- **Weight status labels now state their actual measurement period** ("Slight loss (last 14 days)"), not an unlabelled snapshot.
- **Hardcoded 7,500-step target** in two report views now reads the real configured baseline.
- **TTS keep-alive timer** made explicitly clearable from the read-aloud feature's own cancel path, rather than relying solely on `onend`/`onerror` firing reliably after a direct `.cancel()` call (not always guaranteed across browsers) — a defensive tightening found while investigating a battery-drain report, not a confirmed fix for an actual leak (none was found; the wake locks, camera scanner, sync polling, and service worker were all already correctly built).

## Investigated, No Code Change Needed

- **Activity Credit Balance's "reset" behaviour** — already a true rolling window (recalculated fresh from only the last N days), already goal-aware (different narrative text for maintain/gain/loss). Nothing accumulates forever; nothing needed fixing.
- **Meat/protein category overlap** — deliberately not redundant. "Protein" is a broader umbrella (also covers fish, eggs, whey) that "meat" doesn't. The multi-select picker already gives the "expanded choice" wanted by simply selecting both pills together.
- **Export reminder** — already existed from an earlier session (7-day nudge on the EOD summary, escalating to a 14-day dashboard banner), found while about to build a duplicate.
- **AI data flow** — the three everyday AI calls (logging, recipe building, meal suggestions) send name (if set), today's targets/totals, date, and library item names/macros, but not the specific condition/diagnosis label — that only appears in the GBM-specific features (Monthly Summary, Research Digest) where it's actually the point.

## Known Outstanding Items

- Health Connect bridge (Android) — still not started, deliberately parked.
- Backup/cloud vs local — discussed, not acted on beyond confirming the existing export-reminder system is genuinely sufficient for now; a full cloud migration remains a real, separate decision if ever wanted.
- Documentation (this file, README.md, TECHNICAL.md, user-guide.html, changelog.html) had fallen behind again by the time of this entry — all five were stuck at v3.10.510 while the app had reached v3.10.563. Caught up in this pass; the intent going forward is to keep documentation current per-session rather than letting the gap compound.

**Carried forward from Phase 17, still unresolved:**
- v3.10.472–499 not individually documented (gap predates this entry, not addressed here)
- RingConn sleep backfill only covers 19 Aug 2025 onward — older history not yet corrected
- Same-day multi-session dates (RingConn) silently keep only the later session
- A `bump_and_deploy.sh` version-revert was observed once in Phase 17 (deployed v3.10.508 briefly reverted to v3.10.499 in the working tree before the next deploy) — root cause never identified, not seen recurring since, not actively investigated this session either
- AI photo-reading occasionally misreading polyols rows on certain label layouts — the *manual* fibre/polyols entry gap this caused is now fixed (see Fibre & Polyols above), but the underlying AI vision-reading accuracy itself hasn't been revisited
# MaxedHealth Changelog — Phase 17, continued (v3.10.472 – v3.10.510)

**v3.10.472–499 were never individually documented here** — same gap this file already flags for Phase 13-14, now extended. What follows covers 500–510 in detail, plus a related RingConn pipeline fix and backfill that sit outside `maxhealth.html`'s own versioning entirely.

## Itemized Ingredient Editors — Today's Log + History

- **Real per-ingredient editing for multi-item log entries**, replacing an aggregate-only form that had no way to touch individual ingredients at all — add, remove, or edit any single item; totals are now *derived* from the items list on save rather than typed separately, closing a drift gap where the two could quietly disagree.
- **Extended to History**, which previously had zero awareness of itemized entries whatsoever — worse than Today's old single-item-only sync. Same contract, kept as a deliberately parallel implementation (keyed by day+entry index rather than merged with Today's id-based functions) rather than forcing a shared abstraction that wasn't worth the added indirection.
- **Amount-driven auto-scale** — editing an ingredient's Amount field rescales its macros proportionally from a captured baseline, the same pattern already used elsewhere in the app. A direct macro edit is treated as a manual override and doesn't reset that baseline, so a later Amount edit still scales from the original point, not from whatever was just hand-typed.
- **New: "Scale entire entry to X%"** — one input, one Apply, scales every ingredient in the entry at once (e.g. "I made a big batch but only ate 60% of it"). Deliberately scales from each item's stable baseline rather than its current on-screen value, so applying it twice with different percentages (50% then 70%) gives 70% of the *original* amounts, not 70% of the already-halved ones.
- **New-ingredient baseline gap, closed** — an ingredient added via "+ Add ingredient" had no baseline to scale from at all; typing an Amount did nothing until macros were also manually typed in, and if Amount was typed last, it silently did nothing even then. Now retroactively captures a baseline as fields get filled in, in either order, and locks it in only once a genuine rescale happens (a typed amount that actually differs from what's captured) — so it never freezes mid-entry with some fields still sitting at zero.
- **Pre-log preview editor** got the matching bare-number fix separately (see below) — same underlying gap, different screen.

## Library-Meal Portion Misparse — Critical Fix

- **Root cause of a genuinely alarming real incident**: a saved multi-item meal stores its portion as a string like `"1 serving"`. Re-matching it later via text search extracted the leading digit with a raw `parseFloat`, silently treating "1 serving" as **1 gram**. Reproduced directly: typing "creamy" matched a saved "Creamy Chicken and Veg" meal, the Amount box showed "1", and the resulting figures (2536kcal / 281g protein) looked like an entire day's macros crammed into one gram — correctly triggering the impossible-mass warning, which is what surfaced it.
- Fixed at all five call sites to use the existing strict gram/ml/kg/l-unit extractor instead of a raw `parseFloat`. Also un-conflated two previously-merged conditions: a "these are per-100g values" note that should only ever appear on genuine label-path items was showing on any item with no parseable size, meal-path included — and a hardcoded "100g" fallback in the accompanying warning now reads the real computed baseline instead.
- **Companion fix**: the itemized editors' own Amount field was, correctly, using that same strict extractor — but that meant a bare number like `"50"` (no unit) was rejected even though in this specific interactive context it unambiguously means grams. Added a local bare-number-means-grams fallback scoped to just this field, without loosening the shared extractor itself, which must stay strict everywhere else for exactly the "1 serving" ambiguity above.

## Photo/Label AI Pipeline Unification

- **Removed the manual Meal/Label toggle entirely** — the AI's general system prompt already had full photo-classification logic to self-detect labels vs. meals, making the toggle redundant. This also removed a pre-flight gram-check gate that only fired if the toggle had been manually set to "Label," which was the root cause of a real reported bug: forgetting to tap the toggle silently bypassed the AI's own portion-confirmation flow. ~140 lines of now-dead code removed alongside it.
- **Fibre/polyols visibility added to the single-item preview** — previously only shown after logging, not before.
- **New AI-assumed-amount detector** — flags when the AI filled in a gram figure but its own accompanying message was still asking a clarifying question (e.g. "assumed 28g — correct me if wrong"), so a genuine guess can't be mistaken for a confirmed value. Initially built for label-path items only; extended to meal-path (photos of food, not labels) after confirming the same gap existed there too.

## Dashboard Fixes

- **Weight trend staleness** — the 14-day trend classification was computed purely from finalized history, which excludes today's entry until midnight rollover, while the headline weight figure above it was already live. The trend label could describe yesterday's rate sitting directly under today's fresh number. Now folds today's live entry into the window whenever it's newer than history's.
- **Carb Zones tooltip made condition-aware** — was 100% static HTML with "GBM Protocol" and a metformin/MCT assumption hardcoded regardless of who's viewing it. A real cross-user bug: a second user on a different condition (e.g. Jill) would see Pete Spence's own diagnosis-specific framing presented as if it were theirs. Now swaps to generic wording based on the condition setting, matching the existing pattern already used for hiding the Monthly Summary/Research Digest sections from non-GBM users.

## Fibre/Polyols — Text Search vs. Barcode Parity

- **Traced from a real incident**: a product logged via name search showed no polyols figure at all, despite the physical label clearly listing 17g/100g. Initial suspicion was the AI vision label-reading pipeline (which already has a documented mandate, and a known-failure-mode note, for exactly this kind of miss) — but this item had actually come through Open Food Facts text search, a completely separate code path that never touches the AI at all.
- Root cause: OFF text search's results renderer never captured `fibre_100g`/`polyols_100g` into the result item's data attributes in the first place, unlike the barcode-scan path, which already handled both correctly. `selectFoodResult()` correspondingly had nothing to read back out.
- Fixed to match the barcode path's field coverage exactly, including switching the amount screen's per-100g line from `textContent` to the same styled 🍬 polyols callout the barcode path already renders via `innerHTML`.

## RingConn Sleep Date-Shift Bug — Found, Fixed, Backfilled

- **The bug**: `ringconn.py`'s sleep extractor deliberately shifted any session starting between midnight and 04:00 back to the previous calendar date, on the assumption that a late bedtime belongs to "last night." RingConn's own app doesn't apply this adjustment at all — it labels a session by the raw calendar date of its start time, full stop. Confirmed directly against a real side-by-side comparison: a 01:01 bedtime that RingConn's own app called "Aug 19" was landing in `combined.csv` under "Aug 18."
- **Scale**: checked against a full year's raw export — 173 of 348 sleep sessions (essentially half) had a pre-04:00 bedtime and were affected. 101 of those involved back-to-back affected nights, creating genuine multi-day cascades, not isolated one-off misdatings.
- **Fix**: the shift logic removed outright; the extractor now trusts RingConn's own raw date.
- **Backfill**: a plain pipeline re-run would *not* have corrected the already-wrong dates — the pipeline's field-level source-precedence merge only overwrites a field when a *higher-priority* source provides it, and RingConn re-processing its own already-top-priority field against a date already attributed to "ringconn" doesn't count as higher-priority, even though the underlying value had changed. Corrected instead via a standalone script working directly from the raw export as ground truth, covering all 272 real dates in that export's range: 110 had an actual value correction, 162 were re-confirmed already correct. Deliberately did not touch anything outside the sleep fields, and preserved a genuine, pre-existing, unrelated limitation found along the way — same-day dates with two independent full sleep sessions currently keep only the later one, silently dropping the earlier. Not caused by this bug, not something this backfill changed.
- **Not yet covered**: anything before the export's own range (19 Aug 2025). Older exports could extend the backfill further back if wanted.

## Inbox Retention Cleanup

- `data/inbox/old/` had no retention policy at all — every processed export accumulated indefinitely. Added an automatic 180-day trim, deliberately far longer than the 7-day backup rotation: these are raw source exports, the only way to re-derive history if a future extractor bug is ever found — exactly what made the RingConn backfill above possible at all. A short retention here would have made that impossible for anything older than the window.

## Known Outstanding Items
*(See the Phase 18 entry at the top of this file for the current list — the items below were resolved or carried forward there during this documentation pass, rather than duplicated in two places.)*

# MaxedHealth Changelog — Phase 17 (v3.10.466 – v3.10.471)

Continuation of the same session, spanning three threads: a genuinely useful debugging tool built specifically to solve a real, previously stuck device (Jill's), a long-standing structural bug finally caught by that same tool, and a substantial two-part feature (personalised walking effort, then real trend-based auto-adjustment) that grew out of what started as a simple question about pace classification.

## Remote Diagnostics — App Health Check + `/system-status`

- New server endpoint (`/system-status`) surfaces the real auto-update log, crontab contents, and whether `crond`/`server.py` are actually running — added specifically so a stuck device could be debugged **remotely**, without needing Termux command-line access on the affected phone at all.
- Wired into the existing "🩺 Run health check" button — one tap, then "📋 Copy all text" to send the output to whoever's helping debug.
- **This is what actually solved Jill's device.** Confirmed, end-to-end, on a real device that had been stuck for days: the health check first correctly showed `crond` wasn't running at all (root cause, not yet fixed at that point), then — after `crond` was restarted — showed the real log entries proving auto-update genuinely worked on its own at the very next scheduled tick, jumping five versions in one clean, unattended update.

## Long-Standing Div Balance Bug — Found by the Tool Above

- Building the health check's own version-sync check surfaced a real, pre-existing structural bug: a duplicate, prematurely-placed `</div><!-- /app-wrapper -->` closing the app's outermost wrapper in the *middle* of the document, with the correct matching close already existing at the true end. Different comment styles between the two suggest this had been sitting there for a while, silently — not something introduced this session.
- Found via a proper stack-based HTML parser after simpler counting methods (including the crude raw-text `grep` this project had been relying on) proved unreliable — a raw count happened to look "balanced" for a long time purely because HTML-shaped text sitting inside JS strings was being counted alongside real markup.
- **`bump_and_deploy.sh`'s own safety check had the identical blind spot** — it used the same unreliable raw-count method, meaning it could produce both false-positive aborts (blocking a genuinely correct fix, which is what actually happened) and, more concerningly, false-negative passes if JS-string content ever happened to mask a real imbalance. Fixed to use the same script-stripping method as the in-app Health Check, so the two can never disagree with each other again.
- Also fixed the exact two-places version drift `bump_and_deploy.sh`'s own header comment already warned about — the `APP_VERSION` const had gone stale independently of the display text it's supposed to stay in sync with, for reasons unrelated to the script (a file was shared before a manual edit was made).

## Setup Wizard & Advanced Tools Reorder Bug

- "Redo Setup Wizard" made hideable and reorderable, matching every other settings section — previously a standalone block using different, ad-hoc markup.
- **Found a real bug affecting three existing sections**: Log Mutation Debug, Save Debug Trace, and Settings Change Log were all genuinely, correctly positioned inside the fixed "⚠ Advanced — Troubleshooting Tools" box in the source HTML, but were missing from that box's reorder-exclusion list. The generic reorder system was picking them up and physically moving them out of Advanced Tools via `appendChild` — not hidden, just relocated somewhere nobody would think to look for a debug tool. All three now correctly excluded, matching their siblings.

## Personalised Walking Effort & Activity Level

- **Real research first**: confirmed there's no single correct universal walking-pace threshold for "brisk"/moderate effort — even the AHA (≥2.5mph) and CDC (≥3.5mph) officially disagree, explicitly because it depends on individual fitness. Multiple peer-reviewed studies warn fixed thresholds "may misclassify" intensity for exactly this reason.
- **Activity Level is now a genuine, persistent Profile setting** — previously it was asked once during onboarding, used for a single TDEE calculation, and then discarded entirely with no way to view or change it afterward.
- **New fitness-adjusted walking pace bands**, four tiers anchored on the real AHA/CDC figures rather than arbitrary numbers, replacing a single fixed scale that had the same "brisk" pace meaning completely different things depending who was walking.
- **Found and fixed a real internal inconsistency**: two separate, independently-maintained pace-classification systems existed in the code (one for auto-suggesting an effort label from a logged pace, one for the reverse) and had drifted to disagree with each other even before personalisation was added. Both — plus two further consumers found along the way — now read from one shared source.
- **Full Formulas & Technical Reference documentation** added, including an honest flag about one related thing *not* yet fixed: MET calorie values for walking aren't pace-adjusted the same way yet, so calorie estimates outside the "moderately active" tier may be very slightly off until that's addressed too.

## Activity Level Auto-Switch

- Directly building on the above: the app now detects **sustained, genuine change** in real step-count data and adjusts Activity Level automatically, rather than requiring it to be manually kept up to date as someone's real fitness changes.
- Reuses the app's own existing TDEE step-count thresholds (already closely aligned with the real, widely-cited Tudor-Locke & Bassett 2004 classification, independently confirmed via research) — one consistent definition of each tier, not a second one invented separately.
- **Deliberately more noise-resistant than the existing weight/goal auto-switch it's modelled on**: rather than requiring every single day in the check window to individually match (which a single low-step rest day would break even during genuine sustained improvement), it checks whether the smoothed 30-day rolling average, computed as of each of the last N days, has consistently agreed on a different tier throughout. Proven with real simulated tests: a genuinely noisy but sustained improvement correctly triggers; a stable match correctly doesn't; a short vacation-week spike correctly gets recognised as not sustained rather than falsely triggering a permanent change.
- Improvement gets a real celebration (matching the existing ketosis-streak-milestone pattern); a decline gets a plain, factual notification only — informed either way, celebrated only when it's genuinely something to celebrate, as specifically requested.
- New Activity Level History, mirroring the existing Condition History pattern exactly, so a later auto-switch (or manual change) never retroactively distorts how older logged days get interpreted by AI reports.
- **Two genuine pre-existing bugs found and fixed along the way**, unrelated to what was being built: `mh_notif_autoswitch` was being included in backups but never actually restored from one, and Condition History's own textarea was never populated when Settings first loaded — only ever got filled in as a side effect of something else happening first, meaning a fresh visit could show blank even with real history genuinely stored.

## Known Outstanding Items
- Health Connect bridge app (Kotlin) written but not yet built/run in Android Studio — first build pending
- Heylo crackerbread camera/photo logging reported as "hit and miss" — not yet investigated
- MET calorie values for walking are not yet pace-adjusted the same way the effort-label bands now are (see above)
- Phase 13 and 14 changelog entries were never written up in detail — the live version history has real gaps this file doesn't cover
- Garmin data quality comparison against RingConn/Withings not yet completed
- Coeliac disease and iron deficiency conditions researched and evidence-graded, but deliberately not added — would need ingredient-level allergen flagging and nutrient-timing features respectively, not just another dropdown entry

# MaxedHealth Changelog — Phase 16 (v3.10.451 – v3.10.465)

A single very long session covering three distinct threads: real bug fixes found through direct use (recipe substitution, the polyols/net-carbs feature end-to-end, several condition-aware calculation gaps), a genuinely new feature (site-wide search), and the start of Health Connect integration (server-side complete, native Android bridge app written and pending its first build).

## Recipe & Substitution Fixes

- **Substitute picker pre-fill bug** — tapping the swap icon on a flagged, unmatched ingredient pre-filled the search box with the entire raw label ("⚠️ mascarpone cheese — add nutrition") instead of just the food name, finding poor or no matches until manually retyped. Fixed, scoped specifically to flagged rows so ordinary resolved ingredients with their own parenthetical text aren't mangled by the same stripping.
- **Missing "+ add ingredient" button** — the recipe builder had no way to add a new ingredient to an already-created recipe, only during initial creation. Added, reusing the existing library-add mechanism.
- **Recipe ingredients/steps could silently blank out entirely** — a single malformed ingredient (missing its name field) threw an uncaught exception mid-render, and since the list only gets assigned to the page after the whole render completes, one bad item took the other eleven down with it with no visible error at all. Now wrapped so a broken item shows as a specific, diagnosable red error row while the rest of the list renders correctly — this is what actually caught and fixed the real corrupted ingredient (mascarpone) once deployed.
- **Library/substitute picker had no reachable way to cancel** — the Cancel button existed but sat below a potentially long, scrollable list with nothing visible above it. Added a sticky close button pinned to the top regardless of scroll position, plus tap-outside-to-close.

## Net Carbs & Polyols (UK/EU labelling)

- **Polyols now genuinely subtracted from net carbs**, not just fibre — matching UK/EU convention and directly relevant given how often ketogenic recipes lean on erythritol and similar sweeteners. Sourced only from real barcode/OpenFoodFacts data (`polyols_100g`), never AI-estimated from photos or descriptions, matching the same accuracy principle fibre already followed.
- Threaded through the full chain: barcode extraction → recipe ingredients → the actual logged entry (found and fixed a pre-existing gap here too — fibre itself was missing from the final logged object at one specific step).
- **Found eight separate places checking raw carbs directly** instead of the net-aware calculation once this was built out properly — most visibly the ketosis status badge itself, which could show "BORDERLINE" in gross mode and "DEEP KETOSIS" in net mode for the exact same day. Also fixed: the "Ketosis check" and "What's remaining?" saved prompts, the carb-ceiling-hit warning, a second separate remaining-carbs calculation, History tab's per-day compliance indicator, and two internal streak/pattern-compliance checks.
- Made polyols clearly visible at the moments that matter — barcode scan screen, save-to-library confirmation, logging confirmation, and a small icon on recipe ingredients that carry them — rather than buried as one more number in a long stats string.

## New Conditions: Migraine & Cluster Headache

- Added as full conditions alongside GBM/Epilepsy/Strict Ketosis, following real research: genuine RCT evidence for migraine (including a 74% vs 6% responder-rate trial), earlier-stage but real published evidence for cluster headache (open-label trials, a formal Italian expert consensus statement). Both explicitly framed as promising rather than established standard-of-care, unlike GBM/epilepsy's more settled evidence base.
- This required going well beyond the Settings dropdown — found and fixed **8 separate places** where GBM/epilepsy get special treatment for the shared "≥65% fat therapeutic ratio" trait, updating all consistently. One related spot was deliberately left untouched: an Insights panel that mixes the shared fat-ratio trait with claims specifically about *GBM tumour-outcome research*, which doesn't transfer to a headache condition and would have been actively misleading to extend.
- **Found `CONDITION_META` (the table that actually drives the AI's condition-awareness across Ask AI, AI Reports, and trends) was missing migraine, cluster headache, *and* `recomp`** — meaning AI advice was silently generic for all three despite the UI looking condition-aware. Fixed with real evidence citations for each.
- **Found a second, independently-hardcoded condition→ceiling mapping in onboarding** that only covered 2 of what are now 9 conditions — same class of drift bug as `CONDITION_META`, fixed by routing through the same shared function instead of a second copy.
- **Onboarding expanded from 4 to all 9 conditions** — previously only offered GBM, T2 Diabetes, Recomp, and General, meaning Epilepsy, Strict Keto, T1 Diabetes, Migraine, and Cluster Headache were only reachable by switching later via Settings, with no indication that was needed.
- Added `recomp` (Body Recomposition) to `CONDITION_META`, `strict_keto` and `recomp` to a few other spots — pre-existing gaps found while doing this work, not new to this session.

## Condition History & Period-Aware AI Reports

- New "Condition History" tracking, following the exact same proven pattern as the existing Weight Phase History feature — auto-logs on every genuine condition change (Settings and onboarding both), so a later condition change can't retroactively distort how old, already-logged days get judged.
- `buildPatientContext()` can now filter to a specific condition's real period(s) and judge those days against that period's own actual carb ceiling, rather than whatever's set today — while the default (no filter) behaviour stays exactly as it was, since that's the right choice for a whole-history report.
- Rather than a dropdown selector, **Ask AI and Full Summary are now period-aware automatically** — whenever more than one condition has genuinely been used, a real date-ranged "Condition Periods" block gets included in the prompt (silently absent otherwise), and the AI does its own grouping/comparison from the day-level data it already receives. Supports genuinely natural questions like "compare my general and migraine periods" without needing an explicit filter UI at all.
- Fixed a same-day correction bug (mis-clicking a condition and correcting it moments later created two spurious log entries for a period that never really existed) and a `NaN%` compliance bug that would have appeared for a condition-filtered period with zero logged days.

## Site-Wide Search

- New 🔍 icon in the header, always accessible, opens one search box covering Library, Recipes (the same underlying view, so genuinely one search), Saved Prompts, and a curated list of every real Settings section across all three sub-tabs (Manage/Customise/Import).
- First version missed the entire Import sub-tab and had two mislabelled settings entries, found and fixed once real search terms (Withings, Zepp, android) came back empty — added keyword synonyms for device/brand names so those terms correctly surface the right settings section even though the section's own display label doesn't contain them.
- Fixed collapsed sections being unreachable from search results — `scrollIntoView` on a `display:none` element does nothing, so a search result for a currently-collapsed section would silently appear to do nothing at all. Now expands the section first if needed.

## Health Connect (Android) — server-side complete, native app pending first build

- Researched and confirmed the real current Health Connect SDK (`androidx.health.connect:connect-client:1.2.0-alpha05`) — this only exists as a compiled native Android API, no web or shell-accessible path at all, confirmed before writing any code rather than assumed.
- **Server-side fully built and tested**: new `extractors/health_connect.py` (parses the bridge app's JSON export, same conventions as every other extractor), a `server.py` branch recognising the export filename with matching diagnostics for near-misses, and full registration in `update_health.py`'s device list and precedence tables — deliberately lowest priority in every list, since it's an aggregate of whatever a device's own more detailed export would already provide directly.
- **Native bridge app written** (Kotlin) — minimal by design per the explicit "invisible, no overhead" requirement: request Health Connect permission once, then a WorkManager background job syncs hourly with no further interaction needed. Reads steps (via aggregate, avoiding phone+watch double-counting), sleep, HRV, and weight; writes to the public Downloads folder via MediaStore, landing exactly where Termux's existing pipeline already looks.
- Confirmed (researched properly, not assumed): phone-based step counting flows into Health Connect automatically on Android 14+ with zero extra work, so this covers phone-only users for activity tracking without a separate code path. Sleep/HRV/SpO2 remain a genuine hardware limitation — no software approach changes that.
- **Not yet done**: the actual Android Studio build — written but never compiled, same status the Wear OS project reached before being discontinued. This needs laptop access to progress further.

## Other

- **Wear OS watchapp discontinued** — decided against building a second, separate watch interface given the existing Zepp/Amazfit one already does the job well. Kept as accurate historical record in this changelog rather than removed, since the work and its lessons (the same field-shape bug caught before being repeated) are still genuinely useful reference. GitHub repo archived, local project folder cleaned up.
- Investigated (properly researched, not guessed) nutritional evidence for four other candidate conditions — coeliac disease and iron deficiency both have very strong evidence but need a genuinely different kind of feature (allergen flagging, nutrient-timing) rather than fitting the carb-ceiling model, so both stay parked rather than force-fitted in.

## Known Outstanding Items
*(See the Phase 17 entry at the top of this file for the current list — the items below were carried forward there during this documentation pass, rather than duplicated in two places.)*

# MaxedHealth Changelog — Phase 15 (v3.10.273 – v3.10.450)

Phase 13 and 14's detailed entries were never written up (see Known Outstanding Items below) - this entry starts from where the live version history resumes. A genuinely large session spanning wearable development, several rounds of real-device bug hunting on both Pete Spence's and Jill's phones, and a fair amount of infrastructure most of which won't be visible as a feature but fixes something that was quietly wrong underneath.

## Wearable Development

**Zepp OS watchapp — first real working build**
- Found and corrected a run of wrong assumptions from earlier, undocumented sessions: a phantom `@zeppos/router` package that was never real, `@zeppos/ui` used instead of the actual runtime module `@zos/ui`, an `app.json` written against the wrong schema version, and a TypeScript codebase built against Zeus CLI, which only compiles plain JavaScript
- Converted the whole watchapp to plain JS, corrected `app.json` against the real v2 schema and the Amazfit Active 2's actual device data, and got a genuine first successful `.zab` build
- The `/pattern-signals` field shape assumed while building this (flat fields like `breakfastStart`) didn't match the real server response at all — corrected against a live `curl` test of the actual endpoint

**Wear OS data layer — same field-shape bug caught before it was repeated**
- Room database, repository, and sync manager built for the Galaxy Watch companion, then found to have the identical wrong-field-shape assumption as the Zepp side above
- Rebuilt to store the real response as a single JSON blob rather than modelling nested objects across flat SQL columns, since this cache is always read/written as a whole and never queried field-by-field
- Configurable phone IP added rather than hardcoded `127.0.0.1` — a watch and phone are separate devices, so localhost can never reach the phone's own server no matter how the earlier Zepp build had assumed it would
- UI (Compose, Material3, `TransformingLazyColumn`) built against verified current API samples rather than trained-memory assumptions, given how much the Wear Compose library has moved since
- **Subsequently discontinued** — decided against building a second, separate watch interface when the existing Zepp/Amazfit one already does the job well. This section is kept as an accurate record of the work and its lessons, not as a sign it's still planned.

**Pattern-learning backend actually deployed for the first time**
- `pattern_detector.py` and the `/pattern-signals` endpoint had been built and tested in prior chat sessions but never actually copied to the live device or wired into `server.py` — every real call had been silently returning "unknown endpoint" this whole time
- Deployed properly, confirmed live against real logged data
- Its hardcoded "Day 2" / "Day 5" framing replaced with honest reporting of what's actually available — a `signals_available` breakdown and a real day count computed from the real data span, rather than an assumption baked into the response regardless of how much history genuinely exists

## Nutrition & Recipe Accuracy

**Recipe totals — a million-kcal chicken breast**
- A library entry with `portion: "1g"` (should have been `"100g"`) caused a 1000× scaling error for any recipe using it — root cause was the portion-scaling math faithfully doing what it was told against a mislabelled portion, not a logic bug
- Fixed with a plausibility check (nothing real exceeds ~900 kcal per gram) that falls back to 100g and warns, and the scaling logic itself consolidated into one shared helper — previously triplicated across three separate save paths, which is exactly how a bug like this can exist in one place, get "fixed," and still be live in the other two

**Portion sizes missing from logged history**
- Multi-item meal entries never saved a portion size at the top level even though each individual food item carried its own — fixed at the source for new entries, and the history display now falls back to the item's own amount for anything logged before the fix, so old entries get portions too

**Ingredient substitution — built, then redesigned after a real near-miss**
- Full substitute system built across the recipe builder, Cook Mode, and suggested-meal combos, sharing one picker flow rather than three separate implementations
- First version auto-matched the closest library item and asked for confirmation — a fuzzy match suggested peanut butter as a substitute for dairy butter (100g vs 2,200+ kcal worth of fat, sharing only the word "butter"), which is a category of mistake a human choosing from a real list can't make regardless of how good the matching heuristic is
- Redesigned to open a genuine searchable picker instead of auto-matching, with an online-search fallback when nothing in the library fits
- Nut butters (peanut/almond/cashew) now correctly cross-match each other as reasonable substitutes, while cocoa butter and shea butter stay excluded — grouping every "___ butter" together would have just been a different flavour of the same mistake

**Save-to-library silent overwrite**
- Checking a box meant to save a new item could silently overwrite a completely different, differently-named existing item if it fuzzy-matched — the box defaulted unchecked with a small warning line, but ticking it without noticing the warning meant an unrelated library entry's real data got quietly replaced
- Routed through the same careful compare-and-choose modal the manual Add Food form already used (real side-by-side values, an explicit "same thing, overwrite" vs "different product, save separately" choice) rather than patching the separate, less careful mechanism that had grown up around meal logging specifically

## Data Import

**Withings import — the same hardcoded name existed in two separate files**
- `server.py`'s Download-folder scan and `extractors/withings.py`'s own detection both independently checked for the literal filename fragment `data_pet_` — Pete Spence's own name, from testing only ever against his own export
- Real Withings exports are named `data_{account name}_{timestamp}.zip`, so this silently rejected every other family member's genuinely correctly-formatted export
- Both fixed to match the real filename shape rather than any specific name; the in-app Sync log now also reports exactly what it found and why when nothing matches (name, size, whether it opens, whether it looks like a genuine export the pattern just missed) rather than a bare "nothing found"

## Auto-Update Infrastructure

**Devices could silently run stale code indefinitely**
- No mechanism existed for an installed device to ever catch up with GitHub on its own — every fix required someone to manually `git pull` on that specific device, which is exactly how one real device ended up running code from before several rounds of fixes without anyone realising until symptoms stopped making sense against what was supposedly already fixed
- New `mh_autoupdate.sh` checks GitHub every 30 minutes via cron, and once immediately on every boot — converges via `git reset --hard` rather than attempting a merge, appropriate for a pure end-user device that should never carry real local edits
- `mhstart` itself had a path bug — `cd`'d one directory too shallow, which silently failed and fell through to running from whatever directory the caller happened to already be in, rather than failing loudly. Fixed, and properly installed to `$PREFIX/bin` so it works from anywhere rather than only when someone happens to already be in the right folder
- All of the above folded into `setup.sh` itself, so every future fresh install gets working auto-update and a correct `mhstart` automatically, not just the devices patched by hand this session

## Accuracy & Consistency Fixes

**Vitals score contradicted the pattern-learning backend on the same data**
- Scored HRV against a fixed 80ms population target while the pattern-learning backend elsewhere correctly judged the same HRV reading as "Excellent" relative to the person's own baseline — the same number was being called both "Low" and "Excellent" in different parts of the same app
- Fixed to score HRV against the person's own recent baseline (last 30 readings), consistent with how the backend already treats it

**AI Reports — a fabricated fat target and a missing "today"**
- A hardcoded `247` was presented as a real personal fat target any time the actual target was missing — the combination it produced (247g fat, 1550kcal total) was internally impossible on its own, since 247g of fat alone is over 2,200kcal. Now reports honestly that the target isn't set rather than inventing a number
- Separately, this app only folds "today" into tracked history via a nightly rollover — so a question asked mid-afternoon about "today" had no way to see today's real entries at all, and silently answered using a multi-day average (or the most recent *completed* day) mislabelled as if it were today's actual total. Fixed with an explicit, clearly-labelled block pulled live from the same in-progress log the dashboard itself reads from

**Diabetes condition silently did nothing to nutrition targets**
- Onboarding saved the diabetes condition as `'t2d'` while every other check in the app looked for `'t2_diabetes'` — anyone selecting diabetes at onboarding got none of the diabetes-specific behaviour anywhere, permanently, from a string that simply never matched
- Separately, changing condition later via Settings never cascaded to update the carb ceiling at all, despite the dropdown's own label text explicitly promising a specific number ("Type 2 Diabetes — Low carb ≤100g")
- Both fixed; the ceiling-defaults mapping extracted into one shared function used by both onboarding and the Settings change handler, so the two can't drift apart from each other again the way they just had

**Patterns card's "not enough history" message was actively misleading**
- Fired regardless of *why* nothing was found, including against a 790-day total history — which said nothing about how many of those days also had paired wearable sync (sleep, steps), which is what these specific comparisons actually need
- Now reports the real counts for each requirement separately, so the actual bottleneck (usually wearable sync coverage, not total logging history) is visible rather than a generic message that looked wrong against a large total day count

## Saved Prompts Library

- Replaced two separate sets of hardcoded quick-question pills (the Log-tab chat bar and the Reports-tab Ask AI panel) with one unified, searchable, editable library — add, edit, delete, all shared between both locations rather than two systems that could drift apart
- Voice dictation added for typing new prompts, reusing the existing water-logging voice pattern rather than a new implementation
- Real usage tracking added — prompts sort by how often they're actually run, with visible sort controls (Most used / A–Z / Recently added) rather than an invisible default
- Went through a few rounds of direct revision based on real use: a pin/unpin mechanism was built, then replaced entirely by a single "Browse" entry point once it became clear that showing several pills in a row just competed for attention with everything else on screen — sometimes the simpler version is the right one, not the more configurable one

## Known Outstanding Items
*(See the Phase 16 entry at the top of this file for the current list — the items below were resolved or carried forward there during this documentation pass, rather than duplicated in two places.)*

# MaxedHealth Changelog — Phase 12 (v3.10.202 – v3.10.272)

The biggest single session in the app's history — roughly 70 versions. Most of it was infrastructure and reliability work that doesn't show up as a visible feature, but fixes a genuine, sometimes months-old bug underneath something that looked fine on the surface.

## New Features

**Log food to a past day**
- History → any day → "🍽 + Add food to this day" routes into the exact same AI-parsing pipeline used for today's logging (text, photo, barcode, library — all of it), with a persistent yellow banner making clear which day is being targeted
- Recalculates that day's totals from its full log automatically — no manual arithmetic
- Solves the recurring problem of a missed or mis-logged item on a previous day requiring the day's totals to be hand-adjusted

**Multi-AI consensus check**
- "🔍 Verify across 3 AIs" on any logged item — Claude, Gemini, and ChatGPT independently estimate the same food in parallel via the Cloudflare Worker, one round-trip
- Deliberately does not average or pick a winner by default — three estimates agreeing closely is a genuine reassurance signal; disagreeing by more than 25% on calories is flagged as "find a real label, don't trust any of these"
- Each provider's own numbers are checked for internal consistency (protein×4 + fat×9 + carbs×4 against its own stated kcal) — catches an estimate that's internally sloppy even before comparing it to the others
- Per-provider checkboxes let you exclude an outlier before applying an average to a single item; works per-item within a multi-item meal, not just on a whole plate at once
- Requires Gemini and OpenAI API keys configured as Worker secrets in addition to the existing Anthropic one — genuinely free on Gemini's tier for occasional use, small real cost on OpenAI (no persistent free tier)

**Activity Credit Balance**
- New card in Insights → Trends: rolling-window (default 14 days, adjustable) tracking of exercise calorie credit earned vs actually eaten back, built from real stored history (`day.exercises`, already precomputed), not an estimate
- Goal-aware interpretation — under 25% unclaimed is treated as noise regardless of goal; above that, framed differently for maintain (a real compounding deficit), gain (quietly eating into the intended surplus), and lose (expected in moderation, flagged if it's grown larger than intended)
- Exists because a single day running under an exercise-boosted target is genuinely harmless, but the same pattern repeating often compounds into something real without ever tripping a single day's warning

**Phase-aware calorie context**
- Remaining Today now distinguishes being under the exercise-boosted target (harmless unclaimed activity credit) from genuinely being under the base target (real under-eating) — the two were previously indistinguishable from the headline number alone
- Worded differently depending on the actual Goal/Phase setting (maintain/gain/lose), since "under the boosted number" means something different for each

**440ml Pint water preset**
- Added alongside Glass/Can/Bottle/Custom on the hydration bar

**find_orphans.py**
- Standalone maintenance script (not part of the app) — flags functions/variables that appear only at their own declaration and never anywhere else, plus duplicate function names, as a manual review checklist
- Deliberately a heuristic, not an auto-delete tool — a name showing up here can still be genuinely needed (a reserved feature, something called in a way static text-matching can't see)

## AI Infrastructure — found this session, most of it long-standing

**Cloudflare Worker was silently overriding every request**
- Hardcoded `claude-haiku-4-5` and `max_tokens: 500` regardless of what the app actually requested, for every proxy-routed call — meaning anyone without their own API key (the cloud version's default) had been running on a smaller model with a harder token cap than any individual feature was ever designed around
- Fixed to forward `model`/`max_tokens`/`tools` from the actual request, falling back to sensible defaults only if the client omits them

**Direct-API-key path was structurally broken since it was built**
- Missing the `anthropic-dangerous-direct-browser-access` header required for any direct browser call to Anthropic's API — without it, every direct-key request was silently blocked as a CORS violation, surfacing only as a generic, unhelpful "Failed to fetch"
- Separately, `callHealthAI()`'s direct-Claude branch had **no request body at all** in the fetch call — sending Anthropic a genuinely empty request every time a direct key was configured, which Anthropic reported back as "zero-length, empty document"
- Both fixed; this was likely the actual cause of "Check what fits from my library" failing intermittently for weeks, previously misdiagnosed as an exposed/invalid key several times over

**Wrong localStorage key bypassing the shared AI helper**
- Two functions (`suggestMealFromLibrary`, `_processLabelEstimate`) read `mh_api_key` (with an underscore) instead of the actual key name `mh_apikey`, so they always behaved as if no direct key was configured regardless of what was actually set — consolidated onto the same shared `callHealthAI()` helper every other AI call already used correctly

**App Health Check now tests the real function**
- The AI-connection live test was previously a separately hand-built request that happened to be constructed correctly — meaning it could never have caught the missing-body bug above, since it never actually exercised the buggy code path
- Now calls `callHealthAI()` directly, plus a new live multi-AI test section

**Gemini model — settled after two wrong guesses**
- First attempt (`gemini-3.5-flash`) hit genuine "high demand" 503s; switched to `gemini-2.5-flash` believing an older model would be more stable — turned out Google was actively restricting 2.5-flash for new API keys ahead of its official shutdown date
- Reverted to `gemini-3.5-flash` (confirmed current GA flagship, Google's own recommended replacement), with one automatic retry on a 503 after a short delay, matching Google's own documented guidance for this error class

## Data Pipeline

**Sleep data stalled at a fixed date for over a week**
- A folder restructure moved `server.py`/`maxhealth.html` a level deeper without updating the extractors path inside the copy of `update_health.py` that Sync Now actually calls — every sync silently found zero extractors and reported "no data" without ever touching the real ones
- A second, older, disconnected copy of `update_health.py` existed one level up, resolving `BASE` to a completely different (non-existent) data folder — deleted; one canonical script remains
- Amazfit/Zepp AES-256 decryption fixed — `zipfile` cannot decrypt AES regardless of password; `pyzipper` required. Password flows correctly through the existing CLI arg / `ZEPP_PASSWORD` env var plumbing once the decryption library itself was correct

**Cloud deployment found ~100 versions behind**
- `git push` had been silently failing with no error surfaced for an extended period — added explicit push verification to `bump_and_deploy.sh` (confirms local HEAD matches `origin/main` after pushing, not just that the command ran without throwing)
- `.gitignore` added for `__pycache__/`, backup files, and trash artifacts, which had been accumulating as noise in every `git status`

## Logging & Library

**Whole-item scaling bug**
- A food with a non-numeric amount (e.g. "1 can") defaulted its scaling baseline to 100g — correcting the displayed amount to the item's true size (e.g. 440ml) multiplied already-correct total values by the wrong factor instead of leaving them alone
- Fixed to also check the food's name for an embedded size before falling back to a guess, and to warn explicitly when no real size can be found anywhere rather than silently assuming one
- Live auto-scaling added to the per-ingredient edit modal separately — previously had zero connection between the amount field and the macro fields at all

**Fuzzy-match false positives, two distinct causes found**
- An unrecognized brand on one side let generic word overlap alone trigger a false match ("turkey sausage Asda" matched "Turkey Sausages x2 Oakhahen" on 2 of 3 words, missing only the brand) — now requires every word to match when one side's brand can't be identified at all, rather than falling back to a partial threshold
- Apostrophes broke matching entirely as raw text — "Tennents" (typed) never matched "Tennent's" (library) since the apostrophe interrupts the character sequence; affects any possessive brand name (McDonald's, Cadbury's, etc.), fixed by normalizing apostrophes out of both sides before comparing

**Fuzzy-match confirmation UI was hiding its own real choices**
- Both actual options ("Overwrite" and "save separately") existed in the code but sat behind an unlabeled tap-to-reveal step with nothing signalling it was interactive — looked exactly like only one action existed. Now shows both choices and the value comparison immediately

**Carb auto-correction wrongly zeroing processed meat products**
- Sausage, chorizo, black pudding, pâté and similar were being treated as "plain meat" (definitionally zero carbs) when they're compound products with real fillers/binders that do carry carbs — a turkey sausage's genuine 8.6g label carbs were being zeroed to 0g
- Added these to the exclusion list the correction already used for breaded/battered/sauced items

**"Haven't eaten this" wasn't actually being honoured**
- Tapping "Just add to library (haven't eaten this)" showed a toast reminder but still presented the normal Log It / Save / Cancel choice, relying on a second correct tap — one wrong tap logged food that was never eaten as if it had been
- Fixed: once that intent is declared, Log It is no longer offered at all for that preview, with a note explaining why

**Silent failure saving to library with no pending item**
- A completely silent early exit if the item hadn't finished loading when "save to library" was tapped — now shows a real message, plus diagnostic logging throughout the whole save path for any future case

**Impossible-mass warning now suggests a number**
- Previously flagged that protein+fat+carbs exceeded a food's stated weight without saying what the weight should actually be — now states the real minimum plausible weight, calculated from the same numbers already on screen

**Photo portion-estimation prompt rewritten**
- Now prioritises visible cutlery/glassware as a size reference over the plate itself (a fork is ~18-20cm almost universally; plates vary 23-32cm+ across venues)
- Explicit guidance to account for stacked/overlapping food (sliced meat, piled sides) rather than judging only the visible top-down area
- Asks the AI to flag its own estimates as approximate (~±20%) instead of stating them with false precision

**Raw JSON leaking into chat on AI self-correction**
- When the AI second-guessed itself mid-response (e.g. logging something as water, then catching that it has real calories and correcting to food), the existing JSON-recovery regex was greedy — it swallowed both JSON blocks *and* the English commentary between them into one invalid blob, which failed every repair attempt and fell back to dumping the raw text as-is
- Fixed with proper brace-depth-counted extraction of each complete JSON object individually, preferring the last valid one (since a self-correction means that one is the real answer)

## Dashboard & Activity

**Exercise credit banner disconnected from the real calculation**
- The "+Xkcal from activity" banner was a flat-rate guess based on tag text alone (+150 for any "cardio" tag, whether it represented a 10-minute walk or 3 hours) — completely different from the proper MET-based calculation (`MET × weight × hours`) already powering the dashboard's own total, which could show a wildly different, larger number for the same day
- Unified onto the same real calculation the dashboard already used, so the banner and the dashboard can no longer disagree

**Misleading "below baseline" headline**
- On a day with a substantial logged walk, the headline compared only the *incidental* (non-walk) step remainder against the daily baseline and phrased it as if it were a verdict on the whole day's activity — reworded to make clear it's only describing steps outside the logged walk when one exists

## Settings & Dashboard Polish

**Manage screen defaulting every section open**
- A collapse-by-default mechanism already existed but had every section wired to default open regardless — defeating the entire purpose and making Manage a wall of expanded cards on every visit
- Fixed to default closed except Profile; also found 3 sections missing from the list entirely, meaning they could never even remember a manually-collapsed state

**Dismissible dashboard warnings**
- Goal Check and the Ketosis Zone alert can now be dismissed — deliberately session-only (not persisted to localStorage), so a genuinely ongoing issue reappears next reload/day rather than being silenced forever by one dismissal

**Reset button text bleeding**
- Adding a 6th button (Pint) to the hydration row caused Reset's text to overflow past its own container — added overflow/ellipsis safety to the button style so this can't recur regardless of button count

**Demo Mode reachable from Settings**
- Previously only offered on first-run onboarding; added a link under Settings → About, confirmed safe to trigger mid-session (snapshots real state in memory, never touches localStorage during the swap)

## Website

**Donation messaging corrected to be actually honest**
- "It cost nothing to make it free" was simply false — real API and Claude subscription costs land on Pete Spence, not end users; corrected across `story.html`, and the donation ask on `why-free.html` reframed from "support my costs" to "keep the project running"

**Third-person self-reference converted to first person**
- Across `story.html` and the patient guide's narrative prose — structural elements (bylines, signatures, section headings, table-of-contents entries) deliberately left as-is, since those function as attribution/navigation rather than narrative voice

**Wearables list clarified**
- Was worded like a hard requirement list; now states these are the *tested* devices specifically, and the underlying pipeline works with any export giving one row per day

## Process

**Div-balance validation methodology corrected**
- Had been stripping `<script>` content before counting balance, which misses the vast majority of this app's actual HTML (built dynamically inside JavaScript template literals) — now validates the full file, matching what the deploy script itself checks, after this exact gap let a real deploy-blocking imbalance go undetected for one release

---



## New Features

**Ketosis impact preview**
- Every "Ready to log" screen now shows the actual effect of logging: calories/protein/fat as before → after against today's real targets, and a clear carb ceiling check — still within it, over by how much, and whether it would end a current streak
- Updates live as the portion amount is adjusted, without losing input focus

**Exercise Offset for carb overage**
- Off by default (Settings). Distinguishes a carb overage meaningfully addressed by that day's logged exercise from one left unaddressed
- Never hides or replaces the raw over-ceiling fact — a genuinely additional layer, not a replacement

**Dashboard traffic-light status dots**
- Small coloured indicators on Calories/Protein/Carbs/Fat
- Carbs uses ceiling logic (green under, red over); the other three use gaining-phase logic by default — under-eating is the real risk on a surplus protocol, not exceeding target

**Weight intention status**
- Derives intention from the actual Goal/Phase setting (not a separate, potentially-conflicting setting) and colours the 14-day trend by whether it's serving that goal
- No-consequence preview mode in Settings — see how the status would read under a different goal, using real weight/trend data, without changing anything real

**Your Journey (full-history view)**
- Weight across the entire tracked history, always, independent of the Today/30/60/All filter
- Points coloured by ketosis status; treatment days marked separately; third colour for exercise-addressed overage when that setting is enabled

**Treatment Analysis (merged with the former Chemo Cycle Analysis)**
- Nutrition, ketosis adherence, and weight compared on treatment days vs standard days
- Detected treatment cycles and a specific comparison against the immediate 7-day recovery window folded in from the old standalone section — same information, one coherent story instead of two overlapping ones

**Carb Pattern breakdown**
- % of days at Strict Keto / Keto / Low Carb — or neutral equivalent tiers for non-keto conditions, since "keto" framing isn't meaningful for diabetes management or general health goals
- Encouragement keyed to adherence against the user's own chosen ceiling, not a ranking against strict keto specifically

**GBM Research Digest**
- Persistent, dated, condition-gated home for real research findings, colour-coded Proven / Early Stage / Speculative matching Monthly Summary
- A "Research Now" live-search attempt was built, tested, and found unreliable (the app's AI calls have no real web search) — replaced with "Copy Research Request", a one-tap prompt to paste into a real chat conversation instead

**Formulas & Technical Reference**
- Every calculation the app uses — BMR, TDEE, MET-based exercise calories, macro ratios, carb ceiling logic — documented in plain language, in-app

**Voice logging, finished**
- One-tap "Log it" directly on the transcript rather than needing to find the separate send button
- Real, actionable error messages instead of raw error codes
- Subtle mic highlight on treatment-tagged days

**why-free.html reinstated**
- Rebuilt with the real JustGiving crowdfunding link, generic (non-itemised) donation framing, and a second option (Headcase Cancer Trust)

**Demo mode seeded with real anonymised data**
- Previously generic placeholder data; now a genuinely rich dataset built from real history — full 151-item library, 30 real days of nutrition/wearable history, real recipes/routines/strength sessions
- Sensitive specifics (weight, supplement names/doses, condition tags) fictionalised; food/exercise/recipe data kept as-is since it isn't personally sensitive
- Found and fixed: supplements had no demo-mode protection at all (no guard on load or save) — now matches the same safe pattern as every other dataset

**ℹ️ info-icon pattern**
- Reusable tap-to-reveal explanation component for features that could be confused with a similar one, without cluttering the screen by default

## AI Reliability

**Unified AI calling — one function instead of nine separate copies**
- Every AI call site (Ask AI, Full Summary, GBM Summary, Oncology narrative, portion estimation, health-context queries, both missed-day calculators, barcode reading) now shares one function
- Real errors surfaced (HTTP status, actual message) instead of a generic swallowed "Could not generate" — this is what made it possible to actually diagnose an Anthropic billing/credit issue instead of guessing at 9 separately "broken" features
- Image support added for vision calls (barcode reading), so that path could join the same shared function too
- Several paths previously always hit the shared proxy regardless of a configured personal API key — now correctly respect a configured key first

## Bug Fixes

**Flat carb-ceiling comparison — found in 8 separate places**
- Weekly Summary, Oncology Report, Report Summary, the ketosis streak counter, Treatment Analysis, GBM Stats, the AI Brief generator, and Sleep & Ketosis correlation were all comparing every day against a flat standard-only ceiling, regardless of that day's actual logged mode (occasion/holiday days incorrectly counted as failures)
- Each now judges a day against its own mode's ceiling
- The AI Brief generator specifically had a worse variant: `getTargets().carbs` doesn't exist on the object returned (it returns `{standard, occasion, holiday}`), so the comparison was always `undefined` and adherence was being reported as 0% unconditionally, every time, regardless of actual data

**Library fuzzy-matching — category-mismatch, found in 4 separate functions**
- Generic descriptor words ("white", "slices") were scoring as match evidence with no regard for whether the actual food category matched — "Warburtons white bread" could surface "white cheese" as a match purely on coincidental word overlap
- Fixed in the strict duplicate-check finder first; found the identical bug, unfixed, in three sibling functions (substitute suggestions, Add Food comparison, the duplicate scanner) — all four now share the same food-category disqualification check

**Onboarding: height/age/sex collected but never saved**
- Used for a live TDEE preview during setup but never actually written to the persistent profile keys anywhere in onboarding — a new user would enter this data, see it work, then have it silently discarded on completion
- Fixed at the step where it's collected, plus a defensive re-save in the final "Start Tracking" button

**Print/PDF silently failing in standalone PWA mode**
- `window.open()`-based printing has nowhere to open a new window into once the app is an installed standalone PWA — failed with zero visible error
- Replaced with a hidden-iframe approach that works identically in a normal browser tab or the installed app

**Clinical report buttons never appearing**
- The Clinical export mode was rendering into an old "backwards compatibility" placeholder div, not the real shared output container — Print/Copy/AI-summary buttons were never actually reachable, not just visually broken

**Multi-match library picker going dead after first selection**
- Picking any item cleared the state backing the whole picker before the resulting preview was even confirmed — cancelling that preview left a list that looked interactive but did nothing

**Dashboard/History layout overflow**
- Progress tiles and History day-summary rows switched from cramped single-row layouts to proper 2-column grids after longer text (added target comparisons, percentage figures) no longer fit

**History: no target comparison**
- Added actual/target for every macro on every day, using that day's own mode-aware ceiling — not previously visible at all, only raw totals

## Refactoring

- `updateDashboard`: 413 → 263 lines (4 self-contained blocks extracted, animation logic deduplicated)
- `renderTrends`: 563 → 477 lines (gap-detection extracted, two canvas helpers hoisted out of per-render redefinition, one genuinely dead function removed)
- `processMessage`: 603 → 543 lines (6 keyword-query handlers extracted to named functions)
- Deliberately did not touch the rollover logic, AI-parsing core, or library-matching core during any of the above — extracted only what was clearly safe and self-contained, left the delicate/central logic exactly as it was

## Documentation

- User guide updated with all of the above — two new sections (Dashboard intelligence, Smarter logging), Reports section extended, Demo Mode note added to Setup
- README and this changelog brought current
- Fixed a genuine pre-existing bug in the patient guide (a missing closing `</div>` on the opening-letter container, present since whenever that section was first written) while checking documentation more broadly

---

## New Features

**Library-aware meal suggestions ("📚 From my library")**
- Proposes real combinations of saved library items and Recipes (with proper per-serving math) against today's actual remaining macros — never invents values, only ever uses locked/stored data
- Shows each item's real portion size, not just names
- One-tap logging directly from the suggestion card
- Recipe suggestions reuse the exact same servings-scaling formula as the Recipe Builder itself

**Ingredient substitution flow**
- If a described food doesn't exactly match your library (e.g. wrong brand), offers real alternatives from what you actually have instead of silently falling through to a fresh AI guess
- Works both when no match is found at all, and when you explicitly decline a suggested match
- "Save as new item" option added to the duplicate-comparison screen, for when comparison reveals two genuinely different products rather than a real duplicate

**Ketosis streak milestones**
- One-time celebration messages at 7/14/30/50/100/200/365 consecutive days, shown as both a chat message and a toast (visible regardless of active tab)

**Dashboard & Library section reordering**
- Every section on the Today dashboard (Weight, Day Mode, Ketosis, Macros, Remaining, Macro Ratio, Goal Check, Steps, Activity, Water, Log, Guides & Docs) can be reordered via ▲▼ buttons
- Recipes vs Food Library sections in the Library tab reorderable the same way
- Reports, Manage, and Import tabs also fully reorderable — built as one generic, self-discovering system rather than hand-wiring dozens of sections individually

**Demo mode overhaul**
- "Try a demo first" now seeds realistic sample data across Library, Recipes, Routines, and Strength Training history — previously these sections were completely empty in demo mode, hiding most of what the app actually does
- Built via safe read/write redirection rather than temporarily overwriting real user data

**Library-only ingredient saving**
- New "📚 Just add to library (haven't eaten this)" option when reading a label, for cataloging an ingredient without logging it as eaten today

## Nutrition Logging Accuracy

**Four new sanity checks added to the existing meat-carbs and pure-fat plausibility checks:**
- Atwater kcal-consistency (a food's stated calories must roughly match protein×4 + carbs×4 + fat×9), with an explicit exception for alcohol
- Implausibly low carbs on fruit-named items (the inverse of the meat-carbs check)
- Implausible portion size (under 1g or over 2000g)
- Macro-mass plausibility — protein + fat + carbs in grams cannot physically exceed the food's own stated weight

**Fuzzy-match accuracy (library duplicate detection and substitution)**
- Brand names (Asda, Tesco, Sainsbury's, Lidl, etc.) now correctly disqualify a match when they genuinely differ between query and candidate — previously "double cream is Asda" and "double cream is Lidl" scored identically
- Meat/protein type (chicken vs beef vs pork etc.) now works the same way — previously a single shared generic word like "mince" could match two completely different meats
- Short 2-word queries now require both words to match, not just one — closes the gap where a single generic shared word inflated the match score

**Meal-photo reasoning text**
- AI no longer states its own rough sanity-check total in the message field — previously this could show a different number from the actual, more carefully-calculated logged total, creating a confusing self-contradiction

**Long-meal parsing safety net**
- A named item with every macro at zero is now excluded rather than silently logged — this pattern almost never represents a real food and more likely indicates a parsing failure somewhere in the AI response chain

**Today's summary — fixed missing fat**
- The "show today summary" conversational response was missing fat entirely from its output; now included alongside calories, protein, and carbs

## Data Safety

- "Export All Data" now includes recipes and routines in the JSON backup — previously silently missing
- Corrected misleading "downloads one zip" wording to accurately describe the several separate files actually produced
- Recipe deletion now requires confirmation — previously deleted instantly with no warning

## UX & Organization

- Settings grouped into clear categories (Your Targets, Data & Devices, App Info), with debug/diagnostic tools (Body Comp Debug, Rollover Debug Log) visually and functionally separated from everyday settings via a distinct "⚠ Advanced" warning box
- Recipes vs Meals naming confusion addressed with cross-referencing subtitles in each section, rather than a rename
- Fixed a focus-destroying bug where the reorder system's own render logic was silently kicking users out of text inputs (search box, Daily Steps, custom water amount) on every keystroke

## Donation / Fundraising Page

- Story, cover photo, and donation copy finalized for the JustGiving crowdfunding page and app-linked story page
- Subsequently removed personal fundraising link and photo from the app entirely per decision to direct support toward charity rather than personal fundraising

## Known Outstanding Items
*(See the Phase 15 entry at the top of this file for the current list — the items below were resolved or carried forward there during this documentation pass, rather than duplicated in two places.)*

# MaxedHealth Changelog

## v3.10.39 — Phase 9 (6 Jul 2026)
- **Added:** Goal change (Lose/Maintain/Gain) now automatically appends a timestamped entry to Weight Phase History. No manual entry needed except for historical backdating.

## v3.10.38 — Phase 9 (6 Jul 2026)
- **Added:** ⭐ Full Summary — dedicated one-tap button in Ask AI generating a comprehensive 9-section health analysis (nutrition, weight phases, ketosis quality, sleep, HRV, activity, best periods, areas to improve, protocol verdict). Phase-aware, condition-specific, nil days excluded.
- **Fixed:** Ask AI section title updated with ⭐ star status indicator.

## v3.10.37 — Phase 9 (6 Jul 2026)
- **Added:** Suggested Targets calculator in Settings → Profile. Calculates personalised TDEE (Mifflin-St Jeor × activity multiplier from real avg step count), phase-adjusted calories, protein (1.8g/kg GBM/Epilepsy, 1.6g/kg otherwise), and fat to fill remaining calories. Condition overlay checks ketogenic ratio for GBM/Epilepsy. "Apply these targets →" button applies in one tap. Recalculates when Settings opens or weight updates.

## v3.10.36 — Phase 9 (6 Jul 2026)
- **Added:** Weight Phase History field in Settings. Log intentional weight phases (loss/maintain/gain) with ISO dates, one per line. Used by all AI reports to correctly interpret weight trends — deliberate loss is never flagged as a concern.
- **Fixed:** `savePhaseHistory()` now calls `renderSuggestedTargets()` after saving.

## v3.10.35 — Phase 9 (6 Jul 2026)
- **Fixed:** Nil nutrition days (<100 kcal) now filtered from Ask AI raw data table, Monthly Summary calculations, and `buildPatientContext`. Gap days reported as "tracking gaps, not zero intake" in AI context.

## v3.10.34 — Phase 9 (6 Jul 2026)
- **Fixed:** Report streak now uses `calcKetosisStreak()` which includes today's logged data. Previously the report showed 0 streak even when today was compliant because today's log wasn't included in the history array.
- **Fixed:** Nil nutrition days excluded from protein misses, fat misses and best carbs calculations in report summary.

## v3.10.33 — Phase 9 (6 Jul 2026)
- **Fixed:** JS syntax error — `const trackedCarbs` declaration placed inside a chained expression, breaking all JavaScript. Node syntax check now run on every build before deploy.

## v3.10.32 — Phase 9 (5–6 Jul 2026)
- **Fixed:** File header comment corrected from stale "v2.1.9 Phase 7" to "v3.10.32 Phase 9". The comment was misleading but the file was always Phase 9.
- **Added:** Offline manual entry fallback — when AI is unreachable (flight mode, no network), a manual kcal/protein/fat/carbs form appears automatically instead of an error.
- **Added:** Weight carry-forward — dashboard shows last known weight when today has no reading, labelled "last known". Never writes to data.
- **Fixed:** Watchdog (`mh_watchdog.sh`) was starting server.py from wrong directory, causing `combined_exists: false`. Fixed `cd` path from `app/maxhealth` to `app`.

## v3.10.31 — Phase 9 (5 Jul 2026)
- **Fixed:** Tesco Double Cream fat=0 bug. Three-layer fix: (1) label-locked values (467kcal/50.5g F/1.5g P/1.6g C per 100g), (2) FAT_FLOOR_DB updated with label-confirmed 50.5g, added lamb/pork/single cream, (3) high-kcal backstop — any item >200kcal with 0g fat has fat back-calculated from `(kcal - protein×4 - carbs×4) ÷ 9`.
- **Fixed:** AI fat prompt updated with label-confirmed Tesco double cream values and explicit rule: never return 0g fat for cream/oil/dairy/nuts/eggs.

## v3.10.30 — Phase 9 (5 Jul 2026)
- **Fixed:** Report summary stats (best carbs, protein misses, fat misses) now exclude days with <100 kcal logged, preventing untracked days from skewing statistics.

## v3.10.29 — Phase 9 (2 Jul 2026)
- **Added:** Inline edit (✏) per component row in meal preview. Tap to edit name and gram amount; macros recalculate live from original per-100g base values. Save updates the preview; Cancel reverts.

## v3.10.28 — Phase 9 (2 Jul 2026)
- **Fixed:** story.html links in app used absolute GitHub Pages URL — now works correctly from both localhost and GitHub Pages.

## v3.10.27 — Phase 9 (2 Jul 2026)
- **Fixed:** story.html link path was `docs/story.html` (non-existent subfolder). Corrected to `story.html`.
- **Fixed:** History render — log entries whose description is a mode word ("standard", "holiday", "occasion") now filtered from display. These ghost entries were created by an old rollover bug.
- **Added:** HOL/OCC badge next to date in history header for holiday/occasion days.

## v3.10.26 — Phase 9 (2 Jul 2026)
- **Fixed:** Ghost mode-word log entries filtered from history display.
- **Added:** Day mode badge (HOL/OCC) in history header.

## v3.10.25 — Phase 9 (5 Jul 2026)
- **Fixed:** Carb zone gaps — dropdown labels now use contiguous ceiling values (≤20g / ≤50g / ≤100g / ≤150g). No gaps between zones.
- **Updated:** `CONDITION_META` protocol labels and carb ceilings hint text to match.

## v3.10.24 — Phase 9 (5 Jul 2026)
- **Fixed:** `carer.html` — title and all brand references corrected to "MaxedHealth". Hardcoded carb ceilings replaced with `data.ceilings` from payload. `generateCarerLink()` now embeds actual ceiling values from localStorage.

## v3.10.23 — Phase 9 (5 Jul 2026)
- **Added:** Condition/Protocol dropdown in Settings → Profile (GBM, Epilepsy, Strict Ketosis, Type 1 Diabetes, Type 2 Diabetes, General Health). All AI reports now adapt framing, evidence categorisation and thresholds to the user's condition.
- **Added:** `CONDITION_META` table with per-condition protocol label, evidence note and report framing.
- **Fixed:** `buildPatientContext` and `patientContextBlock` were hardcoded to GBM gaining phase. Now reads `mh_condition` and `mh_goal`.

## v3.10.22 — Phase 9 (5 Jul 2026)
- **Fixed:** Meal/Label toggle was hardcoded to Label as the active state in HTML despite JS defaulting to Meal.

## v3.10.21 — Phase 9 (4 Jul 2026)
- **Fixed:** Step 0 photo classification prompt was too broad. Tightened to binary yes/no: "does this photo show a printed nutrition panel with actual numbers?" Food on a plate is always MEAL PATH.

## v3.10.20 — Phase 9 (2 Jul 2026)
- **Added:** Delete button (✕) per component row in multi-item meal preview.
- **Added:** Step 0 photo classification — AI classifies photo as label or meal before any other reasoning fires.

## v3.10.19 — Phase 9 (2 Jul 2026)
- **Fixed:** When AI asks a clarification question about an ambiguous photo item, the next user reply is now correctly treated as the answer. Stored as `window._pendingClarification`.
- **Fixed:** Sauce double-counting — when a protein is logged "in sauce/curry", sauce is no longer also added as a separate line item.

## v3.10.18 — Phase 9 (2 Jul 2026)
- **Added:** Termux:Boot boot survival — `start-watchdog.sh` runs `termux-wake-lock` and immediately launches `mh_watchdog.sh` on boot.
- **Fixed:** GitHub Pages → localhost auto-redirect blocked by Chrome LNA policy. Removed dead WebSocket probe. Replaced with one-time toast pointing to localhost:5757 shortcut.
- **Fixed:** setup.sh (v3.2) now auto-installs `termux-api`, detects Termux:Boot/API, prompts only when missing.
- **Added:** `buildPatientContext` + `patientContextBlock` — all three report types receive full patient context.
- **Added:** Meal photo ambiguity rule — flags uncertain items and asks before logging.

## v3.10.17 — Phase 9 (27 Jun 2026)
- **Fixed:** Meal photo prompt — removed directional bias. Added Step 4 plate-weight sanity check.

## v3.10.16 — Phase 9 (27 Jun 2026)
- **Added:** `showLocalhostHint()`, `maybeShowHomeScreenTip()`, `offerLocalSwitchIfAvailable()` for post-LNA localhost shortcut guidance.

## v3.10.15 — Phase 9 (27 Jun 2026)
- **Fixed:** `amazfit.py` now uses `pyzipper.AESZipFile` for AES-encrypted Zepp exports.
- **Added:** `AMAZFIT_EXCLUSIVE` fields always overwrite on re-sync. `fix_amazfit_steps.py` one-off retroactive correction script.

## v3.10.14 — Phase 9 (26 Jun 2026)
- **Added:** Post-onboarding local server switch banner.

## v3.10.13 — Phase 9 (26 Jun 2026)
- **Fixed:** GitHub Pages → localhost redirect (first pass). setup.sh v3.2 Termux:Boot/API auto-detection.

- **Fixed:** GitHub Pages → localhost auto-redirect no longer works due to Chrome's
  Local Network Access (LNA) policy (enforced from Chrome ~142–149), which blocks
  cross-origin fetch/WebSocket requests from public HTTPS pages to localhost.
  Removed the now-dead `tryLocalhostRedirect()` WebSocket probe and the
  `checkServer()` auto-redirect; replaced with a one-time toast pointing users to
  their localhost:5757 shortcut instead.
- **Added:** setup.sh (v3.2) now auto-installs `termux-api`, detects whether
  Termux:Boot and Termux:API are already installed, and prompts for the one-time
  manual install only when missing (links open directly). New boot script
  (`start-watchdog.sh`) holds a wake-lock and launches the watchdog immediately
  on boot, alongside the existing cron-based boot script, to prevent Doze
  suspending background checks overnight.
- **Action required (existing installs):** re-pin your home screen shortcut to
  `http://localhost:5757` directly — the old shortcut pointing at the GitHub
  Pages URL will no longer auto-jump to local mode.

## v3.4.0 — Phase 9 (15 Jun 2026)
- Custom themed modals replace all browser confirm/alert/prompt dialogs
- Styled with app design system — dark/light theme aware, danger styling for deletions

## v3.3.9 — Phase 9 (15 Jun 2026)
- All activities deletable including Walking and Resistance
- Confirm dialog before deletion
- Activity types persist permanently — only duration/enabled clears at midnight

## v3.3.8 — Phase 9 (15 Jun 2026)
- Rollover guard prevents ghost duplicate lines in master.csv
- Each date can only roll over once — flag stored in localStorage

## v3.3.7 — Phase 9 (15 Jun 2026)
- Midnight rollover rebuilds full notes from occasion tags + activity state
- Chemotherapy, resistance bands etc now correctly written to master.csv

## v3.3.6 — Phase 9 (14 Jun 2026)
- Rollover date captured before state.lastDate changes — correct date in master.csv
- Water progress bar uses adjusted target (base + exercise)

## v3.3.5 — Phase 9 (14 Jun 2026)
- Duration input uses onchange/onblur — no more focus loss while typing
- dash-scroll overflow fix

## v3.3.4 — Phase 9 (14 Jun 2026)
- Activity row two-line layout — name+kcal on top, duration+effort below
- No more horizontal overflow on small screens

## v3.3.3 — Phase 9 (14 Jun 2026)
- Resistance bands → Resistance (shorter label)
- dash-scroll min-height fix

## v3.3.2 — Phase 9 (14 Jun 2026)
- overflow:hidden on views, subviews and app wrapper (bleeding fix attempt)

## v3.3.1 — Phase 9 (14 Jun 2026)
- Custom activity delete button fixed — uses index >= 2 check

## v3.3.0 — Phase 9 (14 Jun 2026)
- Smart emoji for custom exercises (🏊 swimming, 🚴 cycling, 🏃 running etc)
- Custom activity delete button fixed using custom_ ID prefix

## v3.2.9 — Phase 9 (14 Jun 2026)
- Descriptive effort labels per activity type
- Walking: Easy (<2mph) / Moderate (3–4mph) / Hard (4–5mph+)
- Resistance: Easy — light / Moderate — working hard / Hard — near max

## v3.2.8 — Phase 9 (14 Jun 2026)
### Added
- All macro targets adjust dynamically with exercise:
  - Calories — MET × weight × duration
  - Protein — +15g on resistance days
  - Water — +500ml per hour of activity
  - Carbs — stays fixed (therapeutic ceiling unchanged)
- Activity summary auto-saves to notes/history (e.g. "76min Walking, 45min Resistance")
- History shows exercise minutes as separate 🏃 line in accent colour
- Steps removed from Remaining Today (wearable is authoritative)

## v3.2.7 — Phase 9 (14 Jun 2026)
- GBM summary tokens 6000, concise prompt instruction

## v3.2.6 — Phase 9 (14 Jun 2026)
- Fixed wrong model name across all 15 AI calls (claude-sonnet-4-20250514 → claude-sonnet-4-6)
- This was breaking all AI features including meal logging

## v3.2.5 — Phase 9 (14 Jun 2026)
- GBM summary better error reporting (shows actual API error)

## v3.2.4 — Phase 9 (14 Jun 2026)
- Calorie tile updates dynamically when activities ticked
- Remaining calories recalculates against adjusted target

## v3.2.3 — Phase 9 (13 Jun 2026)
- Daily carb target removed — superseded by Carb Ceilings
- Carb Ceilings section has reference ranges in description
- saveCarbCeilings syncs mh_target_carbs for backwards compatibility

## v3.2.2 — Phase 9 (13 Jun 2026)
- GBM carb adherence fixed (getTargets().standard not getTargets())
- updateGBMStats fixed same way

## v3.2.1 — Phase 9 (13 Jun 2026)
- GBM summary tokens increased 900→4000

## v3.2.0 — Phase 9 (12 Jun 2026)
### Fixed
- Phase banner removed from dashboard
- Protein tile reads from settings (165g), updates dynamically
- Activity card moved just above water section
- Occasion tags preserved when switching to Standard
- History tag × delete fixed — uses data-tag attribute, deletes only tapped tag
- Carer link generates self-contained HTML blob (no missing carer.html)
- Carb ceilings set at onboarding (GBM: 50/75/100g, T2D: 100/150/200g)

## v3.1.9 — Phase 9 (12 Jun 2026)
### Added
- 🏃 Activity card — permanent on dashboard, any day mode
- Walking + Resistance defaults with duration and effort (Easy/Moderate/Hard)
- MET-based calorie calculation (MET × weight × hours)
- + Add exercise for custom activities with smart emoji detection
- Notes/Tags column in Reports query builder with text search
- Occasion tags cleaned — removed Walking/Resistance/Exercise/Birthday/Rest day
  (these moved to activity card)

## v3.1.8 — Phase 9 (11 Jun 2026)
- Steps field visible in Remaining Today
- Occasion button stays highlighted after selecting tags (dayMode sync fix)

## v3.1.7 — Phase 9 (11 Jun 2026)
- Steps labelled as informational — wearable takes precedence
- Walking tag confirmed present in occasion picker

## v3.1.6 — Phase 9 (11 Jun 2026)
- Steps moved to Remaining Today section — visible on any day mode

## v3.1.5 — Phase 9 (12 Jun 2026)
- Occasion button stays highlighted (updateDashboard syncs button state)
- Activity calorie nudge — ⚡ banner shows extra kcal from exercise tags
- Steps field in occasion picker

## v3.1.4 — Phase 9 (11 Jun 2026)
- 😴 Rest day added to occasion tags

## v3.1.3 — Phase 9 (12 Jun 2026)
- Occasion tags write correctly to master.csv
- Legacy values filtered, real tags pass through
- EOD, midnight rollover, sync all, backup all fixed

## v3.1.2 — Phase 9 (11 Jun 2026)
- Saved query card name now visible (accent colour, fallback text)

## v3.1.1 — Phase 9 (11 Jun 2026)
- Saved query card layout fixed — single row, ellipsis on long names

## v3.1.0 — Phase 9 milestone (11 Jun 2026)
- Removable tag pills in history edit — × button per tag
- Docs updated

## v3.0.9 — Phase 9 (11 Jun 2026)
### Added
- 🎤 Voice input — microphone button, Web Speech API
- 📷 Recently scanned — last 10 barcode items for quick re-log
- 📋 Oncology Team View — clinical PDF/text report (30/14/90/7 day periods)
- Custom occasion tag Add button fixed (settings-input class)

## v3.0.8 — Phase 9 (11 Jun 2026)
- Carb ceilings editable per day mode (Standard/Occasion/Holiday)
- Saved to localStorage, used in all adherence calculations

## v3.0.7 — Phase 9 (11 Jun 2026)
- Dark/Light/Auto theme fixed — body attribute, separate from visual theme
- Light theme correctly overrides all colour variables

## v3.0.6 — Phase 9 (11 Jun 2026)
- Weekly summary print — portrait A4, CSS variables resolved for PDF

## v3.0.5 — Phase 9 (11 Jun 2026)
- Dark/Light/Auto theme toggle in Settings → Customise → Appearance
- Weekly summary try/catch

## v3.0.4 — Phase 9 (11 Jun 2026)
### Added
- 📊 Weekly Summary export — day-by-day, print/copy
- Chemo days highlighted purple, treatment days called out

## v3.0.3 — Phase 9 (11 Jun 2026)
- Treatment Analysis in Reports — auto-detects chemo/treatment tags
- Compares calories, protein, fat, carbs on treatment vs standard days

## v3.0.2 — Phase 9 (11 Jun 2026)
- Long-press library card for instant log (600ms, vibrate)

## v3.0.1 — Phase 9 (11 Jun 2026)
- Long-press rebuilt — index from onclick, prevents browser context menu

## v3.0.0 — Phase 9 milestone (11 Jun 2026)
- Legacy notes filtered from tag display
- History shows only real occasion tags

## v2.9.x — Phase 8 (11 Jun 2026)
- Occasion picker multi-tag system
- Ketosis streak counter
- Weight trend prediction
- Swipe left to delete log entries
- Long-press library for instant log
- Save changes closes form
- GBM tile text cutoff fixed

## v2.8.x — Phase 8 (11 Jun 2026)
- Portion badge (↑200%/↓50%) on log entries
- Fat in history edit
- Midnight rollover fix
- History layout, weight card overflow

## v2.7.x — Phase 8 (10–11 Jun 2026)
- Recipe ingredient live scaling
- A-Z library nav, category filter
- Meal ingredients in library view
- 10+ item lists fixed

## v2.6.x — Phase 8 (10 Jun 2026)
- Library split Meals/Ingredients
- Inline amount scaler on LOG
- Fat in running totals

## v2.0.0 — Phase 6 (29 May 2026)
- 4-tab navigation, fat tracking, supplements
- Recipe builder, barcode scanner, missed day flow

## v1.9.0 — Phase 5 (late May 2026)
- Editable correction grid, long meal parallel requests

## v1.0.0 — Initial build (May 2026)
- Dashboard, AI meal logging, Cloudflare Worker proxy
- Python pipeline (Withings, RingConn, Amazfit)
