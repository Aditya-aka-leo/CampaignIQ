# CampaignIQ — Claude Code Project Context

> AI-powered campaign asset analyser. Evaluates a marketing asset across 4 layers and produces a Campaign Health Report with scores, a revised asset, and a predicted ROI delta.

---

## Project Structure

```
campaigniq/
├── backend/
│   ├── data/
│   │   ├── historical_campaigns.csv    # 50-100 banking campaign records
│   │   ├── brand_samples.txt           # 10-15 TrustBank brand voice samples
│   │   └── brand_profile.json          # Pre-extracted brand voice (cached, not regenerated)
│   ├── layers/
│   │   ├── l1.py                       # Performance Prediction
│   │   ├── l2.py                       # Brand Consistency
│   │   ├── l3.py                       # Market Context (web search, async)
│   │   └── l4.py                       # Creative Synthesis
│   ├── adapters/
│   │   ├── base.py                     # Abstract CampaignAdapter
│   │   ├── adobe_campaign.py           # Adobe Campaign stub
│   │   └── salesforce_mc.py            # Salesforce MC stub
│   ├── schemas/
│   │   ├── l1_output.json
│   │   ├── l2_l3_output.json
│   │   └── campaign_report.json
│   ├── tests/
│   │   ├── test_l1.py
│   │   └── test_pipeline.py
│   ├── utils/
│   │   └── llm.py                      # Claude Code CLI subprocess wrapper
│   ├── orchestrator.py                 # asyncio.gather(L1,L2,L3) → L4
│   ├── api.py                          # FastAPI POST /analyse endpoint
│   ├── config.py                       # Constants, file paths, flags
│   └── history.py                      # Analysis run history log
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── InputPanel.jsx          # Channel + segment + asset text input
│   │   │   ├── ScoreCards.jsx          # 3 radial charts (Performance/Brand/Market)
│   │   │   ├── ComparisonTable.jsx     # Original vs Recommended side-by-side
│   │   │   ├── ApprovalGate.jsx        # Human review + approve for launch
│   │   │   └── HistoryPanel.jsx        # Past analysis timeline
│   │   ├── api/
│   │   │   └── analyse.js              # axios.post to FastAPI /analyse
│   │   ├── mock/
│   │   │   └── campaignReport.json     # Mock data for UI development
│   │   └── App.jsx                     # Root layout + state management
│   ├── package.json
│   └── vite.config.js
├── CLAUDE.md                           # ← You are here
├── ADITYA_TASKS.md
└── requirements.txt
```

---

## Architecture — The 4-Layer Pipeline

```
Marketer submits asset (text + channel + audience_segment)
        │
        ▼
┌─────────────────────────────────────────┐
│           Orchestrator (Python)          │
│   asyncio.gather(run_l1, run_l2, run_l3) │ ← L1, L2, L3 run IN PARALLEL
└────────────┬──────────┬─────────────────┘
             │          │          │
             ▼          ▼          ▼
          Layer 1    Layer 2    Layer 3
          Perf.      Brand      Market
          Pred.      Consist.   Context
          ~33s       ~33s       ~70s (web search)
             │          │          │
             └──────────┴──────────┘
                        │
                        ▼
                    Layer 4
                Creative Synthesis
                (rewrites asset)
                        │
                        ▼
              CampaignReport JSON
```

### Layer Details

| Layer | Input | Output | Data Source |
|-------|-------|--------|-------------|
| L1 — Performance Prediction | asset + 5 historical comps | `performance_score, strengths[], weaknesses[], suggestions[], channel_fit` | `historical_campaigns.csv` |
| L2 — Brand Consistency | asset + brand_profile.json | `brand_score, tone_verdict, theme_verdict, cta_verdict, deviations[]` | `brand_profile.json` (cached) |
| L3 — Market Context | asset + web search | `market_score, trends[], competitor_signals[], differentiation_opportunities[]` | Claude web search tool |
| L4 — Creative Synthesis | asset + L1 + L2 + L3 results | `revised_asset, change_explanations[], roi_delta_direction, ready_to_launch` | Upstream layer outputs |

---

## LLM Integration — Claude Code CLI (NOT the Anthropic SDK)

**Critical:** This project does NOT use `import anthropic`. All LLM calls go through the Claude Code CLI as a subprocess.

### The wrapper — `utils/llm.py`

```python
async def call_claude_async(
    system: str,
    user_msg: str,
    schema: dict,
    allow_web_search: bool = False
) -> dict:
    """
    Spawns a Claude Code CLI subprocess and returns structured_output directly.
    Schema is passed as --json-schema — no JSON parsing needed on our end.
    """
    cmd = [
        "claude", "-p", user_msg,
        "--output-format", "json",
        "--json-schema", json.dumps(schema),
        "--system", system,
        "--max-budget-usd", "1.00",   # safety cap
    ]
    if allow_web_search:
        cmd += ["--allowedTools", "WebSearch"]

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    outer = json.loads(stdout)
    return outer["structured_output"]  # schema-validated, no parsing needed
```

### Key rules for all layer implementations
- Always pass a `--json-schema` — this gives back `structured_output` directly
- Only L3 gets `allow_web_search=True` — no other layer should trigger web search
- Always wrap in try/except — on failure return `None` and let orchestrator handle gracefully
- `--max-budget-usd 1.00` on every call — safety cap for demo, estimated ~$0.27 per full run

---

## CampaignReport — The Final Output Schema

```json
{
  "performance_score": 72,
  "brand_score": 45,
  "market_score": 61,
  "suggestions": ["Strengthen CTA", "Add urgency"],
  "deviations": ["Tone too aggressive for TrustBank voice"],
  "revised_asset": "Full rewritten campaign text here...",
  "change_explanations": [
    "Softened CTA based on L2 brand deviation",
    "Added trend reference based on L3 market signal"
  ],
  "roi_delta_direction": "high",
  "ready_to_launch": false,
  "recommended_channel": "push",
  "channel_rationale": "Historical data shows 35% higher CTR for push vs email for this segment",
  "confidence": "medium",
  "bias_flags": [],
  "approved": false,
  "approved_at": null
}
```

> ⚠️ This schema is the contract between backend and frontend. Do NOT change field names without updating both `schemas/campaign_report.json` AND `mock/campaignReport.json`.

---

## FastAPI — Backend API

```
POST http://localhost:8000/analyse
Content-Type: application/json
X-Platform: generic   (or: adobe_campaign | salesforce_mc)

{
  "asset_text": "Your campaign copy here...",
  "channel": "email",
  "audience_segment": "retail_savings"
}
```

- CORS: `allow_origins=["*"]` — required for React dev server on port 5173
- Run with: `uvicorn api:app --reload --port 8000`
- Platform routing: `X-Platform` header selects the adapter before orchestrator runs

---

## Frontend — React + Vite

- **Port:** 5173 (Vite default)
- **State:** Single `report` state in `App.jsx` — null until analysis completes
- **Mock mode:** Import `mock/campaignReport.json` directly in App.jsx during development
- **Live mode:** Replace mock import with `src/api/analyse.js` Axios call (one line change)
- **Score colour logic:** green > 70, amber 40–70, red < 40 (Tailwind classes)
- **No `<form>` tags** — use `onClick` / `onChange` handlers only

---

## Orchestrator — Parallelism Pattern

```python
# L1, L2, L3 run concurrently — L4 waits for all three
l1_result, l2_result, l3_result = await asyncio.gather(
    run_l1(asset, channel, segment),
    run_l2(asset),
    run_l3(asset, channel)
)
l4_result = await run_l4(asset, l1_result, l2_result, l3_result)
return build_campaign_report(l1_result, l2_result, l3_result, l4_result)
```

- L3 takes ~70s due to web search but runs concurrently — total wall time ~70s not ~136s
- Each layer is an independent subprocess — no shared state
- If any layer fails, set its result to `None` and continue — L4 handles `None` gracefully

---

## Error Handling Rules

| Layer fails | Behaviour |
|-------------|-----------|
| L1 fails | `performance_score = None`, surface warning in UI |
| L2 fails | `brand_score = None`, surface warning in UI |
| L3 fails | `market_score = None`, note "market context unavailable" in L4 prompt |
| L4 fails | Return partial report with all upstream scores, no revised asset |

- Never surface Python stack traces to the UI
- Log all errors to console with layer identifier

---

## Phase 7 — Win Features (Already Planned)

These are implemented on top of the core pipeline to target judging criteria:

| Task | Feature | Judging Criterion |
|------|---------|------------------|
| T-7.1 | Human approval gate (ApprovalGate.jsx) | Responsible AI |
| T-7.2 | Confidence bands on scores (±band) | Functionality |
| T-7.3 | Before/after score animation (countUp) | UX |
| T-7.4 | Bias check in L4 prompt → `bias_flags[]` | Responsible AI |
| T-7.5 | Channel recommendation card | Innovation |
| T-7.6 | Two rewrites: Conservative + Bold tabs | Innovation |
| T-7.7 | Hallucination guard on change explanations | Responsible AI + Functionality |
| T-7.8 | Analysis history log + HistoryPanel | Impact / Scalability |

---

## Team & Task Ownership

| Owner | Tasks | Focus |
|-------|-------|-------|
| Aditya | T-0.2, T-0.3, T-0.7, T-3.3, T-3.5, T-4.3, T-4.4, T-4.6, T-4.7, T-5.1, T-5.3, T-5.4, T-5.5, T-6.4, T-7.1, T-7.3, T-7.8 | Frontend, Orchestrator, FastAPI |
| Ayush | T-0.4, T-0.5, T-0.6, T-0.7, T-3.4, T-3.6, T-4.1, T-4.2, T-5.3, T-5.5, T-6.1, T-6.2, T-6.5, T-6.6, T-7.4, T-7.6, T-7.7 | CLI wrapper, Layer 4, MCP Server |
| Jatin | T-1.1, T-1.2, T-1.5, T-2.1, T-2.2, T-2.3, T-2.4, T-2.5, T-5.2, T-6.3, T-7.2, T-7.5 | Data, Layer 1 |
| Pratik | T-1.3, T-1.4, T-1.5, T-3.1, T-3.2, T-5.2, T-5.8, T-7.2 | Brand profile, Layer 2 |

---

## Common Commands

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn api:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev

# Smoke test Claude CLI
claude -p "Return JSON with field status set to working" \
  --output-format json \
  --json-schema '{"type":"object","properties":{"status":{"type":"string"}},"required":["status"]}'

# Test web search
claude -p "What are the top banking marketing trends in 2025?" \
  --allowedTools WebSearch \
  --output-format json

# Run pipeline tests
cd backend
python -m pytest tests/test_pipeline.py -v
```

---

## Cost & Latency Estimates (Per Analysis Run)

| Component | Est. Time | Est. Cost |
|-----------|-----------|-----------|
| L1 + L2 (parallel) | ~33s | ~$0.08 |
| L3 (web search, parallel) | ~70s | ~$0.19 |
| L4 (synthesis) | ~30s | ~$0.05 |
| **Total wall time** | **~100s** | **~$0.27** |

---

## Hackathon Submission Checklist

- [ ] `test_results.md` — 3 test cases with accuracy %, latency, hallucination notes
- [ ] `demo_video.mp4` — 2-min screen capture, before/after visible in first 30s
- [ ] `scoping_sheet.pdf` — impact: 750 hrs/week (50 marketers × 10 campaigns × 1.5 hrs saved)
- [ ] All three uploaded to shared folder before 11:59 PM
