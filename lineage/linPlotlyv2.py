# lineage_app.py
import pandas as pd
import plotly.graph_objects as go
from dash import Dash, html, dcc
import webbrowser
import threading

def get_group(label: str) -> str:
    """
    'Customer.SAP ECC.KNA1.Customer' --> 'Customer.SAP ECC'
    'Vendor.SAP ECC.LFA1.Vendor'     --> 'Vendor.SAP ECC'
    'Customer.Account.CurrencyIsoCode' --> 'Customer.Account'
    """
    parts = label.split(".", 2)          # split on the first two dots only
    return ".".join(parts[:2])           # join back the first two chunks

# ----------------------------------------------------------------------
# 1. Edge list (add / load your own)
# edges = pd.DataFrame({
#     "src": [
#         "Customers.CustomerID", "Vendors.VendorID",
#         "Materials.MaterialID", "Customers.CustomerID",
#         "Sales.CustomerID", "Sales.VendorID"
#     ],
#     "tgt": [
#         "Sales.CustomerID", "Purchasing.VendorID",
#         "Purchasing.MaterialID", "Analytics.CustomerID",
#         "Invoicing.CustomerID", "Analytics.VendorID"
#     ],
#     "wt": [1, 1, 1, 1, 1, 1]          # row-count / data-volume goes here
# })

edges = pd.read_excel('lin.xlsx', sheet_name='cust')

# 2. Group tags from table names (before first dot)
edges["src_group"] = edges["src"].str.split(".").str[0]
edges["tgt_group"] = edges["tgt"].str.split(".").str[0]

# Assuming you already have edges['src'] and edges['tgt']
# edges["src_group"] = edges["src"].apply(get_group)
# edges["tgt_group"] = edges["tgt"].apply(get_group)

# 3. Build node master list + colours
palette = {
    "Account": "#1f77b4",
    "SAP ECC":   "#2ca02c",
    "SAP MDG": "#ff7f0e",
    "Sales":     "#9467bd",
    "Purchasing":"#8c564b",
    "Analytics": "#d62728",
    "Invoicing": "#17becf"
}

# nodes = (pd.concat([
#             edges[["src","src_group"]].rename(columns={"src":"col","src_group":"group"}),
#             edges[["tgt","tgt_group"]].rename(columns={"tgt":"col","tgt_group":"group"})
#         ])
#         .drop_duplicates()
#         .reset_index(drop=True))

# nodes["id"]    = nodes.index
# nodes["color"] = nodes["group"].map(palette).fillna("#CCCCCC")

# # # Optional: lock each domain into its own vertical band
# # x_lookup = {g:i/(len(palette)-1) for i,g in enumerate(palette)}
# # nodes["x"] = nodes["group"].map(x_lookup)
# # nodes["y"] = nodes.groupby("group").cumcount()
# # nodes["y"] = nodes["y"] / nodes.groupby("group")["y"].transform("max")

# groups = list(palette)                           # preserve order
# x_lookup = {g: 0.05 + i * 0.9/(len(groups)-1)    # 0.05 to 0.95 instead of 0 to 1
#             for i, g in enumerate(groups)}
# nodes["x"] = nodes["group"].map(x_lookup)

# # Re-scale y safely (avoids 0 or 1 exactly)
# nodes["y"] = nodes.groupby("group").cumcount()
# nodes["y"] = nodes["y"] / nodes.groupby("group")["y"].transform("max")
# nodes["y"] = 0.02 + nodes["y"] * 0.96  

# # 4. Attach node IDs to edges
# edges = edges.merge(nodes[["col","id"]], left_on="src", right_on="col") \
#              .rename(columns={"id":"src_id"}).drop("col", axis=1)
# edges = edges.merge(nodes[["col","id"]], left_on="tgt", right_on="col") \
#              .rename(columns={"id":"tgt_id"}).drop("col", axis=1)

# # 5. Build Sankey figure
# fig = go.Figure(data=[go.Sankey(
#     arrangement="snap",                     # keeps nodes aligned
#     node=dict(
#         label     = nodes["col"].tolist(),
#         color     = nodes["color"].tolist(),
#         pad       = 20,
#         thickness = 14,
#         x         = nodes["x"].tolist(),
#         y         = nodes["y"].tolist()
#     ),
#     link=dict(
#         source = edges["src_id"].tolist(),
#         target = edges["tgt_id"].tolist(),
#         value  = edges["wt"].tolist(),
#         color  = "rgba(160,160,160,0.4)"
#     )
# )])

# fig.update_layout(
#     title="Column-Level Lineage (Grouped by Domain)",
#     font=dict(size=12),
#     height=800,
#     margin=dict(l=0,r=0,t=40,b=0)
# )

# # ----------------------------------------------------------------------
# # 6. Dash wrapper
# app = Dash(__name__)
# app.layout = html.Div(
#     children=[
#         dcc.Graph(figure=fig, style={"height": "95vh", "width": "100vw"})
#     ],
#     style={"padding": "0 10px"}
# )

# # Automatically open the browser (optional)
# def open_browser():
#     webbrowser.open_new("http://127.0.0.1:8051/")

# if __name__ == "__main__":
#     threading.Timer(1.0, open_browser).start()          # pop browser after server starts
#     app.run(debug=False, host="127.0.0.1", port=8051)

nodes = (pd.concat([
            edges[["src","src_group"]].rename(columns={"src":"col","src_group":"group"}),
            edges[["tgt","tgt_group"]].rename(columns={"tgt":"col","tgt_group":"group"})
        ])
        .drop_duplicates()
        .reset_index(drop=True))

nodes["id"]    = nodes.index
nodes["color"] = nodes["group"].map(palette).fillna("#CCCCCC")

# Optional: lock each domain into its own vertical band
x_lookup = {g:i/(len(palette)-1) for i,g in enumerate(palette)}
nodes["x"] = nodes["group"].map(x_lookup)
nodes["y"] = nodes.groupby("group").cumcount()
nodes["y"] = nodes["y"] / nodes.groupby("group")["y"].transform("max")

# 4. Attach node IDs to edges
edges = edges.merge(nodes[["col","id"]], left_on="src", right_on="col") \
             .rename(columns={"id":"src_id"}).drop("col", axis=1)
edges = edges.merge(nodes[["col","id"]], left_on="tgt", right_on="col") \
             .rename(columns={"id":"tgt_id"}).drop("col", axis=1)

# 5. Build Sankey figure
fig = go.Figure(data=[go.Sankey(
    arrangement="snap",                     # keeps nodes aligned
    node=dict(
        label     = nodes["col"].tolist(),
        color     = nodes["color"].tolist(),
        pad       = 20,
        thickness = 14,
        x         = nodes["x"].tolist(),
        y         = nodes["y"].tolist()
    ),
    link=dict(
        source = edges["src_id"].tolist(),
        target = edges["tgt_id"].tolist(),
        value  = edges["wt"].tolist(),
        color  = "rgba(160,160,160,0.4)"
    )
)])

fig.update_layout(
    title="Column-Level Lineage (Grouped by Domain)",
    # font=dict(size=11),
    # height=1000,
    # margin=dict(l=0,r=0,t=40,b=0)
)

# ✂︎  (everything above unchanged)  ✂︎

# 6. Build Sankey figure  ───────────────────────────────────────────────────────
# fig = go.Figure(data=[go.Sankey(
#     # 👇  use fixed layout instead of snap
#     arrangement="fixed",
#     node=dict(
#         label     = nodes["col"].tolist(),
#         color     = nodes["color"].tolist(),
#         pad       = 20,
#         thickness = 14,
#         x         = nodes["x"].tolist(),   # 0, 0.5, 1  (three columns)
#         y         = nodes["y"].tolist()
#     ),
#     link=dict(
#         source = edges["src_id"].tolist(),
#         target = edges["tgt_id"].tolist(),
#         value  = edges["wt"].tolist(),
#         color  = "rgba(160,160,160,0.35)"
#     )
# )])
# fig.update_layout(
#     title="Column-Level Lineage (3 Fixed Columns)",
#     font=dict(size=12),
#     height=800,
#     margin=dict(l=10, r=10, t=40, b=10)
# )


# ----------------------------------------------------------------------
# 6. Dash wrapper
# app = Dash(__name__)
# app.layout = html.Div(
#     children=[
#         dcc.Graph(figure=fig, style={"height": "95vh", "width": "100vw"})
#     ],
#     style={"padding": "0 10px"}
# )

# # Automatically open the browser (optional)
# def open_browser():
#     webbrowser.open_new("http://127.0.0.1:8051/")

# if __name__ == "__main__":
#     threading.Timer(1.0, open_browser).start()          # pop browser after server starts
#     app.run(debug=False, host="127.0.0.1", port=8051)

app = Dash(__name__)
app.layout = html.Div([dcc.Graph(figure=fig, style={"height": "90vh"})])

if __name__ == "__main__":
    # Dash ≥2.0 uses .run()
    app.run(debug=True, port=8051)