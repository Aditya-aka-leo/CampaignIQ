import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.llm import call_claude_async

L3_SCHEMA = {
    "type": "object",
    "properties": {
        "market_score": {"type": "number", "minimum": 0, "maximum": 100},
        "trends": {"type": "array", "items": {"type": "string"}},
        "competitor_signals": {"type": "array", "items": {"type": "string"}},
        "differentiation_opportunities": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["market_score", "trends", "competitor_signals", "differentiation_opportunities"]
}

SYSTEM_PROMPT = """You are a market intelligence analyst.
Your job is to evaluate how well a campaign asset aligns with the current market landscape.
First infer the industry, product, and target audience from the asset itself.
Use web search to find current trends, competitor campaigns, and opportunities relevant to that industry.
Be specific — name real trends and real competitor signals where possible.
Score 0-100: 100 means the asset perfectly capitalises on current market conditions."""


async def run_l3(asset_text: str, channel: str) -> dict | None:
    user_msg = f"""Analyse the current market context for this {channel} campaign asset:

ASSET:
{asset_text}

First, infer the industry and product category from the asset above.
Then use web search to research:
1. Current trends in that industry relevant to this type of campaign
2. What key competitors are currently messaging on {channel}
3. Any market opportunities this asset could better capitalise on

Score 0-100 how well this asset aligns with the current market context."""

    result = await call_claude_async(
        system=SYSTEM_PROMPT,
        user_msg=user_msg,
        schema=L3_SCHEMA,
        allow_web_search=True
    )

    if result is None:
        print("[L3 ERROR] call_claude_async returned None")
    return result
