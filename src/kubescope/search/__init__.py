"""Global search for KubeScope: find a screen, a list or a resource by its
name."""

from kubescope.sdk import Context


def activate(ctx: Context) -> None:
    """What the app calls to run the extension."""
    from kubescope.search import extension

    extension.activate(ctx)
