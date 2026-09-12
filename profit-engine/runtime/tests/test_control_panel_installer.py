from __future__ import annotations

from pathlib import Path
import unittest


class ControlPanelInstallerContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_root = Path(__file__).resolve().parents[3]
        self.installer = (
            self.repo_root / "profit-engine" / "scripts" / "install-profit-engine-control-panel.sh"
        ).read_text(encoding="utf-8")
        self.bootstrap = (
            self.repo_root / "profit-engine" / "scripts" / "p0-system-bootstrap-mac.sh"
        ).read_text(encoding="utf-8")

    def test_macos_bundle_declares_exact_executable(self) -> None:
        self.assertIn("<key>CFBundleExecutable</key><string>ProfitEngine</string>", self.installer)
        self.assertIn('cat > "$APP/Contents/MacOS/ProfitEngine"', self.installer)
        self.assertIn('chmod 755 "$APP/Contents/MacOS/ProfitEngine"', self.installer)

    def test_installer_validates_executable_before_open(self) -> None:
        validate_pos = self.installer.index('[[ ! -x "$APP/Contents/MacOS/ProfitEngine" ]]')
        open_pos = self.installer.index('/usr/bin/open "$APP"')
        self.assertLess(validate_pos, open_pos)
        self.assertIn("CFBundleExecutable is not bound to ProfitEngine", self.installer)

    def test_finder_open_failure_does_not_abort_p0_bootstrap(self) -> None:
        self.assertIn('if ! /usr/bin/open "$APP"', self.installer)
        self.assertIn("P0 bootstrap will continue", self.installer)
        self.assertIn("=== P0: METRICA GOALS AUDIT ===", self.bootstrap)

    def test_upgrade_restarts_only_profit_engine_control_panel_module(self) -> None:
        self.assertIn("pgrep -f 'profit_engine_runtime[.]control_panel'", self.installer)
        self.assertIn('kill "$pid"', self.installer)
        self.assertNotIn("pkill python", self.installer)
        restart_pos = self.installer.index("old_panel_pids=")
        open_pos = self.installer.rindex('/usr/bin/open "$APP"')
        self.assertLess(restart_pos, open_pos)

    def test_one_app_reuses_one_backend_and_opens_two_distinct_windows(self) -> None:
        self.assertIn('PROFIT_URL="$BASE_URL/profit"', self.installer)
        self.assertIn('PROJECT_URL="$BASE_URL/project"', self.installer)
        self.assertIn('"$BASE_URL/api/health"', self.installer)
        self.assertIn('backend.lock', self.installer)
        self.assertIn('make new document with properties {URL:targetUrl}', self.installer)
        self.assertIn('ensureWindow("http://127.0.0.1:8765/profit")', self.installer)
        self.assertIn('ensureWindow("http://127.0.0.1:8765/project")', self.installer)
        self.assertIn('profit_engine_runtime.owner_control_v2 --open-two', self.installer)
        self.assertEqual(1, self.installer.count('<key>CFBundleIdentifier</key><string>ru.dilivox.profit-engine</string>'))

    def test_real_app_is_on_desktop_and_legacy_location_is_only_a_symlink(self) -> None:
        self.assertIn('APP="$HOME/Desktop/Profit Engine.app"', self.installer)
        self.assertIn('LEGACY_APP="$HOME/Applications/Profit Engine.app"', self.installer)
        self.assertIn('mkdir -p "$INSTALL_ROOT" "$HOME/Applications" "$HOME/Desktop"', self.installer)
        self.assertIn('rm -rf "$LEGACY_APP"', self.installer)
        self.assertIn('ln -s "$APP" "$LEGACY_APP"', self.installer)
        build_pos = self.installer.index('cat > "$APP/Contents/Info.plist"')
        link_pos = self.installer.index('ln -s "$APP" "$LEGACY_APP"')
        validate_pos = self.installer.index('[[ ! -x "$APP/Contents/MacOS/ProfitEngine" ]]')
        self.assertLess(build_pos, validate_pos)
        self.assertLess(validate_pos, link_pos)


if __name__ == "__main__":
    unittest.main()
