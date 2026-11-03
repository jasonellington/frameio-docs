#!/usr/bin/env python3
"""Every source URL, V4 alias and locale sample must resolve on the local preview."""
import json, re, subprocess, sys, collections
from concurrent.futures import ThreadPoolExecutor
B = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:3456'
rows = json.load(open('mirror/inventory.json'))
urls = ['/' + r['slug'] for r in rows]
urls += ['/platform/v4/' + r['slug'][len('platform/'):] for r in rows if r['slug'].startswith('platform/') and not r['slug'].startswith(('platform/v2', 'platform/v4-experimental'))]
urls += ['/de-DE/' + r['slug'] for r in rows[::40]]
for r in json.load(open('redirects.json')):
    if ':slug' not in r['source']: urls.append(r['source'])
urls = sorted(set(urls))
def chk(u):
    o = subprocess.run(['curl', '-s', '-o', '/dev/null', '-L', '--max-time', '60', '-w', '%{http_code} %{num_redirects} %{url_effective}', B + u], capture_output=True, text=True).stdout.split(' ', 2)
    return (o[0], int(o[1] or 0), u, o[2].replace(B, '') if len(o) > 2 else '')
with ThreadPoolExecutor(4) as ex: res = list(ex.map(chk, urls))
print('checked', len(res), collections.Counter(r[0] for r in res))
# Each real page must land on itself, not just return 200.
def expect(s):
    if re.match(r'^platform(/v4-experimental)?/changelog/\d', s): return '/' + s.split('/changelog/')[0] + '/changelog'
    return '/platform/v2' if s == 'platform/v2/index' else '/' + s
wrong = []
byurl = {r[2]: r for r in res}
for row in rows:
    r = byurl.get('/' + row['slug'])
    got = (r[3] or '').split('#')[0].rstrip('/')
    want = expect(row['slug'])
    if got != want and got != want.removesuffix('/index'): wrong.append((row['slug'], got))
print('pages landing somewhere else', len(wrong), wrong[:12])
for r in res:
    if r[0] != '200': print(' ', r)
print('chained redirects', [r for r in res if r[1] > 1][:10], 'count', sum(1 for r in res if r[1] > 1))
