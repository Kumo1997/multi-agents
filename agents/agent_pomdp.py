import random
import copy

class AgentPOMDP:
    def __init__(self, name, energy=120, money=100, epsilon=0.1):
        self.name = name
        self.true_state = {
            "energy": energy,
            "money": money
        }
        self.beliefs = {
            "CheapShop": {
                "expected_cost": 10 + random.uniform(-2, 2),
                "trust": 0.8 + random.uniform(-0.3, 0.3)
            },
            "PremiumShop": {
                "expected_cost": 20 + random.uniform(-1, 1),
                "trust": 0.9 + random.uniform(-0.1, 0.1)
            }
        }
        self.self_energy_belief = energy
        self.epsilon = epsilon
        self.memory = []  # List to record agent's actions and belief history

    def perceive(self, observations):
        """Save noisy observations from the environment."""
        self.last_observations = observations

    def reset(self, reset_belief=False):
        """Reset energy and money, and optionally reset beliefs."""
        self.true_state["energy"] = 120
        self.true_state["money"] = 100
        self.memory = []

        if reset_belief:
            for shop in self.beliefs:
                # Reinitialize trust and expected cost
                self.beliefs[shop]["expected_cost"] = 10 + random.uniform(-2, 2) if shop == "CheapShop" else 20 + random.uniform(-1, 1)
                self.beliefs[shop]["trust"] = 0.8 + random.uniform(-0.2, 0.2)



    def update_belief(self, observations):
        """Update internal belief estimates based on new observations."""
        for shop_name, obs_info in observations.items():
            observed_cost = obs_info["observed_cost"]
            current_estimate = self.beliefs[shop_name]["expected_cost"]
            # Moving average update
            self.beliefs[shop_name]["expected_cost"] = (
                0.8 * current_estimate + 0.2 * observed_cost
            )

    def think(self):
        """Decide on an action based on beliefs and exploration (epsilon-greedy)."""
        if random.random() < self.epsilon:
            shop_choice = random.choice(list(self.beliefs.keys()))
            print(f"{self.name} explores: {shop_choice}")
        else:
            shop_choice = max(
                self.beliefs.keys(),
                key=lambda s: self.beliefs[s]["trust"] / self.beliefs[s]["expected_cost"]
            )
            print(f"{self.name} exploits: {shop_choice}")
        return f"buy_food_{shop_choice}"

    def act(self, action, shop_taken, real_world_shops, actions):
        """Execute the chosen action and update true state."""
        self.true_state["energy"] -= 3  # Daily base energy loss

        if action.startswith("buy_food"):
            shop_name = action.split("_")[-1]
            shop_info = real_world_shops[shop_name]

            if shop_taken.get(shop_name) is None:
                shop_taken[shop_name] = self.name
                if random.random() < shop_info["success_rate"]:
                    self.true_state["money"] -= shop_info["cost"]
                    self.true_state["energy"] += shop_info["energy_gain"]
                    result = "success"
                    self.beliefs[shop_name]["trust"] += 0.05
                else:
                    self.true_state["energy"] -= 5
                    result = "fail"
                    self.beliefs[shop_name]["trust"] -= 0.1
            else:
                self.true_state["energy"] -= 2  # Reduced penalty for shop being full
                result = "fail"

        elif action == "move":
            self.true_state["energy"] -= actions["move"]["energy_cost"]
            result = "move"

        elif action == "rest":
            self.true_state["energy"] += actions["rest"]["energy_gain"]
            result = "rest"

        # Log the action result
        self.memory.append((action, result))

        # Clip trust between 0.0 and 1.0
        for shop in self.beliefs:
            self.beliefs[shop]["trust"] = min(max(self.beliefs[shop]["trust"], 0.0), 1.0)

    def log_belief(self, day):
        """Save a snapshot of beliefs for later analysis."""
        self.memory.append({
            "day": day,
            "belief_snapshot": copy.deepcopy(self.beliefs)
        })

class ExplorerAgent(AgentPOMDP):
    def __init__(self, name):
        super().__init__(name, epsilon=0.6)  # High exploration

class CautiousAgent(AgentPOMDP):
    def think(self):
        shop_choice = max(
            self.beliefs.keys(),
            key=lambda s: self.beliefs[s]["trust"]
        )
        print(f"{self.name} (Cautious) chooses: {shop_choice}")
        return f"buy_food_{shop_choice}"

class CheapOnlyAgent(AgentPOMDP):
    def think(self):
        print(f"{self.name} (CheapOnly) always picks CheapShop")
        return "buy_food_CheapShop"
