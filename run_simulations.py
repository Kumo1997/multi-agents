from agents.agent import Agent
from environment.world import food_shops, actions
from utils.plots import plot_energy 
from utils.updater import update_shop_prices

def main():
    agents = [Agent(name=f"Agent{i+1}") for i in range(5)]  # Example 10 agents

    # Track energy history
    energy_histories = [[] for _ in agents]  

    for day in range(7):  # Simulate 7 days
        print(f"\n=== Day {day+1} ===")
        update_shop_prices(food_shops)
        shop_taken_today = {}

        # Each agent acts
        for idx, agent in enumerate(agents[:]): 
            if agent.state["energy"] <= 0 or agent.state["money"] <= 0:
                agents.remove(agent)
                continue

            action = agent.think(food_shops)
            agent.act(action, shop_taken_today, food_shops, actions)
            energy_histories[idx].append(agent.state["energy"])

        if not agents:
            print("\nAll agents collapsed! Game over.")
            break

    # After simulation, plot energy history
    agent_names = [agent.name for agent in agents]
    plot_energy(energy_histories, agent_names)

if __name__ == "__main__":
    main()

