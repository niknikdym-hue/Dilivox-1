import unittest

from profit_engine_runtime.day12_readiness import Day12ReadinessState
from profit_engine_runtime.day12_readiness_cli import readiness_exit_code


class Day12ReadinessCliTests(unittest.TestCase):
    def test_only_candidate_selection_ready_returns_zero(self):
        self.assertEqual(
            0,
            readiness_exit_code(Day12ReadinessState.READY_FOR_LIVE_CANDIDATE_SELECTION),
        )

    def test_every_blocked_state_returns_nonzero(self):
        for state in Day12ReadinessState:
            if state == Day12ReadinessState.READY_FOR_LIVE_CANDIDATE_SELECTION:
                continue
            with self.subTest(state=state):
                self.assertEqual(2, readiness_exit_code(state))


if __name__ == "__main__":
    unittest.main()
