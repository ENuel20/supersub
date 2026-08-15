"""Command-line interface for supersub."""

from __future__ import annotations

import argparse
import sys
from typing import Optional, Sequence, TextIO

from supersub import __version__
from supersub.format import format_json, format_plain, format_srt, format_timestamps
from supersub.transcript import (
    FetchedTranscript,
    TranscriptError,
    fetch_transcript,
    list_tracks,
)
from supersub.url import InvalidYouTubeURL, extract_video_id


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="supersub",
        description="Fetch the transcript of a YouTube video.",
        epilog="Example:  supersub https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    )
    parser.add_argument(
        "url",
        help="YouTube URL or 11-character video ID",
    )
    parser.add_argument(
        "-l",
        "--lang",
        dest="languages",
        action="append",
        metavar="CODE",
        help="Preferred language code (repeatable). Default: en",
    )
    parser.add_argument(
        "-t",
        "--timestamps",
        action="store_true",
        help="Prefix each line with a [MM:SS] timestamp",
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="FILE",
        help="Write the transcript to FILE instead of stdout",
    )
    parser.add_argument(
        "--list-langs",
        action="store_true",
        help="List available transcript languages and exit",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the transcript as JSON",
    )
    parser.add_argument(
        "--srt",
        action="store_true",
        help="Print the transcript as SubRip (.srt)",
    )
    parser.add_argument(
        "--translate",
        metavar="CODE",
        help="Translate the transcript into this language code",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"supersub {__version__}",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        video_id = extract_video_id(args.url)
    except InvalidYouTubeURL as exc:
        print(exc, file=sys.stderr)
        return 2

    if args.list_langs:
        return _print_languages(video_id)

    try:
        result = fetch_transcript(
            video_id,
            languages=args.languages,
            translate_to=args.translate,
        )
    except TranscriptError as exc:
        print(exc, file=sys.stderr)
        return 1

    body = _render(result, timestamps=args.timestamps, as_json=args.json, as_srt=args.srt)
    _print_status(result, sys.stderr)

    output_path = args.output
    if not output_path:
        output_path = _default_output_path(video_id, as_json=args.json, as_srt=args.srt)

    if output_path == "-":
        print(body)
        return 0

    try:
        with open(output_path, "w", encoding="utf-8") as handle:
            handle.write(body)
            if body and not body.endswith("\n"):
                handle.write("\n")
    except OSError as exc:
        print(f"Could not write {output_path}: {exc}", file=sys.stderr)
        return 1

    label = "Saved transcript to" if not args.output else "Wrote transcript to"
    print(f"{label} {output_path}", file=sys.stderr)
    return 0


def _default_output_path(video_id: str, *, as_json: bool, as_srt: bool) -> str:
    if as_srt:
        suffix = ".srt"
    elif as_json:
        suffix = ".json"
    else:
        suffix = ".txt"
    return f"youtube_{video_id}{suffix}"


def _render(
    result: FetchedTranscript,
    *,
    timestamps: bool,
    as_json: bool,
    as_srt: bool,
) -> str:
    if as_json:
        return format_json(
            result.snippets,
            video_id=result.video.video_id,
            title=result.video.title,
            author=result.video.author,
            url=result.video.url,
            language=result.language,
            language_code=result.language_code,
            generated=result.is_generated,
        )
    if as_srt:
        return format_srt(result.snippets)
    if timestamps:
        return format_timestamps(result.snippets)
    return format_plain(result.snippets)


def _print_status(result: FetchedTranscript, stream: TextIO) -> None:
    video = result.video
    kind = "auto-generated" if result.is_generated else "manual"
    title = video.title or video.video_id
    extra = f" — {video.author}" if video.author else ""
    print(f"{title}{extra}", file=stream)
    print(
        f"{video.url}  [{result.language_code} · {kind}]",
        file=stream,
    )
    print(file=stream)


def _print_languages(video_id: str) -> int:
    try:
        tracks = list_tracks(video_id)
    except TranscriptError as exc:
        print(exc, file=sys.stderr)
        return 1

    if not tracks:
        print("No transcripts available for this video.", file=sys.stderr)
        return 1

    print(f"Available transcripts for {video_id}:\n")
    for track in tracks:
        kind = "auto-generated" if track.is_generated else "manual"
        translatable = "translatable" if track.is_translatable else "not translatable"
        print(f"  {track.language_code:<8} {track.language:<24} ({kind}, {translatable})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
