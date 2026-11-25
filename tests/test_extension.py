from kubescope.sdk.models import SearchHit

import kubescope.search as package
from kubescope.search import extension
from kubescope.search.extension import OPEN, OPEN_ALT, Search, activate


def labels(search: Search) -> list[str]:
    return [entry.label for entry in search.entries()]


def test_the_screens_and_the_lists_of_the_menu_are_what_it_goes_to(ctx) -> None:
    search = Search(ctx)  # type: ignore[arg-type]

    assert labels(search) == [
        "Cluster overview",
        "Workloads overview",
        "Settings",
        "Pods",
        "Services",
    ]
    assert ctx.invoked[0][0] == "views"


def test_each_screen_is_opened_as_the_person_would(ctx) -> None:
    search = Search(ctx)  # type: ignore[arg-type]
    ctx.invoked.clear()

    for entry in search.entries():
        entry.run()

    commands = [
        (name, {k: v for k, v in args.items() if k != "report"})
        for name, args in ctx.invoked
    ]
    assert commands[-5:] == [
        ("open_page", {"page": "overview"}),
        ("open_page", {"page": "workloads_overview"}),
        ("open_page", {"page": "settings"}),
        ("open_view", {"view": "pods"}),
        ("open_view", {"view": "services"}),
    ]


def test_the_window_opens_with_the_screens_and_then_the_resources(ctx) -> None:
    ctx.cluster.hits = [SearchHit("Pod", "ns", "api")]
    search = Search(ctx)  # type: ignore[arg-type]

    search.open()
    dialog = search.dialog
    assert dialog is not None
    assert ctx.cluster.asked == ["prod"]
    assert dialog.note.text() == ""  # the resources came
    dialog.input.setText("api")
    ctx.invoked.clear()
    dialog._choose(dialog.results.item(0))

    [(command, arguments)] = ctx.invoked
    assert command == "show_details"
    assert {k: v for k, v in arguments.items() if k != "report"} == {
        "kind": "Pod",
        "namespace": "ns",
        "name": "api",
    }
    search.open()  # a second time reuses the window
    assert search.dialog is dialog


def test_without_a_context_it_does_not_ask_the_cluster(ctx) -> None:
    ctx.current_context = None
    search = Search(ctx)  # type: ignore[arg-type]

    search.open()

    assert ctx.cluster.asked == [] and search.dialog is not None
    assert search.dialog.note.text() == ""


def test_a_cluster_that_cannot_be_read_says_so(ctx) -> None:
    ctx.cluster.failure = RuntimeError("forbidden")
    search = Search(ctx)  # type: ignore[arg-type]

    search.open()

    assert search.dialog is not None and search.dialog.note.text() == "forbidden"


def test_without_a_window_it_does_nothing(ctx) -> None:
    ctx.ui = None
    search = Search(ctx)  # type: ignore[arg-type]

    search.open()
    search.report("lost")

    assert search.dialog is None and ctx.cluster.asked == []


def test_what_a_command_cannot_do_is_told_to_the_person(ctx) -> None:
    search = Search(ctx)  # type: ignore[arg-type]

    search.report("There is no namespace x")

    assert ctx.ui is not None
    assert ctx.ui.messages == [("information", "Search", "There is no namespace x")]


def test_unloading_takes_the_window_away(ctx) -> None:
    search = Search(ctx)  # type: ignore[arg-type]
    search.close()  # none yet: nothing
    search.open()

    search.close()

    assert search.dialog is None


def test_the_extension_adds_the_two_shortcuts_of_the_search(ctx) -> None:
    activate(ctx)  # type: ignore[arg-type]

    assert [(a, d) for a, _label, d, _h, _app in ctx.shortcuts] == [
        (OPEN, "/"),
        (OPEN_ALT, "Ctrl+K"),
    ]
    ctx.shortcuts[0][3]()  # the shortcut opens the window
    assert ctx.cluster.asked == ["prod"]
    [cleanup] = ctx.cleanups
    cleanup()


def test_the_terminal_has_no_window_to_search_in(ctx) -> None:
    ctx.ui = None

    activate(ctx)  # type: ignore[arg-type]

    assert ctx.shortcuts == [] and ctx.cleanups == []


def test_the_app_runs_it_through_its_extension(monkeypatch) -> None:
    given = []
    monkeypatch.setattr(extension, "activate", given.append)

    package.activate("the context")  # type: ignore[arg-type]

    assert given == ["the context"]
