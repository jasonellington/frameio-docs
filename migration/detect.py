import re, sys, pathlib
E = '[\U0001F000-\U0001FFFF☀-➿]'
P = {
  'A': rf'\[\s*{E}[^\]]*?####[^\]]*?\]\([^)]+\)',
  'B': rf'\[{E}+[A-Z][^\]]+\]\([^)]+\)',
  'C': r'\[\s*\d+\s*\n\s*\n\s*###[^\]]+\]\([^)]+\)',
  'D': rf'(?m)^{E}\s*\n\s*\n####\s',
  'E': r'```prism-code',
  'F': r'(?m)^description:\s*"?:::',
  'G': r'&lt;[A-Za-z0-9_-]+&gt;',
  'H': r'(?m)^---\s*\n\s*\n---\s*$',
  'J': r'(?m)^(Copy page|Edit on GitHub|Edit this page|Was this (page )?helpful)',
  'K': r'(?m)^\|(\s*\|)+\s*$',
}
for f in pathlib.Path(sys.argv[1]).rglob('*'):
    if any(x in f.parts for x in ('mirror', 'migration', 'openapi', 'openapi-src')): continue
    if f.is_file() and f.suffix in ('.md', '.mdx'):
        t = f.read_text(errors='ignore')
        hits = [k for k, p in P.items() if re.search(p, t, re.S)]
        if hits: print(f, ' '.join(hits))
