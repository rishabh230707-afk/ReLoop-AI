# ReLoop AI
## Campus-to-School Resource Reuse Network

ReLoop connects usable surplus campus equipment and furniture with departments and partner schools that need them. It checks existing resources before new purchases, with the goal of preventing waste and improving access to educational equipment.

**Author:** Rishabh Bansal  
**Programme:** 1M1B AI for Sustainability Virtual Internship

## SDG alignment

| Goal | Project contribution | What a pilot should measure |
|---|---|---|
| **SDG 12 — Responsible Consumption and Production (primary)** | Keep useful goods in service through reuse | Accepted transfers, continued use and purchases actually avoided |
| **SDG 4 — Quality Education** | Supply suitable learning equipment to schools with resource shortages | Equipment received and used for teaching; no assumed learning gains |
| **SDG 17 — Partnerships for the Goals** | Coordinate resource sharing between campuses and schools | Participating institutions and completed joint transfers |

This is an intended contribution to these goals, not proof of achieved impact. All inventory, schools, approvals, distances, costs and transfers in the demo are **synthetic**. There are no real institutional partnerships yet.

## What works now

- Classic NLP matching using a small synonym glossary, TF-IDF vectors and cosine similarity.
- Stock, distance and repair filters with explanations and partial-quantity disclosure.
- Campus and school recipients from a demo partner registry.
- Approval checks and a school-sharing eligibility flag for each listing.
- Human inspection confirmation before a transfer can be recorded.
- Local stock updates, recipient records and reuse summaries.
- Optional desktop interface and a command-line demo.

**13 listings · 9 supported item types · 10 passing core test methods.** These are functional tests on synthetic data, not a real-world AI accuracy score.

## Run the project

Requires Python 3.10 or newer. No pip packages or API key needed.

Download and extract the repository ZIP. Open a terminal in its folder:

```bash
python3 reloop.py school-demo
```

This repeatable example finds monitors for a fictional school and records an in-memory transfer. It does not modify local state.

For the desktop interface:

```bash
python3 reloop.py gui
```

Python must include Tk support and run on a graphical desktop. The core and CLI were tested; the desktop interface has not been visually validated in the build environment. On Windows, use `py` if `python3` is unavailable.

## Desktop workspace

- **Find resources:** recipient dropdown, search filters and ranked resource cards.
- **Review transfer:** opens from a selected result and keeps its recipient fixed.
- **Reuse impact:** readable metric cards, transfer confirmations and recent history.
- **Partner network:** fictional institutions and their approval status.

Download the latest repository ZIP to get this redesigned interface. Close the old application before opening the new copy. The matching engine and CLI remain compatible with the existing commands.

## Search for a school

```bash
python3 reloop.py partners
python3 reloop.py match "display for computer lab" --quantity 2 --max-distance 10 --recipient SCHOOL01
```

| Demo partner | Type | Status |
|---|---|---|
| `CAMPUS01` | Campus | Approved fixture |
| `SCHOOL01` | School | Approved fixture |
| `SCHOOL02` | School | Awaiting review; blocked |

Use `CAMPUS01` for internal reuse. The default recipient in CLI searches is `CAMPUS01`; the desktop field starts with `SCHOOL01`. Distances are supplied per-recipient demo values, not map calculations. Listed approval is a fixture, not independently verified identity or an agreement.

## Record a demo school transfer

```bash
python3 reloop.py confirm RL01 --quantity 2 --purchase-price 6000 --transport 300 --refurbishment 250 --inspected --recipient SCHOOL01
python3 reloop.py summary
```

This reduces available stock and saves local history in `local_state.json`. Use only one process per state file. The file is excluded from Git. Delete it to reset the demo, which also deletes its local transfer history.

An example transfer of two monitors produces:

| Measure | Synthetic result |
|---|---:|
| School units supplied | 2 |
| Recipient partners served | 1 |
| Estimated reused mass | 6.4 kg |
| Estimated net savings | INR 11,200 |

Savings use the entered new-purchase benchmark minus refurbishment and transport. They only represent avoided expenditure if a replacement purchase actually would have occurred. A donated item can improve access without cancelling a purchase. Reused mass is not proven landfill diversion or CO2 reduction. “School units supplied” does not measure learning outcomes.

## Screenshots

Add actual application or terminal captures to the [screenshots folder](screenshots/). Follow the [capture and upload guide](screenshots/README.md). No application screenshots have been uploaded yet.

## Why AI is useful

Descriptions differ: a request for a “display” can match a “monitor.” The NLP baseline normalizes supported words and ranks descriptions. Filters enforce eligibility, distance, stock and repair preferences. Staff must still check size, connectors, condition, electrical safety and suitability for learners.

This version uses classic information retrieval, not an LLM, image recognition, neural classifier or IBM Granite. Similarity is a ranking value, not calibrated confidence. Unknown words or complex descriptions may need clarification.

## Responsible AI

- **Fairness:** Evaluate varied terminology and partner needs. The system does not infer deprivation or prioritize a school using sensitive personal data.
- **Transparency:** Explain matched terms and financial assumptions. Mark all demo figures as synthetic.
- **Privacy:** Store institutional fixture information only. No student or child data is collected.
- **Human control:** Staff verify ownership, safe use, eligibility and transfer approval. A checkbox is not a real safety certification.
- **Environmental integrity:** Exclude hazardous goods and keep impact estimates separate from measured outcomes.

Food, chemicals, medicines, loose batteries and hazardous items are outside scope. Partner approval and school-sharing flags must become verified processes before real use.

## Scalability

Start with one campus and one consenting school. Validate demand and item suitability through staff interviews and an approved inventory audit. Follow up after 30 and 90 days to confirm use.

A production network needs institutional authentication, role-based permissions, verified agreements, a transactional database, reservations and an audit trail. Search must respect institutional access. Only then expand to more campuses and schools or integrate with procurement systems. The current local JSON storage is not a concurrent multi-user backend.

## Tests and source

```bash
python3 -m unittest test_reloop.py
```

- `reloop.py`: matching, transfers, desktop interface and CLI.
- `inventory.json`: synthetic reusable stock and sharing constraints.
- `partners.json`: synthetic recipient registry.
- `school_demo_output.json`: actual school demo output.
- `demo_output.json`: actual internal-campus demo output.
- `test_reloop.py`: core regression and school-transfer tests.
- [Expanded scope and impact plan](docs/PROJECT_SCOPE.md)

## References

[UN Goal 4](https://sdgs.un.org/goals/goal4) · [UN Goal 12](https://sdgs.un.org/goals/goal12) · [UN Goal 17](https://sdgs.un.org/goals/goal17)

The project also follows the internship guidelines supplied by the student. Presentation and submission documents will be revised to match this expanded scope after the GitHub setup.
