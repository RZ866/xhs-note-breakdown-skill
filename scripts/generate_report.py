#!/usr/bin/env python3
"""Offline renderer for host-authored analysis. No OCR, scraping or model calls."""
import argparse
import base64
import html
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TYPES = {'FACT': '原笔记事实', 'ANALYSIS': '分析判断', 'RECOMMENDATION': '复刻建议'}
ROLES = {'title', 'cover', 'body', 'gallery', 'product', 'comments', 'metrics'}
TITLES = {'title': '爆款标题拆解', 'cover': '小红书爆款带货封面拆解', 'content': '带货内容拆解', 'full': '小红书爆款带货笔记拆解报告', 'fragment': '小红书商业素材片段拆解'}
SUMMARY = {'product': '卖什么', 'price': '材料标注价格', 'audience': '卖给谁', 'scene': '使用场景', 'pain': '核心痛点', 'content_type': '内容类型', 'click': '点击核心', 'retention': '停留核心', 'trust': '信任核心', 'conversion': '成交核心', 'dna': '爆款 DNA', 'learn': '最值得学'}
STAGES = {'click': '点击', 'retention': '停留', 'trust': '信任', 'interest': '商品兴趣', 'conversion': '成交考虑'}
SECTIONS = {'business', 'title', 'cover', 'body', 'placement', 'traffic', 'retention', 'trust', 'conversion', 'comments', 'metrics', 'limits'}

class ReportError(ValueError):
    pass

def require(condition, message):
    if not condition:
        raise ReportError(message)

def text(value, field, limit=20000):
    require(isinstance(value, str) and bool(value.strip()) and len(value) <= limit, field)
    return value

def identifier(value):
    require(isinstance(value, str) and re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,63}', value), 'invalid identifier')
    return value

def route(materials):
    roles = {role for m in materials for role in m['roles']}
    images = [m for m in materials if m['kind'] == 'image']
    if ('gallery' in roles or (images and 'body' in roles)):
        return 'full'
    if 'body' in roles:
        return 'content'
    if 'cover' in roles:
        return 'cover'
    if 'title' in roles:
        return 'title'
    return 'fragment'

def validate(data):
    require(isinstance(data, dict) and data.get('schema_version') == '1.0', 'schema_version')
    require(data.get('commerce') in ('present', 'uncertain', 'absent'), 'commerce')
    require(type(data.get('example', False)) is bool, 'example')
    materials = data.get('materials')
    require(isinstance(materials, list) and 0 < len(materials) <= 40, 'materials')
    mids = {}
    for m in materials:
        identifier(m.get('id'))
        require(m['id'] not in mids, 'duplicate material')
        require(m.get('kind') in ('text', 'image'), 'material kind')
        require(isinstance(m.get('roles'), list) and m['roles'] and set(m['roles']) <= ROLES, 'roles')
        text(m.get('label'), 'material label', 200)
        if m['kind'] == 'text':
            text(m.get('content'), 'text content', 120000)
        else:
            require(type(m.get('inspected')) is bool, 'image inspected flag')
            if m.get('file') is not None:
                text(m['file'], 'image filename', 500)
        mids[m['id']] = m
    roles = {r for m in materials for r in m['roles']}
    mode = route(materials)
    evidence = data.get('evidence', [])
    require(isinstance(evidence, list) and len(evidence) <= 400, 'evidence')
    eids = {}
    for e in evidence:
        identifier(e.get('id'))
        require(e['id'] not in eids and e.get('material_id') in mids, 'evidence source')
        text(e.get('location'), 'evidence location', 300)
        text(e.get('observation'), 'observation', 4000)
        require(type(e.get('clear')) is bool, 'evidence clarity')
        require(e.get('kind') in ('quote', 'visual', 'user_statement'), 'evidence kind')
        m = mids[e['material_id']]
        if m['kind'] == 'image':
            require(m['inspected'], 'cannot cite unseen image')
        else:
            require(e['kind'] != 'visual', 'visual claim from text')
            text(e.get('quote'), 'text evidence quote', 4000)
            require(e['quote'] in m['content'], 'quote not found in supplied text')
        eids[e['id']] = e
    claims = data.get('claims')
    require(isinstance(claims, dict) and 0 < len(claims) <= 400, 'claims')
    for cid, c in claims.items():
        identifier(cid)
        text(c.get('text'), 'claim text', 4000)
        require(c.get('type') in TYPES, 'claim type')
        ids = c.get('evidence_ids')
        require(isinstance(ids, list) and ids and all(i in eids for i in ids), 'unresolved evidence')
        if c['type'] == 'FACT':
            require(all(eids[i]['clear'] for i in ids), 'fact relies on unclear evidence')
    def refs(ids):
        require(isinstance(ids, list) and all(i in claims for i in ids), 'unknown claim reference')
    summary = data.get('summary', {})
    require(isinstance(summary, dict) and set(summary) <= set(SUMMARY), 'summary keys')
    refs([v for v in summary.values() if v is not None])
    sections = data.get('sections', [])
    require(isinstance(sections, list), 'sections')
    seen_sections = set()
    for section in sections:
        sid = section.get('id')
        require(sid in SECTIONS and sid not in seen_sections, 'section id')
        seen_sections.add(sid)
        text(section.get('heading'), 'section heading', 100)
        refs(section.get('claim_ids'))
        if sid in ('title', 'cover', 'body', 'comments', 'metrics'):
            require(sid in roles, 'section has no corresponding material')
        if sid == 'conversion':
            require(data['commerce'] != 'absent', 'noncommerce conversion')
    funnel = data.get('funnel', [])
    require(isinstance(funnel, list), 'funnel')
    stage_order = []
    for item in funnel:
        require(item.get('stage') in STAGES, 'funnel stage')
        refs([item.get('claim_id')])
        require(claims[item['claim_id']]['type'] == 'ANALYSIS', 'funnel must be hypothetical analysis')
        stage_order.append(list(STAGES).index(item['stage']))
        if mode in ('title', 'cover'):
            require(item['stage'] == 'click', 'partial input cannot establish full funnel')
        if data['commerce'] == 'absent':
            require(item['stage'] not in ('interest', 'conversion'), 'noncommerce funnel')
    require(stage_order == sorted(set(stage_order)), 'funnel order')
    dna = data.get('dna', {})
    require(isinstance(dna, dict) and set(dna) <= {'traffic', 'retention', 'trust', 'conversion', 'formula'}, 'dna keys')
    refs(list(dna.values()))
    require(all(claims[i]['type'] == 'ANALYSIS' for i in dna.values()), 'dna must be analysis')
    if data['commerce'] == 'absent':
        require('conversion' not in dna and not summary.get('conversion'), 'noncommerce claims')
    learning = data.get('learning', [])
    require(isinstance(learning, list) and len(learning) <= 5, 'learning points')
    for item in learning:
        refs([item.get(k) for k in ('what', 'why', 'transfer')])
        require(claims[item['what']]['type'] == 'RECOMMENDATION' and claims[item['transfer']]['type'] == 'RECOMMENDATION', 'learning type')
    tasks = data.get('image_tasks', [])
    require(isinstance(tasks, list), 'image tasks')
    for task in tasks:
        require(task.get('material_id') in mids and mids[task['material_id']]['kind'] == 'image', 'image task source')
        refs(task.get('claim_ids'))
    for metric in data.get('metrics', []):
        text(metric.get('label'), 'metric label', 100)
        text(metric.get('scope'), 'metric scope', 200)
        require(metric.get('evidence_id') in eids, 'metric evidence')
        require(type(metric.get('clear')) is bool, 'metric clarity')
        if metric['clear']:
            require(eids[metric['evidence_id']]['clear'], 'unclear metric evidence')
            text(metric.get('display'), 'metric display', 100)
            observed = eids[metric['evidence_id']]
            require(metric['display'] in (observed.get('quote','') + observed['observation']), 'metric value not observed')
        else:
            require(metric.get('display') is None, 'do not guess blurred numbers')
    for key in ('limitations', 'do_not_copy'):
        require(isinstance(data.get(key, []), list), key)
        for value in data.get(key, []):
            text(value, key, 1000)
    return mode

def image_data(material, media_root, budget):
    """Only embed caller-staged local raster images; no network or arbitrary files."""
    filename = material.get('file')
    if not filename or media_root is None:
        return None, '未嵌入原图；保留图片编号与分析。'
    relative = Path(filename)
    if relative.is_absolute() or '://' in filename or re.match(r'^[A-Za-z]:', filename) or '\\' in filename or '..' in relative.parts:
        raise ReportError('image must be a safe relative path')
    root = Path(media_root).resolve()
    candidate = root / relative
    resolved = candidate.resolve()
    require(resolved.is_relative_to(root), 'image outside material root')
    cursor = candidate
    while cursor != root:
        require(not cursor.is_symlink(), 'image symlink rejected')
        cursor = cursor.parent
    if not candidate.is_file():
        return None, '当前环境未能嵌入原图；保留图片编号与分析。'
    size = candidate.stat().st_size
    if size > 12 * 1024 * 1024 or budget[0] + size > 40 * 1024 * 1024:
        return None, '图片超过报告嵌入上限；保留图片编号与分析。'
    blob = candidate.read_bytes()
    mime = 'image/png' if blob.startswith(b'\x89PNG\r\n\x1a\n') else 'image/jpeg' if blob.startswith(b'\xff\xd8\xff') else 'image/webp' if blob[:4] == b'RIFF' and blob[8:12] == b'WEBP' else None
    if not mime:
        return None, '此图片格式未嵌入；支持 PNG、JPEG、WebP。'
    budget[0] += size
    return 'data:' + mime + ';base64,' + base64.b64encode(blob).decode('ascii'), None

def escape(value):
    return html.escape(str(value), quote=True)

def render(data, media_root=None):
    mode = validate(data)
    materials = {m['id']: m for m in data['materials']}
    evidence = {e['id']: e for e in data['evidence']}
    claims = data['claims']
    warnings = []
    def claim(cid, compact=False):
        c = claims[cid]
        proof = ''
        for eid in dict.fromkeys(c['evidence_ids']):
            e = evidence[eid]
            source = materials[e['material_id']]
            origin = '用户补充，未独立核验' if e['kind'] == 'user_statement' else '截图观察' if source['kind'] == 'image' else '用户提供的原文'
            proof += '<li><strong>' + escape(source['label']) + ' · ' + escape(e['location']) + '</strong><span class="source-kind">' + origin + '</span><p>' + escape(e['observation']) + '</p></li>'
        return '<div class="claim"><span class="badge '+c['type'].lower()+'">【'+TYPES[c['type']]+'】</span><p>'+escape(c['text'])+'</p><details><summary>查看依据 · '+str(len(set(c['evidence_ids'])))+'</summary><ul class="proof">'+proof+'</ul></details></div>'
    def claims_html(ids):
        return ''.join(claim(cid) for cid in ids)
    images = {}
    budget = [0]
    for m in data['materials']:
        if m['kind'] == 'image':
            images[m['id']], warning = image_data(m, media_root, budget)
            if warning:
                warnings.append(m['label']+'：'+warning)
    def figure(mid):
        m = materials[mid]
        picture = '<img src="'+images[mid]+'" alt="'+escape(m['label'])+'，用户提供的分析素材" loading="eager">' if images.get(mid) else '<div class="image-missing">'+escape(m['label'])+'<br>原图未嵌入</div>'
        return '<figure>'+picture+'<figcaption>'+escape(m['label'])+'</figcaption></figure>'
    title = TITLES[mode]
    if data['commerce'] == 'absent':
        title = '非典型带货内容研究'
    heading = data.get('subject', '从内容线索，看见商业路径')
    text(heading, 'subject', 200)
    body = '<header class="hero"><div class="eyebrow">COMMERCE NOTE RESEARCH <span>V1.0</span></div><h1>'+escape(title)+'</h1><p class="subtitle">内容商业逻辑 × 用户心理 × 成交路径 × 爆款 DNA</p><div class="meta"><span>'+escape(data.get('date', str(date.today())))+'</span><span>'+str(len(materials))+' 份素材</span><span>'+{'title':'标题分析','cover':'封面分析','content':'文字内容分析','full':'笔记 / 多图分析','fragment':'素材片段分析'}[mode]+'</span></div></header>'
    if data.get('example'):
        body += '<div class="notice">原创合成演示素材 · 不是真实平台笔记或真实经营数据</div>'
    body += '<main id="main"><section class="overview" aria-labelledby="overview-title"><div class="section-top"><span class="index">01 / 核心结论</span><h2 id="overview-title">'+escape(heading)+'</h2></div><p class="boundary">“爆款”是研究主题，不是效果认证。以下机制分析不证明真实点击、停留或成交。</p><div class="summary-grid">'
    summary_order = ['product','price','audience','scene','pain','content_type','click','retention','trust','conversion','learn']
    for key in summary_order:
        cid = data.get('summary', {}).get(key)
        if cid:
            body += '<article class="summary-card"><h3>'+SUMMARY[key]+'</h3>'+claim(cid, True)+'</article>'
    body += '</div></section>'
    if data.get('metrics'):
        body += '<section class="panel"><h2>材料中的数据</h2><p class="boundary">仅记录可见或用户明确提供的数据；不同对象、时间和口径不能相互替代。</p><div class="metric-grid">'
        for metric in data['metrics']:
            e = evidence[metric['evidence_id']]
            origin = '用户补充，未独立核验' if e['kind'] == 'user_statement' else '材料可见，未独立核验'
            body += '<article><h3>'+escape(metric['label'])+'</h3><strong class="metric">'+escape(metric['display'] if metric['clear'] else '不可辨认')+'</strong><p>'+escape(metric['scope'])+'</p><small>'+origin+' · '+escape(materials[e['material_id']]['label'])+' · '+escape(e['location'])+'</small></article>'
        body += '</div></section>'
    if data.get('funnel'):
        body += '<section class="panel"><div class="section-top"><span class="index">02 / 内容路径</span><h2>内容如何推动下一步</h2></div><p class="boundary">内容机制假设；不是实测转化漏斗。实际成交未由此验证。</p><ol class="funnel">'
        for item in data['funnel']:
            body += '<li><h3>'+STAGES[item['stage']]+'</h3>'+claim(item['claim_id'])+'</li>'
        body += '</ol></section>'
    dna = data.get('dna', {})
    if dna:
        body += '<section class="dna" aria-labelledby="dna-title"><span class="index">03 / 可迁移模型</span><h2 id="dna-title">爆款 DNA</h2><p>解释可能的作用，不保证复制结果。</p><div class="dna-grid">'
        for key,label in [('traffic','流量 DNA'),('retention','停留 DNA'),('trust','信任 DNA'),('conversion','成交 DNA')]:
            if dna.get(key):
                body += '<article><h3>'+label+'</h3>'+claim(dna[key])+'</article>'
        body += '</div>'
        if dna.get('formula'):
            body += '<div class="formula"><h3>DNA 总公式</h3>'+claim(dna['formula'])+'</div>'
        body += '</section>'
    cover_section = next((s for s in data.get('sections', []) if s['id'] == 'cover'), None)
    cover = next((m for m in data['materials'] if m['kind'] == 'image' and 'cover' in m['roles']), None)
    if cover_section and cover:
        body += '<section class="panel"><span class="index">04 / 视觉拆解</span><h2>'+escape(cover_section['heading'])+'</h2><div class="cover-grid">'+figure(cover['id'])+'<div>'+claims_html(cover_section['claim_ids'])+'</div></div></section>'
    if data.get('image_tasks'):
        body += '<section class="panel"><h2>图片卖货路径</h2><p class="boundary">'+escape(data.get('sequence_note','按收到的顺序展示，不确认原发布顺序。'))+'</p><div class="gallery">'
        tasks = {t['material_id']:t for t in data['image_tasks']}
        for m in data['materials']:
            if m['id'] in tasks:
                body += '<article>'+figure(m['id'])+claims_html(tasks[m['id']]['claim_ids'])+'</article>'
        body += '</div></section>'
    body += '<div class="research-grid">'
    for section in data.get('sections', []):
        if section['id'] == 'cover' and cover:
            continue
        if section['claim_ids']:
            body += '<section class="panel" id="section-'+section['id']+'"><h2>'+escape(section['heading'])+'</h2>'+claims_html(section['claim_ids'])+'</section>'
    body += '</div>'
    if data.get('learning'):
        body += '<section class="panel learning"><h2>最值得复刻</h2><p>学结构与验证方法，不复制作品或虚构体验。</p><div class="learning-grid">'
        for i,item in enumerate(data['learning'], 1):
            body += '<article><span class="number">'+str(i).zfill(2)+'</span><h3>做法</h3>'+claim(item['what'])+'<h3>为什么可能起作用</h3>'+claim(item['why'])+'<h3>真正应该学什么</h3>'+claim(item['transfer'])+'</article>'
        body += '</div></section>'
    body += '<section class="closing-grid"><article class="panel caution"><h2>不要直接照搬</h2><ul>'
    for warning in data.get('do_not_copy', ['原作者独有表达、图片与故事；没有证据的效果、销量或第一人称体验。']):
        body += '<li>'+escape(warning)+'</li>'
    body += '</ul></article><article class="panel"><h2>本次分析边界</h2><ul>'
    limits = data.get('limitations', []) + warnings
    if mode == 'cover':
        limits += ['当前分析基于封面。补充完整笔记截图后可继续分析正文、信任与成交逻辑。']
    if mode == 'title':
        limits += ['当前仅有标题，未分析不存在的封面或正文。']
    if data['commerce'] == 'absent':
        limits += ['当前材料不是典型带货内容，不强行建立成交路径。']
    for warning in dict.fromkeys(limits):
        body += '<li>'+escape(warning)+'</li>'
    body += '</ul></article></section></main><footer>基于用户提供素材的内容研究 · 离线单文件 · 可使用浏览器打印保存 PDF</footer>'
    template = (ROOT/'assets/report.html').read_text(encoding='utf-8')
    return template.replace('{{TITLE}}', escape(title)).replace('{{BODY}}', body)

def chat_summary(data):
    validate(data)
    lines = ['# 爆款拆解核心结论', '']
    for key in ('product','audience','pain','click','retention','trust','conversion','dna','learn'):
        cid = data.get('summary', {}).get(key)
        if cid:
            c = data['claims'][cid]
            lines.append('**'+SUMMARY[key]+'：**【'+TYPES[c['type']]+'】'+c['text'])
    lines += ['', '以上为素材分析，不能据此确认实际成交或爆款表现。']
    return '\n\n'.join(lines)

def generate(data, output, media_root=None):
    rendered = render(data, media_root)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered, encoding='utf-8')
    output.with_name('chat-summary.md').write_text(chat_summary(data), encoding='utf-8')
    return output

def main(argv=None):
    parser = argparse.ArgumentParser(description='Offline report renderer for host analysis')
    parser.add_argument('analysis', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--media-root', type=Path)
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args(argv)
    try:
        require(args.analysis.stat().st_size <= 4*1024*1024, 'analysis input too large')
        data = json.loads(args.analysis.read_text(encoding='utf-8-sig'))
        generate(data, args.output, args.media_root)
        print('分析报告已生成。')
        return 0
    except (ValueError, OSError, TypeError, KeyError) as exc:
        if args.debug:
            print(str(exc), file=sys.stderr)
        else:
            print('报告尚未生成：素材或分析记录需要由助手内部检查。', file=sys.stderr)
        return 2

if __name__ == '__main__':
    sys.exit(main())
