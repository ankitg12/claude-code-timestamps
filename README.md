# Claude Code Timestamps Hook

Inject wall-clock timestamps at every critical moment in your Claude Code session.

English | [हिंदी](./README.hi.md)

## What It Does

`timestamps.py` is a Python hook script that injects precise timestamps for 12 lifecycle events in Claude Code — session start/end, user prompts, tool completions, subagent activity, task creation/completion, and compaction operations. Timestamps are formatted as `[HH:MM:SS]` and include elapsed time where relevant. Run multiple Claude Code windows concurrently without interference — session state is keyed by `session_id`.

No external dependencies. Works on macOS, Linux, and Windows. Runs via Claude Code's native hook system.

## Example Output

```
UserPromptSubmit says: [09:21:17 AM] — user message received
PostToolUse says:      [09:21:19 AM] read completed
Stop says:             [09:21:44 AM] — response complete (27.3s) | session 4m12s
SessionEnd says:       [09:22:01 AM] — session ending (logout) — Claude 4m12s | wall 47m33s
```

## Requirements

- Python 3.6+ available on PATH
- Claude Code (latest version recommended)

## Install

### Option A — Plugin (one command, recommended)

```
/plugin add --from https://github.com/ankitg12/claude-code-timestamps
```

Installs the script and wires all 12 hooks automatically. No settings.json editing needed. Activate with `/plugins` to confirm.

> **Requires Python 3 on PATH as `python`.** macOS/Linux users: if your Python is `python3`, clone the repo and edit `.claude-plugin/plugin.json` to use `python3` instead.

### Option B — Let Claude do it

Paste this into Claude Code chat:

```
Please install claude-code-timestamps globally (under ~/.claude/):
1. Download to ~/.claude/hooks/timestamps.py (create dir if needed):
   https://raw.githubusercontent.com/ankitg12/claude-code-timestamps/main/timestamps.py
2. Merge the hooks below into ~/.claude/settings.json preserving all existing config.
3. Validate settings.json is valid JSON, then run /hooks to activate.
```

### Option C — Manual

**1. Download the script:**

```bash
mkdir -p ~/.claude/hooks
curl -o ~/.claude/hooks/timestamps.py \
  https://raw.githubusercontent.com/ankitg12/claude-code-timestamps/main/timestamps.py
```

**2. Add to `~/.claude/settings.json`:**

Merge the `hooks` block below into your existing `~/.claude/settings.json`.
If you have no existing hooks, paste it as a top-level key alongside `"env"`, `"model"`, etc.

> **Windows:** replace `~/.claude/hooks/timestamps.py` with the full path,
> e.g. `C:/Users/YourName/.claude/hooks/timestamps.py`

```json
{
  "hooks": {
    "SessionStart":       [{"matcher":"","hooks":[{"type":"command","command":"python \"~/.claude/hooks/timestamps.py\" session_start","async":true}]}],
    "UserPromptSubmit":   [{"matcher":"","hooks":[{"type":"command","command":"python \"~/.claude/hooks/timestamps.py\" prompt"}]}],
    "PostToolUse":        [{"matcher":"","hooks":[{"type":"command","command":"python \"~/.claude/hooks/timestamps.py\" tool","async":true}]}],
    "PostToolUseFailure": [{"matcher":"","hooks":[{"type":"command","command":"python \"~/.claude/hooks/timestamps.py\" tool_fail"}]}],
    "SubagentStart":      [{"matcher":"","hooks":[{"type":"command","command":"python \"~/.claude/hooks/timestamps.py\" subagent_start","async":true}]}],
    "SubagentStop":       [{"matcher":"","hooks":[{"type":"command","command":"python \"~/.claude/hooks/timestamps.py\" subagent_stop"}]}],
    "TaskCreated":        [{"matcher":"","hooks":[{"type":"command","command":"python \"~/.claude/hooks/timestamps.py\" task_create","async":true}]}],
    "TaskCompleted":      [{"matcher":"","hooks":[{"type":"command","command":"python \"~/.claude/hooks/timestamps.py\" task_done"}]}],
    "PreCompact":         [{"matcher":"","hooks":[{"type":"command","command":"python \"~/.claude/hooks/timestamps.py\" pre_compact"}]}],
    "PostCompact":        [{"matcher":"","hooks":[{"type":"command","command":"python \"~/.claude/hooks/timestamps.py\" post_compact"}]}],
    "Stop":               [{"matcher":"","hooks":[{"type":"command","command":"python \"~/.claude/hooks/timestamps.py\" stop"}]}],
    "SessionEnd":         [{"matcher":"","hooks":[{"type":"command","command":"python \"~/.claude/hooks/timestamps.py\" session_end","async":true}]}]
  }
}
```

**3. Reload:** run `/hooks` in Claude Code (no restart needed — settings are file-watched).

## Events Covered

| Claude Code Event | When It Fires | Output Format |
|---|---|---|
| SessionStart | Session begins | `[HH:MM:SS AM/PM] — session started ({reason})` |
| UserPromptSubmit | User sends a message | `[HH:MM:SS AM/PM] — user message received` |
| PostToolUse | Tool completes successfully | `[HH:MM:SS AM/PM] {tool_name} completed` |
| PostToolUseFailure | Tool execution fails | `[HH:MM:SS AM/PM] ✗ {tool_name} failed` |
| SubagentStart | Subagent spawned | `[HH:MM:SS AM/PM] ↗ {agent_type} subagent started` |
| SubagentStop | Subagent finishes | `[HH:MM:SS AM/PM] ↘ {agent_type} subagent done ({elapsed})` |
| TaskCreated | Task created | `[HH:MM:SS AM/PM] ◎ task created` |
| TaskCompleted | Task finishes | `[HH:MM:SS AM/PM] ✓ task completed` |
| PreCompact | Compaction begins | `[HH:MM:SS AM/PM] — compaction starting` |
| PostCompact | Compaction finishes | `[HH:MM:SS AM/PM] — compaction done ({elapsed})` |
| Stop | Response complete | `[HH:MM:SS AM/PM] — response complete ({turn_elapsed}) \| session {session_elapsed}` |
| SessionEnd | Session closes | `[HH:MM:SS AM/PM] — session ending ({reason}) — Claude {compute_time} \| wall {wall_time}` |

## Uninstall

Paste this into Claude:

```
Please uninstall claude-code-timestamps:

1. Remove all entries for SessionStart, UserPromptSubmit, PostToolUse, PostToolUseFailure, SubagentStart, SubagentStop, TaskCreated, TaskCompleted, PreCompact, PostCompact, Stop, and SessionEnd from ~/.claude/settings.json.
2. Delete ~/.claude/hooks/timestamps.py.
3. Run /hooks to deactivate.
```

## License

MIT — See LICENSE file in the repository.

---

**Related projects:**
- [claude-code-session-timer-hook](https://github.com/jeecgboot/claude-code-session-timer-hook) — covers 4 events with session-level timing only.
