from importlib.metadata import version

from textual.screen import Screen
from textual import on
from textual.app import ComposeResult
from textual.content import Content
from textual import containers
from textual import widgets

from toad.pill import pill
from toad.widgets.mandelbrot import Mandelbrot


QR = """\
█▀▀▀▀▀█ ▄█ ▄▄█▄▄█ █▀▀▀▀▀█
█ ███ █ ▄█▀█▄▄█▄  █ ███ █
█ ▀▀▀ █ ▄ █ ▀▀▄▄▀ █ ▀▀▀ █
▀▀▀▀▀▀▀ ▀ ▀ ▀ █ █ ▀▀▀▀▀▀▀
█▀██▀ ▀█▀█▀▄▄█   ▀ █ ▀ █ 
 █ ▀▄▄▀▄▄█▄▄█▀██▄▄▄▄ ▀ ▀█
▄▀▄▀▀▄▀ █▀▄▄▄▀▄ ▄▀▀█▀▄▀█▀
█ ▄ ▀▀▀█▀ █ ▀ █▀ ▀ ██▀ ▀█
▀  ▀▀ ▀▀▄▀▄▄▀▀▄▀█▀▀▀█▄▀  
█▀▀▀▀▀█ ▀▄█▄▀▀  █ ▀ █▄▀▀█
█ ███ █ ██▄▄▀▀█▀▀██▀█▄██▄
█ ▀▀▀ █ ██▄▄ ▀  ▄▀ ▄▄█▀ █
▀▀▀▀▀▀▀ ▀▀▀  ▀   ▀▀▀▀▀▀▀▀"""


class StoreScreen(Screen):
    CSS_PATH = "store.tcss"

    def compose(self) -> ComposeResult:
        with containers.VerticalGroup(id="title-container"):
            with containers.Grid(id="title-grid"):
                yield Mandelbrot()
                yield widgets.Label(self.get_info(), id="info")
                # yield widgets.Label(QR, id="qr")

    def get_info(self) -> Content:
        content = Content.assemble(
            Content.from_markup("Toad"),
            pill(f"v{version('toad')}", "$primary-muted", "$text-primary"),
            ("\nThe universal interface for AI in your terminal", "$text-success"),
            (
                "\nSoftware lovingly crafted by hand (with a dash of AI) in Edinburgh, Scotland",
                "dim",
            ),
            "\n",
            (
                Content.from_markup(
                    "\nConsider sponsoring [@click=screen.url('https://github.com/sponsors/willmcgugan')]@willmcgugan[/] to support development of Toad!"
                )
            ),
            "\n\n",
            (
                Content.from_markup(
                    "[dim]Code: [@click=screen.url('https://github.com/Textualize/toad')]Repository[/] "
                    "Bugs: [@click=screen.url('https://github.com/Textualize/toad/discussions')]Discussions[/]"
                )
            ),
        )

        return content

    def action_url(self, url: str) -> None:
        import webbrowser

        webbrowser.open(url)


if __name__ == "__main__":
    from textual.app import App

    class StoreApp(App):
        CSS_PATH = "store.tcss"
        DEFAULT_THEME = "dracula"

        def on_ready(self) -> None:
            self.theme = "dracula"

        def get_default_screen(self) -> Screen:
            return StoreScreen()

    StoreApp().run()
