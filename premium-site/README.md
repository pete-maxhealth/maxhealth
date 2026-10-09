# MaxedHealth Premium register-interest page

Two files for pspence.co.uk: `index.html` (the page) and `register.php` (stores sign-ups).

## Put it on GoDaddy
Needs GoDaddy **Linux web hosting (cPanel)**. The Websites + Marketing builder and domain-only plans cannot run PHP.
1. cPanel > File Manager > `public_html`. Create a folder `maxedhealth`.
2. Upload `index.html` and `register.php` into it. Address will be https://pspence.co.uk/maxedhealth/ (this is what the app links to, set by `MH_PREMIUM_URL` in maxhealth.html).
3. Sign-ups are saved to `maxedhealth_interest/interest.csv`, one level ABOVE `public_html`, so the web cannot download it. Download it from File Manager, open in a spreadsheet.
4. Test with your own email. Delete the test row afterwards.

## Before collecting real details
Check the ICO data protection fee self-assessment (ico.org.uk). The page already has a consent tick box and a plain privacy note.
