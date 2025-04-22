import random
from environment.world import food_shops, actions

class Agent:
    def __init__(self, name, energy=50, money=100, epsilon=0.1):
        self.name = name
        self.state = {
            "energy": energy,
            "money": money
        }
        self.q_values = {
            "CheapShop": 5,
            "PremiumShop": 10
        }
        self.memory = []  # Store experiences (optional: for future learning upgrades)
        self.epsilon = epsilon  # Exploration chance
        self.beliefs = {"CheapShop": {"expected_cost": 10, "trust": 0.8},
                        "PremiumShop": {"expected_cost": 20, "trust": 0.9}}
        self.self_energy_belief = 50  # Noisy estimate of own energy



    def perceive(self, environment_info):
        """(Optional) Process environment info (e.g., shop status)."""
        pass  # Not needed for now but useful later if you add dynamic shops

    def think(self, food_shops):
        """Decide what action to take based on current state and given food_shops."""
        if self.state["energy"] < 50 and self.state["money"] >= min(shop["cost"] for shop in food_shops.values()):
            if random.random() < self.epsilon:
                shop_name = random.choice(list(food_shops.keys()))
                print(f"{self.name} explores randomly: {shop_name}")
            else:
                affordable_shops = [shop for shop in food_shops.keys() if self.state["money"] >= food_shops[shop]["cost"]]
                shop_name = max(affordable_shops, key=lambda shop: self.q_values[shop])
                print(f"{self.name} exploits best known: {shop_name}")
            return f"buy_food_{shop_name}"
        elif self.state["energy"] < 30:
            return "rest"
        else:
            return random.choice(["move", "rest"])


    def act(self, action, shop_taken, food_shops, actions):
        """Execute action with dynamic environment passed."""
        self.state["energy"] -= 5  # Daily energy cost

        if action.startswith("buy_food"):
            shop_name = action.split("_")[-1]
            shop = food_shops[shop_name]

            if shop_taken.get(shop_name) is None:
                shop_taken[shop_name] = self.name
                if random.random() < shop["success_rate"]:
                    self.state["money"] -= shop["cost"]
                    self.state["energy"] += shop["energy_gain"]
                    self.q_values[shop_name] += 5
                    result = "success"
                else:
                    self.state["energy"] -= 5
                    self.q_values[shop_name] -= 10
                    result = "fail"
            else:
                self.state["energy"] -= 10
                result = "fail"

        elif action == "move":
            self.state["energy"] -= actions["move"]["energy_cost"]
            result = "move"
        elif action == "rest":
            self.state["energy"] += actions["rest"]["energy_gain"]
            result = "rest"

        self.memory.append((action, result))
