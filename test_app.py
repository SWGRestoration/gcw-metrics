import os
from pathlib import Path
import unittest
from unittest.mock import patch
from streamlit.testing.v1 import AppTest

class AppTests(unittest.TestCase):
    def test_bundled_cycles_and_latest_event(self):
        with patch.dict(os.environ, {'GCW_DATA_DIR': str(Path('data/published').resolve())}):
            at = AppTest.from_file('app.py').run(timeout=60)
            self.assertFalse(at.exception)
            self.assertFalse(at.error)
            for cycle in ['2026-04-12T19:00:03+00:00', '2026-07-19T19:00:03+00:00', '2026-09-06T19:00:03+00:00', 'historical']:
                at.sidebar.selectbox[0].select(cycle).run(timeout=60)
                self.assertFalse(at.exception)
                self.assertFalse(at.error)
                self.assertFalse(any('Shatterpoint Crisis' in h.value for h in at.subheader))
            at.sidebar.radio[0].set_value('Latest Shatterpoint').run(timeout=60)
            self.assertFalse(at.exception)
            self.assertFalse(at.error)
            self.assertTrue(any('Talus' in h.value for h in at.subheader))
            self.assertTrue(any(m.value == '2,576' for m in at.metric))

if __name__ == '__main__':
    unittest.main()
