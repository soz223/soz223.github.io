"""Build a small, dependency-free static research portfolio."""
from pathlib import Path
from html import escape as e
from html.parser import HTMLParser
import json
import re
import shutil
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / 'data/content.json').read_text(encoding='utf-8'))
PROJECTS = DATA['projects']
PAPERS = DATA['publications']
BASE = 'https://soz223.github.io'
PAGES = {}

def link(url, label, cls=''):
    return f'<a href="{e(url, quote=True)}" class="{cls}">{e(label)}</a>'

def tags(values):
    return ''.join(f'<span class="tag">{e(v)}</span>' for v in values)

def head(kicker, title, description):
    return f'<header class="pagehead"><div class="eyebrow">{e(kicker)}</div><h1>{e(title)}</h1><p>{e(description)}</p></header>'

def page(route, title, description, body, scripts=''):
    nav = [('research','Research'),('publications','Publications'),('learning','Learning'),('ai-tooling','AI Tooling')]
    links = ''.join(f'<a href="/{path}/"'+(' aria-current="page"' if route==path else '')+f'>{label}</a>' for path,label in nav)
    extra = ''.join(link('/'+path+'/',label) for path,label in [('projects','Selected work'),('collaboration','AI Collaboration Record'),('github','GitHub activity'),('about','About & CV'),('hire','Recruiter brief'),('contact','Contact')])
    html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(title)} · Songlin Zhao</title><meta name="description" content="{e(description,quote=True)}"><meta name="theme-color" content="#183944"><link rel="canonical" href="{BASE}/{route + '/' if route else ''}"><link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/assets/site.css"></head><body><a class="skip" href="#main">Skip to content</a><header class="topbar"><div class="wrap"><nav class="nav" aria-label="Main navigation"><a class="brand" href="/"><i>sz.</i>Songlin Zhao</a><div class="navlinks">{links}<details class="navdetails"><summary>Explore</summary><div>{extra}</div></details></div></nav></div></header><main id="main" class="wrap">{body}</main><footer class="foot"><div class="wrap"><div>Songlin Zhao<br>Multimodal foundation models · Research agents</div><div>{link('mailto:soz223@lehigh.edu','Email')}{link('https://github.com/soz223','GitHub')}{link('/contact/','Contact')}</div></div></footer>{scripts}</body></html>'''
    path = ROOT / route / 'index.html'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding='utf-8')
    PAGES[route] = title

def project_rows():
    return ''.join(f'''<article class="project"><div class="projectid">0{i+1}</div><div><div class="eyebrow">{p['area']}</div><h3>{link('/projects/'+p['id']+'/',p['name'])}</h3><p>{e(p['summary'])}</p>{tags(p['tags'])}</div><div class="note"><span class="statusdot"></span>{p['status']}<p>{e(p['role'])}</p>{link(p['repo'],'View repository ↗')}</div></article>''' for i,p in enumerate(PROJECTS))

def papers_html(papers):
    return ''.join(f'''<article class="paper" data-type="{p['type']}"><div class="year">{p['year']}</div><div><h3>{link(p['url'],p['title']) if p['url'] else e(p['title'])}</h3><p>{e(p['authors']).replace('Songlin Zhao','<strong>Songlin Zhao</strong>')}</p><p>{e(p['venue'])} · <span class="tag">{p['type']}</span></p></div></article>''' for p in papers)

def build_home():
    body = f'''<section class="hero"><div><div class="eyebrow">Research · Engineering · Clinical collaboration</div><h1>Multimodal foundation models &amp; research agents.</h1><p>{e(DATA['intro'])}</p><div class="actions">{link('/projects/','Explore selected work','button primary')}{link('/contact/','Get in touch ↗','button')}</div></div><aside class="heroaside"><div><span class="meta">RESEARCH</span><strong>Lehigh University</strong><span>Computer Science PhD</span></div><div><span class="meta">CLINICAL CONNECTION</span><strong>Mayo Clinic</strong><span>Research Assistant · Collaboration</span></div><div><span class="meta">FOCUS</span><strong>Images + text + agents</strong></div></aside></section><img class="banner" src="/assets/research-loop.svg" alt="Medical images and text connect to foundation models, research agents and clinical collaboration at Mayo Clinic."><section class="section"><div class="sectionhead"><div><div class="eyebrow">Selected work</div><h2>From images to useful systems.</h2></div>{link('/research/','Research overview ↗')}</div>{project_rows()}</section><section class="section"><div class="sectionhead"><div><div class="eyebrow">Open research practice</div><h2>AI Collaboration Record</h2></div><p>A public record of AI-assisted development, linked to the commits that support it.</p></div><a href="/collaboration/"><img class="banner" src="/assets/ai-collaboration.svg" alt="Evidence-based AI collaboration landscape and activity totals"></a><div class="actions">{link('/collaboration/','Explore the interactive record ↗','button')}</div></section><section class="section"><div class="sectionhead"><div><div class="eyebrow">Read & build</div><h2>A connected research workspace.</h2></div></div><div class="grid"><article class="card"><span class="number">01</span><h3>Publications</h3><p>Medical imaging, brain networks and multimodal learning.</p>{link('/publications/','Read the papers ↗')}</article><article class="card"><span class="number">02</span><h3>Learning</h3><p>A practical route through imaging, distributed training and agent systems.</p>{link('/learning/','Explore the roadmap ↗')}</article><article class="card"><span class="number">03</span><h3>AI Tooling</h3><p>Research assistants, retrieval workflows and evaluation prototypes.</p>{link('/ai-tooling/','Browse the tools ↗')}</article></div></section>'''
    page('', 'Multimodal foundation models & research agents', DATA['intro'], body)

def build_remaining():
    body = head('Research','Images, language and individual variation.','My research connects multimodal modeling with clinically grounded questions and reusable research tools.')
    body += '<div class="flow"><div><strong>Represent</strong>Learn from images and text.</div><div><strong>Scale</strong>Train across parallel compute.</div><div><strong>Evaluate</strong>Study transfer and individual variation.</div><div><strong>Assist</strong>Connect models to research workflows.</div></div><img class="banner" src="/assets/research-capabilities.svg" alt="50 H200 GPUs in parallel, high-quality medical data at scale, and advanced medical models.">'
    body += '<section class="section">'+project_rows()+'</section><section class="section prose"><h2>Clinical collaboration</h2><p>I work with Wei Liu’s group in Radiation Oncology at Mayo Clinic Arizona on medical image analysis, radiotherapy segmentation and multimodal foundation models. At Lehigh University, I am advised by Lifang He.</p><p>My engineering experience includes coordinating training across 50 H200 GPUs, volumetric imaging pipelines and extensive agent applications.</p></section>'
    page('research','Research','Multimodal foundation models, neuroimaging and clinical research.',body)
    page('projects','Selected work','Research projects and public implementation artifacts.',head('Selected work','Four connected research directions.','Explore the research question, my role and the public materials for each direction.')+project_rows())
    for p in PROJECTS:
        body = head(p['area'],p['name'],p['summary'])+tags(p['tags'])+f'<div class="ribbon"><strong>{p["status"]}</strong></div><section class="prose"><h2>Research question</h2><p>{e(p["question"])}</p><h2>Approach</h2><p>{e(p["details"])}</p><h2>My contribution</h2><p>{e(p["role"])}</p><h2>Public materials</h2><ul>'+''.join('<li>'+link(u,t)+'</li>' for t,u in p['resources'])+'</ul></section><div class="actions">'+link('/projects/','← All selected work','button')+'</div>'
        page('projects/'+p['id'],p['name'],p['summary'],body)
    body = head('Publications','Papers & preprints.','Selected work in medical imaging, multimodal learning and brain network analysis.')
    body += '<div class="toolbar" aria-label="Filter publications"><button data-paper-filter="All" aria-pressed="true">All</button><button data-paper-filter="Peer-reviewed" aria-pressed="false">Peer-reviewed</button><button data-paper-filter="Preprint" aria-pressed="false">Preprints</button></div>'+papers_html(PAPERS)
    body += '<section class="section prose"><h2>Ongoing work</h2><p>Current directions include text-prompted volumetric tumor and lesion segmentation, BrainNet benchmarking, and multimodal normative modeling. These projects are presented as research in progress.</p><p class="meta">Publication metadata follows the June 2026 CV and linked publisher or arXiv records. MICCAI AMAI is a workshop; AAAI Symposium Series is a symposium venue.</p></section>'
    page('publications','Publications','Peer-reviewed papers and preprints by Songlin Zhao.',body,'<script src="/assets/site.js" defer></script>')
    learning = [
      ('Medical imaging foundations','Start with image geometry, coordinate systems and reproducible preprocessing.', [('MONAI tutorials','https://github.com/Project-MONAI/tutorials'),('NiBabel documentation','https://nipy.org/nibabel/')], 'Build a small NIfTI loading and preprocessing notebook. Inspect spacing and orientation before modeling.'),
      ('Multimodal representation learning','Connect visual representations with language, prompts and downstream tasks.', [('Hugging Face learning hub','https://huggingface.co/learn'),('MedGPT-oss technical report','https://arxiv.org/abs/2603.00842')], 'Trace how images and text enter a model, and write down what an evaluation example actually measures.'),
      ('Training at scale','Understand data parallelism, memory use and reproducible experiment configuration.', [('PyTorch distributed training','https://docs.pytorch.org/tutorials/intermediate/ddp_tutorial.html'),('PyTorch distributed documentation','https://docs.pytorch.org/docs/stable/distributed.html')], 'Run a small multi-process experiment, then compare throughput, memory and convergence with a single-process baseline.'),
      ('Brain networks & normative models','Study connectivity construction and the interpretation of individual deviations.', [('BrainNet toolkit','https://pypi.org/project/brainnet-graph/'),('FAAE research implementation','https://github.com/soz223/FAAE')], 'Compare a small set of network construction choices under the same evaluation protocol.'),
      ('Research agents & evaluation','Connect retrieval and tool use to inspectable outputs and repeatable checks.', [('UniBrainAssistant','https://github.com/soz223/UniBrainAssistant'),('Hugging Face agents course','https://huggingface.co/learn/agents-course')], 'Define a bounded task, record tool inputs and outputs, and evaluate successful completion alongside failure cases.')]
    body=head('Learning','A roadmap for building research systems.','A curated starting point around my research areas, with official resources and small practice tasks.')+'<div class="roadmap">'
    for title,desc,resources,task in learning:
        body+=f'<section class="step"><div><h2>{title}</h2><p>{desc}</p><ul>'+''.join('<li>'+link(u,t)+'</li>' for t,u in resources)+f'</ul><p><strong>Try it:</strong> {task}</p></div></section>'
    body+='</div><p class="meta">This is a curated learning route, not a record of course completion. Linked resources belong to their respective authors.</p>'
    page('learning','Learning','A practical learning roadmap for imaging, multimodal models, parallel training and research agents.',body)
    tools=[('UniBrainAssistant','Conversational interface for structural brain MRI workflows, with tool calling and retrieval.','Public prototype','https://github.com/soz223/UniBrainAssistant'),('BrainNet assistant','An assistant project connected to brain-network research workflows.','Public repository','https://github.com/soz223/brainnetassistant.help'),('green-medagentbench','A public repository for medical-agent benchmark exploration.','Evaluation prototype','https://github.com/soz223/green-medagentbench'),('brainnet-graph','A Python package for functional brain network construction and analysis.','Published package','https://pypi.org/project/brainnet-graph/'),('P-MimicGraphRAG','An early design for personalized graph-based retrieval. The public repository contains project documentation.','Concept / documentation','https://github.com/soz223/P-MimicGraphRAG'),('AI Collaboration Record','The public snapshot and visualizations behind this portfolio’s collaboration dashboard.','Live record','/collaboration/')]
    body=head('AI Tooling','Tools that connect research steps.','Public projects spanning imaging assistants, retrieval and benchmark workflows.')+'<div class="grid two">'+''.join(f'<article class="card">{tags([s])}<h3>{n}</h3><p>{d}</p>{link(u,"Explore ↗")}</article>' for n,d,s,u in tools)+'</div><section class="section"><h2>Working stack</h2>'+tags(['Python','PyTorch','MONAI','3D medical imaging','LLM / VLM','RAG','Agent workflows','Distributed training','Docker'])+'</section>'
    page('ai-tooling','AI Tooling','Research agents, imaging workflows and open-source tooling.',body)
    body=head('About','Songlin Zhao','Computer Science PhD researcher at Lehigh University, working on multimodal foundation models and research agents.')+'<section class="prose"><h2>Research</h2><p>'+e(DATA['intro'])+'</p><h2>Experience & education</h2><article class="resource"><strong>Mayo Clinic · Research Assistant</strong><p>2025–present · Research collaboration with Wei Liu’s group, Radiation Oncology, Arizona.</p></article><article class="resource"><strong>Lehigh University · PhD in Computer Science</strong><p>2023–present · Advised by Lifang He. Expected graduation: approximately May 2027.</p></article><article class="resource"><strong>Tongji University · BS in Computer Science</strong><p>2019–2023</p></article><h2>Teaching</h2><p>Teaching Assistant and recitation host for CSE 262: Programming Languages at Lehigh University, Fall 2024. Contributions to research-oriented technology teaching in Fall 2026 include agents, harnesses and evaluation.</p><h2>Selected review service</h2><p>IEEE TMI, IEEE JBHI, Medical Physics, ACM HEALTH and ACM TKDD; conference service includes KDD 2024, NeurIPS 2024 and AAAI Spring Symposium Series 2025.</p><h2>Selected publications</h2>'+papers_html([PAPERS[2],PAPERS[5],PAPERS[7]])+'<div class="actions">'+link('/publications/','Full publication list','button')+link('/contact/','Contact','button')+'</div><p class="meta">This web CV summarizes the author-provided CV and subsequent updates, as of September 2026.</p></section>'
    page('about','About & web CV','Research background, education, teaching and service.',body)
    body=head('Recruiter brief','Research depth. Practical implementation.','Experience across multimodal modeling, medical imaging and agent applications.')+'<div class="grid"><article class="card"><h3>Foundation models</h3><p>3D medical images and text, volumetric segmentation, multimodal learning and model evaluation.</p>'+link('/projects/omnitumor/','OmniTumor ↗')+'</article><article class="card"><h3>Research engineering</h3><p>50 H200 GPUs in parallel, imaging preprocessing, reproducible experiments and benchmark development.</p>'+link('/projects/brainnet/','BrainNet ↗')+'</article><article class="card"><h3>Agent applications</h3><p>Conversational workflows, tool calling, retrieval and research-oriented evaluation.</p>'+link('/ai-tooling/','Public tooling ↗')+'</article></div><section class="section prose"><h2>Current context</h2><p>Computer Science PhD at Lehigh University, with ongoing research at Mayo Clinic. Expected graduation is approximately May 2027.</p><p>I welcome conversations about research and engineering opportunities involving multimodal AI, imaging and agent systems.</p><div class="actions">'+link('/about/','View web CV','button')+link('mailto:soz223@lehigh.edu','Email Songlin ↗','button primary')+'</div></section>'
    page('hire','Recruiter brief','A concise overview of Songlin Zhao’s research and engineering experience.',body)
    body=head('Contact','Let’s connect.','For research collaborations, technical conversations and opportunities in multimodal AI and agent systems.')+'<p class="contactlarge">'+link('mailto:soz223@lehigh.edu','soz223@lehigh.edu ↗')+'</p><section class="section"><div class="grid two"><article class="card"><h3>Research & work</h3><p>Lehigh University · Computer Science<br>Mayo Clinic · Research collaboration</p>'+link('/about/','About & web CV ↗')+'</article><article class="card"><h3>On GitHub</h3><p>Public research repositories, prototypes and development records.</p>'+link('https://github.com/soz223','github.com/soz223 ↗')+'</article></div></section>'
    page('contact','Contact','Contact Songlin Zhao at soz223@lehigh.edu.',body)
    body=head('GitHub','An open development record.','Public commit activity and repository snapshots, refreshed daily.')+'<img class="banner" src="/assets/github-activity.svg" alt="Animated public commit activity calendar"><section class="section"><h2>Public repositories</h2><div id="repo-list" class="grid two"><p class="loading">Loading repository snapshot…</p></div></section><section class="section"><h2>How this is counted</h2><p>Owned public repositories, excluding forks. The activity graph counts commits authored by soz223 on default branches over the last 365 days and deduplicates them by commit SHA. GitHub’s native contribution calendar uses different rules.</p>'+link('https://github.com/soz223?tab=repositories','See all repositories on GitHub ↗')+'</section>'
    page('github','GitHub activity','A public-only commit calendar and repository overview.',body,'<script src="/assets/site.js" defer></script>')
    body=head('Open development','AI Collaboration Record','Explore explicit AI assistance in public development, with a daily landscape and links to individual commits.')+'''<div id="collaboration"><div class="loading" role="status">Loading public collaboration records…</div></div><details class="method"><summary>How to read this record</summary><p>The scope is commits authored by soz223 on default branches of owned public, non-fork repositories over the last 365 days. Commits are deduplicated by SHA. This does not measure time spent, tokens, productivity or all AI use.</p><p>AI attribution requires an explicit AI trailer, a recognized AI co-author identity, or a documented assistance record for known public commits. A commit may involve multiple tools, so tool counts can overlap. Unattributed commits are not classified as human-only.</p><p>The Codex records from September 7, 2026 document assistance in creating this profile. Earlier unmarked history is left unattributed. Only public commit metadata is published; local conversations and private repositories are not scanned.</p><p><a href="/data/ai-evidence.json">Documented assistance records</a> · <a href="/data/activity.json">Download the public snapshot</a></p><h3>Record future assistance</h3><p>Add an explicit trailer when applicable:</p><pre><code>AI-Tool: Codex</code></pre><p>Automated snapshot updates do not receive AI attribution just because an AI helped write the updater.</p></details>'''
    page('collaboration','AI Collaboration Record','Interactive, evidence-based AI collaboration dashboard for Songlin Zhao.',body,'<script src="/assets/collaboration.js" defer></script>')

def validate():
    class Links(HTMLParser):
        def handle_starttag(self,tag,attrs):
            for key,value in attrs:
                if key in ('src','href') and value and value.startswith('/') and not value.startswith('//'):
                    clean=value.split('#')[0].split('?')[0]
                    target=ROOT/clean.lstrip('/')
                    if clean.endswith('/'):
                        target=target/'index.html'
                    assert target.exists(), f'Missing local target: {value}'
    for route in PAGES:
        content=(ROOT/route/'index.html').read_text(encoding='utf-8')
        assert not re.search(r'[\u4e00-\u9fff]', content), f'Non-English text in {route}'
        Links().feed(content)
    for path in (ROOT/'assets').glob('*.svg'):
        ET.parse(path)
    print(f'Built and validated {len(PAGES)} pages; local links and SVGs passed.')

if __name__=='__main__':
    import sys
    build_home()
    if '--home-only' not in sys.argv:
        build_remaining()
        sitemap='<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{BASE}/{r+"/" if r else ""}</loc></url>' for r in PAGES)+'</urlset>'
        (ROOT/'sitemap.xml').write_text(sitemap,encoding='utf-8')
        validate()
        # Stage only public artifacts for Pages, excluding scripts and repository metadata.
        dist=ROOT/'_site'
        dist.mkdir(exist_ok=True)
        for name in ['index.html','assets','data','archive','sitemap.xml','robots.txt','.nojekyll','THIRD_PARTY_NOTICES.md']+[r for r in PAGES if r and '/' not in r]:
            source=ROOT/name
            if source.is_dir():
                shutil.copytree(source,dist/name,dirs_exist_ok=True)
            elif source.exists():
                shutil.copy2(source,dist/name)
