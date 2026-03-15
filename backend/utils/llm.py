import asyncio
import json


async def call_claude_async(
    system: str,
    user_msg: str,
    schema: dict,
    allow_web_search: bool = False
) -> dict | None:
    """
    Spawns a Claude Code CLI subprocess and returns structured_output.
    Schema is passed as --json-schema — no JSON parsing needed on our end.
    """
    cmd = [
        "claude", "-p", user_msg,
        "--output-format", "json",
        "--json-schema", json.dumps(schema),
        "--system-prompt", system,
        "--max-budget-usd", "1.00",
    ]
    if allow_web_search:
        cmd += ["--allowedTools", "WebSearch"]

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        outer = json.loads(stdout)
        return outer["structured_output"]
    except Exception as e:
        print(f"[llm.py] call_claude_async failed: {e}")
        return None
