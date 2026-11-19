# Play Console: paste-ready answers (drafted 19 Nov 2026)

Companion to PLAY_STORE_LISTING.md (store text) and PLAY_STORE.md (why and how). Every answer below was checked against the app and docs/legal.html on 19 Nov 2026. Where Play's form wording differs from what is written here, answer the question as Play asks it, using the facts here.

## 1. Create the app (Play Console > Create app)
- App name: MaxedHealth: Food & Goals
- Default language: English (United Kingdom)
- App or game: **App**
- Free or paid: **Free** (the free app has no in-app purchases; Premium is not sold inside the Play build)
- Declarations: tick Developer Program Policies and US export laws.

## 2. App content > the declarations
- **Privacy policy:** https://pete-maxhealth.github.io/maxhealth/docs/legal.html#privacy (a normal page, no login; updated 19 Nov 2026 to name Open Food Facts).
- **Ads:** No, the app contains no ads.
- **App access:** All functionality is available without logging in. No account exists. (Tip for the reviewer: the demo people on the first screen show the app with sample data.)
- **Target audience:** 18 and over only. Not designed for children. (The privacy policy says not directed at under 16s.)
- **News app / government app / financial features:** No.
- **Health apps declaration:** The app is a health and fitness / nutrition tracker. It is **not** a medical device and makes no diagnostic or treatment claims. Do not tick Medical, and do not tick "Disease and condition management" unless Play's wording forces it; the personal account cannot publish medical apps (see BACKLOG, 18 Nov). Health Connect: **No** (that is the Premium launcher).
- **Content rating (IARC questionnaire):** category "Utility, productivity, communication or other" or Health, whichever is offered. Answer No to violence, sexual content, language, gambling, controlled substances, user-generated content shared between users, and location sharing. Expected rating: Everyone / PEGI 3. AI features: the user types or photographs their own food; nothing generated is shared with other users.
- **Data safety:** see section 3.
- **Government/Photo permissions:** the wrapper uses camera (barcode and label photo) and microphone (voice logging) only when the user taps those buttons. Be ready to say so if Play asks for a permissions declaration.

## 3. Data safety form, question by question
Does the app collect or share required user data types? **Yes.**
Is all of the data encrypted in transit? **Yes** (HTTPS to the Worker and Open Food Facts).
Do you provide a way for users to request data deletion? **Yes, but CHECK FIRST**: I could not find one single "delete everything" button in Settings (there are per-area Clear buttons, Export and Backup). The developer holds no user records, so deletion is "uninstall the app or clear its storage". Answer in those terms with the privacy policy link, or add a delete-everything button before submitting (Pete's call).

| Data type (Play's name) | Collected? | Shared? | Why / notes |
|---|---|---|---|
| Health info (food, symptoms, conditions the user types) | Yes, only when the user uses an AI feature | Yes, with the AI provider via the developer's proxy | Purpose: App functionality. Optional. Not stored by the proxy. Processed by Anthropic (and Google/OpenAI only if the user turns on "Verify across 3 AIs"). Mark "processed ephemerally". |
| Fitness info (activity, steps, sleep) | Same as above | Same as above | Only if included in an AI question or report. |
| Photos (food, label, barcode photos) | Yes, only on the AI photo features | Yes, with the AI provider via the proxy | App functionality, optional, ephemeral. |
| Other user-generated content (text and voice transcripts typed or said into chat) | Yes, only on AI features | Yes, same route | App functionality. CHECK: voice logging uses the browser's speech recognition, which on Android Chrome sends the audio to Google for transcription. If Play asks about audio, declare Voice or sound recordings: collected, shared with Google (speech-to-text), App functionality, optional, ephemeral. The privacy policy does not yet say this; add a sentence before submitting. |
| App activity / other info (barcode numbers and search words) | Yes | Yes, with Open Food Facts | App functionality. Not linked to identity. |
| Device or other IDs (random device code) | Yes, once a day | No (developer's proxy only) | Analytics (install counts) and fair-use limits. Not linked to the person. Record expires after about a year. |
| App info and performance (app version) | Yes, once a day | No | Analytics. |
| Name, email, address, phone, location, contacts, financial info, web history, files, audio recordings stored | **No** | No | |

- Data is **not** sold. No data is used for advertising or sold to data brokers.
- Optional vs required: all of the above is optional except the daily device code and version ping.
- Fonts: the page loads Google Fonts, which can see the device address. This is standard web-page loading, not data the app collects; it is mentioned in the privacy policy.

## 4. Store listing extras (not in PLAY_STORE_LISTING.md)
- **Category:** Health & Fitness. **Tags:** nutrition, diet and weight management, fitness tracking (choose what Play offers).
- **Contact email:** use the public contact address you are happy to show (Play shows it; your trader status makes it public). The privacy policy lists pspence@pspence.co.uk.
- **Website:** https://pete-maxhealth.github.io/maxhealth/ (landing page). It must not link to Premium until Premium is live; check it before submitting.
- **Release notes (first release, 500 max):** "First release on Google Play. Track food, movement, sleep and weight for your goal. Free, no account, your records stay on your phone. Try the demo people to see it with a month of sample data."
- **Screenshots:** 4 to 8 phone shots from the demo people (Doris, Sam, John, Alex), no personal data, no Premium card (the Play build hides it). Take them from the Play-mode link ?src=play so no Premium appears.
- **Feature graphic 1024x500, icon 512x512 (icons/):** still to make.

## 5. Things to double-check before submitting
1. The store text says "scan a barcode", "photograph a label" and "speak what you ate": all exist. "Type 2 diabetes" is a goal name in the app; keep the store wording to tracking, never "manage" or "treat".
2. "Reports you can share with a clinician or carer" is fine: it is a share, not a medical claim.
3. Premium: the Settings "Premium licence" key box still shows in the Play build (see BACKLOG, 17 Nov). Decide before review.
4. Play review is most likely to object to medical wording: keep to the disclaimer paragraph already in the listing.
5. If the closed test needs 12 testers, ask for them early; the 14 days only count once the app is live to that test track.
