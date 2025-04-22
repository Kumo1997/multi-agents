import streamlit as st
import random
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import os
import plotly.express as px


from agents.agent import Agent
from utils.updater import update_shop_prices

# Default world settings
default_shops = {
    "CheapShop": {"cost": 8, "energy_gain": 25, "success_rate": 0.6},
    "PremiumShop": {"cost": 15, "energy_gain": 40, "success_rate": 0.9}
}

actions = {
    "move": {"energy_cost": 15},
    "rest": {"energy_gain": 10}
}

# Sidebar: World Settings
st.sidebar.header("World Settings")

cheap_cost = st.sidebar.slider("CheapShop Cost", 5, 20, default_shops["CheapShop"]["cost"])
cheap_energy = st.sidebar.slider("CheapShop Energy Gain", 10, 50, default_shops["CheapShop"]["energy_gain"])
cheap_success = st.sidebar.slider("CheapShop Success Rate", 0.0, 1.0, default_shops["CheapShop"]["success_rate"])

premium_cost = st.sidebar.slider("PremiumShop Cost", 10, 30, default_shops["PremiumShop"]["cost"])
premium_energy = st.sidebar.slider("PremiumShop Energy Gain", 20, 60, default_shops["PremiumShop"]["energy_gain"])
premium_success = st.sidebar.slider("PremiumShop Success Rate", 0.0, 1.0, default_shops["PremiumShop"]["success_rate"])

# Update world settings dynamically
food_shops = {
    "CheapShop": {"cost": cheap_cost, "energy_gain": cheap_energy, "success_rate": cheap_success},
    "PremiumShop": {"cost": premium_cost, "energy_gain": premium_energy, "success_rate": premium_success}
}

# Main: Simulation Settings
st.title("🧠 Multi-Agent Competition Simulator")

num_agents = st.slider("Number of Agents", 1, 20, 5)
num_days = st.slider("Number of Days to Simulate", 1, 100, 10)

# Button to start simulation
if st.button("Run Simulation"):
    # Create agents
    agents = [Agent(name=f"Agent{i+1}") for i in range(num_agents)]
    agent_names = [agent.name for agent in agents]

    # Track energy and wealth histories
    energy_histories = {name: [] for name in agent_names}
    wealth_histories = {name: [] for name in agent_names}

    # Create progress bar
    progress_bar = st.progress(0)

    # Simulation loop
    for day in range(num_days):
        update_shop_prices(food_shops)
        shop_taken_today = {}

        current_agents = agents[:]
        for agent in current_agents:
            if agent.state["energy"] <= 0 or agent.state["money"] <= 0:
                agents.remove(agent)
                continue

            action = agent.think(food_shops)
            agent.act(action, shop_taken_today, food_shops, actions)

            # Track energy and wealth
            energy_histories[agent.name].append(agent.state["energy"])
            wealth = agent.state["energy"] + agent.state["money"]
            wealth_histories[agent.name].append(wealth)

        # Update progress bar
        progress_bar.progress((day + 1) / num_days)

        if not agents:
            break

    # Simulation Complete
    st.success(f"{len(agents)} agents survived out of {num_agents}!")

    # ⚡ Energy Plot
    if agents and any(len(history) > 0 for history in energy_histories.values()):
        st.subheader("⚡️ Agent Energy Over Time")

        # Prepare data for Plotly
        energy_data = []
        for agent_name, energy_list in energy_histories.items():
            for day, energy in enumerate(energy_list):
                energy_data.append({"Agent": agent_name, "Day": day, "Energy": energy})

        df_energy = pd.DataFrame(energy_data)

        # Create interactive plot
        fig_energy = px.line(
            df_energy,
            x="Day",
            y="Energy",
            color="Agent",
            title="Agent Energy Over Time",
            markers=True,
            hover_name="Agent",
            hover_data=["Energy"]
        )
        st.plotly_chart(fig_energy, use_container_width=True)

    else:
        st.warning("No surviving agents or no energy data collected.")


    # 🏆 Leaderboard
    if agents:
        st.subheader("🏆 Leaderboard - Final Agent Results")

        leaderboard_data = []

        for agent in agents:
            total_wealth = agent.state["energy"] + agent.state["money"]
            leaderboard_data.append({
                "Agent": agent.name,
                "Energy": agent.state["energy"],
                "Money": agent.state["money"],
                "Total Wealth": total_wealth
            })

        # Sort leaderboard
        leaderboard_data = sorted(leaderboard_data, key=lambda x: x["Total Wealth"], reverse=True)

        # 🥇 Add trophy for top-scoring agents (handle ties)
        if leaderboard_data:
            top_score = leaderboard_data[0]["Total Wealth"]
            for entry in leaderboard_data:
                if entry["Total Wealth"] == top_score:
                    entry["Agent"] = f"🥇 {entry['Agent']}"
                else:
                    break

        df = pd.DataFrame(leaderboard_data)

        st.dataframe(
            df.style
            .highlight_max(axis=0, color="lightgreen")
            .format(precision=1)
        )

        # Save leaderboard to CSV
        os.makedirs("data", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = f"data/leaderboard_{timestamp}.csv"
        df.to_csv(csv_path, index=False)
        st.success(f"Leaderboard saved to: `{csv_path}`")

    else:
        st.warning("All agents collapsed. No leaderboard to show.")

    # 📈 Top Agent(s) Wealth Chart
    st.subheader("📈 Top Agent(s) Wealth Progression")

    top_agents = sorted(agents, key=lambda a: a.state["energy"] + a.state["money"], reverse=True)[:3]
    top_agent_names = [agent.name for agent in top_agents]
    df = pd.DataFrame(leaderboard_data)

    if top_agent_names:
        wealth_data = []
        for agent_name in top_agent_names:
            if agent_name in wealth_histories:
                for day, wealth in enumerate(wealth_histories[agent_name]):
                    wealth_data.append({"Agent": agent_name, "Day": day, "Wealth": wealth})

        df_wealth = pd.DataFrame(wealth_data)

        fig_wealth = px.line(
            df_wealth,
            x="Day",
            y="Wealth",
            color="Agent",
            title="Top Agent(s) Wealth Over Time",
            markers=True,
            hover_name="Agent",
            hover_data=["Wealth"]
        )
        st.plotly_chart(fig_wealth, use_container_width=True)
    else:
        st.warning("No top agents to plot wealth.")

