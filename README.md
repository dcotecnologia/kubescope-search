# KubeScope Global search

[![CI](https://github.com/dcotecnologia/kubescope-search/actions/workflows/ci.yml/badge.svg)](https://github.com/dcotecnologia/kubescope-search/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fdcotecnologia%2Fkubescope-search%2Fbadges%2Fcoverage.json)](https://github.com/dcotecnologia/kubescope-search/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/dcotecnologia/kubescope-search)](https://github.com/dcotecnologia/kubescope-search/releases)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.15](https://img.shields.io/badge/python-3.15-3776AB.svg?logo=python&logoColor=white)](pyproject.toml)
[![Qt for Python](https://img.shields.io/badge/Qt-PySide6-41CD52.svg?logo=qt&logoColor=white)](https://doc.qt.io/qtforpython-6/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-D7FF64.svg?logo=ruff&logoColor=black)](https://docs.astral.sh/ruff/)
[![KubeScope extension](https://img.shields.io/badge/KubeScope-extension-326CE5.svg?logo=kubernetes&logoColor=white)](https://github.com/dcotecnologia/kubescope)

Global search for [KubeScope](https://github.com/dcotecnologia/kubescope): press `/` or `Ctrl+K` to find a
screen, a list or a resource of **any namespace** by its name, and open it.

It is an **extension** written against the [KubeScope SDK](https://github.com/dcotecnologia/kubescope-sdk)
and nothing else of the app. KubeScope installs it on the first run, and you can uninstall and reinstall it
in **Settings → Extensions**.

## What it does

- **Finds as you type.** Every word you type has to be in the name of what it finds, in any order and
  whatever the case; a name that starts with what you typed comes first, then a name that has it as a word.
- **Screens and lists.** The cluster overview, the workloads overview, the Settings and every list of the
  side menu (Pods, Deployments, Services, ...), found by their names.
- **Resources of any namespace.** The main resources of the cluster of the selected context, with their kind
  and namespace; choosing one opens its details in a tab. A kind you may not list is left out instead of
  failing the whole search.
- **Keyboard first.** The arrows move, `Enter` goes, `Esc` or a click outside closes it. The window follows
  the theme of the app.

## Requirements

KubeScope 1.12 or newer (the extension API `0`) and the SDK 1.1 or newer, which the app brings.

## Install

It comes with KubeScope: the first time it runs, it downloads the latest release. To install or reinstall by
hand open **Settings → Extensions** and either:

- **Install from GitHub...** and type `dcotecnologia/kubescope-search`, or
- **Install from a folder...** and pick the `kubescope-extension.toml` of a clone of this repository.

A dialog shows where it comes from, its permissions and the sha256 of its content before anything of it runs.

## Use

| Key | What happens |
| --- | ------------ |
| `/` | Opens the search (left to the text fields: typing a `/` in one does not open it) |
| `Ctrl+K` | Opens the search, from anywhere |
| **Settings → Shortcuts** | Change both keys |

## Permissions

| Permission | Why |
| ---------- | --- |
| `cluster.read` | List the names of the resources of the cluster to search them |
| `ui.window` | Its window, its two shortcuts and the messages when something cannot be opened |

It reads names only (kind, namespace and name); it never reads the content of a resource, and it changes
nothing.

## Develop

```text
workspace/
├── kubescope/         # the app
├── kubescope-sdk/     # the SDK
└── kubescope-search/  # this project
```

```bash
make setup                           # dependencies and the pre-commit hook
make test FILE=tests/test_dialog.py  # one test file; `make test` runs them all, with the coverage
make lint typecheck
make i18n                            # keep languages/ in step with the texts of the code
```

To see your changes in the app as you make them, tick **Development mode** in **Settings → Extensions** and
install this folder: the app runs it in place and reloads it when a file changes.

A test (`tests/test_independence.py`) keeps its imports to `kubescope.sdk` and itself; another
(`tests/test_in_the_app.py`) runs it in the real window of the app, which is a development dependency only.

### Layout

| Path | What it is |
| ---- | ---------- |
| `kubescope-extension.toml` | The manifest the app reads before installing |
| `src/kubescope/search/extension.py` | `activate(ctx)`: the shortcuts, and what the search goes to |
| `src/kubescope/search/dialog.py` | The window: the input, the results, the ranking and the keys |
| `languages/` | The translations of its texts, one file per language; they join the app's while it runs |
| `tests/` | The tests |

## License

MIT. See [LICENSE](LICENSE).
