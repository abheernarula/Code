import pandas as pd
import plotly.graph_objects as go
from dash import Dash, html, dcc  # ✅ new import style

# ------------------------------------------------------------------
# 1. Build your edge list
# edges = pd.DataFrame({
#     "src": ["Customers.CustomerID", "Sales.CustomerID",
#             "Inventory.ProductID", "Sales.ProductID"],
#     "tgt": ["Sales.CustomerID", "Invoicing.CustomerID",
#             "Sales.ProductID", "Analytics.ProductID"],
#     "wt":  [2, 1, 1, 2]
# })
# print(edges)

edges = pd.read_excel('lin.xlsx',sheet_name='cust')

# 2. Convert labels to integer IDs
labels = pd.Index(pd.concat([edges.src, edges.tgt]).unique())
edges["src_id"] = edges.src.map(labels.get_loc)
edges["tgt_id"] = edges.tgt.map(labels.get_loc)

# 3. Plotly Sankey figure
fig = go.Figure(data=[go.Sankey(
    node=dict(label=labels.tolist(), pad=20, thickness=15),
    link=dict(source=edges.src_id, target=edges.tgt_id, value=edges.wt)
)])

# ------------------------------------------------------------------
# 4. Dash app wrapper
app = Dash(__name__)
app.layout = html.Div([dcc.Graph(figure=fig, style={"height": "90vh"})])

if __name__ == "__main__":
    # Dash ≥2.0 uses .run()
    app.run(debug=True, port=8051)
