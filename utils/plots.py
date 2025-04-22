# plots.py

import matplotlib.pyplot as plt
import os

def plot_energy(energies, agent_names, save_path="data/energy_plot.png"):
    for agent, energy_list in zip(agent_names, energies):
        plt.plot(energy_list, label=agent)
    
    plt.xlabel("Days")
    plt.ylabel("Energy")
    plt.title("Agent Energy Over Time")
    plt.legend()

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path)
    print(f"✅ Energy plot saved to {save_path}")

    # Then display it
    plt.show()
