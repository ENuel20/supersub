# supersub

Fetch the transcript of a YouTube video from the command line.

```bash
supersub https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

Works with watch links, `youtu.be` shorts, `/shorts/`, `/embed/`, `/live/`, and a bare 11-character video ID.

## Install

From this directory:

```bash
pipx install --force .
```

Or, without pipx:

```bash
python3 -m pip install --user .
```

After that, `supersub` is on your PATH.

## Usage

```text
supersub [OPTIONS] URL
```

By default, `supersub` downloads the transcript and saves it in your current directory as:

```text
youtube_<video_id>.txt
```

So this works exactly as requested:

```bash
supersub https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

This creates a file like:

```text
youtube_dQw4w9WgXcQ.txt
```

| Flag | What it does |
| --- | --- |
| `-t`, `--timestamps` | Prefix each line with `[MM:SS]` |
| `-l`, `--lang CODE` | Prefer this language (repeatable). Default: `en` |
| `-o`, `--output FILE` | Save the transcript to a custom file |
| `-o -` | Print the transcript to stdout instead of saving a file |
| `--list-langs` | Show every caption track YouTube has |
| `--json` | JSON output |
| `--srt` | SubRip (`.srt`) output |
| `--translate CODE` | Translate via YouTube into that language |

## Examples

```bash
# default: save transcript to a file in the current folder
supersub https://youtu.be/dQw4w9WgXcQ

# custom output file
supersub -o notes.txt https://youtu.be/dQw4w9WgXcQ

# print to stdout instead of saving
supersub -o - https://youtu.be/dQw4w9WgXcQ

# with timestamps
supersub -t https://youtu.be/dQw4w9WgXcQ

# Spanish if available, otherwise English
supersub -l es -l en https://youtu.be/dQw4w9WgXcQ

# what languages exist?
supersub --list-langs https://youtu.be/dQw4w9WgXcQ
```

Videos with captions disabled, or with no captions in the language you asked for, get a clear error instead of a stack trace.
