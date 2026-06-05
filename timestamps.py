#!/usr/bin/env python
"""
Timestamp injection hook for Claude Code.

Single script, one mode per CC lifecycle event. Absorbs all session_timer.py
functionality: per-session turn/session timing keyed by session_id.

State directory: ~/.claude/session_timing/<session_id>.{turn_start,session_start,total}

Event → mode argument → async?
  SessionStart       session_start   async  (init timing state; fire-and-forget)
  UserPromptSubmit   prompt          sync   (write turn_start; elapsed available at Stop)
  PostToolUse        tool            async  (additionalContext in next model call)
  PostToolUseFailure tool_fail       sync   (appears before next model call)
  SubagentStart      subagent_start  async  (fire-and-forget)
  SubagentStop       subagent_stop   sync   (elapsed since subagent_start)
  TaskCreated        task_create     async  (fire-and-forget)
  TaskCompleted      task_done       sync   (appears in context)
  PreCompact         pre_compact     sync   (message enters context before compaction)
  PostCompact        post_compact    sync   (elapsed since pre_compact)
  Stop               stop            sync   (turn elapsed + session total)
  SessionEnd         session_end     async  (Claude compute vs wall time + cleanup)

Usage in settings.json:
  SessionStart:       python "...timestamps.py" session_start   [async]
  UserPromptSubmit:   python "...timestamps.py" prompt
  PostToolUse:        python "...timestamps.py" tool            [async]
  PostToolUseFailure: python "...timestamps.py" tool_fail
  SubagentStart:      python "...timestamps.py" subagent_start  [async]
  SubagentStop:       python "...timestamps.py" subagent_stop
  TaskCreated:        python "...timestamps.py" task_create     [async]
  TaskCompleted:      python "...timestamps.py" task_done
  PreCompact:         python "...timestamps.py" pre_compact
  PostCompact:        python "...timestamps.py" post_compact
  Stop:               python "...timestamps.py" stop
  SessionEnd:         python "...timestamps.py" session_end     [async]
"""
import json
import sys
import time
from datetime import datetime
from pathlib import Path

_DIR        = Path.home() / ".claude"
_TIMING_DIR = _DIR / "session_timing"   # per-session: <sid>.{turn_start,session_start,total}
_SUBAGENT_START_FILE = _DIR / "timestamps_subagent_start.txt"
_COMPACT_START_FILE  = _DIR / "timestamps_compact_start.txt"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def now() -> str:
    return datetime.now().strftime("%I:%M:%S %p")


def fmt_secs(secs: float) -> str:
    """Compact human-readable duration: '250ms', '3.14s', '2m5s', '1h3m5s'."""
    if secs < 1:
        return f"{secs * 1000:.0f}ms"
    if secs < 60:
        return f"{secs:.2f}s"
    mins, s = divmod(secs, 60)
    if mins < 60:
        return f"{int(mins)}m{s:.0f}s"
    h, m = divmod(mins, 60)
    return f"{int(h)}h{int(m)}m{s:.0f}s"


def read_stdin() -> dict:
    try:
        raw = sys.stdin.read()
        if raw.strip():
            return json.loads(raw)
    except Exception:
        pass
    return {}


def timing_files(sid: str) -> tuple[Path, Path, Path]:
    """Return (turn_start_file, session_start_file, total_file) for a session."""
    _TIMING_DIR.mkdir(parents=True, exist_ok=True)
    return (
        _TIMING_DIR / f"{sid}.turn_start",
        _TIMING_DIR / f"{sid}.session_start",
        _TIMING_DIR / f"{sid}.total",
    )


def write_global(path: Path, value: float) -> None:
    try:
        path.write_text(str(value), encoding="utf-8")
    except Exception:
        pass


def elapsed_global(path: Path) -> str:
    """Return ' (Xs)' from a global timestamp file, else ''."""
    try:
        secs = time.time() - float(path.read_text(encoding="utf-8"))
        return f" ({fmt_secs(secs)})"
    except Exception:
        return ""


def sys_msg(msg: str) -> None:
    print(json.dumps({"systemMessage": msg}))


def additional_ctx(event_name: str, msg: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": event_name,
            "additionalContext": msg,
        }
    }))


def combined_output(event_name: str, banner: str, context: str) -> None:
    """Emit systemMessage (visible banner) + additionalContext (Claude's context) in one response."""
    print(json.dumps({
        "systemMessage": banner,
        "hookSpecificOutput": {
            "hookEventName": event_name,
            "additionalContext": context,
        }
    }))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "prompt"
    t = time.time()

    if mode == "session_start":
        data = read_stdin()
        sid = data.get("session_id", "default")
        reason = data.get("trigger") or data.get("start_reason") or ""
        suffix = f" ({reason})" if reason else ""
        turn_f, sess_f, total_f = timing_files(sid)
        sess_f.write_text(str(t), encoding="utf-8")
        total_f.write_text("0", encoding="utf-8")
        sys_msg(f"[{now()}] — session started{suffix}")

    elif mode == "prompt":
        data = read_stdin()
        sid = data.get("session_id", "default")
        turn_f, sess_f, total_f = timing_files(sid)
        turn_f.write_text(str(t), encoding="utf-8")
        # Bootstrap session files if session_start hook didn't fire (e.g. resume)
        if not sess_f.exists():
            sess_f.write_text(str(t), encoding="utf-8")
        if not total_f.exists():
            total_f.write_text("0", encoding="utf-8")
        # Idle gap: tell Claude how long the user was away if > 1 minute
        idle_part = ""
        last_stop_f = _TIMING_DIR / f"{sid}.last_stop"
        if last_stop_f.exists():
            try:
                gap = t - float(last_stop_f.read_text(encoding="utf-8"))
                if gap > 60:
                    idle_part = f" (after {fmt_secs(gap)} idle)"
            except Exception:
                pass
        sys_msg(f"[{now()}] — user message received{idle_part}")

    elif mode == "tool":
        data = read_stdin()
        tool = data.get("tool_name", "tool")
        sys_msg(f"[{now()}] {tool} completed")

    elif mode == "tool_fail":
        data = read_stdin()
        tool = data.get("tool_name", "tool")
        sys_msg(f"[{now()}] ✗ {tool} failed")

    elif mode == "subagent_start":
        data = read_stdin()
        agent_type = data.get("agent_type", "subagent")
        write_global(_SUBAGENT_START_FILE, t)
        sys_msg(f"[{now()}] ↗ {agent_type} subagent started")

    elif mode == "subagent_stop":
        data = read_stdin()
        agent_type = data.get("agent_type", "subagent")
        elapsed = elapsed_global(_SUBAGENT_START_FILE)
        banner = f"[{now()}] ↘ {agent_type} subagent done{elapsed}"
        context = f"{agent_type} subagent completed{elapsed}."
        combined_output("SubagentStop", banner, context)

    elif mode == "task_create":
        data = read_stdin()
        desc = data.get("description") or data.get("title") or data.get("task") or ""
        suffix = f": {desc[:60]}" if desc else ""
        sys_msg(f"[{now()}] ◎ task created{suffix}")

    elif mode == "task_done":
        data = read_stdin()
        desc = data.get("description") or data.get("title") or data.get("task") or ""
        suffix = f": {desc[:60]}" if desc else ""
        sys_msg(f"[{now()}] ✓ task completed{suffix}")

    elif mode == "pre_compact":
        write_global(_COMPACT_START_FILE, t)
        data = read_stdin()
        trigger = data.get("trigger") or data.get("compact_type") or ""
        suffix = f" ({trigger})" if trigger else ""
        sys_msg(f"[{now()}] — compaction starting{suffix}")

    elif mode == "post_compact":
        elapsed = elapsed_global(_COMPACT_START_FILE)
        data = read_stdin()
        trigger = data.get("trigger") or data.get("compact_type") or ""
        suffix = f" ({trigger})" if trigger else ""
        sys_msg(f"[{now()}] — compaction done{suffix}{elapsed}")

    elif mode == "stop":
        data = read_stdin()
        sid = data.get("session_id", "default")
        turn_f, _, total_f = timing_files(sid)
        turn_part = ""
        session_part = ""
        try:
            if turn_f.exists():
                elapsed = t - float(turn_f.read_text(encoding="utf-8"))
                turn_part = f" ({fmt_secs(elapsed)})"
                total = float(total_f.read_text(encoding="utf-8")) if total_f.exists() else 0.0
                total += elapsed
                total_f.write_text(str(total), encoding="utf-8")
                turn_f.unlink(missing_ok=True)
                session_part = f" | session {fmt_secs(total)}"
        except Exception:
            pass
        banner = f"[{now()}] — response complete{turn_part}{session_part}"
        context = f"Turn took{turn_part}." + (f" Session total{session_part.replace(' | session ', ': ')}." if session_part else "")
        combined_output("Stop", banner, context)
        (_TIMING_DIR / f"{sid}.last_stop").write_text(str(t), encoding="utf-8")

    elif mode == "session_end":
        data = read_stdin()
        sid = data.get("session_id", "default")
        reason = data.get("trigger") or data.get("end_reason") or ""
        suffix = f" ({reason})" if reason else ""
        stats = ""
        turn_f, sess_f, total_f = timing_files(sid)
        try:
            total = float(total_f.read_text(encoding="utf-8")) if total_f.exists() else 0.0
            wall = (t - float(sess_f.read_text(encoding="utf-8"))) if sess_f.exists() else 0.0
            if wall > 0:
                stats = f" — Claude {fmt_secs(total)} | wall {fmt_secs(wall)}"
            for f in (turn_f, sess_f, total_f, _TIMING_DIR / f"{sid}.last_stop"):
                f.unlink(missing_ok=True)
        except Exception:
            pass
        sys_msg(f"[{now()}] — session ending{suffix}{stats}")

    sys.exit(0)


if __name__ == "__main__":
    main()
