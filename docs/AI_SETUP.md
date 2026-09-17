# RAG and agent setup

ReLoop has two explicit modes. A model installation is required for actual generation and model-directed tool selection. The no-model mode never claims to be generative AI.

| Mode | Answers | Planner |
|---|---|---|
| `demo` (default) | Retrieved source excerpts, no generation | Scripted tool sequence, no model decisions |
| `ollama` | Actual retrieval-augmented generation | LLM selects tools from their observations |

## On your Mac

1. Install [Ollama](https://ollama.com/download) and open the Ollama application.
2. In Terminal, download the local model once:

   ```bash
   ollama pull qwen3:4b
   ```

3. Open Terminal in your freshly downloaded/extracted ReLoop-AI folder:

   ```bash
   python3 web_app.py --ai-mode ollama --model qwen3:4b
   ```

4. Open `http://127.0.0.1:8765` and select **Reuse assistant**. The banner should say **Local model mode: qwen3:4b**. The banner reflects configuration; a successful answer or plan confirms connection.
5. Ask **What should I check before transferring a monitor to a school?** Open the Evidence sections and compare each generated claim with its excerpt.
6. In Resource exchange, select SCHOOL01, request **display for computer lab**, quantity 2 and radius 10 km. Return to Reuse assistant and click **Prepare reuse plan**. Expand Tool activity.
7. Inspect the actual item before using **Inspect and review proposal**. That opens the existing form. The agent never records or reserves a transfer.

Qwen3:4b is an example tool-capable local model, not IBM Granite. The Ollama model page lists an approximately 2.5 GB download. Inference speed and memory requirements depend on the computer. Start with no other large applications running if memory is limited. No paid API account is required. Other Ollama tool-capable models can be selected with `--model`, but their behavior must be tested.

If Ollama is unavailable, the app returns an error. It does not silently replace a generative answer with a preview. To deliberately run the offline preview instead:

```bash
python3 web_app.py
```

## Architecture

### RAG

Project-authored Markdown guidance → heading-based chunks → TF-IDF retrieval → top relevant source excerpts → local LLM → structured claims with source IDs → citation ID checks → answer and evidence.

The knowledge base covers prototype rules, impact methods and responsible AI. It is not official MAIT policy or legal advice. No embeddings or vector database are required for this small collection. Retrieval without a matching excerpt abstains before calling the model. The model can also abstain. Unknown citation IDs and malformed answers are rejected. Valid IDs do not prove factual entailment; human review is still needed.

### Agent

The LLM observes the fixed user request and selects from three read-only tools:

- `search_inventory`: uses the user-selected recipient, quantity, radius and repair preference.
- `retrieve_guidance`: returns source-labelled excerpts for a focused question.
- `estimate_reuse`: only accepts an item returned by this run's eligible search, after guidance retrieval.

Each observation is returned to the model. The controller stops after a valid proposal, six model turns or eight calls. Structured numeric estimates are computed by Python, not invented by the model. No transfer, purchase, email, shell or arbitrary file access tool exists. The request's recipient and constraints cannot be changed by a tool call. A proposal is a snapshot, not a reservation; stock is checked again during human confirmation.

## Validation status

31 automated tests pass: 10 original core tests, 16 assistant tests and 5 HTTP integration tests. These cover retrieval, citations, abstention, invalid input, tool boundaries, approved partners, partial stock and no automatic writes. Model protocol tests use an explicit scripted test double; they are not real Qwen inference. Ollama was not installed in the build environment, so live local model quality and latency remain to be evaluated on the user's computer. The new assistant browser layout has not been visually tested in a real browser in this environment.

## Sources

- [Ollama chat API](https://docs.ollama.com/api/chat)
- [Ollama tool calling](https://docs.ollama.com/capabilities/tool-calling)
- [Qwen3:4b model](https://ollama.com/library/qwen3:4b)
