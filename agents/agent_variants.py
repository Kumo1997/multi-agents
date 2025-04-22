# agent_variants.py
from .agent_pomdp import AgentPOMDP
import random

class GreedyAgent(AgentPOMDP):
    """Default greedy policy: trust / expected_cost."""
    def __init__(self, name):
        super().__init__(name, epsilon=0.1)

class ExplorerAgent(AgentPOMDP):
    """High exploration agent."""
    def __init__(self, name):
        super().__init__(name, epsilon=0.5)  # Higher epsilon

class CautiousAgent(AgentPOMDP):
    """Chooses the shop with highest trust, ignoring cost."""
    def think(self):
        shop_choice = max(
            self.beliefs.keys(),
            key=lambda s: self.beliefs[s]["trust"]
        )
        print(f"{self.name} (Cautious) chooses: {shop_choice}")
        return f"buy_food_{shop_choice}"

class CheapOnlyAgent(AgentPOMDP):
    """Always picks CheapShop."""
    def think(self):
        print(f"{self.name} (CheapOnly) always picks CheapShop")
        return "buy_food_CheapShop"
