import os
from pathlib import Path
import unittest
from unittest.mock import patch
import pandas as pd
from streamlit.testing.v1 import AppTest
from analytics import grouped_totals, breakdown_bar_figure

ROOT = Path(__file__).parent

class AppTests(unittest.TestCase):
    def start(self):
        with patch.dict(os.environ, {"GCW_DATA_DIR": str(ROOT / "data/published")}):
            return AppTest.from_file(str(ROOT / "app.py")).run(timeout=60)

    def healthy(self, at):
        self.assertFalse(at.exception)
        self.assertFalse(at.error)

    def test_three_periods_and_latest_event(self):
        at = self.start()
        self.healthy(at)
        self.assertEqual(len(at.sidebar.selectbox[0].options), 3)
        self.assertEqual(len(at.get("file_uploader")), 0)
        self.assertEqual([m.value for m in at.metric][:3], ["6,260,446", "3,545,186", "141,871"])
        for cycle, count in [("2026-04-12T19:00:03+00:00", "136,459"), ("historical", "27,367"), ("2026-07-19T19:00:03+00:00", "141,871")]:
            at.sidebar.selectbox[0].select(cycle).run(timeout=60)
            self.healthy(at)
            self.assertEqual(at.metric[2].value, count)
        at.sidebar.radio[0].set_value("Latest Shatterpoint").run(timeout=60)
        self.healthy(at)
        self.assertTrue(any("Talus" in h.value for h in at.subheader))
        self.assertEqual(at.metric[0].value, "2,576")

    def test_filters_reset(self):
        at = self.start()
        at.sidebar.multiselect[0].set_value(["Rebel"]).run(timeout=60)
        self.healthy(at)
        self.assertEqual(at.metric[1].value, "0")
        at.sidebar.button[0].click().run(timeout=60)
        self.healthy(at)
        self.assertEqual(at.metric[1].value, "3,545,186")
        at.sidebar.multiselect[1].set_value(["Talus"]).run(timeout=60)
        self.healthy(at)
        self.assertEqual(at.metric[3].value, "1")

    def test_breakdown_preserves_deductions(self):
        df = pd.DataFrame({"type":["Award", "Deduction"], "faction":["Rebel", "Rebel"], "pointValue":[200, -100]})
        totals = grouped_totals(df, "type", "faction")
        fig = breakdown_bar_figure(totals, "type")
        self.assertEqual(sum(sum(trace.x) for trace in fig.data), 100)
        self.assertTrue(any(value < 0 for trace in fig.data for value in trace.x))

if __name__ == "__main__":
    unittest.main()
