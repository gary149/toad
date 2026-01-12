# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Toad is a terminal UI for running AI coding agents using the ACP (Agent Client Protocol). Built with Textual (Python TUI framework), it acts as a JSON-RPC client/server communicating with agent subprocesses via stdio.

## Development Commands

```bash
# Run Toad
uv run toad                    # Launch TUI
uv run toad <path>             # Run on specific project directory
uv run toad -a <agent>         # Launch with specific agent (e.g., "open-hands")
uv run toad serve              # Run as web server on localhost:8000

# Makefile shortcuts
make run                       # Run Toad
make gemini-acp               # Run with Gemini ACP agent
make claude-acp               # Run with Claude Code ACP agent
```

No test suite or linting configuration exists in this project.

## Architecture

### Entry Flow
1. `cli.py` (Click commands) → validates args and creates `ToadApp`
2. `app.py` (`ToadApp`) → manages settings, themes, screens
3. `screens/main.py` (`MainScreen`) → layout with sidebar + conversation
4. `widgets/conversation.py` (`Conversation`) → central hub for agent interaction

### ACP Protocol Layer (`src/toad/acp/`)
- **`agent.py`** - `Agent` class spawns agent subprocess, handles JSON-RPC communication
- **`protocol.py`** - TypedDicts for all ACP messages (tool calls, session updates, capabilities)
- **`api.py`** - JSON-RPC method definitions (`initialize`, `session/new`, `session/prompt`)
- **`messages.py`** - Textual Message classes for UI updates

### Agent Lifecycle
1. `Agent.start()` spawns subprocess with `run_command` from agent TOML
2. `acp_initialize()` → sends protocol version and client capabilities
3. `acp_new_session()` → creates session with working directory
4. Agent sends `session/update` RPC calls with thoughts, tool calls, responses
5. `Agent.post_message()` routes updates to `Conversation` widget handlers

### JSON-RPC Exposed Methods (agent can call these)
- `session/update` - Agent status updates, tool calls, thoughts
- `session/request_permission` - Request user permission for actions
- `fs/read_text_file`, `fs/write_text_file` - File operations
- `terminal/create`, `terminal/output`, `terminal/wait_for_exit` - Terminal management

### Key Widget Patterns
- **BlockProtocol** - Cursor navigation between conversation blocks (alt+up/down)
- **MenuProtocol** - Context menus on blocks (Enter key)
- **ExpandProtocol** - Collapsible content (tool calls, thoughts)
- **MarkdownStream** - Incremental streaming for agent responses

### Agent Discovery
Agents defined in TOML files at `src/toad/data/agents/`. Each specifies:
- `identity` - Unique domain identifier
- `run_command` - OS-specific launch command
- `actions` - Installation commands

### Settings
Stored at `~/.config/toad/toad.json`. Schema in `settings_schema.py`. Categories: `ui.*`, `shell.*`, `agent.*`, `notifications.*`.

## Key Files

| Path | Purpose |
|------|---------|
| `src/toad/app.py` | Main Textual App, settings, themes |
| `src/toad/acp/agent.py` | Agent subprocess + JSON-RPC handling |
| `src/toad/widgets/conversation.py` | Central UI hub, message handlers |
| `src/toad/widgets/terminal.py` | ANSI terminal emulator |
| `src/toad/jsonrpc.py` | JSON-RPC 2.0 server/client implementation |
| `src/toad/toad.tcss` | Textual CSS styling |
