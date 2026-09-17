import copy
import json
import unittest
from unittest.mock import patch
from ai_assistant import Agent, Knowledge, ModelError, Ollama, rag_answer
from reloop import initial_state

def call(name, args):
    return {'role': 'assistant', 'tool_calls': [{'function': {'name': name, 'arguments': args}}]}

class ScriptedModel:
    """Test double, not real model inference."""
    def __init__(self, responses):
        self.responses, self.messages = iter(responses), []
    def chat(self, messages, **kwargs):
        self.messages.append(copy.deepcopy(messages))
        return next(self.responses)

class AssistantTests(unittest.TestCase):
    def setUp(self):
        self.state = initial_state()
        self.request = {'query': 'display for computer lab', 'quantity': 2, 'radius': 10,
                        'recipient': 'SCHOOL01', 'price': 6000, 'refurbishment': 250, 'transport': 300}
    def test_retrieval_provenance(self):
        docs = Knowledge().retrieve('What physical inspection is needed before monitor transfer?')
        self.assertIn('reuse_rules-3', [d['id'] for d in docs])
        self.assertTrue(all(d['file'].startswith('knowledge/') for d in docs))
    def test_unknown_question_abstains_without_model(self):
        model = ScriptedModel([])
        self.assertEqual(rag_answer('quasars astrophysics', model)['status'], 'insufficient_evidence')
        self.assertEqual(model.messages, [])
    def test_preview_does_not_claim_rag(self):
        self.assertEqual(rag_answer('How is reused mass estimated?')['mode'], 'retrieval_preview')
    def test_rag_receives_evidence_and_validates_citations(self):
        model = ScriptedModel([{'content': json.dumps({'insufficient_evidence': False,
                 'claims': [{'text': 'Inspect the item before transfer.', 'source_ids': ['reuse_rules-3']}]})}])
        r = rag_answer('What inspection is required before monitor transfer?', model)
        self.assertEqual(r['status'], 'answered')
        self.assertIn('[reuse_rules-3]', r['answer'])
        payload = json.loads(model.messages[0][-1]['content'])
        self.assertIn('sources', payload)
        self.assertIn('question', payload)
    def test_fabricated_citations_are_rejected(self):
        model = ScriptedModel([{'content': '{"insufficient_evidence":false,"claims":[{"text":"Approved.","source_ids":["invented"]}]}'}])
        self.assertEqual(rag_answer('inspection before transfer', model)['status'], 'invalid_generation')
    def test_malformed_generation_is_not_displayed_as_answer(self):
        for content in ['not json', '[]', '{"claims":[]}']:
            r = rag_answer('inspection transfer', ScriptedModel([{'content': content}]))
            self.assertEqual(r['status'], 'invalid_generation')
    def test_model_abstention(self):
        r = rag_answer('inspection transfer', ScriptedModel([{'content': '{"insufficient_evidence":true}'}]))
        self.assertEqual(r['status'], 'insufficient_evidence')
    def test_preview_proposal_does_not_mutate_state(self):
        before = copy.deepcopy(self.state)
        r = Agent(self.state, self.request).run()
        self.assertEqual(r['mode'], 'workflow_preview')
        self.assertEqual(r['proposal']['estimated_mass_reused_kg'], 6.4)
        self.assertEqual(r['proposal']['estimated_net_savings_inr'], 11200)
        self.assertFalse(r['transfer_recorded'])
        self.assertEqual(self.state, before)
    def test_model_tool_loop_observes_results(self):
        model = ScriptedModel([call('search_inventory', {}),
            call('retrieve_guidance', {'question': 'inspection before school transfer'}),
            call('estimate_reuse', {'item_id': 'RL01'})])
        r = Agent(self.state, self.request, model).run()
        self.assertEqual(r['status'], 'awaiting_human_inspection')
        self.assertEqual(r['mode'], 'agent_ollama')
        self.assertEqual(len(r['trace']), 3)
        self.assertEqual(model.messages[1][-1]['role'], 'tool')
        self.assertFalse(self.state['transfers'])
    def test_unapproved_recipient_blocked(self):
        with self.assertRaises(ValueError):
            Agent(self.state, {**self.request, 'recipient': 'SCHOOL02'})
    def test_model_cannot_transfer_or_change_constraints(self):
        model = ScriptedModel([call('confirm_transfer', {'item_id': 'RL01'}),
                               call('search_inventory', {'radius': 999}), {'content': 'done'}])
        r = Agent(self.state, self.request, model).run()
        self.assertTrue(all('error' in t['observation'] for t in r['trace']))
        self.assertIsNone(r['proposal'])
        self.assertFalse(self.state['transfers'])
    def test_unsearched_item_and_missing_guidance_rejected(self):
        a = Agent(self.state, self.request)
        self.assertIn('error', a.call('estimate_reuse', {'item_id': 'RL01'}))
        a.call('search_inventory', {})
        self.assertIn('error', a.call('estimate_reuse', {'item_id': 'RL01'}))
    def test_no_match_and_partial_stock(self):
        r = Agent(self.state, {**self.request, 'radius': 0}).run()
        self.assertIsNone(r['proposal'])
        self.assertEqual(r['status'], 'no_match')
        r = Agent(self.state, {**self.request, 'quantity': 20}).run()
        self.assertEqual(r['proposal']['quantity'], 8)
        self.assertEqual(r['proposal']['remaining_need'], 12)
    def test_bounded_loop(self):
        r = Agent(self.state, self.request, ScriptedModel([call('search_inventory', {})]*10)).run()
        self.assertEqual(len(r['trace']), 6)
        self.assertIsNone(r['proposal'])
    def test_invalid_numeric_inputs(self):
        for key, value in [('quantity', True), ('quantity', 1.5), ('radius', float('nan')), ('price', -1), ('repair', 'yes')]:
            with self.assertRaises(ValueError):
                Agent(self.state, {**self.request, key: value})
    def test_ollama_contract_and_unavailable(self):
        with patch('urllib.request.build_opener') as opener:
            opener.return_value.open.return_value.__enter__.return_value.read.return_value = b'{"message":{"role":"assistant","content":"hello"}}'
            self.assertEqual(Ollama().chat([{'role':'user','content':'hi'}], json_mode=True)['content'], 'hello')
            request = opener.return_value.open.call_args.args[0]
            self.assertEqual(request.full_url, 'http://127.0.0.1:11434/api/chat')
            self.assertEqual(json.loads(request.data)['format'], 'json')
            opener.return_value.open.side_effect = OSError('offline')
            with self.assertRaises(ModelError): Ollama().chat([])

if __name__ == '__main__': unittest.main()
