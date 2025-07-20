from toad.widgets.menu import Menu


CONVERSATION_MENUS: dict[str, list[Menu.Item]] = {
    "fence": [
        Menu.Item("explain", "explain", "e"),
        Menu.Item("copy_to_clipboard", "Copy to clipboard", "c"),
        Menu.Item("copy_to_prompt", "Copy to prompt", "p"),
    ]
}
