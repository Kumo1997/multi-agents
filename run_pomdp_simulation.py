from agents.agent_pomdp import AgentPOMDP
from agents.agent_variants import GreedyAgent, ExplorerAgent, CautiousAgent, CheapOnlyAgent
from environment.world_pomdp import EnvironmentManager
import pandas as pd

# Setup real world
food_shops = {
    "CheapShop": {"cost": 8, "energy_gain": 25, "success_rate": 0.7},
    "PremiumShop": {"cost": 15, "energy_gain": 40, "success_rate": 0.9}
}

actions = {
    "move": {"energy_cost": 15},
    "rest": {"energy_gain": 10}
}

# Create environment and agents
env = EnvironmentManager(food_shops, actions)
agents = [
    ExplorerAgent("Agent1"),
    GreedyAgent("Agent2"),
    CheapOnlyAgent("Agent3"),
    CautiousAgent("Agent4"),
    GreedyAgent("Agent5")
]

num_episodes = 3
num_days_per_episode = 5  

all_results = []
agent_actions = []  # 🌟 New: store actions for analysis


for episode in range(num_episodes):
    print(f"\n=== Episode {episode+1} ===")
    
    # Reset environment
    env = EnvironmentManager(food_shops, actions)

    reset_belief = (episode % 5 == 0)

    for agent in agents:
        agent.reset(reset_belief=reset_belief)
        agent.epsilon = min(agent.epsilon + 0.05, 0.6)

    # Normal day loop inside one episode
    for day in range(num_days_per_episode):
        env.reset_day()
        env.update_shop_prices()

        alive_agents = []

        for agent in agents:
            if not env.is_agent_alive(agent):
                continue

            observations = env.generate_noisy_observation()
            agent.perceive(observations)
            agent.update_belief(observations)
            agent.log_belief(day)

            action = agent.think()
            result = env.apply_agent_action(agent, action)

            agent_actions.append({
                "episode": episode,
                "day": day,
                "agent_name": agent.name,
                "agent_type": agent.__class__.__name__,
                "action": action,
                "result": result
            })
            env.apply_agent_action(agent, action)

            if env.is_agent_alive(agent):
                alive_agents.append(agent)

        agents = alive_agents

        if not agents:
            print("All agents collapsed! Ending this episode.")
            break

    # ✅ After each episode: record results
    for agent in agents:
        total_score = agent.true_state["energy"] + agent.true_state["money"]
        all_results.append({
            "episode": episode,
            "agent_name": agent.name,
            "agent_type": agent.__class__.__name__,
            "score": total_score
        })


    # Convert agent_actions to DataFrame
    df_actions = pd.DataFrame(agent_actions)

    # Convert world_events to DataFrame
    df_events = pd.DataFrame(env.world_events)

    print("\n=== Behavior Analysis ===")

    for _, event in df_events.iterrows():
        event_day = event["day"]
        print(f"\nAfter event on Day {event_day}: {event['events']}")

        # Look at next day actions
        next_day_actions = df_actions[(df_actions["day"] == event_day)]

        shop_choices = next_day_actions["action"].apply(lambda x: x.split("_")[-1])
        shop_counts = shop_choices.value_counts()

        print("Agent choices next day:")
        print(shop_counts)