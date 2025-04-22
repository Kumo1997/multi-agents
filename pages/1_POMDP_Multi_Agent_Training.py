import streamlit as st
import pandas as pd
import plotly.express as px
import random
import copy

from agents.agent_variants import GreedyAgent, ExplorerAgent, CautiousAgent, CheapOnlyAgent
from environment.world_pomdp import EnvironmentManager

st.set_page_config(page_title="Multi-Agent POMDP Dashboard", layout="wide")

st.title("🧠 Multi-Agent POMDP Training Dashboard")

# 📌 Sidebar - World Settings
st.sidebar.header("🌍 World Settings")

cheap_cost = st.sidebar.slider("CheapShop Cost", 5, 20, 8)
cheap_energy = st.sidebar.slider("CheapShop Energy Gain", 10, 50, 25)
cheap_success = st.sidebar.slider("CheapShop Success Rate", 0.0, 1.0, 0.7)

premium_cost = st.sidebar.slider("PremiumShop Cost", 10, 30, 15)
premium_energy = st.sidebar.slider("PremiumShop Energy Gain", 20, 60, 40)
premium_success = st.sidebar.slider("PremiumShop Success Rate", 0.0, 1.0, 0.9)

# 📌 Sidebar - Simulation Settings
st.sidebar.header("⚙️ Training Settings")

num_episodes = st.sidebar.slider("Training Episodes", 5, 50, 10)
num_days_per_episode = st.sidebar.slider("Days per Episode", 1, 10, 5)

# 📌 Sidebar - Agent Team Setup
st.sidebar.header("👥 Customize Agent Team")

num_explorers = st.sidebar.number_input("Number of Explorer Agents", 0, 20, 1)
num_greedy = st.sidebar.number_input("Number of Greedy Agents", 0, 20, 2)
num_cautious = st.sidebar.number_input("Number of Cautious Agents", 0, 20, 1)
num_cheaponly = st.sidebar.number_input("Number of CheapOnly Agents", 0, 20, 1)

# 📌 Sidebar - Policy Filters
st.sidebar.header("🔍 Agent Type Filters")
policy_filter = st.sidebar.multiselect(
    "Select agent types to show:",
    ["ExplorerAgent", "GreedyAgent", "CautiousAgent", "CheapOnlyAgent"],
    default=["ExplorerAgent", "GreedyAgent", "CautiousAgent", "CheapOnlyAgent"]
)

# 🌍 Setup dynamic food shops
food_shops = {
    "CheapShop": {"cost": cheap_cost, "energy_gain": cheap_energy, "success_rate": cheap_success},
    "PremiumShop": {"cost": premium_cost, "energy_gain": premium_energy, "success_rate": premium_success}
}
actions = {
    "move": {"energy_cost": 15},
    "rest": {"energy_gain": 10}
}

# 🚀 Start Training
if st.button("🚀 Start Training"):
    agents = []
    agent_counter = 1

    for _ in range(num_explorers):
        agents.append(ExplorerAgent(f"Explorer{agent_counter}"))
        agent_counter += 1
    for _ in range(num_greedy):
        agents.append(GreedyAgent(f"Greedy{agent_counter}"))
        agent_counter += 1
    for _ in range(num_cautious):
        agents.append(CautiousAgent(f"Cautious{agent_counter}"))
        agent_counter += 1
    for _ in range(num_cheaponly):
        agents.append(CheapOnlyAgent(f"CheapOnly{agent_counter}"))
        agent_counter += 1

    if len(agents) == 0:
        st.error("❌ Please create at least one agent to start training.")
        st.stop()

    all_results = []
    survival_stats = []
    agent_lifetimes = {agent.name: 0 for agent in agents}

    env = EnvironmentManager(food_shops, actions)

    for episode in range(num_episodes):
        env = EnvironmentManager(food_shops, actions)

        reset_belief = (episode % 5 == 0)
        for agent in agents:
            agent.reset(reset_belief=reset_belief)
            agent.epsilon = min(agent.epsilon + 0.05, 0.6)

        for day in range(num_days_per_episode):
            env.reset_day()

            alive_agents = []

            for agent in agents:
                if not env.is_agent_alive(agent):
                    continue

                agent_lifetimes[agent.name] += 1

                observations = env.generate_noisy_observation()
                agent.perceive(observations)
                agent.update_belief(observations)
                action = agent.think()
                env.apply_agent_action(agent, action)

                if env.is_agent_alive(agent):
                    alive_agents.append(agent)

            agents = alive_agents

            if not agents:
                break

        survival_stats.append({
            "Episode": episode,
            "SurvivingAgents": len(agents)
        })

        for agent in agents:
            all_results.append({
                "Episode": episode,
                "Agent": agent.name,
                "Policy": agent.__class__.__name__,
                "Energy": agent.true_state["energy"],
                "Money": agent.true_state["money"],
                "Score": agent.true_state["energy"] + agent.true_state["money"]
            })

    df = pd.DataFrame(all_results)
    df_lifetime = pd.DataFrame([
        {"Agent": name, "DaysSurvived": days}
        for name, days in agent_lifetimes.items()
    ])

    if not df.empty:
        df_filtered = df[df["Policy"].isin(policy_filter)]

        tab1, tab2, tab3, tab4, tab5 = st.tabs(["🧠 Overview", "🎯 Final Results", "🎬 Score Animation", "📊 Survival & Lifetime", "🏆 Final Outcome (Energy vs Money)"])

        with tab1:
            st.subheader("📈 How Our POMDP Simulation Works")

            flowchart = """
            digraph {
                rankdir=LR;
                node [shape=rect fontsize=14 style="rounded,filled" fontname="Helvetica"]

                World [label="🌍 World\n(Food Shops + Prices)" fillcolor="#AED6F1" style=filled]
                Observe [label="👀 Agent Observes\n(Noisy Observations)" fillcolor="#F9E79F" style=filled]
                BeliefUpdate [label="🧠 Update Beliefs\n(Trust + Cost)" fillcolor="#F9E79F" style=filled]
                Think [label="🤔 Plan Action\n(Based on Belief)" fillcolor="#ABEBC6" style=filled]
                Act [label="🏃 Take Action\n(Buy Food / Move / Rest)" fillcolor="#ABEBC6" style=filled]
                EnvChange [label="🔄 Environment Update\n(Success/Failure, Prices)" fillcolor="#AED6F1" style=filled]

                World -> Observe -> BeliefUpdate -> Think -> Act -> EnvChange -> World
            }
            """
            st.graphviz_chart(flowchart)

            st.subheader("📈 How Multi-Episode Training Works")
            training_flowchart = """
            digraph {
                rankdir=LR;
                node [shape=rect fontsize=14 style="rounded,filled" fontname="Helvetica"]

                Start [label="🚀 Start New Episode" fillcolor="#D6EAF8" style=filled]
                Reset [label="🔄 Reset Agents\n(Energy, Money, Maybe Beliefs)" fillcolor="#FAD7A0" style=filled]
                Train [label="🎯 Train Agents\n(Observe → Update Belief → Act)" fillcolor="#ABEBC6" style=filled]
                EndDay [label="📆 End of Day Check" fillcolor="#F5CBA7" style=filled]
                EndEpisode [label="🏁 End of Episode\n(Update Results)" fillcolor="#D6EAF8" style=filled]

                Start -> Reset -> Train -> EndDay
                EndDay -> Train [label="If Alive" fontsize=12]
                EndDay -> EndEpisode [label="If Dead/End Day" fontsize=12]
                EndEpisode -> Start
            }
            """
            st.graphviz_chart(training_flowchart)

            st.subheader("🤖 How Different Agent Strategies Think")
            agent_flowcharts = """
            digraph G {
                rankdir=TB;
                node [shape=rect fontsize=12 style="rounded,filled" fontname="Helvetica"]

                subgraph cluster_greedy {
                    label="Greedy Agent 🧠"
                    ThinkGreedy [label="Pick Shop\nHighest Trust / Cost Ratio" fillcolor="#A9CCE3" style=filled]
                }

                subgraph cluster_explorer {
                    label="Explorer Agent 🌍"
                    ThinkExplorer [label="With ε chance:\nRandom Shop\nElse: Highest Trust/Cost" fillcolor="#A3E4D7" style=filled]
                }

                subgraph cluster_cautious {
                    label="Cautious Agent 🔎"
                    ThinkCautious [label="Pick Shop\nHighest Trust Only" fillcolor="#F9E79F" style=filled]
                }

                subgraph cluster_cheaponly {
                    label="CheapOnly Agent 🛒"
                    ThinkCheapOnly [label="Always Pick\nCheapShop" fillcolor="#F5B7B1" style=filled]
                }
            }
            """
            st.graphviz_chart(agent_flowcharts)

        with tab2:
            st.subheader("🎯 Final Agent Scores Across Episodes (Filtered)")
            st.dataframe(df_filtered)

        with tab3:
            st.subheader("🎬 Agent Score Evolution Animation (Filtered)")

            df_filtered["IsBest"] = False
            for ep in df_filtered["Episode"].unique():
                ep_df = df_filtered[df_filtered["Episode"] == ep]
                if not ep_df.empty:
                    best_idx = ep_df["Score"].idxmax()
                    df_filtered.at[best_idx, "IsBest"] = True

            fig = px.scatter(
                df_filtered,
                x="Episode",
                y="Score",
                color="Policy",
                animation_frame="Episode",
                animation_group="Agent",
                size=df_filtered["IsBest"].apply(lambda x: 20 if x else 10),
                symbol=df_filtered["IsBest"].apply(lambda x: "star" if x else "circle"),
                hover_name="Agent",
                title="🏆 Agent Score Evolution (Best Highlighted)",
                range_y=[0, max(df["Score"].max() + 50, 200)]
            )
            st.plotly_chart(fig, use_container_width=True)

        with tab4:
            st.subheader("📊 Survival Across Episodes")
            df_survival = pd.DataFrame(survival_stats)

            fig_survival = px.line(
                df_survival,
                x="Episode",
                y="SurvivingAgents",
                markers=True,
                title="Surviving Agents Across Episodes",
                labels={"SurvivingAgents": "Number of Surviving Agents"}
            )
            st.plotly_chart(fig_survival, use_container_width=True)

            st.subheader("⏳ Lifetime Analysis (Days Survived per Agent)")
            fig_lifetime = px.bar(
                df_lifetime,
                x="Agent",
                y="DaysSurvived",
                color="Agent",
                title="⏳ Days Each Agent Survived",
                labels={"DaysSurvived": "Days Survived"},
                height=500
            )
            st.plotly_chart(fig_lifetime, use_container_width=True)

        with tab5:
            st.subheader("🏆 Final Outcome - Energy vs Money (Stacked Bar)")

            final_episode = df["Episode"].max()
            df_final = df[df["Episode"] == final_episode]

            df_stacked = df_final.melt(
                id_vars=["Agent", "Policy"],
                value_vars=["Energy", "Money"],
                var_name="Resource",
                value_name="Amount"
            )

            fig_stacked = px.bar(
                df_stacked,
                x="Agent",
                y="Amount",
                color="Policy",  # 🎯 DIFFERENT POLICIES different colors
                pattern_shape="Resource",  # 🎯 Energy vs Money using different patterns
                barmode="stack",
                title=f"🏆 Final Breakdown: Energy vs Money After Episode {final_episode}",
                labels={"Amount": "Value"},
                height=600,
                text_auto=True
            )
            st.plotly_chart(fig_stacked, use_container_width=True)


    else:
        st.warning("No agents survived any episodes.")
