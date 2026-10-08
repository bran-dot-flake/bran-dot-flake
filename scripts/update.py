#!/usr/bin/env python3
"""Build a GitHub-native profile from public repository evidence. Python 3.12+."""
import collections, concurrent.futures, datetime as dt, html, json, os
from pathlib import Path
import shutil, subprocess, tempfile, time, urllib.request

ROOT = Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT / 'config.json').read_text())
USER = CFG['username']
NOW = dt.datetime.now(dt.timezone.utc)
SINCE = (NOW - dt.timedelta(days=90)).isoformat()
PALETTE = ['#79dfb5','#77baff','#ba9cff','#ef92be','#f4bf75','#83d7df']

def get(url):
    headers = {'User-Agent':'profile-dashboard', 'Accept':'application/vnd.github+json'}
    # Never send an API credential to a download/redirect host.
    if url.startswith('https://api.github.com/') and os.getenv('GH_TOKEN'):
        headers['Authorization'] = 'Bearer ' + os.environ['GH_TOKEN']
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=90) as r:
                return r.read()
        except Exception:
            if attempt == 2: raise
            time.sleep(2 ** attempt)

def pages(path):
    result=[]
    for page in range(1,1001):
        sep='&' if '?' in path else '?'
        batch=json.loads(get(f'https://api.github.com/{path}{sep}per_page=100&page={page}'))
        if not isinstance(batch,list): raise ValueError('Unexpected API response')
        result.extend(batch)
        if len(batch)<100: return result
    raise RuntimeError('Pagination limit reached; refusing partial totals')

def scan(repo):
    name=repo['name']
    print('Scanning', name, flush=True)
    if not repo['size']: return {'name':name,'languages':{},'files':0,'commits':[]}
    with tempfile.TemporaryDirectory() as temp:
        dest=Path(temp)/'repo'
        subprocess.run(['git','clone','--quiet','--depth=1','--single-branch',
                        repo['clone_url'],str(dest)],check=True,timeout=300)
        command=[os.getenv('CLOC','cloc')]
        if command[0].endswith('/cloc') and not os.access(command[0],os.X_OK): command.insert(0,'perl')
        out=subprocess.run(command+['--json','--quiet','--vcs=git',
            '--exclude-dir=node_modules,vendor,dist,build,.venv,venv,coverage',str(dest)],
            check=True,capture_output=True,text=True,timeout=180)
        data=json.loads(out.stdout or '{}')
        # cloc treats prose/data as languages; keep them out of the code metric.
        excluded={'SUM','header','Markdown','JSON','YAML','Text','CSV','XML','SVG','TOML','INI','reStructuredText'}
        languages={k:v['code'] for k,v in data.items() if k not in excluded and isinstance(v,dict)}
        files=len(subprocess.check_output(['git','-C',str(dest),'ls-files','-z']).split(b'\0'))-1
    commits=pages(f'repos/{USER}/{name}/commits?since={SINCE}')
    # All authors, default branch. Bot commits excluded when GitHub identifies the account.
    commits=[{'sha':c['sha'],'date':c['commit']['committer']['date']} for c in commits
             if (c.get('author') or {}).get('type')!='Bot' and '[bot]' not in c['commit']['author']['name']]
    return {'name':name,'languages':languages,'files':files,'commits':commits}

def text(x,y,value,size=13,color='#a3b1c3',weight=400,anchor='start'):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}" text-anchor="{anchor}">{html.escape(str(value))}</text>'
def rect(x,y,w,h,fill,rx=12,stroke='none'):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}"/>'
def svg(w,h,body,title):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{html.escape(title)}">
<title>{html.escape(title)}</title><style>text{{font-family:Segoe UI,Arial,sans-serif}}.pulse{{animation:pulse 5s ease-in-out infinite}}.flow{{stroke-dasharray:4 9;animation:flow 24s linear infinite}}@keyframes pulse{{0%,100%{{opacity:.45}}50%{{opacity:1}}}}@keyframes flow{{to{{stroke-dashoffset:-130}}}}@media(prefers-reduced-motion:reduce){{*{{animation:none!important}}}}</style>{body}</svg>'''

def render(data):
    repos=data['repos']; scans=data['scans']
    langs=collections.Counter()
    for s in scans: langs.update(s['languages'])
    commits={c['sha']:c for s in scans for c in s['commits']}
    counts=[sum(bool(set(r['topics']) & set(a['topics'])) for r in repos) for a in CFG['specializations']]
    b=rect(1,1,898,436,'#0d131d',18,'#253043')
    b+=text(26,29,'PUBLIC WORK / AT A GLANCE',11,'#79dfb5',700)
    b+=text(874,29,'Updated '+data['updated'],11,anchor='end')
    metrics=[(f'{sum(langs.values()):,}','lines of code'),(f'{sum(s["files"] for s in scans):,}','tracked files'),(len(commits),'commits / 90 days'),(len(repos),'repositories')]
    for i,(value,label) in enumerate(metrics):
        x=26+i*220
        b+=text(x,74,value,30,'#edf3fb',650)+text(x,97,label,12)
        b+=rect(x,112,192,3,PALETTE[i],1)
    b+=text(26,146,'CODE COMPOSITION',11,'#d4deeb',650)
    top=langs.most_common(4); total=sum(langs.values())
    if len(langs)>4: top.append(('Other',sum(v for _,v in langs.most_common()[4:])))
    for i,(name,num) in enumerate(top):
        y=174+i*29; width=188*num/max(1,max(langs.values(),default=1))
        b+=text(26,y,name,12,'#cbd6e6')+rect(119,y-10,188,8,'#202b3c',4)+rect(119,y-10,round(width,2),8,PALETTE[i],4)
        b+=text(392,y,f'{num:,}  /  {num/max(1,total):.0%}',11,anchor='end')
    if not top: b+=text(26,178,'No eligible source code found.')
    b+=text(452,146,'SPECIALIZATION / REPOSITORY TOPICS',11,'#d4deeb',650)
    center=(663,233)
    positions=[(501,181),(797,181),(503,289),(796,289),(662,324)]
    for i,((x,y),area,n) in enumerate(zip(positions,CFG['specializations'],counts)):
        color=area['color']
        b+=f'<path d="M{center[0]} {center[1]} Q {x} {center[1]} {x} {y}" fill="none" stroke="{color}" opacity=".28"/>'
        b+=f'<path class="flow" d="M{center[0]} {center[1]} Q {x} {center[1]} {x} {y}" fill="none" stroke="{color}" opacity=".55"/>'
        b+=f'<circle cx="{x}" cy="{y}" r="{8+min(n,8)}" fill="{color}" fill-opacity=".12" stroke="{color}"/>'
        b+=text(x,y+4,n,11,color,700,'middle')
        b+=text(x,y+29,area['name'],12,'#cbd6e6',400,'middle')
    b+=f'<circle cx="663" cy="233" r="37" fill="#141f2e" stroke="#3b4b61"/>'
    b+=text(663,231,'SECURITY',10,'#edf3fb',700,'middle')+text(663,246,'OPERATIONS',9,'#a3b1c3',400,'middle')
    b+=text(26,350,'WEEKLY COMMITS',10,'#d4deeb',650)
    bins=[0]*13
    end=dt.datetime.fromisoformat(data['collected_at'])
    for c in commits.values():
        age=(end-dt.datetime.fromisoformat(c['date'].replace('Z','+00:00'))).days
        if 0<=age<90: bins[12-min(12,age//7)]+=1
    points=' '.join(f'{26+i*30},{393-n/max(1,max(bins))*30:.1f}' for i,n in enumerate(bins))
    b+=f'<polyline points="{points}" fill="none" stroke="#79dfb5" stroke-width="2" stroke-linejoin="round"/>'
    b+=text(26,418,'90 days ago',10)+text(386,418,'now',10,anchor='end')
    b+=text(452,393,'Nodes count matching repos; areas can overlap.',11)
    b+=text(452,414,'Public originals · default branches · bots excluded from commits',10)
    (ROOT/'assets/dashboard.svg').write_text(svg(900,438,b,'Public repository metrics, code composition, weekly commits and specialization network'))
    for i,item in enumerate(CFG['featured']):
        repo=next((r for r in repos if r['name']==item['repo']),None)
        if not repo: raise ValueError('Featured repository missing: '+item['repo'])
        c=item['color']; b=rect(1,1,438,144,'#101824',14,'#283449')+rect(19,20,3,103,c,1)
        b+=text(35,30,item['category'],10,c,700)+text(35,60,item['title'],19,'#edf3fb',650)
        for j,line in enumerate(item['lines']): b+=text(35,84+j*20,line,12)
        b+=text(35,130,f'Updated {repo["pushed_at"][:10]}',10)
        if repo['stargazers_count']:
            b+=text(415,130,f'{repo["stargazers_count"]} stars',10,c,400,'end')
        (ROOT/f'assets/project-{i+1}.svg').write_text(svg(440,146,b,item['title']+' — '+'. '.join(item['lines'])))
    cards=[]
    for i,item in enumerate(CFG['featured']):
        cards.append(f'<a href="https://github.com/{USER}/{item["repo"]}"><img width="49%" src="assets/project-{i+1}.svg" alt="{html.escape(item["title"])} — {html.escape(item["lines"][0])}" /></a>')
    readme=f'''# Brandon Chaney
**IT foundation. Security focus. Evidence behind the work.**

I support users and infrastructure, investigate security events, and build tools that make the next investigation easier.

[Portfolio](https://brandonchaney.dev) · [All repositories](https://github.com/{USER}?tab=repositories)

<img src="assets/dashboard.svg" width="900" alt="Public work: {sum(langs.values()):,} lines of code, {sum(s['files'] for s in scans):,} tracked files, {len(commits)} non-bot commits in 90 days, {len(repos)} repositories. Topic counts: {', '.join(a['name']+': '+str(n) for a,n in zip(CFG['specializations'],counts))}." />

### Tools I work with

<img src="https://skillicons.dev/icons?i={CFG['skills']}&amp;theme=dark&amp;perline=8" height="46" alt="Python, Azure, Linux, Bash, Docker, Git, PowerShell, Windows" />

**Investigate:** Splunk · Sentinel · Wireshark · Sysmon &nbsp; **Automate:** Wazuh · Shuffle · TheHive

### Selected work

<p>
{cards[0]}
{cards[1]}
<br />
{cards[2]}
{cards[3]}
</p>

<details>
<summary>Behind the dashboard</summary>

Updated daily by GitHub Actions. Code and files are measured from current default branches of public, non-fork, non-archived repositories; this profile repository is excluded. Code uses cloc and excludes prose, data/config formats, and common build/vendor folders. Files include all tracked files, including images and documentation. Code totals describe repository contents, not sole authorship.

Commits cover the last 90 days on those default branches, across all authors, excluding identifiable bots and deduplicating hashes. The line shows 13 weekly buckets (the oldest is partial); it is not GitHub's contribution calendar. The specialization network counts repository topics, not proficiency. Skills and featured-project descriptions are deliberately curated.

</details>
'''
    (ROOT/'README.md').write_text(readme)
    (ROOT/'data/metrics.json').write_text(json.dumps({'updated':data['updated'],'lines_of_code':sum(langs.values()),'tracked_files':sum(s['files'] for s in scans),'commits_90d':len(commits),'repositories':len(repos),'languages':dict(langs),'specializations':dict(zip([a['name'] for a in CFG['specializations']],counts))},indent=2)+'\n')

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(); parser.add_argument('--render-only',action='store_true'); args=parser.parse_args()
    cache=ROOT/'data/source.json'
    if args.render_only:
        data=json.loads(cache.read_text())
    else:
        repos=[r for r in pages(f'users/{USER}/repos?type=owner') if not r['fork'] and not r['archived'] and r['name'] not in CFG['exclude_repositories']]
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool: scans=list(pool.map(scan,repos))
        # All fetches must succeed before generated output or the last good snapshot changes.
        data={'updated':NOW.strftime('%b %d, %Y'),'collected_at':NOW.isoformat(),'repos':[{k:r[k] for k in ['name','topics','pushed_at','stargazers_count']} for r in repos],'scans':scans}
    render(data)
    cache.write_text(json.dumps(data,indent=2)+'\n')
    print('Dashboard updated successfully.')
