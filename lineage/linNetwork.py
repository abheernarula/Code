import networkx as nx
from pyvis.network import Network

G = nx.DiGraph()
# Add lineage edges
G.add_edge("Customers.CustomerID", "Sales.CustomerID")
G.add_edge("Sales.CustomerID", "Invoicing.CustomerID")
G.add_edge("Inventory.ProductID", "Sales.ProductID")
G.add_edge("Sales.ProductID", "Analytics.ProductID")

# Visualise
net = Network(height="700px", width="100%", directed=True)
net.from_nx(G)
net.show("lineage.html", notebook=False)   # Opens in browser; embed in Streamlit/PowerBI
