# Updated submission fields

## Technologies
Python, HTML, CSS, JavaScript, TF-IDF and cosine similarity, Retrieval-Augmented Generation (RAG), Ollama local LLM integration, bounded tool-calling agent workflow and JSON local storage. Actual generative RAG and model-selected tool calls require Ollama model setup. Default mode is a clearly labelled no-model preview. IBM Granite and IBM BOB are not currently integrated.

## AI solution
ReLoop matches campus surplus with school needs. A document-grounded RAG assistant retrieves project-authored reuse guidance and generates source-cited answers through a local model. A bounded agent selects inventory search, guidance retrieval and estimate tools to prepare a nonbinding reuse proposal. Tool observations are visible. Python enforces recipient approval, item eligibility and user constraints. Only a person can inspect and confirm a transfer through the existing form.

## Validation
31 automated tests pass. Model protocol and tool selection tests use scripted responses. Live Ollama quality and latency have not been evaluated in the build environment; run the setup guide before claiming a live-model demonstration. All impact records remain synthetic.
