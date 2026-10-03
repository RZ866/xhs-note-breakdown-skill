"""Rebuild safe original examples without network or an inference service."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'tests'))
from sample_cases import CASES
from scripts.generate_report import generate

if __name__=='__main__':
    for name,build in CASES.items():
        data=build();dest=ROOT/'examples/analysis'/f'{name}.json';dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
        generate(data,ROOT/'examples/reports'/name/'xiaohongshu-analysis-report.html',ROOT/'examples/media')
        print('Generated '+name)
