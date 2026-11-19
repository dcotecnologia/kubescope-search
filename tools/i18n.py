"""Keep the JSON languages in step with the texts of the code.

`update` finds every text wrapped for translation (`tr(...)`,
`translate(...)` and the `.ui` file) with `pyside6-lupdate`, then adds
the new ones to every `languages/<code>.json` with an empty translation
(untranslated) and drops the ones the code no longer uses. The
translations already written are kept. The files have the same shape as
the ones of the app, whose languages these join while the extension
runs.
"""

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "src" / "kubescope" / "search"
LANGUAGES = ROOT / "languages"
SOURCES = [*sorted(SOURCE.glob("*.py")), *sorted(SOURCE.glob("*.ui"))]


def extract() -> dict[str, list[str]]:
    """Every context with the texts the code asks to translate."""
    with tempfile.TemporaryDirectory() as directory:
        target = Path(directory) / "texts.ts"
        subprocess.run(
            [
                str(Path(sys.executable).parent / "pyside6-lupdate"),
                "-no-obsolete",
                *map(str, SOURCES),
                "-ts",
                str(target),
            ],
            check=True,
            capture_output=True,
        )
        return {
            context.findtext("name") or "": [
                message.findtext("source") or "" for message in context.iter("message")
            ]
            for context in ElementTree.parse(target).iter("context")
        }


def write(path: Path, name: str, rtl: bool, strings: dict) -> None:
    document = {"name": name, "rtl": rtl, "strings": strings}
    path.parent.mkdir(exist_ok=True)
    path.write_text(
        json.dumps(document, ensure_ascii=False, indent=4, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def update() -> int:
    texts = extract()
    for path in sorted(LANGUAGES.glob("*.json")):
        known = json.loads(path.read_text(encoding="utf-8"))
        old = known.get("strings", {})
        strings = {
            context: {text: old.get(context, {}).get(text, "") for text in sources}
            for context, sources in texts.items()
        }
        write(path, known["name"], known.get("rtl") is True, strings)
        missing = sum(
            1 for texts_ in strings.values() for v in texts_.values() if not v
        )
        print(f"{path.name}: {missing} untranslated")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    return update()


if __name__ == "__main__":
    sys.exit(main())
