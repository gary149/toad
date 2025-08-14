from rich.cells import cell_len

from textual import on, work
from textual.reactive import var
from textual.app import ComposeResult

from textual.binding import Binding
from textual.geometry import Offset
from textual import getters
from textual.message import Message
from textual.widgets import OptionList, TextArea
from textual import containers
from textual.widgets.option_list import Option
from textual import events


from toad.widgets.markdown_textarea import MarkdownTextArea
from toad.widgets.condensed_path import CondensedPath
from toad.messages import UserInputSubmitted
from toad.slash_command import SlashCommand


class AutoCompleteOptions(OptionList):
    pass


class PromptTextArea(MarkdownTextArea):
    BINDING_GROUP_TITLE = "Prompt"
    BINDINGS = [Binding("ctrl+j", "newline", "New line", key_display="⇧+enter")]

    class Submitted(Message):
        def __init__(self, markdown: str) -> None:
            self.markdown = markdown
            super().__init__()

    def on_mount(self) -> None:
        self.highlight_cursor_line = False

    def on_key(self, event: events.Key) -> None:
        if event.key == "enter":
            event.stop()
            event.prevent_default()
            self.post_message(UserInputSubmitted(self.text))
            self.clear()

    def action_newline(self) -> None:
        self.insert("\n")


class Prompt(containers.VerticalGroup):
    auto_complete = getters.query_one(AutoCompleteOptions)
    prompt_text_area = getters.query_one(PromptTextArea)
    auto_complete_options = getters.query_one(AutoCompleteOptions)

    auto_completes: var[list[Option]] = var(list)
    slash_commands: var[list[SlashCommand]] = var(list)

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ):
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)

    def focus(self) -> None:
        self.query(MarkdownTextArea).focus()

    def append(self, text: str) -> None:
        self.query_one(MarkdownTextArea).insert(text)

    def watch_auto_completes(self, auto_complete: list[Option]) -> None:
        self.auto_complete_options.clear_options()
        if auto_complete:
            self.auto_complete_options.add_options(auto_complete)
            self.auto_complete_options.display = True
        else:
            self.auto_complete_options.display = False

    def set_auto_completes(self, auto_completes: list[Option] | None) -> None:
        self.auto_completes = auto_completes.copy() if auto_completes else []

    @on(MarkdownTextArea.CursorMove)
    def on_cursor_move(self, event: MarkdownTextArea.CursorMove) -> None:
        selection = event.selection
        if selection.end != selection.start:
            self.auto_complete.display = False
            return

        self.auto_complete.display = self.prompt_text_area.has_focus

        cursor_offset = (
            self.prompt_text_area.cursor_screen_offset
            - self.prompt_text_area.region.offset
            + Offset(-2, 1)
        )
        self.auto_complete.styles.offset = cursor_offset
        event.stop()

    @on(TextArea.Changed)
    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        cursor_row, cursor_column = self.prompt_text_area.selection.end
        line = self.prompt_text_area.document.get_line(cursor_row)
        post_cursor = line[cursor_column:]
        pre_cursor = line[:cursor_column]
        self.prompt_text_area.suggestion = "Foo"
        self.load_suggestions(pre_cursor, post_cursor)

    @work(exclusive=True)
    async def load_suggestions(self, pre_cursor: str, post_cursor: str) -> None:
        pre_cursor = pre_cursor.casefold()
        post_cursor = post_cursor.casefold()
        suggestions: list[Option] = []

        if not pre_cursor:
            self.set_auto_completes(None)
            return

        command_length = (
            max(
                cell_len(slash_command.command) for slash_command in self.slash_commands
            )
            + 1
        )

        for slash_command in self.slash_commands:
            self.log(repr(slash_command.content.expand_tabs(command_length)))
            if str(slash_command).startswith(pre_cursor):
                suggestions.append(
                    Option(slash_command.content.expand_tabs(command_length))
                )

        self.set_auto_completes(suggestions)

    @on(events.DescendantBlur, "PromptTextArea")
    def on_descendant_blur(self, event: events.DescendantBlur) -> None:
        self.auto_complete.display = False

    @on(events.DescendantFocus, "PromptTextArea")
    def on_descendant_focus(self, event: events.DescendantFocus) -> None:
        self.auto_complete.display = True

    def compose(self) -> ComposeResult:
        yield AutoCompleteOptions()
        yield PromptTextArea()
        with containers.HorizontalGroup():
            yield CondensedPath()
