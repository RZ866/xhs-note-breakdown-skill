"""Audit and package only the public Skill tree. Never package task materials."""
import hashlib,json,re,sys,zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
NAME='xiaohongshu-viral-commerce-note-analyzer'
ROOT_FILES={'SKILL.md','README.md','LICENSE','CHANGELOG.md','VERSION','.gitignore','.gitattributes'}
PUBLIC_DIRS={'agents','references','scripts','assets','examples','tests','.github'}
EXCLUDED={'__pycache__','.qa','.git','outputs','private-inputs','dist','node_modules','.venv'}
PATTERNS={
    'private-key':r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
    'github-credential':r'\b(?:ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})',
    'model-credential':r'\bsk-(?:proj-)?[A-Za-z0-9_-]{35,}',
    'personal-absolute-path':r'(?i)(?:[A-Z]:[/\\](?:Users|用户)[/\\][A-Za-z0-9_.\u4e00-\u9fff -]+[/\\]|/(?:Users|home)/[A-Za-z0-9_.-]+/)',
    'secret-assignment':r'''(?i)(?:api[_-]?key|password|web_session|access_token)\s*[=:]\s*["']([A-Za-z0-9_-]{24,})["']''',
}

def public_files(root=ROOT):
    files=[]
    for p in root.rglob('*'):
        rel=p.relative_to(root)
        if any(part in EXCLUDED for part in rel.parts) or p.suffix=='.pyc':continue
        if p.is_symlink():raise ValueError('symbolic link in public tree')
        if p.is_file() and (rel.as_posix() in ROOT_FILES or rel.parts[0] in PUBLIC_DIRS):files.append(p)
    return sorted(files)

def audit(files,root=ROOT):
    findings=[]
    for p in files:
        rel=p.relative_to(root)
        if p.name.startswith('.env') or p.suffix=='.key' or any(x in p.name.lower() for x in ['credentials','cookies','secrets']):findings.append((str(rel),'private filename'))
        if p.suffix in ('.png','.jpg','.jpeg','.webp'):
            if rel.parts[0] not in ('assets','examples'):findings.append((str(rel),'unapproved public image location'))
            continue
        content=p.read_text(encoding='utf-8-sig')
        for kind,pattern in PATTERNS.items():
            if re.search(pattern,content):findings.append((str(rel),kind))
    return findings

def main():
    files=public_files();findings=audit(files)
    required=['SKILL.md','README.md','LICENSE','CHANGELOG.md','references/analysis-framework.md','references/html-report-spec.md','scripts/generate_report.py','assets/report.html','tests/test_report.py']
    for rel in required:
        if not (ROOT/rel).is_file():findings.append((rel,'missing required file'))
    if findings:
        for location,kind in findings:print(location,kind)
        return 1
    dest=ROOT/'dist';dest.mkdir(exist_ok=True)
    package=dest/(NAME+'-v'+(ROOT/'VERSION').read_text().strip()+'.zip')
    with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as archive:
        for p in files:archive.write(p,NAME+'/'+p.relative_to(ROOT).as_posix())
    result={'public_files':len(files),'findings':0,'archive':package.name,'sha256':hashlib.sha256(package.read_bytes()).hexdigest(),'scope':'Public tree pattern scan; original images reviewed manually. Not a proof of semantic privacy.'}
    (dest/'release-audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result));return 0

if __name__=='__main__':sys.exit(main())
