import unittest
from reloop import initial_state, match, confirm, summary
class ReLoopTests(unittest.TestCase):
    def test_school_matching_and_eligibility(self):
        state=initial_state()
        self.assertTrue(match(state,'display',recipient_id='SCHOOL01')['matches'])
        self.assertEqual(match(state,'stand',recipient_id='SCHOOL01')['status'],'no_match')
        self.assertEqual(match(state,'monitor',max_distance=1,recipient_id='SCHOOL01')['status'],'no_match')
        with self.assertRaises(ValueError):match(state,'monitor',recipient_id='SCHOOL02')
    def test_school_transfer_accounting(self):
        state=initial_state();confirm(state,'RL01',2,6000,300,250,True,'SCHOOL01')
        self.assertEqual(summary(state)['school_units_supplied'],2)
        self.assertEqual(summary(state)['recipient_partners_served'],1)
        with self.assertRaises(ValueError):confirm(state,'RL09',1,100,0,0,True,'SCHOOL01')
    def test_synonym_retrieval(self):
        result=match(initial_state(),'display for computer lab',2)
        self.assertEqual(result['matches'][0]['id'],'RL01')
    def test_distance_and_condition(self):
        self.assertTrue(all(x['distance_km']<=1 and x['condition']=='working' for x in match(initial_state(),'seating',2,1)['matches']))
        self.assertNotIn('RL12',[x['id'] for x in match(initial_state(),'monitor')['matches']])
        self.assertIn('RL12',[x['id'] for x in match(initial_state(),'monitor',max_distance=20)['matches']])
    def test_ambiguous_unknown_and_negated(self):
        for query in ['things','desk and chair','not a monitor','medical stand']:
            self.assertEqual(match(initial_state(),query)['status'],'clarify')
    def test_partial_stock(self):
        result=match(initial_state(),'HDMI projector',3)['matches'][0]
        self.assertEqual((result['offered_quantity'],result['remaining_need']),(1,2))
    def test_recorded_impact_and_stock(self):
        state=initial_state();confirm(state,'RL01',2,6000,300,250,True)
        self.assertEqual(state['inventory'][0]['quantity'],6)
        self.assertEqual(summary(state)['estimated_net_savings_inr'],11200)
        self.assertEqual(summary(state)['estimated_mass_reused_kg'],6.4)
        with self.assertRaises(ValueError):confirm(state,'RL01',7,6000,0,0,True)
    def test_no_savings_on_search(self):
        state=initial_state();match(state,'monitor');self.assertEqual(summary(state)['units_reused'],0)
    def test_invalid_input(self):
        for quantity in [0,-1]:
            with self.assertRaises(ValueError):match(initial_state(),'monitor',quantity)
        with self.assertRaises(ValueError):match(initial_state(),'monitor',max_distance=float('nan'))
        with self.assertRaises(ValueError):confirm(initial_state(),'RL01',1,6000,0,0,False)
        with self.assertRaises(ValueError):confirm(initial_state(),'RL01',1,float('inf'),0,0,True)
    def test_depleted_stock(self):
        state=initial_state();confirm(state,'RL07',1,10000,0,0,True)
        self.assertEqual(match(state,'projector')['status'],'no_match')
if __name__=='__main__':unittest.main(verbosity=2)
