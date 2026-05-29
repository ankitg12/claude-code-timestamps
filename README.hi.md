# Claude Code Timestamps Hook

अपने Claude Code सेशन के हर महत्वपूर्ण क्षण पर wall-clock timestamps inject करें।

[English](./README.md) | हिंदी

## यह क्या करता है

`timestamps.py` एक Python hook script है जो Claude Code में 12 lifecycle events के लिए precise timestamps inject करता है — session start/end, user prompts, tool completions, subagent activity, task creation/completion, और compaction operations। Timestamps को `[HH:MM:SS]` के रूप में formatted किया जाता है और relevant जगहों पर elapsed time शामिल होता है। Multiple Claude Code windows को simultaneously चलाएं बिना किसी interference के — session state को `session_id` से key किया जाता है।

कोई भी external dependencies नहीं। macOS, Linux, और Windows पर काम करता है। Claude Code के native hook system के through चलता है।

## उदाहरण आउटपुट

```
UserPromptSubmit says: [09:21:17 AM] — user message received
PostToolUse says:      [09:21:19 AM] read completed
Stop says:             [09:21:44 AM] — response complete (27.3s) | session 4m12s
SessionEnd says:       [09:22:01 AM] — session ending (logout) — Claude 4m12s | wall 47m33s
```

## आवश्यकताएं

- Python 3.6+ PATH पर उपलब्ध हो
- Claude Code (latest version recommended)

## इंस्टॉल करें

### विकल्प A — Claude से करवाएं (recommended)

यह पूरा block Claude Code chat में paste करें:

```
Please install claude-code-timestamps globally (under ~/.claude/):
1. Download to ~/.claude/hooks/timestamps.py (create dir if needed):
   https://raw.githubusercontent.com/ankitg12/claude-code-timestamps/main/timestamps.py
2. Merge the hooks from https://github.com/ankitg12/claude-code-timestamps into ~/.claude/settings.json
   preserving all existing config. The hooks block is in the README.
3. Validate settings.json is valid JSON, then run /hooks to activate.
```

### विकल्प B — Manual

**1. Script download करें:**

```bash
mkdir -p ~/.claude/hooks
curl -o ~/.claude/hooks/timestamps.py \
  https://raw.githubusercontent.com/ankitg12/claude-code-timestamps/main/timestamps.py
```

**2. `~/.claude/settings.json` में add करें:**

नीचे दिया गया `hooks` block अपने existing `~/.claude/settings.json` में merge करें।
अगर आपके पास कोई existing hooks नहीं हैं, तो इसे `"env"`, `"model"` आदि के साथ top-level key के रूप में paste करें।

> **Windows:** `~/.claude/hooks/timestamps.py` को full path से replace करें,
> जैसे `C:/Users/YourName/.claude/hooks/timestamps.py`

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

**3. Reload:** Claude Code में `/hooks` run करें (restart की जरूरत नहीं — settings file-watched हैं)।

## कवर की गई घटनाएं

| Claude Code Event | कब फायर होता है | आउटपुट फॉर्मेट |
|---|---|---|
| SessionStart | Session शुरू होता है | `[HH:MM:SS AM/PM] — session started ({reason})` |
| UserPromptSubmit | User एक message भेजता है | `[HH:MM:SS AM/PM] — user message received` |
| PostToolUse | Tool successfully complete होता है | `[HH:MM:SS AM/PM] {tool_name} completed` |
| PostToolUseFailure | Tool execution fail होता है | `[HH:MM:SS AM/PM] ✗ {tool_name} failed` |
| SubagentStart | Subagent spawn होता है | `[HH:MM:SS AM/PM] ↗ {agent_type} subagent started` |
| SubagentStop | Subagent finish होता है | `[HH:MM:SS AM/PM] ↘ {agent_type} subagent done ({elapsed})` |
| TaskCreated | Task create होता है | `[HH:MM:SS AM/PM] ◎ task created` |
| TaskCompleted | Task finish होता है | `[HH:MM:SS AM/PM] ✓ task completed` |
| PreCompact | Compaction शुरू होता है | `[HH:MM:SS AM/PM] — compaction starting` |
| PostCompact | Compaction finish होता है | `[HH:MM:SS AM/PM] — compaction done ({elapsed})` |
| Stop | Response complete होता है | `[HH:MM:SS AM/PM] — response complete ({turn_elapsed}) \| session {session_elapsed}` |
| SessionEnd | Session close होता है | `[HH:MM:SS AM/PM] — session ending ({reason}) — Claude {compute_time} \| wall {wall_time}` |

## अनइंस्टॉल करें

यह Claude में paste करें:

```
Please uninstall claude-code-timestamps:

1. Remove all entries for SessionStart, UserPromptSubmit, PostToolUse, PostToolUseFailure, SubagentStart, SubagentStop, TaskCreated, TaskCompleted, PreCompact, PostCompact, Stop, and SessionEnd from ~/.claude/settings.json.
2. Delete ~/.claude/hooks/timestamps.py.
3. Run /hooks to deactivate.
```

## लाइसेंस

MIT — Repository में LICENSE file देखें।

---

**संबंधित प्रोजेक्ट:**
- [claude-code-session-timer-hook](https://github.com/jeecgboot/claude-code-session-timer-hook) — केवल 4 events को session-level timing के साथ कवर करता है।
