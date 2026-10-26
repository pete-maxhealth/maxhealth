# Premium: one-button backup, then household sync (design, 26 Oct 2026)

Status: design only, nothing built. Testers: Pete and Jill (hand-issued founder keys).

## What already exists (verified in code, v3.10.1225)
- `autoBackupIfNeeded()` posts `buildFullBackupPayload()` to the phone's own `server.py` (`/save-full-backup`) on the first open each day.
- Server keeps one file per day in `data/backup/`, 7-day rotation, refuses a same-day backup under half the size of the existing one.
- `/list-backups` and `/load-full-backup` feed a restore screen (`executeRestoreFromBackup`, `mhApplyBackupObject`).
- The stock object (`mh_shopping_stock_v1`) already rides in the full backup.
- Free web app (no server): manual export/import only, plus a reminder (`checkBackupReminder`).

## The gap
Every copy lives on the same phone. A reinstall of Termux, a lost or broken phone, or a wiped data folder takes the backups with it. Retention is only 7 days. Restoring onto a new phone is manual.

## Phase 1: Back up now / Restore (Premium)
- One button "Back up now" and a list of dated copies with a "Restore" button on each. Same card on every screen that offers it: show/hide and reorder controls, existing help "?" pattern.
- Copy is encrypted in the app (WebCrypto AES-GCM, key derived from the person's recovery passphrase with PBKDF2). The service stores ciphertext only. A lost passphrase means a lost backup; the app says so before the first backup and shows a recovery code to write down.
- Home for the copies: the existing Cloudflare Worker (`worker.js`) with a KV namespace, gated by the licence token (`X-MH-Licence`, already verified by `verifyLicence`). No new vendor, no Google Cloud.
- Retention (defaults, all constants in one place): 7 daily, 4 weekly, 6 monthly. Pruned on write.
- Safety rules carried over: refuse a new copy under half the size of the latest; never overwrite, only add; restore always offers "keep what is on this phone" (takes a pre-restore copy first).
- Size: payloads are a few MB at most (`_BACKUP_BIG_OK` caps single keys at 3 MB); KV values allow 25 MB. Check real size on Pete's phone before relying on it.
- Free users keep today's behaviour unchanged.

## Phase 2: Household space (Premium)
- Peer model, no master. Every phone holds a full copy; what travels is a small signed list of changes (id, phone id, time, action), applied in any order.
- Counts are adjustments (use 1, bought 2), so two phones using an egg gives two used. Only a stock-take is last-writer-wins, and the losing figure is shown as a note.
- Shared: cupboard stock, shopping list (ticks), recipes, food library (with a soft delete and a history of who changed a figure). Not shared: meals logged, weights, symptoms, targets, layout, hidden cards.
- Personal override: any person can keep their own version of a shared food; logged meals keep the figures they had on the day.
- Join by code/QR. One licence = one household, up to 5 devices. Same relay and encryption as phase 1, with a household key instead of a personal one.

## Pre-requisites Pete must do (cannot be done from here)
1. Deploy `worker.js` in the Cloudflare dashboard, add the KV namespace binding and the `LICENCE_SECRET` secret (HOME_CHECKLIST A2, B3).
2. Issue two founder keys by hand (Pete, Jill).

## Honest wording for the video and the Premium page
"Coming soon". Say an encrypted copy is held for backup and sync, and that the passphrase is the only way back in. No price, no link except the Tally register-interest form.

## Tests (persona tests, targeted only, no sweep unless Pete asks)
- Phase 1: back up, change data, restore, compare; tiny-backup refusal; wrong passphrase; retention pruning; reload; Data tab neighbours (export/import, restore list); show/hide and reorder of the new card; side-by-side render against the existing Data cards.
- Phase 2: two simulated phones applying the same changes in different orders reach the same stock; stock-take clash; soft delete; override keeps logged meals; join and leave.

## Open decisions (defaults chosen, Pete can veto)
- Retention 7/4/6.
- Passphrase plus written recovery code (no key escrow, so nothing we could be compelled to read).
