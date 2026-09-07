"""Generate a public-only, evidence-based activity snapshot. Standard library only."""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path
import json
import math
import os
import re
import urllib.request
import urllib.error

ROOT = Path(__file__).resolve().parents[1]
OWNER = 'soz223'
NOW = datetime.now(timezone.utc)
START = (NOW - timedelta(days=364)).date()
TOKEN = os.environ.get('GH_TOKEN', os.environ.get('GITHUB_TOKEN', ''))

def api(route):
    headers = {'User-Agent': 'Songlin-Public-Activity', 'Accept': 'application/vnd.github+json'}
    if TOKEN:
        headers['Authorization'] = 'Bearer ' + TOKEN
    req = urllib.request.Request('https://api.github.com' + route, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=40) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        if error.code == 409:
            return []
        raise RuntimeError(f'Public activity fetch failed: {route}, HTTP {error.code}') from None

def pages(route):
    result = []
    for page in range(1, 101):
        part = api(route + ('&' if '?' in route else '?') + f'per_page=100&page={page}')
        result.extend(part)
        if len(part) < 100:
            return result
    raise RuntimeError('Pagination limit reached; previous snapshot must be retained.')

def providers(message):
    found = set()
    # Only explicit AI trailers or recognized AI co-author identities qualify.
    for line in message.splitlines():
        if re.match(r'^(AI-Tool|AI-Provider|AI-Assisted-By|AI-Actor):', line, re.I):
            value = line.split(':', 1)[1].strip()
            if value:
                found.add(value)
        if re.match(r'^Co-authored-by:', line, re.I):
            for name, pattern, identity in [('Codex', r'\bcodex\b', r'@openai\.com|codex.*@users\.noreply\.github\.com'), ('Claude', r'\bclaude\b', r'@anthropic\.com'), ('GitHub Copilot', r'\bcopilot\b', r'copilot.*@(?:users\.noreply\.)?github\.com'), ('Gemini', r'\bgemini\b', r'gemini.*\[bot\]|@google\.com')]:
                if re.search(pattern, line, re.I) and re.search(identity, line, re.I):
                    found.add(name)
    return sorted(found)

def collect():
    repos = [r for r in pages(f'/users/{OWNER}/repos?type=owner') if not r['private'] and not r['fork']]
    evidence = json.loads((ROOT / 'data/ai-evidence.json').read_text())
    declared = {item['sha']: item for item in evidence['commits']}
    def history(repo):
        route = f"/repos/{OWNER}/{repo['name']}/commits?author={OWNER}&since={START}T00:00:00Z"
        return repo['name'], pages(route)
    unique = {}
    with ThreadPoolExecutor(max_workers=4) as pool:
        for repo, commits in pool.map(history, repos):
            for commit in commits:
                item = commit['commit']
                day = item['author']['date'][:10]
                if not str(START) <= day <= str(NOW.date()):
                    continue
                tools = providers(item['message'])
                kind = 'Commit trailer' if tools else 'Unattributed'
                if commit['sha'] in declared:
                    tools = sorted(set(tools + declared[commit['sha']]['tools']))
                    kind = 'Documented assistance'
                unique.setdefault(commit['sha'], {'sha': commit['sha'], 'date': day, 'repo': repo,
                    'url': commit['html_url'], 'tools': tools, 'evidence': kind})
    commits = sorted(unique.values(), key=lambda c: (c['date'], c['sha']), reverse=True)
    daily = []
    for i in range(365):
        day = str(START + timedelta(days=i))
        records = [c for c in commits if c['date'] == day]
        daily.append({'date': day, 'total': len(records), 'ai': sum(bool(c['tools']) for c in records)})
    tool_counts = Counter(t for c in commits for t in c['tools'])
    languages = Counter(r['language'] for r in repos if r.get('language'))
    snapshot = {'updated': NOW.isoformat(timespec='seconds'), 'from': str(START), 'to': str(NOW.date()),
        'scope': 'Commits authored by soz223 on the default branches of owned public, non-fork repositories, over the last 365 days. Deduplicated by SHA. This is not the complete GitHub contribution calendar.',
        'repositories': [{'name': r['name'], 'url': r['html_url'], 'language': r['language'], 'stars': r['stargazers_count'], 'forks': r['forks_count']} for r in repos],
        'total': len(commits), 'ai': sum(bool(c['tools']) for c in commits),
        'active_days': sum(d['total'] > 0 for d in daily), 'ai_days': sum(d['ai'] > 0 for d in daily),
        'tools': dict(tool_counts), 'languages': dict(languages), 'days': daily, 'commits': commits}
    (ROOT / 'data/activity.json').write_text(json.dumps(snapshot, indent=2) + '\n')
    render(snapshot)
    print(json.dumps({k: snapshot[k] for k in ['updated', 'total', 'ai', 'active_days', 'tools']}))

def wrap(title, body, height=440):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 {height}" role="img" aria-labelledby="title"><title id="title">{escape(title)}</title><style>text{{font-family:Arial,sans-serif;fill:#23414c}}.small{{font-size:16px;fill:#59717b}}.pulse{{animation:pulse 3s ease-in-out infinite}}@keyframes pulse{{50%{{opacity:.35}}}}@media(prefers-reduced-motion:reduce){{.pulse{{animation:none}}.signal{{display:none}}}}</style><rect x="1" y="1" width="1198" height="{height-2}" rx="22" fill="#f6fafb" stroke="#dce8eb"/>{body}</svg>'''

def render(data):
    (ROOT / 'assets').mkdir(exist_ok=True)
    body = '<text x="40" y="48" font-size="25" font-weight="600">GitHub activity</text>'
    body += f'<text x="40" y="78" class="small">{data["from"]} to {data["to"]} · Owned public repositories</text>'
    for x, value, label in [(40, data['total'], 'Public commits'), (330, data['active_days'], 'Active days'), (610, len(data['repositories']), 'Repositories'), (890, data['ai'], 'AI-attributed commits')]:
        body += f'<text x="{x}" y="140" font-size="35" font-weight="600">{value}</text><text x="{x}" y="170" class="small">{label}</text>'
    colors = ['#e3edf0', '#b6dcd2', '#79bca9', '#439682', '#236a5e']
    maximum = max((d['total'] for d in data['days']), default=1) or 1
    offset = (datetime.fromisoformat(data['from']).weekday() + 1) % 7
    path = []
    for i, day in enumerate(data['days']):
        col, row = divmod(i + offset, 7)
        x, y = 42 + col * 21, 212 + row * 21
        level = 0 if day['total'] == 0 else min(4, 1 + math.ceil(day['total'] / maximum * 3))
        body += f'<rect x="{x}" y="{y}" width="16" height="16" rx="4" fill="{colors[level]}"><title>{day["date"]}: {day["total"]} commits</title></rect>'
        path.append(f'{x+8},{y+8}')
    motion_path = 'M' + ' L'.join(path)
    for i in range(5):
        body += f'<circle class="signal" r="{5-i*.45}" fill="#d7a347" opacity="{.95-i*.14}"><animateMotion dur="40s" begin="{-i*.13}s" repeatCount="indefinite" path="{motion_path}"/></circle>'
    body += '<text x="40" y="392" class="small">A moving signal traces the calendar. Cell color represents the actual public commit count.</text>'
    body += f'<text x="40" y="418" class="small">Snapshot: {data["updated"][:10]} UTC · GitHub REST API · Default branches · Deduplicated commits</text>'
    (ROOT / 'assets/github-activity.svg').write_text(wrap('Public commit activity with an animated calendar signal', body), encoding='utf-8')
    body = '<text x="40" y="48" font-size="25" font-weight="600">AI Collaboration Record</text><text x="40" y="78" class="small">A research observatory built from explicit assistance records</text>'
    body += f'<text x="40" y="143" font-size="42" font-weight="600">{data["ai"]}</text><text x="40" y="173" class="small">AI-attributed commits</text><text x="40" y="231" font-size="32">{data["ai_days"]}</text><text x="40" y="261" class="small">Active AI days</text><text x="40" y="319" font-size="32">{data["total"]-data["ai"]}</text><text x="40" y="349" class="small">Unattributed commits</text>'
    recent = data['days'][-84:]
    peak = max((d['total'] for d in recent), default=1) or 1
    for i, day in enumerate(recent):
        col, row = divmod(i, 7)
        x, y = 570 + col * 34 - row * 24, 150 + col * 8 + row * 15
        height = 4 + day['total'] / peak * 105
        ai_height = day['ai'] / peak * 105
        body += f'<path d="M{x},{y}l22,6 0,{-height} -22,-6Z" fill="#b6c9d2"/><path d="M{x+22},{y+6}l17,-10 0,{-height} -17,10Z" fill="#8fa8b5"/><path d="M{x},{y-height}l17,-10 22,6 -17,10Z" fill="#dbe7ed"/>'
        if ai_height:
            body += f'<path class="pulse" d="M{x},{y-height}l17,-10 22,6 -17,10Z" fill="#339e88"/><path d="M{x},{y-height}l22,6 0,{ai_height} -22,-6Z" fill="#63b9a4"/>'
    body += '<rect x="435" y="358" width="12" height="12" rx="3" fill="#63b9a4"/><text x="455" y="370" class="small">Explicit AI evidence</text><rect x="660" y="358" width="12" height="12" rx="3" fill="#b6c9d2"/><text x="680" y="370" class="small">Unattributed</text><text x="40" y="411" class="small">84-day landscape · Unknown does not mean human-only · Open the dashboard to inspect records</text>'
    (ROOT / 'assets/ai-collaboration.svg').write_text(wrap('AI collaboration: evidence-based isometric public commit landscape', body), encoding='utf-8')

if __name__ == '__main__':
    collect()
