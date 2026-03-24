# pytest-faah

Plays a sound when your pytest tests fail — so you know without looking at the screen.

## How it works

When you run pytest with `--sound`, the plugin hooks into pytest's test reporting. Every time a test fails, it plays an audio file in a background thread so it doesn't block test execution.

**Audio playback backends** (tried in order):
1. `pygame` — if installed
2. `playsound` — if installed
3. System command — no extra dependencies needed:
   - macOS: `afplay`
   - Linux: `mpg123`, `ffplay`, or `aplay`

**Sound file resolution** (in order):
1. Path passed via `--sound-file`
2. `faah.mp3` in your project root (next to `conftest.py`)
3. Auto-downloaded from the internet on first run and saved as `faah.mp3`

## Installation

```bash
pip install -e .
```

## Usage

```bash
# Enable sound alerts
pytest --sound

# Use a custom sound file
pytest --sound --sound-file /path/to/your/sound.mp3
```

## Bring your own sound

Drop any `.mp3` file named `faah.mp3` in your project root and it will be picked up automatically when you run `pytest --sound`.
