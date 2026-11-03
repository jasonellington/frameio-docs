#!/usr/bin/env python3
"""Download every asset the converter referenced, plus logo, favicon and font."""
import json, os, subprocess
from concurrent.futures import ThreadPoolExecutor
A = json.load(open('mirror/assets.json'))
H = 'https://developer.frame.io'
A[H + '/_fern-files/frame-io.docs.buildwithfern.com/a50c9704d731d0a28156d3481281d88b5e8c2bced7af007b60ff8f7a2553d184/docs/assets/Frame.io_Symbol_18.svg'] = '/logo/frame-io-symbol.svg'
A[H + '/api/fern-docs/favicon.ico'] = '/favicon.jpg'
A[H + '/_fern-files/frame-io.docs.buildwithfern.com/74306710c319c6a89285b5169c6c6365387c61c33fe04b426fb12505430595c1/docs/assets/font1.woff2'] = '/fonts/frame-gothic.woff2'
def get(kv):
    u, l = kv
    p = l.lstrip('/')
    os.makedirs(os.path.dirname(p) or '.', exist_ok=True)
    if os.path.exists(p) and os.path.getsize(p) > 0: return (0, u, p)
    r = subprocess.run(['curl', '-sSL', '--retry', '3', '--max-time', '180', '-w', '%{http_code}', '-o', p, u], capture_output=True, text=True)
    return (r.stdout.strip(), u, p)
with ThreadPoolExecutor(6) as ex: res = list(ex.map(get, A.items()))
bad = [r for r in res if r[0] not in (0, '200')]
print('assets', len(res), 'failed', len(bad), bad[:10])
big = sorted(((os.path.getsize(r[2]), r[2]) for r in res if os.path.exists(r[2])), reverse=True)[:6]
print(big); print('total MB', sum(os.path.getsize(r[2]) for r in res if os.path.exists(r[2])) / 1e6)
