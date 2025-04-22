import graphviz
import streamlit as st

st.subheader("📈 How Our POMDP Simulation Works")

# Build the main POMDP flowchart
flowchart = graphviz.Digraph(comment="POMDP Simulation")
flowchart.attr(rankdir="LR", fontname="Helvetica", fontsize="14", style="rounded")

flowchart.node("World", "🌍 World\n(Food Shops + Prices)", style="filled", fillcolor="#AED6F1")
flowchart.node("Observe", "👀 Agent Observes\n(Noisy Observations)", style="filled", fillcolor="#F9E79F")
flowchart.node("BeliefUpdate", "🧠 Update Beliefs\n(Trust + Cost)", style="filled", fillcolor="#F9E79F")
flowchart.node("Think", "🤔 Plan Action\n(Based on Belief)", style="filled", fillcolor="#ABEBC6")
flowchart.node("Act", "🏃 Take Action\n(Buy Food / Move / Rest)", style="filled", fillcolor="#ABEBC6")
flowchart.node("EnvChange", "🔄 Environment Update\n(Success/Failure, Prices)", style="filled", fillcolor="#AED6F1")

flowchart.edges([
    ("World", "Observe"),
    ("Observe", "BeliefUpdate"),
    ("BeliefUpdate", "Think"),
    ("Think", "Act"),
    ("Act", "EnvChange"),
    ("EnvChange", "World")
])

# Display POMDP flowchart
st.graphviz_chart(flowchart)

# Save POMDP flowchart as PNG
pomdp_path = "pomdp_flowchart"
flowchart.render(pomdp_path, format="png", cleanup=True)

st.subheader("🤖 How Different Agent Strategies Think")

# Define colorful Agent Strategies flowchart as a string
agent_flowcharts = """
digraph G {
    rankdir=TB;
    node [shape=rect fontsize=12 style="rounded,filled" fontname="Helvetica"];

    subgraph cluster_greedy {
        style=filled;
        color="#A9CCE3";
        label="Greedy Agent 🧠";
        ThinkGreedy [label="Pick Shop\\nHighest Trust / Cost Ratio" fillcolor="#A9CCE3" style=filled];
    }

    subgraph cluster_explorer {
        style=filled;
        color="#A3E4D7";
        label="Explorer Agent 🌍";
        ThinkExplorer [label="With ε chance:\\nRandom Shop\\nElse: Highest Trust/Cost" fillcolor="#A3E4D7" style=filled];
    }

    subgraph cluster_cautious {
        style=filled;
        color="#F9E79F";
        label="Cautious Agent 🔎";
        ThinkCautious [label="Pick Shop\\nHighest Trust Only" fillcolor="#F9E79F" style=filled];
    }

    subgraph cluster_cheaponly {
        style=filled;
        color="#F5B7B1";
        label="CheapOnly Agent 🛒";
        ThinkCheapOnly [label="Always Pick\\nCheapShop" fillcolor="#F5B7B1" style=filled];
    }
}
"""

# Display colorful Agent Strategies flowchart
st.graphviz_chart(agent_flowcharts)

# Save Agent Strategies flowchart as PNG
agent_path = "agent_strategies_flowchart"

# --- Important: build graph from string to save it ---
# You cannot .render() a string directly, so:
graph = graphviz.Source(agent_flowcharts)
graph.render(agent_path, format="png", cleanup=True)

# --- Download Buttons ---
st.subheader("📥 Download Flowcharts")

# Button for POMDP flowchart
with open(f"{pomdp_path}.png", "rb") as file:
    st.download_button(
        label="Download POMDP Simulation Flowchart",
        data=file,
        file_name="pomdp_flowchart.png",
        mime="image/png"
    )

# Button for Agent Strategies flowchart
with open(f"{agent_path}.png", "rb") as file:
    st.download_button(
        label="Download Agent Strategies Flowchart",
        data=file,
        file_name="agent_strategies_flowchart.png",
        mime="image/png"
    )
