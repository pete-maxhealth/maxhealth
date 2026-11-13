# Google Play: what it would take (investigated 13 Nov 2026)

Route: wrap the existing web app as a Trusted Web Activity (TWA) with Bubblewrap. The app itself stays the same web page; Play only holds a thin Android shell that opens it full screen. Nothing here has been started.

## Cost
- **$25 one-off** Play Console registration fee (Google's own help pages and several guides agree). No yearly fee. The free app means no Play fees on sales; Premium would be a separate question (see Risks).
- Bubblewrap, Android Studio command line tools and the signing key are free. The one real cost is your time: roughly a day to build and submit, then waiting.

## What has to change on the account (Pete)
1. **Choose the account type.** A *personal* account created after 13 Nov 2023 must run a **closed test with at least 12 testers, each opted in for 14 days in a row**, before Play grants production access (Google's help page, quoted). An *organisation* account is not mentioned in that rule but needs a registered organisation and a D-U-N-S number (free, can take days to weeks). If MaxedHealth is not a company, this means a personal account and finding 12 testers.
2. **Identity verification.** New personal accounts must verify identity (government photo ID, proof of address under 90 days old, a phone that takes SMS or calls). This one is from a third-party guide (TesterBee, July 2026), so check it on screen when you sign up. Only you can do this step.
3. **Public developer details.** Because Premium will sell, Google may treat you as a "trader" and show your name and contact details on the store page. Check what the sign-up form says before choosing, and whether a business address or a separate contact email can be used instead of your home address.
4. **Use a Google account for this only.** It is a Play Console account, not Google Cloud: no billing account and no contract beyond the registration fee and Play's developer terms.

## What the app and website need
- **Digital Asset Links file.** The wrapper only goes full screen if the site proves it belongs to the app, with a file at `https://<site>/.well-known/assetlinks.json`. The app is served from a GitHub *project* page (`pete-maxhealth.github.io/maxhealth/`), so the file has to live at the root of the user site, which means a separate repository named `pete-maxhealth.github.io` with a `.nojekyll` file (otherwise GitHub hides dot-folders). Your own domain would be cleaner. This needs the signing key's fingerprint, which comes from the build.
- **Privacy policy link.** Must be a public, non-PDF web page. `docs/legal.html#privacy` exists; Play wants a plain URL it can open, and it must match what the app really does (AI calls go through the Cloudflare Worker).
- **Health apps declaration** in Play Console (App content). Because MaxedHealth is not a medical device, the store description must say so in terms close to: "not a medical device and does not diagnose, treat, cure or prevent any medical condition", and remind people to consult a healthcare professional (Google's Health apps policy, fetched).
- **Description wording.** Google forbids misleading health claims and health misinformation. The current website wording ("Therapeutic Nutrition Intelligence", "Fight smarter", clinical reports) would be read as claims. The store text should describe tracking and sourced, labelled information only, in line with the stance already adopted in the app.
- **Data safety form.** Declare what leaves the phone: AI text and images via the Worker, and the licence check for Premium. Nothing is shared by default.
- **Content rating, target audience (not children), screenshots, a 512px icon and a feature graphic.** All routine.
- **Updates.** The web content updates by itself. The wrapper only needs rebuilding for Android changes (Play requires a recent target API level each year).

## Risks and decisions for you
- **Premium links inside the Play version.** Google requires its own billing for digital goods sold inside a Play app, with exceptions that depend on region. The app has Premium links (`MH_PREMIUM_URL`, the demo Premium card, the Settings entry). In the Play build these should be hidden. That is done (v3.10.1403): the wrapper's start address is `.../maxhealth.html?src=play`, which hides the Premium card, the Ko-fi card and the demo Premium cards. It also means Premium would not be promoted to Play users.
- **Android developer verification (this affects the Premium launcher APK, not just Play).** From 30 Sep 2026 Android apps on certified devices must come from a verified developer, starting in Brazil, Indonesia, Singapore and Thailand, with global expansion in 2027 (Android Developers Blog). A third-party report puts the UK in 2027; Google's own pages I could read do not name the UK. Apps outside Play can register in the Android Developer Console: a **limited distribution account is free (up to 20 devices, no ID)**, a full one is $25. The launcher is currently sideloaded from the Cloudflare Worker, so it will need registering before the UK date. Registering it and publishing the free app on Play could share one developer identity.
- **Time.** Counting verification, the 14-day test and review, expect about three weeks from sign-up to a public listing (a guide's estimate).
- **Medical wording on the Play page** is the most likely cause of a rejection, so draft it carefully.

## Suggested order
1. Decide personal vs organisation, and check the public-details screen at sign-up.
2. Create the Play Console account (you; ID and payment are yours to enter).
3. I prepare: store text, privacy page URL, assetlinks hosting plan, the Premium-hiding switch, screenshots from the demo personas.
4. Build the wrapper with Bubblewrap (needs the laptop for the signing key; keep the key backed up like the launcher key).
5. Closed test with 12 people for 14 days, then production.

## Sources
- Play Console Help, app testing requirements for new personal accounts: https://support.google.com/googleplay/android-developer/answer/14151465
- Play Console Help, Health apps policy: https://support.google.com/googleplay/android-developer/answer/13996823
- Android Developers Blog, Android developer verification (June 2026): https://android-developers.googleblog.com/2026/06/android-developer-verification.html
- Android Developer Console help, understanding developer verification: https://support.google.com/android-developer-console/answer/16561738
- TesterBee, Google Play developer verification 2026 (third party): https://testerbee.com/blog/google-play-developer-verification-2026
- Chrome for Developers, Trusted Web Activity (the page I could read was from 2020; check the live docs before building): https://developer.chrome.com/docs/android/trusted-web-activity/whats-new
