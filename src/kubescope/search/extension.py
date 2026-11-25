"""What the app calls to run the global search: its shortcuts and its
window."""

from collections.abc import Callable
from typing import Any

from kubescope.sdk import Context, translate
from kubescope.sdk.models import SearchHit

from kubescope.search.entries import SearchEntry

OPEN = "kubescope.search.open"
OPEN_ALT = "kubescope.search.open_alt"


def tr(text: str) -> str:
    return translate("SearchExtension", text)


class Search:
    """Opens the window of the search and goes where the person chooses."""

    def __init__(self, ctx: Context) -> None:
        self.ctx = ctx
        self.dialog: Any = None

    def report(self, text: str) -> None:
        """Tell the person why the window could not go where they chose."""
        ui = self.ctx.ui
        if ui is not None:
            ui.show_message("information", tr("Search"), text)

    def entries(self) -> list[SearchEntry]:
        """The screens and the lists the search goes to."""
        ctx = self.ctx

        def page(name: str) -> Callable[[], None]:
            return lambda: ctx.invoke("open_page", page=name, report=self.report)

        found = [
            SearchEntry(tr("Cluster overview"), tr("Screen"), page("overview")),
            SearchEntry(
                tr("Workloads overview"), tr("Screen"), page("workloads_overview")
            ),
            SearchEntry(tr("Settings"), tr("Screen"), page("settings")),
        ]
        for view, label in ctx.invoke("views", report=self.report):
            found.append(
                SearchEntry(
                    label,
                    tr("Screen"),
                    lambda view=view: ctx.invoke(
                        "open_view", view=view, report=self.report
                    ),
                )
            )
        return found

    def open(self) -> None:
        """/ or Ctrl+K: find a screen, a list or a resource of any
        namespace."""
        ui = self.ctx.ui
        if ui is None:
            return
        if self.dialog is None:
            self.dialog = ui.components.palette(
                ui.window,
                translate("GlobalSearch", "Search"),
                translate("GlobalSearch", "Search screens, actions and resources..."),
                translate("GlobalSearch", "Loading resources..."),
            )
        dialog = self.dialog
        dialog.open_with(self.entries())
        context = self.ctx.current_context
        if not context:
            dialog.resources_failed("")
            return

        def found(hits: list[SearchHit]) -> None:
            dialog.set_resources(hits, self.show)

        ui.run_action(
            self.ctx.cluster.search_resources,
            found,
            context,
            on_error=dialog.resources_failed,
            quiet=True,
        )

    def show(self, hit: SearchHit) -> None:
        """Open the details of the resource that was chosen."""
        self.ctx.invoke(
            "show_details",
            kind=hit.kind,
            namespace=hit.namespace,
            name=hit.name,
            report=self.report,
        )

    def close(self) -> None:
        """The extension is unloaded: take the window away."""
        if self.dialog is not None:
            self.dialog.close()
            self.dialog.deleteLater()
            self.dialog = None


def activate(ctx: Context) -> None:
    if ctx.ui is None:  # the terminal has no window to search in
        return
    search = Search(ctx)
    ctx.add_shortcut(OPEN, tr("Global search"), "/", search.open)
    ctx.add_shortcut(
        OPEN_ALT, tr("Global search (second shortcut)"), "Ctrl+K", search.open
    )
    ctx.on_unload(search.close)
