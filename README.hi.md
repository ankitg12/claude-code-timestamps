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

यह पूरा block Claude के chat में paste करें:

```
Please install claude-code-timestamps from https://github.com/ankitg12/claude-code-timestamps globally (under ~/.claude/, NOT the current project). Steps:

1. Download timestamps.py to ~/.claude/hooks/ (create if needed):
   https://raw.githubusercontent.com/ankitg12/claude-code-timestamps/main/timestamps.py
2. Merge these hooks into ~/.claude/settings.json (preserve existing config):
   - SessionStart       → python "$HOME/.claude/hooks/timestamps.py" session_start   [async: true]
   - UserPromptSubmit   → python "$HOME/.claude/hooks/timestamps.py" prompt
   - PostToolUse        → python "$HOME/.claude/hooks/timestamps.py" tool            [async: true]
   - PostToolUseFailure → python "$HOME/.claude/hooks/timestamps.py" tool_fail
   - SubagentStart      → python "$HOME/.claude/hooks/timestamps.py" subagent_start  [async: true]
   - SubagentStop       → python "$HOME/.claude/hooks/timestamps.py" subagent_stop
   - TaskCreated        → python "$HOME/.claude/hooks/timestamps.py" task_create     [async: true]
   - TaskCompleted      → python "$HOME/.claude/hooks/timestamps.py" task_done
   - PreCompact         → python "$HOME/.claude/hooks/timestamps.py" pre_compact
   - PostCompact        → python "$HOME/.claude/hooks/timestamps.py" post_compact
   - Stop               → python "$HOME/.claude/hooks/timestamps.py" stop
   - SessionEnd         → python "$HOME/.claude/hooks/timestamps.py" session_end     [async: true]
   Each hook type is "command".
3. Validate settings.json is valid JSON, then run /hooks to activate.
```

## मैनुअल इंस्टॉल (विकल्प)

अगर आप Claude की सहायता के बिना install करना पसंद करते हैं:

1. **Hook script download करें:**
   ```bash
   mkdir -p ~/.claude/hooks
   curl -o ~/.claude/hooks/timestamps.py https://raw.githubusercontent.com/ankitg12/claude-code-timestamps/main/timestamps.py
   chmod +x ~/.claude/hooks/timestamps.py  # (Unix/macOS/WSL)
   ```

2. **`~/.claude/settings.json` में hooks add करें:**
   `hooks` section को edit करें और प्रत्येक event type के लिए entries add करें जैसा ऊपर listed है। प्रत्येक entry एक Claude Code event को एक command से map करता है जो `timestamps.py` को event name के साथ invoke करता है। Claude Code के hooks documentation को refer करें `settings.json` syntax के लिए। Restart से पहले JSON को validate करें।

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
