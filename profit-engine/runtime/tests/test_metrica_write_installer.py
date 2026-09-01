from __future__ import annotations

from pathlib import Path
import unittest


class MetricaWriteInstallerContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        root = Path(__file__).resolve().parents[3]
        cls.script = (root / "profit-engine" / "scripts" / "install-metrica-write-token-mac.sh").read_text(encoding="utf-8")

    def test_uses_separate_keychain_and_required_scopes(self) -> None:
        self.assertIn('SERVICE="ProfitEngine-MetricaOAuth-Write"', self.script)
        self.assertIn('ACCOUNT="profit-engine"', self.script)
        self.assertIn("metrika:read", self.script)
        self.assertIn("metrika:write", self.script)
        self.assertIn("Рабочее Direct OAuth-приложение НЕ меняйте", self.script)

    def test_verifies_with_current_checkout_runtime(self) -> None:
        self.assertIn('SOURCE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"', self.script)
        self.assertIn('export PYTHONPATH="$SOURCE_ROOT/profit-engine/runtime"', self.script)
        self.assertNotIn('PYTHONPATH="$HOME/.local/share/profit-engine', self.script)

    def test_token_is_local_and_not_printed(self) -> None:
        self.assertIn("with hidden answer", self.script)
        self.assertIn('security add-generic-password -U -s "$SERVICE" -a "$ACCOUNT" -w "$token"', self.script)
        self.assertIn("unset token", self.script)
        self.assertNotIn('echo "$token"', self.script)


if __name__ == "__main__":
    unittest.main()
