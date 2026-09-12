from __future__ import annotations

import unittest

from profit_engine_runtime import control_panel
from profit_engine_runtime.owner_control_v2 import Handler, _profit_html
from profit_engine_runtime.project_control_ui import render_project_html


class OwnerControlV2Tests(unittest.TestCase):
    def test_one_backend_exposes_two_distinct_owner_windows(self) -> None:
        profit = _profit_html("test-token")
        project = render_project_html("test-token")
        self.assertIn("Пульт прибыли", profit)
        self.assertNotIn("Критический путь", profit)
        self.assertNotIn("GitHub", profit)
        self.assertIn("DILIVOX — Управление проектом", project)
        self.assertIn("Критический путь", project)
        self.assertIn("Весь проект", project)
        self.assertIn('href="/profit"', project)
        self.assertEqual(Handler.server_version, "ProfitEngineOwnerControl/3.0")

    def test_project_window_has_all_required_views_and_controls(self) -> None:
        html = render_project_html("test-token")
        for text in (
            "Adaptive Funnel",
            "Контент",
            "Провайдеры и compliance",
            "Owner Gates",
            "Разработка",
            "История",
            "Запустить выбранную",
            "Запустить следующую",
            "Запустить пакет 1–5",
            "Пауза",
            "Продолжить",
            "Стоп",
            "AUTO / QUALITY-FIRST",
        ):
            self.assertIn(text, html)
        for endpoint in (
            "/api/project/refresh",
            "/api/development/start",
            "/api/development/package/start",
            "/api/development/pause",
            "/api/development/resume",
            "/api/development/stop",
        ):
            self.assertIn(endpoint, html)

    def test_security_token_is_per_render_and_not_browser_storage(self) -> None:
        html = render_project_html("opaque-token")
        self.assertIn('content="opaque-token"', html)
        self.assertNotIn("localStorage", html)
        self.assertNotIn("sessionStorage", html)
        self.assertIn("X-Profit-Engine-CSRF", html)
        self.assertNotIn("OPENAI_API_KEY", html)
        self.assertNotIn("GITHUB_TOKEN", html)
        self.assertNotIn("ghp_", html)

    def test_profit_regression_surface_is_preserved(self) -> None:
        html = _profit_html("test-token")
        for marker in (
            "Фактический K5",
            "Расход Директа",
            "Доход РСЯ",
            "Экономика по кампаниям",
            "Ручной Яндекс Поиск",
            "WRITER LOCKED",
        ):
            self.assertIn(marker, html)
        self.assertIn(control_panel.HTML.split("<title>")[1].split("</title>")[0], html)

    def test_project_ui_has_no_provider_or_deploy_controls(self) -> None:
        html = render_project_html("test-token")
        for forbidden in (
            "/api/write",
            "/api/direct",
            "/api/yan",
            "/api/metrica/write",
            "/api/deploy",
            "/api/merge",
            "KeywordBids.set",
        ):
            self.assertNotIn(forbidden, html)
        self.assertIn("provider writes", html.lower())
        self.assertIn("no automatic merge", html.lower())


if __name__ == "__main__":
    unittest.main()
