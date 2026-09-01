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


if __name__ == "__main__":
    unittest.main()
