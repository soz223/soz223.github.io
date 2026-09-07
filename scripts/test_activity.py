"""Check attribution boundaries and snapshot accounting."""
import json
from pathlib import Path
import unittest
from update_activity import providers

class ActivityTests(unittest.TestCase):
    def test_no_style_or_keyword_inference(self):
        self.assertEqual(providers('Refactor Claude client and add AI support'), [])
        self.assertEqual(providers('Co-authored-by: Claude Smith <claude@example.com>'), [])

    def test_explicit_evidence(self):
        self.assertEqual(providers('Add portfolio\n\nAI-Tool: Codex'), ['Codex'])
        self.assertEqual(providers('Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>'), ['Claude'])
        self.assertEqual(providers('AI-Tool: Codex\nAI-Tool: Codex'), ['Codex'])

    def test_snapshot_consistency(self):
        data=json.loads((Path(__file__).resolve().parents[1]/'data/activity.json').read_text())
        self.assertEqual(len(data['days']),365)
        self.assertEqual(len({c['sha'] for c in data['commits']}),data['total'])
        self.assertEqual(sum(d['total'] for d in data['days']),data['total'])
        self.assertEqual(sum(d['ai'] for d in data['days']),data['ai'])
        self.assertTrue(all(0 <= d['ai'] <= d['total'] for d in data['days']))
        self.assertTrue(all(c['url'].startswith('https://github.com/soz223/') for c in data['commits']))
        self.assertFalse(any('message' in c or 'email' in c for c in data['commits']))

if __name__=='__main__':
    unittest.main()
