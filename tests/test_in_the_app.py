"""The extension in the window of the app, with the real services lent to
it."""

import time

import pytest
from kubescope.extensions import testing
from kubescope.extensions.context import ExtensionContext
from kubescope.sdk.models import SearchHit

from kubescope.search import activate


@pytest.fixture
def window(monkeypatch):
    from kubescope import window as window_module

    application = testing.application()
    # the window downloads the extensions the app recommends on its first run
    monkeypatch.setattr("kubescope.extensions.defaults.DEFAULTS", ())
    monkeypatch.setattr(window_module, "list_contexts", lambda: ([], None))
    monkeypatch.setattr(
        window_module.WorkloadWindow, "refresh_overview", lambda *_a: None
    )
    shown = window_module.WorkloadWindow()
    deadline = time.monotonic() + 10
    while shown._action_workers and time.monotonic() < deadline:
        application.processEvents()
        time.sleep(0.005)
    yield shown
    shown.close()


def test_the_shortcuts_open_a_search_that_goes_to_the_screens_and_the_resources(
    window, monkeypatch
) -> None:
    from kubescope import cluster

    monkeypatch.setattr(
        cluster, "search_resources", lambda context: [SearchHit("Pod", "ns", "api")]
    )
    window.context_combo.blockSignals(True)
    window.context_combo.addItem("prod")
    window.context_combo.setCurrentIndex(0)
    window.context_combo.blockSignals(False)
    context = ExtensionContext(
        "kubescope.search",
        frozenset({"cluster.read", "ui.window"}),
        window.extension_host,
    )

    activate(context)
    window._apply_extension_contributions()
    assert window._shortcuts["kubescope.search.open"].key().toString() == "/"
    assert window._shortcuts["kubescope.search.open_alt"].key().toString() == "Ctrl+K"
    window._shortcuts["kubescope.search.open"].activated.emit()
    from kubescope.extensions.palette import Palette

    [dialog] = window.findChildren(Palette)
    deadline = time.monotonic() + 10
    while dialog.note.text() and time.monotonic() < deadline:
        testing.settle()
        time.sleep(0.005)

    labels = [dialog.results.item(row).text() for row in range(dialog.results.count())]
    assert "Settings    Screen" in labels and any(t.startswith("Pods") for t in labels)
    dialog.input.setText("api")
    shown: list[tuple] = []
    monkeypatch.setattr(window, "_open_resource", lambda *args: shown.append(args))
    dialog._choose(dialog.results.item(0))
    assert shown == [("Pod", "ns", "api")]
    context.close()
