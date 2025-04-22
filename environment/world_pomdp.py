import random
import copy

class EnvironmentManager:
    def __init__(self, food_shops, actions):
        self.day = 0
        self.food_shops = copy.deepcopy(food_shops)
        self.actions = actions
        self.shop_taken_today = {}
        self.world_events = []  # 🌎 Store events for analysis


    def reset_day(self):
        self.shop_taken_today = {}
        self.day += 1

        event_today = []

        if random.random() < 0.1:
            self.food_shops["CheapShop"]["success_rate"] = 0.0
            print(f"[World Event] Day {self.day}: CheapShop is CLOSED!")
            event_today.append("CheapShop Closed")
        else:
            self.food_shops["CheapShop"]["success_rate"] = 0.7

        if random.random() < 0.1:
            original_cost = self.food_shops["PremiumShop"]["cost"]
            self.food_shops["PremiumShop"]["cost"] = max(1, original_cost - 5)
            print(f"[World Event] Day {self.day}: PremiumShop is DISCOUNTED!")
            event_today.append("PremiumShop Discounted")
        else:
            self.food_shops["PremiumShop"]["cost"] = 15

        self.update_shop_prices()

        if event_today:
            self.world_events.append({"day": self.day, "events": event_today})




    def update_shop_prices(self, price_variation=2):
        """Randomly adjust shop prices each day (dynamic world)."""
        for shop_name, shop_info in self.food_shops.items():
            change = random.randint(-price_variation, price_variation)
            new_cost = max(1, shop_info["cost"] + change)
            self.food_shops[shop_name]["cost"] = new_cost

    def generate_noisy_observation(self):
        """Provide a noisy observation of the current world for agents."""
        observations = {}
        for shop_name, shop_info in self.food_shops.items():
            real_cost = shop_info["cost"]
            noisy_cost = real_cost + random.randint(-3, 3)  # Small noise
            observations[shop_name] = {
                "observed_cost": max(1, noisy_cost)
            }
        return observations

    def apply_agent_action(self, agent, action):
        """Apply agent's action to the environment."""
        agent.true_state["energy"] -= 2  # Base daily energy cost
        
        if action.startswith("buy_food"):
            shop_name = action.split("_")[-1]
            shop_info = self.food_shops[shop_name]

            if self.shop_taken_today.get(shop_name) is None:
                self.shop_taken_today[shop_name] = agent.name

                if random.random() < shop_info["success_rate"]:
                    agent.true_state["money"] -= shop_info["cost"]
                    agent.true_state["energy"] += shop_info["energy_gain"]
                    if shop_name == "PremiumShop":
                        agent.true_state["energy"] += 5  # Bonus only if success
                    result = "success"
                    agent.beliefs[shop_name]["trust"] += 0.05
                else:
                    agent.true_state["energy"] -= 5
                    result = "fail"
                    agent.beliefs[shop_name]["trust"] -= 0.1
            else:
                agent.true_state["energy"] -= 10
                result = "fail"

        elif action == "move":
            agent.true_state["energy"] -= self.actions["move"]["energy_cost"]
            result = "move"

        elif action == "rest":
            agent.true_state["energy"] += self.actions["rest"]["energy_gain"]
            result = "rest"

        # Clip trust between 0 and 1
        for shop in agent.beliefs:
            agent.beliefs[shop]["trust"] = min(max(agent.beliefs[shop]["trust"], 0.0), 1.0)

        # Save memory
        agent.memory.append((action, result))

        return result

    def is_agent_alive(self, agent):
        """Check if agent still alive (energy and money)."""
        return agent.true_state["energy"] > 0 and agent.true_state["money"] > 0
