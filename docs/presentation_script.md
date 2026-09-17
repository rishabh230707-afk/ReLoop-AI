# ReLoop AI — presentation notes

Rishabh Bansal · MAIT Delhi


## Slide 1

Title and internship attribution follow the supplied brief. College confirmed by the user as MAIT Delhi. This prototype does not claim an IBM model integration.

## Slide 2

Problem hypothesis: disconnected inventory and purchasing workflows can hide useful stock. Validate through campus stock records and interviews. No claim has been made that this problem has already been measured at the student’s college.

## Slide 3

Sources: https://sdgs.un.org/goals/goal12 ; https://sdgs.un.org/goals/goal4 ; https://sdgs.un.org/goals/goal17 . SDG 12 target 12.5 is the primary alignment. SDG 4 contribution is access to functional educational resources; learning gains are not established. SDG 17 is an intended institutional partnership contribution, not evidence of existing formal partnerships.

## Slide 4

Editable flow diagram is the prototype evidence permitted by the internship guidelines. Inspection is a human confirmation in the demo, not an independent safety certificate. Continued-use tracking is proposed pilot work. Source: reloop.py and web_app.py in https://github.com/rishabh230707-afk/ReLoop-AI .

## Slide 5

This is an implemented classic NLP retrieval baseline, combined with deterministic business rules. Similarity is not a probability or safety assessment. Unsupported and multi-item requests ask for clarification. The inventory baseline remains classic NLP. A separate local Ollama assistant now implements generative RAG and model-selected tool calls. IBM Granite and IBM BOB are not integrated. Tools: Python standard library, HTML, CSS and JavaScript; no API key required. Compare advanced models only after measuring baseline usefulness.

## Slide 6

Implemented in ai_assistant.py. Knowledge is project-authored prototype guidance, not official MAIT policy. Actual RAG generation requires local Ollama. No-model mode returns labelled excerpts only. Source identifiers and answer schema are validated, not semantic entailment. Models can misinterpret evidence. Source: https://docs.ollama.com/api/chat . Live model output has not been evaluated in the build environment.

## Slide 7

The Ollama model selects tool calls and receives observations. The controller exposes only search_inventory, retrieve_guidance and estimate_reuse. Unknown tools or extra arguments are rejected. Estimate requires an item from the current eligible search and retrieved guidance. Python calculates amounts. No stock is reserved or written. The normal confirmation endpoint revalidates stock. Agent model behavior was tested with explicit scripted responses, not live inference. Source: https://docs.ollama.com/capabilities/tool-calling .

## Slide 8

Validation: python3 -m unittest test_reloop.py test_ai_assistant.py test_web_ai.py passed 31 tests. Coverage includes source retrieval, invalid citations, abstention, agent tool restrictions, partial stock, unapproved recipients, no automatic writes and HTTP routes. Scripted model responses test the model protocol without claiming real inference. Ollama was not installed in the build environment. New assistant UI has not been visually tested in a live browser here.

## Slide 9

Example local model is Qwen3:4b, not IBM Granite. Default --model is qwen3:4b. It is downloaded once through Ollama. Check hardware suitability and available memory. Install: https://ollama.com/download . Model: https://ollama.com/library/qwen3:4b . The default python3 web_app.py runs preview mode. Configuration banner alone does not prove model connectivity; verify a successful answer and tool trace.

## Slide 10

User-supplied screenshot of the original local ReLoop AI workspace before the assistant tab was added. Synthetic demo data, not measured environmental or educational outcomes. The visible session has four school units and two transfers, with 14 kg estimated mass and INR0 displayed savings. Initial inventory counts and the separate CLI example differ from this session.

## Slide 11

User-supplied screenshot of the original local ReLoop AI workspace before the assistant tab was added. Synthetic demo data, not measured environmental or educational outcomes. The visible session has four school units and two transfers, with 14 kg estimated mass and INR0 displayed savings. Initial inventory counts and the separate CLI example differ from this session.

## Slide 12

User-supplied screenshot of the original local ReLoop AI workspace before the assistant tab was added. Synthetic demo data, not measured environmental or educational outcomes. The visible session has four school units and two transfers, with 14 kg estimated mass and INR0 displayed savings. Initial inventory counts and the separate CLI example differ from this session.

## Slide 13

Distinctive choices in this project are reuse before buying, school eligibility filtering and a local transfer ledger. No claim of global novelty is made. A resource passport is a proposed future feature, not implemented: it could record item condition, maintenance, transfers and continued use, with institutional access controls.

## Slide 14

Fairness: description quality and a limited synonym list can affect discovery. Evaluate requests across schools and departments. Privacy: a production rollout needs institutional roles and access controls; these are not currently implemented. Ethics: food, medicines, chemicals, loose batteries and hazardous items are excluded. Partner approval flags are fictional fixtures, not verified agreements. A human must verify ownership, safe condition and suitability.

## Slide 15

Design thinking: empathize and validate the stated problem through planned interviews; define the inventory visibility gap; ideate a reuse-before-purchase workflow; prototype retrieval and a transfer ledger; test and refine. 31 test methods verify core, assistant and HTTP behavior, not real-world AI accuracy. Model tests use scripted responses. Live Ollama inference has not been tested in this environment. HTTP integration checks cover assets, matching, invalid token, fractional quantity, unapproved school and persisted transfer totals. Original interface screenshots were supplied by the user. The added assistant view has not been visually tested in a live browser here. User interviews and mentor feedback are planned, not completed.

## Slide 16

Scalability is a proposed design, not a current capability. Move local JSON state to a transactional database. Add tenant-aware access, reservations and concurrency control to prevent double allocation; verified listings and partner agreements; accessible interfaces and procurement integration. Evaluate cost, transport and refurbishment before expanding.

## Slide 17

Impact statement: If implemented successfully, ReLoop AI could make checking existing resources a routine step before purchasing, extending useful item life while improving access to school equipment through institutional collaboration. Environmental benefits depend on continued use, displaced purchases and collection/refurbishment costs. Do not equate equipment delivery with learning gains. All pilot targets are proposed.

## Slide 18

Repository: https://github.com/rishabh230707-afk/ReLoop-AI . Run commands from the extracted repository folder with Python 3 installed. Browser address http://127.0.0.1:8765 . School demo runs synthetic in-memory data. Sources: student-provided internship guidelines; https://sdgs.un.org/goals/goal4 ; https://sdgs.un.org/goals/goal12 ; https://sdgs.un.org/goals/goal17 . College name confirmed as MAIT Delhi.