import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from supersub.cli import main
from supersub.transcript import FetchedTranscript, TranscriptError, TranscriptTrack
from supersub.url import watch_url


def _result():
    snippet = SimpleNamespace(text="Hello there", start=0.0, duration=1.5)
    video = SimpleNamespace(
        video_id="dQw4w9WgXcQ",
        title="Demo Video",
        author="Tester",
        url=watch_url("dQw4w9WgXcQ"),
    )
    return FetchedTranscript(
        video=video,
        language="English",
        language_code="en",
        is_generated=False,
        snippets=[snippet],
    )


class CliTests(unittest.TestCase):
    def test_invalid_url_exits_2(self):
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            code = main(["https://example.com/not-youtube"])
        self.assertEqual(code, 2)
        self.assertIn("Not a YouTube URL", stderr.getvalue())

    @patch("supersub.cli.fetch_transcript")
    def test_saves_transcript_by_default(self, fetch):
        fetch.return_value = _result()
        stdout = io.StringIO()
        stderr = io.StringIO()
        import os
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            old_cwd = os.getcwd()
            os.chdir(tmp)
            try:
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    code = main(["dQw4w9WgXcQ"])
            finally:
                os.chdir(old_cwd)

            self.assertEqual(code, 0)
            self.assertEqual(stdout.getvalue().strip(), "")
            self.assertIn("Saved transcript to", stderr.getvalue())
            transcript_path = os.path.join(tmp, "youtube_dQw4w9WgXcQ.txt")
            self.assertTrue(os.path.exists(transcript_path))
            with open(transcript_path, encoding="utf-8") as handle:
                self.assertEqual(handle.read().strip(), "Hello there")
        fetch.assert_called_once()

    @patch("supersub.cli.fetch_transcript")
    def test_timestamps_flag(self, fetch):
        fetch.return_value = _result()
        stdout = io.StringIO()
        stderr = io.StringIO()
        import os
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            old_cwd = os.getcwd()
            os.chdir(tmp)
            try:
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    code = main(["-t", "dQw4w9WgXcQ"])
            finally:
                os.chdir(old_cwd)

            self.assertEqual(code, 0)
            self.assertEqual(stdout.getvalue().strip(), "")
            transcript_path = os.path.join(tmp, "youtube_dQw4w9WgXcQ.txt")
            with open(transcript_path, encoding="utf-8") as handle:
                self.assertIn("[00:00] Hello there", handle.read())
            self.assertIn("Saved transcript to", stderr.getvalue())

    @patch("supersub.cli.fetch_transcript")
    def test_writes_output_file(self, fetch):
        fetch.return_value = _result()
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "out.txt")
            stderr = io.StringIO()
            with redirect_stdout(io.StringIO()), redirect_stderr(stderr):
                code = main(["-o", path, "dQw4w9WgXcQ"])
            self.assertEqual(code, 0)
            with open(path, encoding="utf-8") as handle:
                self.assertEqual(handle.read().strip(), "Hello there")
            self.assertIn("Wrote transcript", stderr.getvalue())

    @patch("supersub.cli.fetch_transcript")
    def test_transcript_error(self, fetch):
        fetch.side_effect = TranscriptError("nope")
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            code = main(["dQw4w9WgXcQ"])
        self.assertEqual(code, 1)
        self.assertIn("nope", stderr.getvalue())

    @patch("supersub.cli.list_tracks")
    def test_list_langs(self, list_tracks):
        list_tracks.return_value = [
            TranscriptTrack(
                language="English",
                language_code="en",
                is_generated=False,
                is_translatable=True,
            )
        ]
        stdout = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(io.StringIO()):
            code = main(["--list-langs", "dQw4w9WgXcQ"])
        self.assertEqual(code, 0)
        self.assertIn("en", stdout.getvalue())
        self.assertIn("English", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
