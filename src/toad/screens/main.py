from textual import on
from textual.app import ComposeResult
from textual.screen import Screen
from textual.reactive import var, reactive
from textual import getters
from textual.widgets import Footer, OptionList
from textual import containers

from toad.widgets.prompt import AutoCompleteOptions
from toad.widgets.throbber import Throbber
from toad.widgets.conversation import Conversation
from toad.widgets.explain import Explain
from toad.widgets.version import Version


class MainScreen(Screen, can_focus=False):
    AUTO_FOCUS = "Conversation Prompt TextArea"

    BINDING_GROUP_TITLE = "Screen"
    busy_count = var(0)
    throbber: getters.query_one[Throbber] = getters.query_one("#throbber")
    conversation = getters.query_one(Conversation)

    column = reactive(False)
    column_width = reactive(100)
    scrollbar = reactive("")

    def compose(self) -> ComposeResult:
        yield Version("Toad v0.1")
        yield AutoCompleteOptions()
        with containers.Center():
            yield Explain()
            yield Conversation()
            yield Footer()

    @on(OptionList.OptionHighlighted)
    def on_option_list_option_highlighted(
        self, event: OptionList.OptionHighlighted
    ) -> None:
        if event.option.id is not None:
            self.conversation.prompt.suggest(event.option.id)

    def action_focus_prompt(self) -> None:
        self.conversation.focus_prompt()

    def watch_column(self, column: bool) -> None:
        self.set_class(column, "-column")
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
        self.conversation.add_class(f"-scrollbar-{scrollbar}")
