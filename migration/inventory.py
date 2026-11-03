#!/usr/bin/env python3
"""Build the page inventory from Fern nav assets, cross-checked with sitemap + llms.txt."""
import json, glob, os, re, sys
NAV = {
 'platform_welcome': ('Platform','V4','Home'),
 'platform_api-reference_files_show': ('Platform','V4','API Reference'),
 'platform_docs_overview': ('Platform','V4','Docs'),
 'platform_changelog': ('Platform','V4','Changelog'),
 'platform_v4-experimental_welcome': ('Platform','V4 Experimental','Home'),
 'platform_v4-experimental_api-reference_files_bulk-copy': ('Platform','V4 Experimental','API Reference'),
 'platform_v4-experimental_docs_overview': ('Platform','V4 Experimental','Docs'),
 'platform_v4-experimental_changelog': ('Platform','V4 Experimental','Changelog'),
 'platform_v2_index': ('Platform','Legacy','Docs'),
 'platform_v2_api-reference_webhooks_delete-webhook': ('Platform','Legacy','API Reference'),
 'camera-to-cloud_welcome': ('Camera to Cloud',None,'Home'),
 'camera-to-cloud_getting-started-with-cloud-device-integrations': ('Camera to Cloud',None,'Docs'),
 'camera-to-cloud_api-reference_device-identify': ('Camera to Cloud',None,'API Reference'),
}
rows = []
def walk(n, trail, ctx):
    t = n.get('type')
    if t in ('page','endpoint','changelogEntry','changelog','webhook','webSocket','grpc','graphql'):
        rows.append(dict(slug=n.get('slug'), title=n.get('title'), kind=t, product=ctx[0], version=ctx[1], tab=ctx[2],
                         trail=trail, method=n.get('method'), node_id=n.get('id'), hidden=bool(n.get('hidden')),
                         availability=n.get('availability'), icon=n.get('icon'),
                         endpoint_id=n.get('endpointId'), api=n.get('apiDefinitionId')))
    label = n.get('title')
    for c in n.get('children') or []:
        walk(c, trail + ([label] if t in ('section','apiPackage','apiReference') else []), ctx)
for k, ctx in NAV.items():
    d = json.load(open(f'mirror/nav/{k}.json'))
    for n in d['sidebarChildren']:
        walk(n, [], ctx)
json.dump(rows, open('mirror/inventory.json','w'), indent=1)
from collections import Counter
print(Counter((r['product'],r['version'],r['tab'],r['kind']) for r in rows))
print('rows', len(rows), 'unique slugs', len({r['slug'] for r in rows}))
