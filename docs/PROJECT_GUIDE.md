# AI upgrade notice

The assistant now implements RAG and bounded tool calling through Ollama. See [AI_SETUP.md](AI_SETUP.md) for current setup and validation status. The original project scope below describes the inventory baseline. Any earlier statement that no LLM is implemented refers to that baseline only.

# ReLoop AI
## Campus Waste Prevention & Resource Reuse

A project for the 1M1B AI for Sustainability Virtual Internship, in collaboration with IBM SkillsBuild and AICTE.

**Student:** Rishabh Bansal  
**College:** Add your official college name before submitting.  
**Primary SDG:** 12 — Responsible Consumption and Production, especially target 12.5.

## The environmental problem

A usable monitor, desk or lab stand can remain in storage while another department buys a similar item. ReLoop connects surplus stock to real demand before procurement. The aim is to keep materials in use and prevent avoidable waste. This is a proposed campus problem to validate through interviews and stock records, not a claim that a particular college already has this problem.

## What makes the idea distinctive

- A purchase request becomes a reuse search before a new order is placed.
- Classic NLP connects descriptions such as “display” and “monitor” using an explicit vocabulary and TF-IDF retrieval.
- Physical constraints filter candidates by stock, distance and repair status.
- Only an inspected, recorded transfer updates the reuse ledger. A search creates no impact credit.
- Environmental accounting reports estimated mass kept in use. It does not turn a match into a carbon claim.

## Run the demo on macOS, Windows or Linux

Install Python 3.10 or newer if needed. The core uses only the standard library; no API key, model download or pip install is required.

Open a terminal in this folder:

```bash
python3 reloop.py demo
python3 reloop.py match "display for computer lab" --quantity 2 --max-distance 10
python3 reloop.py match "seating" --quantity 4 --accept-repair
python3 reloop.py match "projector" --quantity 3
python3 reloop.py match "monitor" --quantity 2 --max-distance 20
```

On Windows, use `py` in place of `python3` if that is your Python launcher.

### Optional desktop interface

```bash
python3 reloop.py gui
```

Python must include Tk support and a graphical desktop. If Tk is unavailable, all matching, confirmation and reporting functions remain accessible through the CLI. The automated checks cover the core and CLI; the desktop window was not visually validated in the build environment.

### Record a demo transfer

```bash
python3 reloop.py confirm RL01 --quantity 2 --purchase-price 6000 --transport 300 --refurbishment 250 --inspected
python3 reloop.py summary
```

The confirmation command changes `local_state.json` and reduces stock. Its costs and inspection flag are user-entered demo assumptions, not externally verified facts. Run only one process against a state file. Delete `local_state.json` to reset synthetic inventory; this also deletes its local demo transfer history. The `demo` command operates in memory and never changes that file.

Example arithmetic: 2 × (INR 6,000 − INR 250) − INR 300 = **INR 11,200 estimated net savings**. Reused mass: 2 × 3.2 kg = **6.4 kg**. These are synthetic example values. A purchase must actually have been avoided for the savings interpretation to hold.

## Prototype scope

Implemented: 13 synthetic inventory listings, 9 supported item types, text normalization, explicit synonym mapping, TF-IDF/cosine ranking, distance and repair filters, partial quantity disclosure, stock checks, manual inspection gating, local transfer history, and summary calculations.

This is a **classic NLP retrieval prototype**, not a trained neural classifier, LLM, image model or RAG system. It has no IBM model integration. The internship permits other AI workflows, so IBM branding is not treated as evidence of tool use.

Distance is a supplied sample value, not a GPS or map calculation. Specifications such as connector, size, load rating and electrical safety require human checking. Only the supported item vocabulary is recognized. Arbitrary paraphrases, spelling errors and other languages may fail. The similarity score is a text ranking value, not calibrated confidence.

Out of scope: food, medicines, chemicals, loose batteries, hazardous materials, live institutional accounts, ownership verification, pickup scheduling, payment, ERP integration and concurrent use. Listings are assumed to be approved for reuse within this fictional demo.

## Architecture

1. Inventory JSON provides title, description, condition, quantity, distance and estimated unit mass.
2. Request normalization expands a small explicit synonym glossary.
3. Ambiguous, unsupported and excluded requests trigger clarification.
4. Category-compatible stock is filtered by distance and repair permission.
5. TF-IDF vectors and cosine similarity rank remaining descriptions.
6. The user inspects a candidate and enters a purchase benchmark and transfer costs.
7. Confirmation reduces stock and writes a local transfer record atomically.
8. The ledger totals transferred units, estimated reused mass and estimated purchase savings.

There is no external data transfer. “Atomic write” avoids partial file writes; it does not make this prototype safe for concurrent users.

## Responsible AI

**Fairness:** Test matching across departments and common vocabulary. Short or unfamiliar descriptions can rank poorly. Production ranking must not favor departments that can afford better listings.  
**Transparency:** Show matched terms, similarity, condition, quantity and distance. Show the assumptions behind savings.  
**Privacy:** The demo uses fictional departments and no personal data. Production access should use institutional accounts and minimum necessary contact details.  
**Ethics and environmental integrity:** Exclude unsafe categories; require staff approval and physical inspection. Report reuse separately from proven waste prevention. Do not invent CO2 factors or assume every reused item displaces a new purchase.  
**Human control:** Rankings propose candidates. Staff decide suitability, ownership, safety and transfer eligibility.

## Validation

```bash
python3 -m unittest test_reloop.py
```

Eight automated test methods verify synonym retrieval, distance/repair filters, ambiguity, partial stock, ledger arithmetic, impact only after confirmation, invalid input, and exhausted inventory. These tests passed during creation. They are engineering checks on synthetic data, not a real-world accuracy score.

Before a pilot, obtain 50 anonymized real requests and have staff label acceptable matches. Measure Precision@3, no-match quality and performance by department. Keep this evaluation set separate from glossary tuning.

## Environmental pilot and scaling

Start with one campus and a limited stock audit. Interview storekeepers and procurement staff before assuming demand. Register only institution-approved safe goods. Record receiving-department acceptance, follow up after 30 and 90 days, and ask whether a planned new purchase was cancelled.

Pilot measures: completed reuse transfers; units still in use; estimated or weighed reused mass; purchases actually cancelled; rejection/repair rates. Proposed success criteria: at least 10 accepted transfers with 90-day follow-up and no unsafe-category transfer. These are targets, not results.

To scale, replace JSON with a transactional database. Add institutional tenants, department roles, approval and reservation workflows, audit logs and idempotent transfer confirmations. Use a search index with access filtering, then evaluate embedding retrieval against the TF-IDF baseline. Integrate the reuse check into procurement software only after staff validate usefulness. Expand to partner colleges before considering office parks. This architecture is proposed, not implemented.

Economic model to test: annual institutional subscription for inventory coordination and procurement integration. Environmental benefit depends on actual displaced purchases and longer useful life, not user growth alone.

## Included files

- `reloop.py`: core, CLI and optional desktop interface.
- `inventory.json`: synthetic demonstration inventory.
- `test_reloop.py`: core behavior checks.
- `demo_output.json`: actual output of the non-persistent demo.
- `submission_answers.md`: ready-to-paste project form content.
- `presentation_script.md`: short presenter script and likely questions.
- `ReLoop_AI.pptx`: editable submission presentation.

## References

- UN SDG 12 and target 12.5: https://sdgs.un.org/goals/goal12
- Internship project guidelines: supplied by the student in this conversation.

The inventory, prices, masses and distances are synthetic author-created demonstration data. No live campus survey, transfer or environmental measurement is claimed.

The images `prototype_workflow.png` and `demo_results.png` are presentation visuals of the workflow and actual synthetic demo results, not desktop application screenshots.
