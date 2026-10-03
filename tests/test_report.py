import copy,json,tempfile,unittest,sys,base64
from pathlib import Path
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'tests'))
from scripts.generate_report import validate,render,generate,route,ReportError,chat_summary,image_data
from sample_cases import CASES,title_case,cover_case,full_case,text_case,noncommerce_case,blurred_case

class Inspect(HTMLParser):
    def __init__(self):super().__init__();self.tags=[];self.attrs=[];self.data=[]
    def handle_starttag(self,tag,attrs):self.tags.append(tag);self.attrs.append((tag,dict(attrs)))
    def handle_data(self,data):self.data.append(data)

class ReportTests(unittest.TestCase):
    def test_title_mode(self):self.assertEqual(validate(title_case()),'title');self.assertNotIn('封面如何',render(title_case()))
    def test_cover_mode(self):self.assertEqual(validate(cover_case()),'cover')
    def test_text_mode(self):self.assertEqual(validate(text_case()),'content')
    def test_full_note_mode(self):
        d=full_case();d['materials'][0]['roles']=['cover','title','body'];self.assertEqual(validate(d),'full')
    def test_multi_images_mode(self):self.assertEqual(validate(full_case()),'full')
    def test_missing_image_fallback(self):
        d=cover_case();d['materials'][0].pop('file');self.assertIn('原图未嵌入',render(d));self.assertIn('当前分析基于封面',render(d))
    def test_blurred_not_guessed(self):
        result=render(blurred_case());self.assertIn('不可辨认',result);self.assertNotIn('metric">0',result)
    def test_noncommerce(self):
        d=noncommerce_case();out=render(d);self.assertIn('非典型带货',out);self.assertNotIn('<ol class="funnel">',out);self.assertNotIn('<h3>成交 DNA',out)
    def test_output_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=generate(full_case(),Path(tmp)/'report.html',ROOT/'examples/media');self.assertTrue(p.exists());self.assertTrue(p.with_name('chat-summary.md').exists());self.assertIn('data:image/png;base64,',p.read_text(encoding='utf-8'))
    def test_valid_all_cases(self):
        for name,builder in CASES.items():
            with self.subTest(name=name):validate(builder())
    def test_html_no_external_resources(self):
        p=Inspect();p.feed(render(full_case(),ROOT/'examples/media'))
        self.assertNotIn('script',p.tags)
        for tag,attrs in p.attrs:
            if 'src' in attrs:self.assertTrue(attrs['src'].startswith('data:image/'))
            if 'href' in attrs:self.assertTrue(attrs['href'].startswith('#'))
    def test_chinese_and_semantics(self):
        p=Inspect();p.feed(render(full_case()));self.assertEqual(p.tags.count('h1'),1);self.assertIn('爆款 DNA', ''.join(p.data));self.assertIn('main',p.tags)
    def test_embedded_image_alt(self):
        p=Inspect();p.feed(render(full_case(),ROOT/'examples/media'))
        images=[a for t,a in p.attrs if t=='img'];self.assertTrue(images);self.assertTrue(all(a.get('alt') for a in images))
    def test_script_injection(self):
        d=title_case();d['subject']='</title><script>globalThis.pwned=1</script>';d['claims']['click']['text']='<img src=x onerror=alert(1)> & " < >';out=render(d)
        p=Inspect();p.feed(out);self.assertNotIn('script',p.tags);self.assertNotIn('img',p.tags);self.assertIn('&lt;script&gt;',out)
    def test_attribute_injection(self):
        d=cover_case();d['materials'][0]['label']='" onload="evil()';p=Inspect();p.feed(render(d,ROOT/'examples/media'))
        self.assertTrue(all('onload' not in a for _,a in p.attrs))
    def test_evidence_escaping(self):
        d=cover_case();d['evidence'][0]['observation']='<svg onload="evil()">';p=Inspect();p.feed(render(d));self.assertNotIn('svg',p.tags)
    def test_unknown_evidence(self):
        d=title_case();d['claims']['click']['evidence_ids']=['nonexistent']
        with self.assertRaises(ReportError):validate(d)
    def test_empty_evidence(self):
        d=title_case();d['claims']['click']['evidence_ids']=[]
        with self.assertRaises(ReportError):validate(d)
    def test_fact_unclear_rejected(self):
        d=blurred_case();d['claims']['unknown']['type']='FACT'
        with self.assertRaises(ReportError):validate(d)
    def test_blurred_number_rejected(self):
        d=blurred_case();d['metrics'][0]['display']='10000'
        with self.assertRaises(ReportError):validate(d)
    def test_fabricated_metric_rejected(self):
        d=title_case();d['metrics']=[{'label':'销量','scope':'未知','display':'10000','clear':True,'evidence_id':'E1'}]
        with self.assertRaises(ReportError):validate(d)
    def test_quote_must_be_supplied(self):
        d=title_case();d['evidence'][0]['quote']='不存在于原文的文字'
        with self.assertRaises(ReportError):validate(d)
    def test_unseen_image_rejected(self):
        d=cover_case();d['materials'][0]['inspected']=False
        with self.assertRaises(ReportError):validate(d)
    def test_visual_claim_from_text_rejected(self):
        d=title_case();d['evidence'][0]['kind']='visual'
        with self.assertRaises(ReportError):validate(d)
    def test_no_body_without_body_material(self):
        d=cover_case();d['sections'].append({'id':'body','heading':'正文','claim_ids':['click']})
        with self.assertRaises(ReportError):validate(d)
    def test_noncommerce_funnel_rejected(self):
        d=noncommerce_case();d['funnel']=[{'stage':'conversion','claim_id':'mechanism'}]
        with self.assertRaises(ReportError):validate(d)
    def test_cover_complete_funnel_rejected(self):
        d=cover_case();d['funnel'].append({'stage':'trust','claim_id':'click'})
        with self.assertRaises(ReportError):validate(d)
    def test_fact_funnel_rejected(self):
        d=title_case();d['funnel'][0]['claim_id']='price'
        with self.assertRaises(ReportError):validate(d)
    def test_funnel_order(self):
        d=full_case();d['funnel'].reverse()
        with self.assertRaises(ReportError):validate(d)
    def test_duplicate_material(self):
        d=title_case();d['materials']*=2
        with self.assertRaises(ReportError):validate(d)
    def test_bad_claim_type(self):
        d=title_case();d['claims']['click']['type']='CERTAIN'
        with self.assertRaises(ReportError):validate(d)
    def test_dna_not_fact(self):
        d=title_case();d['dna']['formula']='price'
        with self.assertRaises(ReportError):validate(d)
    def test_learning_limit(self):
        d=title_case();d['learning']*=2
        with self.assertRaises(ReportError):validate(d)
    def test_empty_input(self):
        d=title_case();d['materials']=[]
        with self.assertRaises(ReportError):validate(d)
    def test_local_path_traversal(self):
        for filename in ['../secret.png','/etc/secret.png','C:/private/secret.png','https://example.com/a.png','..\\secret.png']:
            with self.subTest(path=filename),self.assertRaises(ReportError):image_data({'file':filename},ROOT/'examples/media',[0])
    def test_svg_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp)/'x.png').write_text('<svg><script>evil()</script></svg>');uri,msg=image_data({'file':'x.png'},tmp,[0]);self.assertIsNone(uri);self.assertTrue(msg)
    def test_missing_image(self):self.assertIsNone(image_data({'file':'missing.png'},ROOT,[0])[0])
    def test_embedding_limit(self):self.assertIsNone(image_data({'file':'image-01.png'},ROOT/'examples/media',[40*1024*1024])[0])
    def test_jpeg_support(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp)/'x.jpg').write_bytes(b'\xff\xd8\xfftest');self.assertTrue(image_data({'file':'x.jpg'},tmp,[0])[0].startswith('data:image/jpeg'))
    def test_embedded_bytes_portable(self):
        uri,_=image_data({'file':'image-01.png'},ROOT/'examples/media',[0]);self.assertEqual(base64.b64decode(uri.split(',')[1]),(ROOT/'examples/media/image-01.png').read_bytes())
    def test_image_order_not_task_order(self):
        d=full_case();d['image_tasks'].reverse();out=render(d);part=out.split('图片卖货路径')[1];self.assertLess(part.index('图1：'),part.index('图2：'));self.assertLess(part.index('图2：'),part.index('图3：'))
    def test_metrics_keep_scope(self):
        d=blurred_case();self.assertIn('对象与统计时间未确定',render(d))
    def test_chat_is_shorter(self):
        d=full_case();self.assertLess(len(chat_summary(d)),len(render(d))/3);self.assertNotIn('正文按什么功能',chat_summary(d))
    def test_user_statement_provenance(self):
        d=title_case();d['evidence'][0]['kind']='user_statement';self.assertIn('用户补充，未独立核验',render(d))
    def test_no_runtime_network_imports(self):
        import ast
        tree=ast.parse((ROOT/'scripts/generate_report.py').read_text(encoding='utf-8'))
        imported=[n.names[0].name if isinstance(n,ast.Import) else n.module for n in ast.walk(tree) if isinstance(n,(ast.Import,ast.ImportFrom))]
        self.assertFalse(set(imported)&{'requests','urllib','socket','http','selenium','playwright'})
    def test_no_default_rewrite_pack(self):
        for build in CASES.values():self.assertNotIn('仿写笔记',render(build()))
    def test_cover_formula_is_separate_from_total_dna(self):
        d=full_case()
        cover=next(s for s in d['sections'] if s['id']=='cover')
        self.assertIn('cover_formula',cover['claim_ids'])
        self.assertNotEqual(d['claims']['cover_formula']['text'],d['claims']['formula']['text'])

if __name__=='__main__':unittest.main()
