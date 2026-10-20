import unittest
from unittest.mock import MagicMock, patch

from components import batch_progress, export_panel


class TestReportComponents(unittest.TestCase):
    def test_batch_summary_distinguishes_missing_and_detected_checks(self):
        scans = [
            {
                "url": "https://missing.example",
                "score": 20,
                "cookie_consent": "Not Found",
                "privacy_policy": "Not Found",
                "contact_info": "Not Found",
            },
            {
                "url": "https://detected.example",
                "score": 100,
                "cookie_consent": "Found - consent banner",
                "privacy_policy": "Found - privacy link",
                "contact_info": "Found - email",
            },
        ]

        with patch.object(batch_progress, "st") as ui:
            ui.columns.side_effect = lambda spec, **kwargs: [
                MagicMock() for _ in range(spec if isinstance(spec, int) else len(spec))
            ]
            batch_progress.render_batch_summary(scans, [])

            table = ui.dataframe.call_args_list[0].args[0].set_index("Website")
            for column in ("Cookie Consent", "Privacy Policy"):
                self.assertEqual(table.loc["https://missing.example", column], "❌")
                self.assertEqual(table.loc["https://detected.example", column], "✅")

            successes = [call.args[0] for call in ui.success.call_args_list]
            self.assertFalse(any("Not Found" in message for message in successes))
            for status in (
                "Found - consent banner",
                "Found - privacy link",
                "Found - email",
            ):
                self.assertIn(f"✅ {status}", successes)
            self.assertEqual(
                [call.args[0] for call in ui.error.call_args_list],
                ["❌ Not Found", "❌ Not Found"],
            )
            ui.warning.assert_called_once_with("⚠️ Not Found")

    def test_copy_summary_uses_current_score_with_legacy_fallback(self):
        for mode in ("batch", "history"):
            for scan, expected in [
                ({"score": 85}, "85.0%"),
                ({"overall_score": 75}, "75.0%"),
                ({"score": 0, "overall_score": 95}, "0.0%"),
            ]:
                with self.subTest(mode=mode, scan=scan):
                    with patch.object(export_panel, "st") as ui:
                        ui.button.return_value = True
                        export_panel._render_batch_export(
                            [{"url": "https://example.com", **scan}],
                            MagicMock(), MagicMock(), MagicMock(),
                            mode, "test_export",
                        )

                        ui.code.assert_called_once()
                        self.assertIn(f"Score: {expected}", ui.code.call_args.args[0])
                        ui.error.assert_not_called()


if __name__ == "__main__":
    unittest.main()
