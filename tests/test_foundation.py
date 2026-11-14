from datetime import date
import unittest

from src.agents.contracts import SourceReference
from src.services.finance import UnitEconomics


class FoundationTests(unittest.TestCase):
    def test_reference_requires_http_source(self):
        reference = SourceReference("Fonte de teste", "https://example.com/item", date(2026, 11, 14))
        self.assertEqual(reference.observed_on, date(2026, 11, 14))
        for url in ("file:///item", "https://", "https://user:secret@example.com"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                SourceReference("Fonte de teste", url, date(2026, 11, 14))

    def test_contribution_includes_all_variable_costs(self):
        economics = UnitEconomics(2500, 200, 30, 40, 70, 250, 250, 60)
        self.assertEqual(economics.contribution_jpy, 1600)

    def test_loss_can_be_reported(self):
        self.assertEqual(UnitEconomics(100, 120, 0, 0, 0, 0, 0, 0).contribution_jpy, -20)

    def test_negative_cost_is_rejected(self):
        with self.assertRaises(ValueError):
            UnitEconomics(2500, -200, 30, 40, 70, 250, 250, 60)
