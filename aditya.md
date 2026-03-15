# CampaignIQ — Aditya's Work File
> Owner: Aditya | 17 Tasks | Frontend + Orchestrator + FastAPI + Platform Adapters

---

## My Quick Stats

| Stat | Value |
|------|-------|
| Total Tasks | 17 |
| Phases | 0, 3, 4, 5, 6, 7 |
| Primary Stack | React, FastAPI, asyncio, Python |
| First Blocker I Must Clear | T-0.3 → T-0.7 (everyone is waiting on mock JSON) |
| Hardest Task | T-3.5 (async wrapper — gets parallelism wrong = broken demo) |
| Demo Centrepiece | T-5.3 + T-7.3 (ComparisonTable + animation) |

---

## Status Legend
- [ ] Not Started
- [~] In Progress  
- [x] Done
- [!] Blocked — add reason

---

## Day-by-Day Plan

| Day | Tasks | Goal |
|-----|-------|------|
| Day 1 | T-0.2, T-0.3, T-0.7 | Unblock the whole team |
| Day 2 | T-3.3, T-3.5 | Async layer 3 wrapper working |
| Day 3–4 | T-4.3, T-4.4 | Orchestrator assembles all layers |
| Day 5–6 | T-4.6, T-4.7 | FastAPI endpoint live |
| Day 7–8 | T-5.1, T-5.3, T-5.4 | UI components built against mock |
| Day 9 | T-5.5 | Swap mock → live API |
| Day 10 | T-6.4, T-6.6 | Platform routing + MCP test |
| Day 11–12 | T-7.1, T-7.3, T-7.8 | Win features + demo polish |

---

## Phase 0 — Prerequisites & Environment Setup

### [ ] T-0.2 — Python environment & backend dependency install
- **Est. Time:** ~20 min
- **Output:** `requirements.txt`
- **Depends on:** —
- **Blocks:** —
- **Subtasks:**
  - [ ] `pip install pandas fastapi uvicorn python-dotenv`
  - [ ] ⚠️ Do NOT install `anthropic` SDK — Claude Code CLI handles all LLM calls
  - [ ] Pin all versions: `pandas==2.2.0 fastapi==0.110.0 uvicorn==0.27.0 python-dotenv==1.0.0`
  - [ ] Verify with `pip list`

---

### [ ] T-0.3 — Project directory structure scaffolding
- **Est. Time:** ~30 min
- **Output:** `project scaffold`
- **Depends on:** —
- **Blocks:** T-0.7, all layer files
- **⚠️ Do this first — everything else depends on the folder structure existing**
- **Subtasks:**
  - [ ] Create `/backend/data/` — CSVs, brand samples, cached JSON
  - [ ] Create `/backend/layers/` — empty `l1.py, l2.py, l3.py, l4.py`
  - [ ] Create `/backend/adapters/` — empty `base.py, adobe_campaign.py, salesforce_mc.py`
  - [ ] Create `/backend/schemas/` — empty JSON schema files
  - [ ] Create `/backend/tests/` — empty `test_l1.py, test_pipeline.py`
  - [ ] Create `/backend/utils/` — empty `llm.py`
  - [ ] Create `/backend/orchestrator.py`, `api.py`, `config.py`, `history.py`
  - [ ] Scaffold frontend: `npm create vite@latest frontend -- --template react`
  - [ ] `cd frontend && npm install tailwindcss axios recharts`

---

### [ ] T-0.7 — React scaffold + mock API contract *(sync with Ayush)*
- **Est. Time:** ~45 min
- **Output:** `frontend/src/mock/campaignReport.json`
- **Depends on:** T-0.3
- **Blocks:** T-5.1, T-5.2, T-5.3, T-5.4 — ALL frontend work
- **🚨 Highest priority Day 1 task — Jatin and Pratik's UI work is blocked until this is committed**
- **Subtasks:**
  - [ ] Agree final schema with Ayush before writing the mock
  - [ ] Create `frontend/src/mock/campaignReport.json` with ALL fields populated with realistic dummy values:
  ```json
  {
    "performance_score": 54,
    "brand_score": 38,
    "market_score": 71,
    "suggestions": ["Strengthen CTA with specific benefit", "Add urgency trigger"],
    "deviations": ["Tone too aggressive — violates TrustBank warm voice guideline"],
    "revised_asset": "Revised copy goes here — make it realistic length...",
    "change_explanations": [
      "Softened opening line (L2: tone deviation)",
      "Added trending savings stat (L3: market signal)"
    ],
    "roi_delta_direction": "high",
    "ready_to_launch": false,
    "recommended_channel": "push",
    "channel_rationale": "Historical data shows 35% higher CTR for push vs email for retail_savings segment",
    "confidence": "medium",
    "bias_flags": [],
    "approved": false,
    "approved_at": null
  }
  ```
  - [ ] Commit immediately — Jatin + Pratik start ScoreCards against this
  - [ ] Backend will swap in real API on Day 9 — Aditya changes one import line in App.jsx

---

## Phase 3 — Layer 3: Market Context

### [ ] T-3.3 — Layer 3 web search tool integration *(with Ayush)*
- **Est. Time:** ~1.5 hrs
- **Output:** `backend/layers/l3.py` (initial shell)
- **Depends on:** T-0.5 (Ayush's `utils/llm.py`)
- **Blocks:** T-3.4
- **Subtasks:**
  - [ ] Import `call_claude_async` from `utils/llm.py`
  - [ ] Call with `allow_web_search=True` — this adds `--allowedTools WebSearch` to CLI
  - [ ] Do NOT define tool JSON manually — Claude Code CLI routes search automatically
  - [ ] Handle structured output: CLI manages multi-turn internally, returns final `structured_output`
  - [ ] Verify: run a test call and confirm `web_search_requests > 0` in CLI output
  - [ ] Verify: `permission_denials` must be empty — if not, fix before proceeding

---

### [ ] T-3.5 — Layer 3 async wrapper
- **Est. Time:** ~1 hr
- **Output:** `backend/layers/l3.py` (async version) + `orchestrator.py` gather pattern
- **Depends on:** T-3.4 (Ayush)
- **Blocks:** T-4.3
- **⚠️ Performance critical — wrong implementation = sequential = 170s instead of 70s**
- **Subtasks:**
  - [ ] Convert `run_l3()` to `async def`
  - [ ] Use `asyncio.create_subprocess_exec` — NOT `subprocess.run` (that blocks the event loop)
  - [ ] In orchestrator, wire the gather pattern:
  ```python
  l1_result, l2_result, l3_result = await asyncio.gather(
      run_l1(asset, channel, segment),
      run_l2(asset),
      run_l3(asset, channel)   # ← runs concurrently, not after L1+L2
  )
  ```
  - [ ] Each subprocess is independent — no shared state between L1/L2/L3
  - [ ] Test: time `asyncio.gather()` call — total must be < sum of individual layer times
  - [ ] Expected: L1+L2 ~33s, L3 ~70s → total wall time ~70s (not 136s)

---

## Phase 4 — Layer 4: Creative Synthesis & Orchestrator

### [ ] T-4.3 — Orchestrator — pipeline assembly
- **Est. Time:** ~1 hr
- **Output:** `backend/orchestrator.py`
- **Depends on:** T-4.2 (Ayush), T-3.5
- **Blocks:** T-4.4, T-4.5
- **Subtasks:**
  - [ ] Import all four layer runners: `run_l1, run_l2, run_l3, run_l4`
  - [ ] Implement main `run()` function:
  ```python
  async def run(asset_text: str, channel: str, audience_segment: str) -> dict:
      l1, l2, l3 = await asyncio.gather(
          run_l1(asset_text, channel, audience_segment),
          run_l2(asset_text),
          run_l3(asset_text, channel)
      )
      l4 = await run_l4(asset_text, l1, l2, l3)
      return build_campaign_report(l1, l2, l3, l4)
  ```
  - [ ] `build_campaign_report()` merges all four outputs into final CampaignReport dict
  - [ ] Return must match `schemas/campaign_report.json` exactly

---

### [ ] T-4.4 — Error handling & graceful degradation
- **Est. Time:** ~45 min
- **Output:** Updated `orchestrator.py` + each layer file
- **Depends on:** T-4.3
- **Blocks:** —
- **Subtasks:**
  - [ ] Wrap each layer call in try/except inside orchestrator
  - [ ] L1 fails → `performance_score = None`, `suggestions = []`
  - [ ] L2 fails → `brand_score = None`, `deviations = []`
  - [ ] L3 fails → `market_score = None` — L4 prompt receives "market context unavailable"
  - [ ] L4 fails → return partial report with upstream scores only, `revised_asset = None`
  - [ ] Log errors: `print(f"[L3 ERROR] {e}")` — never surface stack traces to UI
  - [ ] Test: manually raise an exception in L3, verify pipeline still completes

---

### [ ] T-4.6 — Output schema finalisation — CampaignReport *(with Ayush)*
- **Est. Time:** ~20 min
- **Output:** `backend/schemas/campaign_report.json`
- **Depends on:** T-4.5
- **Blocks:** T-4.7
- **Subtasks:**
  - [ ] Write final JSON schema with all fields and types
  - [ ] Cross-check every field against `mock/campaignReport.json` from T-0.7 — must match exactly
  - [ ] Any field name change here = breaking change in React components — version it

---

### [ ] T-4.7 — FastAPI wrapper — POST /analyse endpoint
- **Est. Time:** ~1.5 hrs
- **Output:** `backend/api.py`
- **Depends on:** T-4.6
- **Blocks:** T-5.5
- **Subtasks:**
  - [ ] Create FastAPI app with CORS — add this on line 1, before anything else:
  ```python
  from fastapi.middleware.cors import CORSMiddleware
  app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
  ```
  - [ ] Define request model:
  ```python
  class AssetRequest(BaseModel):
      asset_text: str
      channel: str          # "email" | "push" | "banner"
      audience_segment: str # e.g. "retail_savings"
  ```
  - [ ] `POST /analyse` calls `orchestrator.run()` and returns `CampaignReport` as JSON
  - [ ] Add `X-Platform` header routing (calls adapter before orchestrator)
  - [ ] Add `--max-budget-usd 1.00` safety cap to each CLI call
  - [ ] Run: `uvicorn api:app --reload --port 8000`
  - [ ] Test with curl:
  ```bash
  curl -X POST http://localhost:8000/analyse \
    -H "Content-Type: application/json" \
    -d '{"asset_text":"Test campaign","channel":"email","audience_segment":"retail_savings"}'
  ```
  - [ ] Confirm response matches mock schema

---

## Phase 5 — React UI, API Integration & Demo

### [ ] T-5.1 — InputPanel component
- **Est. Time:** ~1.5 hrs
- **Output:** `frontend/src/components/InputPanel.jsx`
- **Depends on:** T-0.7
- **Blocks:** T-5.4
- **Subtasks:**
  - [ ] Channel selector: `<select>` with options email / push / banner
  - [ ] Audience segment selector: retail_savings / business / premium
  - [ ] Campaign text area with live character count
  - [ ] Analyse button — `disabled={isLoading}` while API call in flight
  - [ ] Animated progress indicator while loading: L1 → L2 → L3 → L4 (step through every 15s)
  - [ ] No `<form>` tags — use `onClick` on button, `onChange` on inputs
  - [ ] Submit calls `onAnalyse(payload)` prop — does NOT call API directly

---

### [ ] T-5.3 — ComparisonTable component *(with Ayush)*
- **Est. Time:** ~2.5 hrs
- **Output:** `frontend/src/components/ComparisonTable.jsx`
- **Depends on:** T-0.7
- **Blocks:** T-5.4
- **🎯 This is the demo centrepiece — judges form their impression here**
- **Subtasks:**
  - [ ] CSS Grid 2-column layout: `Original | Recommended`
  - [ ] Rows: Performance score / Brand score / Market score / ROI delta / Channel recommendation
  - [ ] Score cells colour-coded: red in Original column, green in Recommended column
  - [ ] Revised asset in highlighted `<pre>` block — green highlight on changed phrases
  - [ ] Change explanations as accordion — each item shows which layer drove the change
  - [ ] Ready to launch badge: green pill "Ready to launch" or red pill "Needs revision"
  - [ ] `approved` prop controls ApprovalGate visibility below table

---

### [ ] T-5.4 — App.jsx — layout & state management
- **Est. Time:** ~1 hr
- **Output:** `frontend/src/App.jsx`
- **Depends on:** T-5.1, T-5.2 (Jatin+Pratik), T-5.3
- **Blocks:** T-5.5
- **Subtasks:**
  - [ ] `const [report, setReport] = useState(null)` — null = pre-analysis state
  - [ ] `const [isLoading, setIsLoading] = useState(false)`
  - [ ] Two-panel layout: InputPanel left, results right (hidden until `report !== null`)
  - [ ] During development: import mock JSON and set as initial `report` to see full UI
  - [ ] Pass `isLoading` down to InputPanel to disable button + show progress
  - [ ] Pass `report` down to ScoreCards, ComparisonTable, ApprovalGate

---

### [ ] T-5.5 — API integration — swap mock for live FastAPI
- **Est. Time:** ~1 hr
- **Output:** `frontend/src/api/analyse.js`
- **Depends on:** T-5.4, T-4.7
- **Blocks:** T-5.6
- **⚠️ This is a one-line swap — changing the import in App.jsx is all that changes**
- **Subtasks:**
  - [ ] Create `src/api/analyse.js`:
  ```javascript
  import axios from 'axios';
  export const analyseAsset = async (payload) => {
    const res = await axios.post('http://localhost:8000/analyse', payload);
    return res.data;
  };
  ```
  - [ ] In App.jsx replace mock import with: `import { analyseAsset } from './api/analyse'`
  - [ ] Set `isLoading=true` on submit, `false` on response or error
  - [ ] Show error toast if API call fails
  - [ ] Smoke test: submit real campaign text, verify all 5 UI components populate correctly

---

## Phase 6 — Platform Adapters + MCP Server

### [ ] T-6.4 — X-Platform header routing in FastAPI
- **Est. Time:** ~30 min
- **Output:** `backend/api.py` (updated)
- **Depends on:** T-6.1 (Ayush's base adapter)
- **Blocks:** T-6.6
- **Subtasks:**
  - [ ] Add `x_platform: str = Header(default='generic')` to `/analyse` endpoint
  - [ ] Create `ADAPTERS` dict:
  ```python
  ADAPTERS = {
      'generic': GenericAdapter(),
      'adobe_campaign': AdobeCampaignAdapter(),
      'salesforce_mc': SalesforceMCAdapter()
  }
  ```
  - [ ] Call `adapter = ADAPTERS.get(x_platform, GenericAdapter())`
  - [ ] Call `normalised = adapter.normalise(request)` before `orchestrator.run()`
  - [ ] Test: `curl -H "X-Platform: adobe_campaign" ...` routes to AdobeCampaignAdapter

---

### [ ] T-6.6 — MCP server integration test + demo config *(with Ayush)*
- **Est. Time:** ~45 min
- **Output:** `mcp_test_results.md`
- **Depends on:** T-6.5 (Ayush)
- **Blocks:** —
- **Subtasks:**
  - [ ] Add CampaignIQ to `claude_desktop_config.json` and verify tools appear
  - [ ] Test all 4 MCP tools: `predict_performance`, `check_brand_consistency`, `get_market_context`, `analyse_campaign`
  - [ ] Verify `analyse_campaign` returns valid `CampaignReport` JSON
  - [ ] Document the config snippet — demo talking point: "one entry, any LLM client gets the full pipeline"
  - [ ] Record pass/fail + latency for each tool in `mcp_test_results.md`

---

## Phase 7 — Win Features

### [ ] T-7.1 — Human review gate + approval flow
- **Est. Time:** ~1 hr
- **Output:** `frontend/src/components/ApprovalGate.jsx`
- **Depends on:** T-5.3
- **Blocks:** —
- **🎯 Directly targets Responsible AI judging criterion**
- **Subtasks:**
  - [ ] Render below ComparisonTable only when `report !== null`
  - [ ] "Approve for Launch" button — `onClick` calls `POST /approve` with `{report_id, approved_by}`
  - [ ] On approval: set `approved=true`, show green badge "Approved for Launch" + timestamp
  - [ ] Unapproved state: amber badge "Pending Human Review"
  - [ ] Add `approved_by` + `approved_at` fields to FastAPI response schema
  - [ ] Demo line: *"AI recommends, human decides — clear accountability at every run"*

---

### [ ] T-7.3 — Before/after delta animation in ComparisonTable
- **Est. Time:** ~1 hr
- **Output:** `frontend/src/components/ComparisonTable.jsx` (updated)
- **Depends on:** T-5.3
- **Blocks:** —
- **🎯 Demo money shot — value is visible in 5 seconds without reading a single word**
- **Subtasks:**
  - [ ] Original scores render first in red (no animation)
  - [ ] Recommended scores animate in 800ms after: CSS `@keyframes countUp` from 0 → final value
  - [ ] Colour transitions red → green on the recommended column simultaneously
  - [ ] Example CSS:
  ```css
  @keyframes countUp {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  ```
  - [ ] Stagger each row by 150ms for a cascade effect
  - [ ] Pre-warm backend before demo recording — avoids cold-start latency on camera

---

### [ ] T-7.8 — Campaign analysis history log
- **Est. Time:** ~1 hr
- **Output:** `backend/history.py` + `frontend/src/components/HistoryPanel.jsx`
- **Depends on:** T-4.7, T-5.4
- **Blocks:** —
- **🎯 Makes impact story concrete — judges see cumulative value not just a single run**
- **Subtasks:**
  - [ ] `backend/history.py`: append each `/analyse` run to `data/history.json`:
  ```json
  {
    "timestamp": "2025-03-15T14:32:00",
    "channel": "email",
    "performance_score": 54,
    "brand_score": 38,
    "market_score": 71,
    "ready_to_launch": false,
    "approved": true
  }
  ```
  - [ ] Add `GET /history` endpoint returning last 20 runs
  - [ ] `HistoryPanel.jsx`: timeline of past runs showing scores + approved status
  - [ ] Demo talking point: *"12 campaigns analysed today, 8 approved, 4 sent back for revision"*

---

## My Dependency Map

```
T-0.2 ──────────────────────────────► (unblocks backend setup)
T-0.3 ──► T-0.7 ──► T-5.1 ──┐
                   T-5.2 ──┤──► T-5.4 ──► T-5.5 ──► T-5.6 ──► T-5.7
                   T-5.3 ──┘
T-3.3 ──► T-3.5 ──────────────────► T-4.3 ──► T-4.4
                                           └──► T-4.5 ──► T-4.6 ──► T-4.7
T-6.1(Ayush) ──► T-6.4 ──► T-6.6
T-5.3 ──► T-7.1
T-5.3 ──► T-7.3
T-4.7 ──► T-7.8
```

---

## Things I Must NOT Do

| Don't | Why |
|-------|-----|
| `import anthropic` | Project uses Claude Code CLI, not the SDK |
| Use `subprocess.run()` for layer calls | Blocks the event loop — use `asyncio.create_subprocess_exec` |
| Use `<form>` tags in React | Use `onClick`/`onChange` handlers only |
| Change field names in CampaignReport | Breaking change across backend + frontend + mock |
| Forget CORS on line 1 of api.py | React dev server on 5173 will be blocked by 8000 |
| Run L3 sequentially after L1+L2 | Kills demo latency — must use `asyncio.gather` |

---

## Estimated Total Time: ~20 hrs across 12 days