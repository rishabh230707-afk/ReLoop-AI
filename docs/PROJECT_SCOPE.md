# ReLoop AI: expanded project scope

## Problem statement
How might we use AI to match usable surplus campus resources with the needs of departments and partner schools, so that we prevent avoidable waste and improve access to educational equipment?

## Users
Campus stores and procurement teams, school coordinators and institutional sustainability leads. No student accounts or personal student records are needed.

## Workflow
1. An institution audits stock and approves safe, usable items for sharing.
2. A school or department records a specific equipment need.
3. NLP retrieves candidate listings; rules check stock, repair permission, sharing eligibility and distance.
4. Staff inspect specifications, ownership and safety and authorize the transfer.
5. The recipient confirms receipt. In production, receipt and approval should be separate authenticated actions; the current demo uses one local confirmation.
6. Follow-up checks confirm whether the item remains useful after 30 and 90 days.

## SDGs and evidence
SDG 12 is primary: prevent premature disposal and keep goods in use. Track transferred units and reused mass, then verify continued use and whether a new purchase was displaced.

SDG 4 is supporting: direct suitable resources to schools that report a need. Track equipment availability and use in teaching. Equipment transfers alone do not prove improved education outcomes.

SDG 17 is supporting: establish accountable campus-school sharing arrangements. Track active institutional agreements and completed joint transfers. The demo registry is synthetic, not evidence of real partnerships.

## Proposed pilot
Interview campus stores and a prospective school coordinator. Obtain institutional approval. Start with safe, suitable furniture and inspected equipment. Collect no child-level data. Evaluate at least 50 staff-labelled search requests separately from glossary tuning. Measure Precision@3 and failures, including school eligibility and unclear requests. Aim for 10 accepted transfers with follow-up; these are future targets.

## Implementation boundary
The offline prototype has a fixture partner registry, school-sharing flags, per-recipient supplied distances, NLP ranking and a local ledger. It does not perform identity verification, create agreements, calculate routes, schedule pickups or safely support simultaneous users. Approval flags and inspections are demo inputs. Production needs authenticated approvals, database transactions and audit logs.
