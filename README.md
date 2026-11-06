# Anshin — member app prototype (password-protected)

Clickable prototype of **Anshin** (安心, "peace of mind"), the digital front door for a virtual-first, no-deductible health plan.

`index.html` is **encrypted**. It shows a password screen; the app is decrypted in the browser (AES-256-GCM, key derived with PBKDF2) only when the right password is entered. The repository never contains the readable prototype.

## Update the prototype
```
python3 lock.py path/to/anshin.html index.html 'your-password'
git commit -am "update" && git push
```
Keep the unencrypted file outside the repo (the `.private/` folder is git-ignored).

## What's in it
Sign-in → eligibility match → Apple Health permissions → Home (copay dollars, 10 points = $1) → weekly check-in → Get care (12 doors, price-first recommendations, free-text triage, schedule-for-later, share-from-record) → Schedule → Copay $ → Longitudinal record → Anshin Chats (nurse line with 10-minute promise, care team, pharmacist, updates, preferences).

All names, prices, wait times and readings are sample data.
