#!/usr/bin/env python3
"""Encrypt anshin.html into a password-gated index.html (AES-256-GCM, PBKDF2-SHA256).
Usage: python3 lock.py <source.html> <output.html> <password>
"""
import sys, os, base64, json
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

src, out, pw = sys.argv[1], sys.argv[2], sys.argv[3]
ITER = 150_000
salt, iv = os.urandom(16), os.urandom(12)
key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITER).derive(pw.encode())
ct = AESGCM(key).encrypt(iv, open(src, 'rb').read(), None)
b64 = lambda b: base64.b64encode(b).decode()
payload = json.dumps({"salt": b64(salt), "iv": b64(iv), "iter": ITER, "ct": b64(ct)})

page = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="#0B5D6B">
<title>Anshin</title>
<style>
  html, body { margin:0; height:100%; background:#F7F5F0; font-family:-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, system-ui, sans-serif; color:#15232A; }
  .wrap { min-height:100%; display:flex; align-items:center; justify-content:center; padding:24px; box-sizing:border-box; }
  .card { width:100%; max-width:360px; background:#fff; border-radius:24px; padding:32px 28px; box-shadow:0 20px 60px rgba(21,35,42,0.12); display:flex; flex-direction:column; gap:18px; align-items:center; text-align:center; }
  h1 { margin:0; font-size:28px; font-weight:800; letter-spacing:-0.02em; }
  .tag { font-size:12px; font-weight:700; color:#0B5D6B; letter-spacing:0.08em; }
  p { margin:0; font-size:14px; color:#5F655F; line-height:1.45; }
  input { width:100%; height:52px; border:1.5px solid #D9D4CA; border-radius:14px; padding:0 16px; font-size:17px; box-sizing:border-box; text-align:center; letter-spacing:0.1em; }
  input:focus { outline:2px solid #0B5D6B; outline-offset:1px; }
  button { width:100%; height:52px; border:0; border-radius:16px; background:#0B5D6B; color:#fff; font-size:17px; font-weight:700; cursor:pointer; }
  button:disabled { opacity:0.6; }
  .err { color:#C2410C; font-weight:700; min-height:18px; font-size:13px; }
</style>
</head>
<body>
<div class="wrap"><form class="card" id="f">
  <svg width="72" height="72" viewBox="0 0 72 72" role="img" aria-label="Anshin logo"><circle cx="36" cy="36" r="27" fill="none" stroke="#0B5D6B" stroke-width="7" stroke-linecap="round" stroke-dasharray="148 22" transform="rotate(-70 36 36)"></circle><circle cx="36" cy="36" r="7" fill="#E07A5F"></circle></svg>
  <div><h1>Anshin</h1><div class="tag">安心 · PEACE OF MIND</div></div>
  <p>This prototype is private. Enter the password to open it.</p>
  <label for="pw" style="position:absolute;left:-9999px">Password</label>
  <input id="pw" type="password" autocomplete="current-password" autofocus placeholder="Password">
  <button id="go" type="submit">Open</button>
  <div class="err" id="err"></div>
</form></div>
<script id="payload" type="application/json">__PAYLOAD__</script>
<script>
(function () {
  var P = JSON.parse(document.getElementById('payload').textContent);
  var b = function (s) { return Uint8Array.from(atob(s), function (c) { return c.charCodeAt(0); }); };
  var form = document.getElementById('f'), pw = document.getElementById('pw'), err = document.getElementById('err'), go = document.getElementById('go');
  async function unlock(pass) {
    var km = await crypto.subtle.importKey('raw', new TextEncoder().encode(pass), 'PBKDF2', false, ['deriveKey']);
    var key = await crypto.subtle.deriveKey({ name: 'PBKDF2', salt: b(P.salt), iterations: P.iter, hash: 'SHA-256' }, km, { name: 'AES-GCM', length: 256 }, false, ['decrypt']);
    var pt = await crypto.subtle.decrypt({ name: 'AES-GCM', iv: b(P.iv) }, key, b(P.ct));
    return new TextDecoder().decode(pt);
  }
  function launch(html) {
    var fr = document.createElement('iframe');
    fr.setAttribute('title', 'Anshin');
    fr.style.cssText = 'position:fixed;inset:0;width:100%;height:100%;border:0;background:#F7F5F0';
    fr.srcdoc = html;
    document.body.innerHTML = ''; document.body.style.background = '#F7F5F0'; document.body.appendChild(fr);
  }
  async function tryPass(pass, remember) {
    go.disabled = true; err.style.color = '#0B5D6B'; err.textContent = 'Unlocking…';
    if (!(window.crypto && crypto.subtle)) { err.style.color = '#C2410C'; err.textContent = 'This viewer can’t run the app. Open the file in Safari or Chrome.'; go.disabled = false; return; }
    try {
      var html = await unlock(pass);
      if (remember) { try { sessionStorage.setItem('anshin.pw', pass); } catch (e) {} }
      launch(html);
    } catch (e) { err.style.color = '#C2410C'; err.textContent = 'That password didn’t work.'; go.disabled = false; pw.select(); }
  }
  form.addEventListener('submit', function (e) { e.preventDefault(); tryPass(pw.value, true); });
  try { var saved = sessionStorage.getItem('anshin.pw'); if (saved) tryPass(saved, false); } catch (e) {}
})();
</script>
</body>
</html>
'''
open(out, 'w').write(page.replace('__PAYLOAD__', payload))
print(out, os.path.getsize(out), 'bytes')
