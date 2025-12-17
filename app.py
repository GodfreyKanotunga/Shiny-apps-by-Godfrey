from shiny.express import ui, input, render
from shinywidgets import render_widget
import pandas as pd
import plotly.express as px

df = pd.read_excel("data/shopping_behavior_Shinyapps-Godfrey.xlsx")

palette_blue = ["#1f77b4", "#4a90e2", "#8ab4e0", "#c7ddf2"]

state_map = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
    "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID",
    "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
    "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN",
    "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE",
    "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ",
    "New Mexico": "NM", "New York": "NY", "North Carolina": "NC",
    "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR",
    "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT",
    "Vermont": "VT", "Virginia": "VA", "Washington": "WA",
    "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY"
}

df["State_Abbrev"] = df["Location"].map(state_map)
df = df.dropna(subset=["State_Abbrev"])

def get_filtered():
    d = df.copy()
    if input.season() != "All":
        d = d[d["Season"] == input.season()]
    if input.gender() != "All":
        d = d[d["Gender"] == input.gender()]
    if input.cat() != "All":
        d = d[d["Category"] == input.cat()]
    return d

ui.page_opts(title="Shopping Behavior Dashboard", fillable=True)

with ui.sidebar(open="open"):
    ui.input_select("season", "Season", ["All"] + sorted(df["Season"].dropna().unique()))
    ui.input_select("gender", "Gender", ["All"] + sorted(df["Gender"].dropna().unique()))
    ui.input_select("cat", "Category", ["All"] + sorted(df["Category"].dropna().unique()))

with ui.navset_tab():

    with ui.nav_panel("Overview"):
        with ui.layout_columns():
            with ui.card():
                ui.h3("Total Purchases")
                @render.text
                def total_purchases():
                    return f"{len(get_filtered()):,}"
            with ui.card():
                ui.h3("Total Revenue (USD)")
                @render.text
                def total_revenue():
                    d = get_filtered().dropna(subset=["Purchase Amount (USD)"])
                    total = d["Purchase Amount (USD)"].sum()
                    return f"${total:,.0f}"
            with ui.card():
                ui.h3("Unique Customers")
                @render.text
                def unique_customers():
                    d = get_filtered().dropna(subset=["Customer ID"])
                    return f"{d['Customer ID'].nunique():,}"
        with ui.layout_columns():
            with ui.card():
                ui.h3("Average Review Rating")
                @render.text
                def avg_rating():
                    d = get_filtered().dropna(subset=["Review Rating"])
                    avg = d["Review Rating"].mean() if len(d) else 0
                    return f"{avg:.2f} / 5"
            with ui.card():
                ui.h3("Categories Purchased")
                @render.text
                def num_categories():
                    d = get_filtered().dropna(subset=["Category"])
                    return f"{d['Category'].nunique():,}"

    with ui.nav_panel("Product Preference"):
        with ui.layout_columns():
            with ui.card():
                ui.h3("Top Items Purchased")
                @render_widget
                def items_plot():
                    d = get_filtered()
                    out = d["Item Purchased"].value_counts().reset_index()
                    out.columns = ["Item", "Count"]
                    fig = px.bar(out, x="Item", y="Count",
                                 height=300, color_discrete_sequence=palette_blue)
                    fig.update_yaxes(range=[0, 200], dtick=50)
                    fig.update_layout(plot_bgcolor="white", paper_bgcolor="white")
                    fig._config = {"displayModeBar": False}
                    return fig
            with ui.card():
                ui.h3("Top Colors Purchased")
                @render_widget
                def colors_plot():
                    d = get_filtered()
                    out = d.groupby("Color").size().reset_index(name="Count")
                    out = out.sort_values("Count", ascending=False)
                    fig = px.bar(out, x="Color", y="Count",
                                 height=300, color_discrete_sequence=palette_blue)
                    fig.update_yaxes(range=[0, 200], dtick=50)
                    fig.update_layout(plot_bgcolor="white", paper_bgcolor="white")
                    fig._config = {"displayModeBar": False}
                    return fig
        with ui.layout_columns():
            with ui.card():
                ui.h3("Category Breakdown by Item")
                @render_widget
                def treemap():
                    d = get_filtered()
                    out = d.groupby(["Category","Item Purchased"]).size().reset_index(name="Count")
                    out["Label"] = out["Item Purchased"] + "<br>" + out["Count"].astype(str)
                    fig = px.treemap(out, path=["Category","Label"], values="Count",
                                     height=600, color="Count",
                                     color_continuous_scale="Blues")
                    fig.update_coloraxes(showscale=False)
                    fig.update_layout(plot_bgcolor="white", paper_bgcolor="white")
                    fig._config = {"displayModeBar": False}
                    return fig
            with ui.card():
                ui.h3("Total Purchase Amount by Age Group")
                @render_widget
                def age_purchase_line():
                    d = get_filtered().dropna(subset=["Age","Purchase Amount (USD)"])
                    d["Age Group"] = pd.cut(
                        d["Age"],
                        bins=[0,20,30,40,50,60,100],
                        labels=["<20","20-29","30-39","40-49","50-59","60+"],
                        right=False)
                    age_totals = d.groupby("Age Group")["Purchase Amount (USD)"].sum().reset_index()
                    fig = px.line(age_totals, x="Age Group", y="Purchase Amount (USD)",
                                  markers=True, height=600)
                    fig.update_traces(line_color="#1f77b4",
                                      marker=dict(color="#1f77b4", size=8))
                    fig.update_layout(plot_bgcolor="white", paper_bgcolor="white")
                    fig._config = {"displayModeBar": False}
                    return fig

    with ui.nav_panel("Customer Segments"):
        with ui.layout_columns():
            with ui.card():
                ui.h3("Category Preference by Gender")
                @render_widget
                def category_gender():
                    d = get_filtered().dropna(subset=["Gender","Category"])
                    out = d.groupby(["Gender","Category"]).size().reset_index(name="Count")
                    fig = px.bar(out, x="Category", y="Count", color="Gender",
                                 barmode="group", height=350,
                                 color_discrete_sequence=palette_blue)
                    fig.update_layout(plot_bgcolor="white", paper_bgcolor="white")
                    fig._config = {"displayModeBar": False}
                    return fig
            with ui.card():
                ui.h3("Average Spending by Age Group")
                @render_widget
                def spending_age():
                    d = get_filtered().dropna(subset=["Age","Purchase Amount (USD)"])
                    d["Age Group"] = pd.cut(
                        d["Age"],
                        bins=[0,20,30,40,50,60,100],
                        labels=["<20","20-29","30-39","40-49","50-59","60+"],
                        right=False)
                    out = d.groupby("Age Group")["Purchase Amount (USD)"].mean().reset_index()
                    fig = px.bar(out, x="Age Group", y="Purchase Amount (USD)",
                                 height=350, color_discrete_sequence=["#1f77b4"])
                    fig.update_layout(plot_bgcolor="white", paper_bgcolor="white")
                    fig._config = {"displayModeBar": False}
                    return fig
        with ui.card():
            ui.h3("Top 10 Items Purchased by Age Group")
            @render_widget
            def top_items_age():
                d = get_filtered().dropna(subset=["Age","Item Purchased"])
                d["Age Group"] = pd.cut(
                    d["Age"],
                    bins=[0,20,30,40,50,60,100],
                    labels=["<20","20-29","30-39","40-49","50-59","60+"],
                    right=False)
                out = (d.groupby(["Age Group","Item Purchased"])
                         .size().reset_index(name="Count")
                         .sort_values("Count", ascending=False)
                         .head(10))
                fig = px.bar(out, x="Item Purchased", y="Count",
                             color="Age Group", height=400,
                             color_discrete_sequence=palette_blue)
                fig.update_layout(plot_bgcolor="white", paper_bgcolor="white")
                fig._config = {"displayModeBar": False}
                return fig

    with ui.nav_panel("Discount & Payment Insights"):
        with ui.layout_columns():
            with ui.card():
                ui.h3("Number of Purchases: Discount vs No Discount")
                @render_widget
                def discount_impact():
                    d = get_filtered().dropna(subset=["Discount Applied"])
                    status = d["Discount Applied"].replace(
                        {0:"No Discount",1:"Discount Applied",
                         "No":"No Discount","Yes":"Discount Applied",
                         "False":"No Discount","True":"Discount Applied"}
                    )
                    out = status.value_counts().reset_index()
                    out.columns=["Discount Status","Purchase Count"]
                    fig = px.bar(out, x="Discount Status", y="Purchase Count",
                                 height=350, color_discrete_sequence=["#1f77b4"])
                    fig.update_layout(plot_bgcolor="white", paper_bgcolor="white")
                    fig._config = {"displayModeBar": False}
                    return fig
            with ui.card():
                ui.h3("Payment Method Usage")
                @render_widget
                def payment_preferences():
                    d = get_filtered().dropna(subset=["Payment Method"])
                    out = d["Payment Method"].value_counts().reset_index()
                    out.columns=["Payment Method","Count"]
                    fig = px.bar(out, x="Payment Method", y="Count",
                                 height=350, color_discrete_sequence=["#1f77b4"])
                    fig.update_layout(plot_bgcolor="white", paper_bgcolor="white")
                    fig._config = {"displayModeBar": False}
                    return fig
        with ui.card():
            ui.h3("Discount Usage by Category")
            @render_widget
            def discount_by_category():
                d = get_filtered().dropna(subset=["Category","Discount Applied"])
                d["Discount Group"] = d["Discount Applied"].replace(
                    {0:"No Discount",1:"Discount Applied",
                     "No":"No Discount","Yes":"Discount Applied",
                     "False":"No Discount","True":"Discount Applied"}
                )
                out = d.groupby(["Category","Discount Group"]).size().reset_index(name="Count")
                fig = px.bar(out, x="Category", y="Count",
                             color="Discount Group", barmode="group",
                             height=400, color_discrete_sequence=palette_blue)
                fig.update_layout(plot_bgcolor="white", paper_bgcolor="white")
                fig._config = {"displayModeBar": False}
                return fig

    with ui.nav_panel("Shipping Type by Location"):
        with ui.card():
            ui.h3("Most Popular Shipping Type by U.S. State")
            @render_widget
            def shipping_map():
                d = get_filtered().dropna(subset=["State_Abbrev","Shipping Type"])
                grouped = d.groupby(["Location","State_Abbrev","Shipping Type"]).size().reset_index(name="Count")
                grouped = grouped.sort_values(["State_Abbrev","Count"], ascending=[True,False])
                top = grouped.drop_duplicates("State_Abbrev", keep="first")
                fig = px.choropleth(
                    top,
                    locations="State_Abbrev",
                    locationmode="USA-states",
                    color="Shipping Type",
                    hover_name="Location",
                    hover_data=["Shipping Type","Count"],
                    scope="usa",
                    height=600,
                    color_discrete_sequence=palette_blue
                )
                for _, row in top.iterrows():
                    fig.add_scattergeo(
                        locationmode="USA-states",
                        locations=[row["State_Abbrev"]],
                        text=row["State_Abbrev"],
                        mode="text",
                        textfont=dict(size=10, color="black"),
                        showlegend=False,
                        hoverinfo="skip"
                    )
                fig.update_layout(
                    paper_bgcolor="white",
                    plot_bgcolor="white",
                    margin=dict(l=20, r=20, t=20, b=20)
                )
                fig._config = {"displayModeBar": False}
                return fig

    with ui.nav_panel("Customer Satisfaction"):
        with ui.layout_columns():
            with ui.card():
                ui.h3("Average Review Rating by Category")
                @render_widget
                def rating_by_category():
                    d = get_filtered().dropna(subset=["Category","Review Rating"])
                    out = d.groupby("Category")["Review Rating"].mean().reset_index()
                    out = out.sort_values("Review Rating", ascending=False)
                    fig = px.bar(out, x="Category", y="Review Rating",
                                 height=350, color_discrete_sequence=["#1f77b4"])
                    fig.update_yaxes(range=[0,5])
                    fig.update_layout(plot_bgcolor="white", paper_bgcolor="white")
                    fig._config = {"displayModeBar": False}
                    return fig
            with ui.card():
                ui.h3("Average Review Rating by Age Group")
                @render_widget
                def rating_by_age():
                    d = get_filtered().dropna(subset=["Age","Review Rating"])
                    d["Age Group"] = pd.cut(
                        d["Age"],
                        bins=[0,20,30,40,50,60,100],
                        labels=["<20","20-29","30-39","40-49","50-59","60+"],
                        right=False)
                    out = d.groupby("Age Group")["Review Rating"].mean().reset_index()
                    fig = px.bar(out, x="Age Group", y="Review Rating",
                                 height=350, color_discrete_sequence=["#1f77b4"])
                    fig.update_yaxes(range=[0,5])
                    fig.update_layout(plot_bgcolor="white", paper_bgcolor="white")
                    fig._config = {"displayModeBar": False}
                    return fig
        with ui.card():
            ui.h3("Review Rating vs Previous Purchases")
            @render_widget
            def rating_vs_loyalty():
                d = get_filtered().dropna(subset=["Review Rating","Previous Purchases"])
                fig = px.scatter(
                    d,
                    x="Previous Purchases",
                    y="Review Rating",
                    height=400
                )
                fig.update_traces(marker=dict(color="#1f77b4", size=8))
                fig.update_yaxes(range=[0,5])
                fig.update_layout(plot_bgcolor="white", paper_bgcolor="white")
                fig._config = {"displayModeBar": False}
                return fig
