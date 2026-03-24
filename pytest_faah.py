"""pytest-faah — plays a sound when tests fail."""

import os
import platform as _platform
import subprocess
import threading
import urllib.request

_FAAH_DEFAULT_FILENAME = "faah.mp3"
_FAAH_DEFAULT_URL = "https://www.myinstants.com/media/sounds/faaah.mp3"


def _play_audio(path: str) -> None:
    """Try multiple backends in order; fall through on any exception."""
    # 1. pygame
    try:
        import pygame  # type: ignore

        pygame.mixer.init()
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        import time as _time

        while pygame.mixer.music.get_busy():
            _time.sleep(0.05)
        return
    except Exception:
        pass

    # 2. playsound
    try:
        from playsound import playsound  # type: ignore

        playsound(path, block=True)
        return
    except Exception:
        pass

    # 3. System subprocess — no extra deps
    system = _platform.system()
    try:
        if system == "Darwin":
            subprocess.run(["afplay", path], check=True)
        elif system == "Linux":
            for cmd in [
                ["mpg123", "-q", path],
                ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", path],
                ["aplay", path],
            ]:
                try:
                    subprocess.run(cmd, check=True)
                    return
                except Exception:
                    continue
    except Exception:
        pass


def _resolve_sound_file(config) -> str | None:
    """Return the resolved path to the audio file, or None if unavailable."""
    custom = config.getoption("--sound-file", default=None)

    if custom:
        if os.path.isfile(custom):
            return custom
        print(f"[pytest-faah] ⚠ File {custom} not found, skipping.")
        return None

    # Look for faah.mp3 next to the rootdir (project root)
    default_path = os.path.join(str(config.rootdir), _FAAH_DEFAULT_FILENAME)
    if os.path.isfile(default_path):
        return default_path

    # Auto-download
    print("[pytest-faah] Downloading faah.mp3...")
    try:
        req = urllib.request.Request(
            _FAAH_DEFAULT_URL,
            headers={"User-Agent": "Mozilla/5.0 (compatible; pytest-faah/1.0)"},
        )
        with urllib.request.urlopen(req) as resp, open(default_path, "wb") as f:
            f.write(resp.read())
        if os.path.getsize(default_path) < 1024:
            os.remove(default_path)
            raise ValueError("Downloaded file too small — likely an error page.")
        return default_path
    except Exception:
        pass

    print("[pytest-faah] ⚠ Place a faah.mp3 next to your conftest.py")
    return None


class _FaahPlugin:
    def __init__(self, config):
        self._sound_path = _resolve_sound_file(config)

    def pytest_runtest_logreport(self, report):
        if report.when == "call" and report.failed and self._sound_path:
            t = threading.Thread(target=_play_audio, args=(self._sound_path,), daemon=True)
            t.start()


def pytest_addoption(parser):
    group = parser.getgroup("faah", "pytest-faah sound alerts")
    group.addoption("--sound", action="store_true", default=False, help="Play a sound when tests fail.")
    group.addoption("--sound-file", action="store", default=None, metavar="PATH", help="Path to a custom audio file.")


def pytest_configure(config):
    if config.getoption("--sound", default=False):
        plugin = _FaahPlugin(config)
        config.pluginmanager.register(plugin, "_faah_plugin")
