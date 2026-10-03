"""Public release audit regression checks with synthetic values only."""
import re,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from package_release import PATTERNS,audit,public_files

class PackageTests(unittest.TestCase):
    def test_public_tree_has_no_pattern_findings(self):
        self.assertEqual(audit(public_files()),[])
    def test_private_paths_are_detected(self):
        for value in ['C:'+ '/Users/'+'example/file.txt','/'+'home/'+'example/file.txt']:
            self.assertIsNotNone(re.search(PATTERNS['personal-absolute-path'],value))
    def test_synthetic_token_is_detected(self):
        value='ghp_'+'a'*36
        self.assertIsNotNone(re.search(PATTERNS['github-credential'],value))
    def test_qa_and_private_inputs_are_excluded(self):
        for p in public_files():
            self.assertFalse(set(p.relative_to(ROOT).parts)&{'.qa','private-inputs','outputs','dist'})

if __name__=='__main__':unittest.main()
