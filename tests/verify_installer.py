"""Exercise the actual host installer with a local archive replacing HTTP only.
This verifies package/root-path compatibility, not a live GitHub download.
"""
import argparse,importlib.util,sys,tempfile,zipfile
from pathlib import Path

def run(installer_path,package):
    installer_path=Path(installer_path);sys.path.insert(0,str(installer_path.parent))
    spec=importlib.util.spec_from_file_location('official_skill_installer',installer_path)
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    requests=[]
    def local_archive(url):requests.append(url);return Path(package).read_bytes()
    module._request=local_archive
    name='xiaohongshu-viral-commerce-note-analyzer'
    with tempfile.TemporaryDirectory(prefix='skill-install-contract-') as tmp:
        args=['--url','https://github.com/test-owner/'+name,'--path','.','--name',name,'--dest',tmp,'--method','download']
        code=module.main(args)
        assert code==0 and (Path(tmp)/name/'SKILL.md').is_file()
        assert (Path(tmp)/name/'scripts/generate_report.py').is_file()
        assert (Path(tmp)/name/'assets/report.html').is_file()
        assert not (Path(tmp)/name/'.qa').exists()
        assert requests==['https://codeload.github.com/test-owner/'+name+'/zip/main']
        assert module.main(args)==1,'existing installation must not silently overwrite'
    print('PASS actual installer local archive/root path/copy/duplicate protection; live GitHub download NOT RUN')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--installer',required=True);p.add_argument('--package',required=True);a=p.parse_args();run(a.installer,a.package)
