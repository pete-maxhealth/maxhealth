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

## Licence service (licence.php)

Upload `licence.php` next to `register.php`. Then, ONE LEVEL ABOVE `public_html` (never inside it), create the folder `maxedhealth_licence/` containing `config.php`:

```php
<?php return ['signing_secret' => 'LONG-RANDOM-STRING', 'admin_secret' => 'ANOTHER-LONG-RANDOM-STRING'];
```

`signing_secret` must be exactly the same value as the Cloudflare Worker secret `LICENCE_SECRET` (Workers > maxhealth-ai > Settings > Variables and Secrets). The service keeps its state (hashed keys, bound devices, trials) in `state.json` in that same private folder. Publish the Premium files by placing `premium_payload.zip` there too (build it with `python3 tools/split_premium.py --out /tmp/split`).

Issue a key (founder keys allow 5 devices, premium keys 2):

```
curl -s -X POST https://pspence.co.uk/maxedhealth/licence.php -H 'Content-Type: application/json' -d '{"action":"issue","admin":"YOUR-ADMIN-SECRET","tier":"founder","note":"Pete"}'
```

Revoke with `{"action":"revoke","admin":"...","key":"XXXX-XXXX-XXXX-XXXX"}`. Keys are stored only as hashes, so a lost key cannot be looked up: revoke and issue another.
