import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'tests'))
from sample_cases import title_case
from scripts.generate_report import generate

if __name__=='__main__':
    data=title_case();data['subject']='</h1><script>globalThis.pwned=1</script>'
    data['claims']['click']['text']='<img src="https://example.invalid/test" onerror="globalThis.pwned=1"> & 中文'
    generate(data,ROOT/'.qa/hostile.html')
