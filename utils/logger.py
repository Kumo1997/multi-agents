# logger.py

def save_memory(agent_name, memory, filename="data/agent_memory_log.txt"):
    with open(filename, "a") as f:
        f.write(f"Agent: {agent_name}\n")
        for action, result in memory:
            f.write(f"{action} -> {result}\n")
        f.write("\n")
