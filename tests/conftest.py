"""Fixtures of the tests of the global search."""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtCore import QCoreApplication, QEvent
from PySide6.QtWidgets import QApplication, QWidget


@pytest.fixture(autouse=True)
def isolated_config(tmp_path, monkeypatch):
    """Never read or write the real user settings during tests."""
    monkeypatch.setenv("KUBESCOPE_CONFIG_DIR", str(tmp_path / "config"))
    home = tmp_path / "isolated-home"
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("USERPROFILE", str(home))


@pytest.fixture(autouse=True)
def light_theme():
    from kubescope import theme

    theme.set_theme("light")
    yield
    theme.set_theme("light")


@pytest.fixture(autouse=True)
def delete_the_windows():
    """Delete what a test shows before the application goes away: a window that
    outlives it crashes the run when it ends."""
    if QApplication.instance() is None:
        QApplication([])
    before = set(QApplication.topLevelWidgets())
    yield
    for widget in set(QApplication.topLevelWidgets()) - before:
        widget.close()
        widget.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)


class FakeUi:
    """`ctx.ui`: runs an action at once and remembers what was shown."""

    def __init__(self) -> None:
        self.window = QWidget()
        self.window.resize(800, 600)
        self.messages: list[tuple[str, str, str]] = []

    def themed(self, color, text=False):
        return color

    def show_message(self, icon, title, text):
        self.messages.append((icon, title, text))

    def run_action(self, function, on_success, *arguments, on_error=None, quiet=False):
        try:
            answer = function(*arguments)
        except Exception as error:
            if on_error is None:
                raise
            on_error(str(error))
            return
        on_success(answer)


class FakeCluster:
    def __init__(self) -> None:
        self.hits: list = []
        self.failure: Exception | None = None
        self.asked: list[str] = []

    def search_resources(self, context):
        self.asked.append(context)
        if self.failure is not None:
            raise self.failure
        return self.hits


class FakeCtx:
    """What the app gives the extension, in the hands of the test."""

    id = "kubescope.search"
    permissions = frozenset({"cluster.read", "ui.window"})

    def __init__(self) -> None:
        self.ui: FakeUi | None = FakeUi()
        self.cluster = FakeCluster()
        self.current_context: str | None = "prod"
        self.views: list[tuple[str, str]] = [("pods", "Pods"), ("services", "Services")]
        self.invoked: list[tuple] = []
        self.shortcuts: list[tuple] = []
        self.cleanups: list = []

    def invoke(self, command, /, **arguments):
        self.invoked.append((command, arguments))
        return self.views if command == "views" else None

    def add_shortcut(self, action, label, default, handler, application=False):
        self.shortcuts.append((action, label, default, handler, application))

    def on_unload(self, callback):
        self.cleanups.append(callback)


@pytest.fixture
def ctx():
    return FakeCtx()


@pytest.fixture(autouse=True)
def no_recommended_extensions(monkeypatch):
    """The window of the app downloads what it recommends the first time it runs;
    a test never reaches GitHub."""
    monkeypatch.setattr("kubescope.extensions.defaults.DEFAULTS", ())
