# tests/test_agent.py

import unittest
from agents.agent import Agent
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestAgent(unittest.TestCase):
    def test_initial_state(self):
        agent = Agent(name="TestAgent")
        self.assertEqual(agent.state["energy"], 50)
        self.assertEqual(agent.state["money"], 100)
    
    def test_q_values_initialized(self):
        agent = Agent(name="TestAgent")
        self.assertIn("CheapShop", agent.q_values)
        self.assertIn("PremiumShop", agent.q_values)

if __name__ == '__main__':
    unittest.main()
