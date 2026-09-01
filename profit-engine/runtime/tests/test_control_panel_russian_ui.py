from __future__ import annotations

import unittest

from profit_engine_runtime.control_panel import HTML


class ControlPanelRussianUiTests(unittest.TestCase):
    def test_primary_operator_surface_is_russian_and_actionable(self):
        required = (
            "Пульт прибыли",
            "Фактический K5",
            "Что делать сейчас",
            "Приоритетные действия",
            "Экономика по кампаниям",
            "Три рычага прибыли",
            "Дешевле покупать трафик",
            "Больше дохода с читателя",
            "Масштабировать только доказанное",
            "Ручной Яндекс Поиск",
            "Техническая диагностика",
            "Используем существующие dv_*",
            "ЗАБЛОКИРОВАНЫ",
        )
        for text in required:
            self.assertIn(text, HTML)

    def test_technical_state_codes_are_not_primary_card_copy(self):
        self.assertNotIn('<div class="value">LOCKED</div>', HTML)
        self.assertNotIn('Search only</span>', HTML)
        self.assertNotIn('BUILD FIRST</span>', HTML)
        self.assertNotIn('WRITE LOCKED</span>', HTML)


if __name__ == "__main__":
    unittest.main()
