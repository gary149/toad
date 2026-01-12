from functools import partial
from pathlib import Path
import random

from textual import on
from textual.app import ComposeResult
from textual import getters
from textual.command import Hit, Hits, Provider, DiscoveryHit
from textual.content import Content
from textual.screen import Screen
from textual.reactive import var, reactive
from textual.widgets import Footer, OptionList
from textual import containers
from textual.widget import Widget


from toad.app import ToadApp
from toad.agent_schema import Agent
from toad.widgets.throbber import Throbber
from toad.widgets.conversation import Conversation


class ModeProvider(Provider):
    async def search(self, query: str) -> Hits:
        """Search for Python files."""
        matcher = self.matcher(query)

        screen = self.screen
        assert isinstance(screen, MainScreen)

        for mode in sorted(
            screen.conversation.modes.values(), key=lambda mode: mode.name
        ):
            command = mode.name
            score = matcher.match(command)
            if score > 0:
                yield Hit(
                    score,
                    matcher.highlight(command),
                    partial(screen.conversation.set_mode, mode.id),
                    help=mode.description,
                )

    async def discover(self) -> Hits:
        screen = self.screen
        assert isinstance(screen, MainScreen)

        for mode in sorted(
            screen.conversation.modes.values(), key=lambda mode: mode.name
        ):
            yield DiscoveryHit(
                mode.name,
                partial(screen.conversation.set_mode, mode.id),
                help=mode.description,
            )


class MainScreen(Screen, can_focus=False):
    AUTO_FOCUS = "Conversation Prompt TextArea"

    COMMANDS = {ModeProvider}

    BINDING_GROUP_TITLE = "Screen"
    busy_count = var(0)
    throbber: getters.query_one[Throbber] = getters.query_one("#throbber")
    conversation = getters.query_one(Conversation)

    column = reactive(False)
    column_width = reactive(100)
    scrollbar = reactive("")
    project_path: var[Path] = var(Path("./").expanduser().absolute())

    app = getters.app(ToadApp)

    def __init__(self, project_path: Path, agent: Agent | None = None) -> None:
        super().__init__()
        self.set_reactive(MainScreen.project_path, project_path)
        self._agent = agent

    def watch_title(self, title: str) -> None:
        self.app.update_terminal_title()

    def get_loading_widget(self) -> Widget:
        throbber = self.app.settings.get("ui.throbber", str)
        if throbber == "quotes":
            from toad.app import QUOTES
            from toad.widgets.future_text import FutureText

            quotes = QUOTES.copy()
            random.shuffle(quotes)
            return FutureText([Content(quote) for quote in quotes])
        return super().get_loading_widget()

    def compose(self) -> ComposeResult:
        with containers.Center():
            yield Conversation(self.project_path, self._agent).data_bind(
                project_path=MainScreen.project_path,
                column=MainScreen.column,
            )
        yield Footer()

    def update_node_styles(self, animate: bool = True) -> None:
        self.conversation.update_node_styles(animate=animate)
        self.query_one(Footer).update_node_styles(animate=animate)

    @on(OptionList.OptionHighlighted)
    def on_option_list_option_highlighted(
        self, event: OptionList.OptionHighlighted
    ) -> None:
        if event.option.id is not None:
            self.conversation.prompt.suggest(event.option.id)

    def action_focus_prompt(self) -> None:
        self.conversation.focus_prompt()

    def watch_column(self, column: bool) -> None:
        self.conversation.styles.max_width = (
            max(10, self.column_width) if column else None
        )

    def watch_column_width(self, column_width: int) -> None:
        self.conversation.styles.max_width = (
            max(10, column_width) if self.column else None
        )

    def watch_scrollbar(self, old_scrollbar: str, scrollbar: str) -> None:
        if old_scrollbar:
            self.conversation.remove_class(f"-scrollbar-{old_scrollbar}")
        if scrollbar:
            self.conversation.add_class(f"-scrollbar-{scrollbar}")
