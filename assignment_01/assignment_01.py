import numpy as np
import mesa
import pandas as pd
import seaborn as sns
from mesa.discrete_space import CellAgent, OrthogonalMooreGrid, Network
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.cm import ScalarMappable



## defining an agent 
class Agent(CellAgent):
    def __init__(self, model, cell):
        super().__init__( model)
        self.opinion = np.random.random()
        self.property = np.random.uniform(0.1, 0.3)
        self.cell = cell
    
    def say_hi(self):
        print(f"Hello, I am agent {self.unique_id} with wealth {self.opinion} and property {self.property}")


    def exchange(self):
        if not self.cell.neighborhood.agents:
            return
        avg_opinion = sum([agent.opinion for agent in self.cell.neighborhood.agents]) / len(list(self.cell.neighborhood.agents))
    
        if abs(avg_opinion - self.opinion) > 0.1:
            new_opinion = self.opinion+ 0.5 * (avg_opinion - self.opinion)
            self.opinion = np.clip(new_opinion, 0, 1)


class opinionmodel(mesa.Model):
    def __init__(self, num_agents, avg_node_degree):
        super().__init__(seed = None)
        self.num_agents = num_agents
        p = avg_node_degree / num_agents

        self.g = nx.erdos_renyi_graph(n=num_agents, p=p)
        self.grid = Network(self.g, capacity=1, random = self.random)
        # print(self.grid.all_cells.cells)
        Agent.create_agents(self, num_agents, list(self.grid.all_cells.cells))

        self.datacollector = mesa.DataCollector(
            model_reporters={"mean_opinion": lambda m: np.mean([agent.opinion for agent in m.grid.agents])},
            agent_reporters={"opinion": "opinion"}  )


    def step(self):
        self.agents.shuffle_do("exchange")
        self.datacollector.collect(self)

    def draw_network(self, ax, step):
        g= self.g
        opinion = [agent.opinion for agent in self.grid.agents]
        if not hasattr(self, 'pos'):
            self.pos = nx.spring_layout(g, seed=42)
        
        nx.draw_networkx(
            g, 
            pos=self.pos, 
            ax=ax,
            with_labels=False,  # No labels for cleaner look
            node_size=50,       # Adjust size as needed
            node_color=opinion, # Color based on opinion value (0 to 1)
            cmap='viridis',     # Colormap to use (viridis is good for continuous data)
            edge_color='gray',
            linewidths=0.5,
            alpha=0.8
        )

        # 5. Add a colorbar and title
        sm = plt.cm.ScalarMappable(cmap='viridis', norm=plt.Normalize(vmin=0, vmax=1))
        sm._A = [] # necessary line for older matplotlib versions
        plt.colorbar(sm, ax=ax, orientation='vertical', label='Agent Opinion')
        ax.set_title(f"Network State at Step {step}")
        ax.axis('off') # Hide axes
        

                               
if __name__ == "__main__":
    # 2. Setup Figure
    fig, axes = plt.subplots(1, 2, figsize=(14, 7))

    # 3. Draw initial state (Step 0)
    
    model = opinionmodel(num_agents=10, avg_node_degree=10)
    model.draw_network(axes[0], step=0)
    for i in range(200):
        model.step()

    model.draw_network(axes[1], step=200)
    plt.tight_layout()
    plt.show()

    
    agent_data = model.datacollector.get_agent_vars_dataframe()
    mean_opinion = model.datacollector.get_model_vars_dataframe()

    print(mean_opinion)
    print(agent_data)

    



    
