import networkx as nx
import matplotlib.pyplot as plt

G = nx.DiGraph()

for i in range(16):
    G.add_node(i)

G.add_edge(0, 3)
G.add_edge(1, 3)
G.add_edge(1, 4)
G.add_edge(1, 5)
G.add_edge(2, 5)
G.add_edge(2, 6)
G.add_edge(3, 7)
G.add_edge(4, 7)
G.add_edge(5, 7)
G.add_edge(6, 7)
G.add_edge(5, 8)
G.add_edge(7, 9)
G.add_edge(8, 9)
G.add_edge(7, 10)
G.add_edge(9, 12)
G.add_edge(9, 13)
G.add_edge(10, 13)
G.add_edge(12, 14)
G.add_edge(12, 15)
G.add_edge(13, 14)
G.add_edge(13, 15)
G.add_edge(13, 11)
G.add_edge(11, 8)
G.add_edge(11, 6)
G.add_edge(8, 7)

G_tmp = G.copy()
G_tmp.remove_node(11)

print(list(G.nodes))
print(list(G.edges))
print(list(nx.simple_cycles(G)))
for path in nx.all_simple_paths(G, source=0, target=15):
    print(path)


print(list(G_tmp.nodes))
print(list(G_tmp.edges))
print(list(nx.simple_cycles(G_tmp)))
for path in nx.all_simple_paths(G_tmp, source=0, target=15):
    print(path)