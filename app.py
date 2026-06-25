from shiny.express import ui, input, render
from shinywidgets import render_widget
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── Data ──────────────────────────────────────────────────────────────────────
df = pd.read_excel("data/shopping_behavior_Shinyapps-Godfrey.xlsx")

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

# ── Colour palette ────────────────────────────────────────────────────────────
BLUE   = "#1f4e79"
BLUES  = ["#1f4e79", "#2e75b6", "#4a90e2", "#74b3e8", "#a8d0f5", "#d0e8fb"]
ACCENT = "#e67e22"

# ── Layout config ────────────────────────────────────────────────────────────
CHART_H = 380
LAYOUT  = dict(
    plot_bgcolor="white",
    paper_bgcolor="white",
    font=dict(family="Segoe UI, Arial", size=12, color="#333"),
    margin=dict(l=50, r=20, t=40, b=60),
    legend=dict(bgcolor="rgba(0,0,0,0)", borderwidth=0),
)

def styled_fig(fig, height=CHART_H):
    fig.update_layout(**LAYOUT, height=height)
    fig._config = {"displayModeBar": False}
    return fig

# ── Filter helper ─────────────────────────────────────────────────────────────
def get_filtered():
    d = df.copy()
    if input.season()  != "All": d = d[d["Season"]              == input.season()]
    if input.gender()  != "All": d = d[d["Gender"]              == input.gender()]
    if input.cat()     != "All": d = d[d["Category"]            == input.cat()]
    if input.sub()     != "All": d = d[d["Subscription Status"] == input.sub()]
    return d

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE
# ═══════════════════════════════════════════════════════════════════════════════
ui.page_opts(title="🛒 Shopping Behavior Dashboard", fillable=True)

ui.tags.style("""
    .kpi-card  { text-align:center; padding:16px 8px; }
    .kpi-value { font-size:2rem; font-weight:700; color:#1f4e79; line-height:1.1; }
    .kpi-label { font-size:0.8rem; color:#666; text-transform:uppercase; letter-spacing:.05em; margin-top:4px; }
    .nav-tabs .nav-link.active { font-weight:600; color:#1f4e79 !important; }
""")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with ui.sidebar(open="open", width=220):
    ui.h5("Filters", style="color:#1f4e79; margin-bottom:12px;")
    ui.input_select("season", "Season",
                    ["All"] + sorted(df["Season"].dropna().unique()))
    ui.input_select("gender", "Gender",
                    ["All"] + sorted(df["Gender"].dropna().unique()))
    ui.input_select("cat",    "Category",
                    ["All"] + sorted(df["Category"].dropna().unique()))
    ui.input_select("sub",    "Subscription",
                    ["All"] + sorted(df["Subscription Status"].dropna().unique()))
    ui.hr()
    ui.p("3,900 customer records across 18 features.",
         style="font-size:0.75rem; color:#999;")

# ── Tabs ──────────────────────────────────────────────────────────────────────
with ui.navset_tab():

    # ── 1. Overview ───────────────────────────────────────────────────────────
    with ui.nav_panel("📊 Overview"):

        with ui.layout_columns(col_widths=[2, 2, 2, 3, 3]):

            with ui.card():
                @render.ui
                def kpi_purchases():
                    n = len(get_filtered())
                    return ui.div(
                        ui.div(f"{n:,}",    class_="kpi-value"),
                        ui.div("Total Purchases", class_="kpi-label"),
                        class_="kpi-card")

            with ui.card():
                @render.ui
                def kpi_revenue():
                    d = get_filtered().dropna(subset=["Purchase Amount (USD)"])
                    v = d["Purchase Amount (USD)"].sum()
                    return ui.div(
                        ui.div(f"${v:,.0f}", class_="kpi-value"),
                        ui.div("Total Revenue", class_="kpi-label"),
                        class_="kpi-card")

            with ui.card():
                @render.ui
                def kpi_customers():
                    d = get_filtered().dropna(subset=["Customer ID"])
                    v = d["Customer ID"].nunique()
                    return ui.div(
                        ui.div(f"{v:,}", class_="kpi-value"),
                        ui.div("Unique Customers", class_="kpi-label"),
                        class_="kpi-card")

            with ui.card():
                @render.ui
                def kpi_rating():
                    d = get_filtered().dropna(subset=["Review Rating"])
                    v = d["Review Rating"].mean() if len(d) else 0
                    return ui.div(
                        ui.div(f"{v:.2f} / 5", class_="kpi-value"),
                        ui.div("Avg Review Rating", class_="kpi-label"),
                        class_="kpi-card")

            with ui.card():
                @render.ui
                def kpi_avg_spend():
                    d = get_filtered().dropna(subset=["Purchase Amount (USD)"])
                    v = d["Purchase Amount (USD)"].mean() if len(d) else 0
                    return ui.div(
                        ui.div(f"${v:.2f}", class_="kpi-value"),
                        ui.div("Avg Order Value", class_="kpi-label"),
                        class_="kpi-card")

        with ui.layout_columns(col_widths=[6, 6]):

            with ui.card(full_screen=True):
                ui.card_header("Revenue by Category")
                @render_widget
                def overview_cat_revenue():
                    d = get_filtered().dropna(subset=["Category","Purchase Amount (USD)"])
                    out = d.groupby("Category")["Purchase Amount (USD)"].sum().reset_index()
                    out = out.sort_values("Purchase Amount (USD)", ascending=False)
                    fig = px.bar(out, x="Category", y="Purchase Amount (USD)",
                                 text_auto=".2s",
                                 color_discrete_sequence=[BLUE])
                    fig.update_traces(textposition="outside")
                    fig.update_yaxes(title="Revenue (USD)", tickprefix="$")
                    fig.update_xaxes(title="")
                    return styled_fig(fig)

            with ui.card(full_screen=True):
                ui.card_header("Purchase Frequency Distribution")
                @render_widget
                def overview_freq():
                    d = get_filtered().dropna(subset=["Frequency of Purchases"])
                    order = ["Weekly","Bi-Weekly","Fortnightly","Monthly",
                             "Every 3 Months","Quarterly","Annually"]
                    out = d["Frequency of Purchases"].value_counts().reindex(order).reset_index()
                    out.columns = ["Frequency","Count"]
                    fig = px.bar(out, x="Frequency", y="Count",
                                 color_discrete_sequence=[BLUE])
                    fig.update_xaxes(title="Purchase Frequency")
                    fig.update_yaxes(title="Number of Customers")
                    return styled_fig(fig)

    # ── 2. Product Preference ─────────────────────────────────────────────────
    with ui.nav_panel("🛍️ Products"):

        with ui.layout_columns(col_widths=[6, 6]):

            with ui.card(full_screen=True):
                ui.card_header("Top 15 Items Purchased")
                @render_widget
                def items_plot():
                    d = get_filtered()
                    out = d["Item Purchased"].value_counts().head(15).reset_index()
                    out.columns = ["Item","Count"]
                    fig = px.bar(out, x="Count", y="Item", orientation="h",
                                 color_discrete_sequence=[BLUE])
                    fig.update_yaxes(autorange="reversed", title="")
                    fig.update_xaxes(title="Number of Purchases")
                    return styled_fig(fig)

            with ui.card(full_screen=True):
                ui.card_header("Top Colors Purchased")
                @render_widget
                def colors_plot():
                    d = get_filtered()
                    out = d["Color"].value_counts().reset_index()
                    out.columns = ["Color","Count"]
                    fig = px.bar(out, x="Count", y="Color", orientation="h",
                                 color_discrete_sequence=["#4a90e2"])
                    fig.update_yaxes(autorange="reversed", title="")
                    fig.update_xaxes(title="Number of Purchases")
                    return styled_fig(fig)

        with ui.layout_columns(col_widths=[6, 6]):

            with ui.card(full_screen=True):
                ui.card_header("Category Breakdown by Item")
                @render_widget
                def treemap():
                    d = get_filtered()
                    out = d.groupby(["Category","Item Purchased"]).size().reset_index(name="Count")
                    fig = px.treemap(out, path=["Category","Item Purchased"],
                                     values="Count", color="Count",
                                     color_continuous_scale="Blues")
                    fig.update_coloraxes(showscale=False)
                    fig.update_traces(textinfo="label+value")
                    return styled_fig(fig, height=420)

            with ui.card(full_screen=True):
                ui.card_header("Revenue by Age Group")
                @render_widget
                def age_purchase_line():
                    d = get_filtered().dropna(subset=["Age","Purchase Amount (USD)"])
                    d = d.copy()
                    d["Age Group"] = pd.cut(d["Age"],
                        bins=[0,20,30,40,50,60,100],
                        labels=["<20","20-29","30-39","40-49","50-59","60+"],
                        right=False)
                    out = d.groupby("Age Group", observed=True)["Purchase Amount (USD)"].sum().reset_index()
                    fig = px.line(out, x="Age Group", y="Purchase Amount (USD)",
                                  markers=True)
                    fig.update_traces(line_color=BLUE,
                                      marker=dict(color=ACCENT, size=9))
                    fig.update_yaxes(title="Total Revenue (USD)", tickprefix="$")
                    fig.update_xaxes(title="Age Group")
                    return styled_fig(fig, height=420)

    # ── 3. Customer Segments ──────────────────────────────────────────────────
    with ui.nav_panel("👥 Segments"):

        with ui.layout_columns(col_widths=[6, 6]):

            with ui.card(full_screen=True):
                ui.card_header("Category Preference by Gender")
                @render_widget
                def category_gender():
                    d = get_filtered().dropna(subset=["Gender","Category"])
                    out = d.groupby(["Gender","Category"]).size().reset_index(name="Count")
                    fig = px.bar(out, x="Category", y="Count", color="Gender",
                                 barmode="group",
                                 color_discrete_sequence=BLUES)
                    fig.update_xaxes(title="")
                    fig.update_yaxes(title="Number of Purchases")
                    return styled_fig(fig)

            with ui.card(full_screen=True):
                ui.card_header("Average Spend by Age Group")
                @render_widget
                def spending_age():
                    d = get_filtered().dropna(subset=["Age","Purchase Amount (USD)"]).copy()
                    d["Age Group"] = pd.cut(d["Age"],
                        bins=[0,20,30,40,50,60,100],
                        labels=["<20","20-29","30-39","40-49","50-59","60+"],
                        right=False)
                    out = d.groupby("Age Group", observed=True)["Purchase Amount (USD)"].mean().reset_index()
                    fig = px.bar(out, x="Age Group", y="Purchase Amount (USD)",
                                 color_discrete_sequence=[BLUE], text_auto=".2f")
                    fig.update_traces(textposition="outside", texttemplate="$%{text}")
                    fig.update_yaxes(title="Avg Spend (USD)", tickprefix="$")
                    fig.update_xaxes(title="Age Group")
                    return styled_fig(fig)

        with ui.layout_columns(col_widths=[6, 6]):

            with ui.card(full_screen=True):
                ui.card_header("Top Items by Age Group")
                @render_widget
                def top_items_age():
                    d = get_filtered().dropna(subset=["Age","Item Purchased"]).copy()
                    d["Age Group"] = pd.cut(d["Age"],
                        bins=[0,20,30,40,50,60,100],
                        labels=["<20","20-29","30-39","40-49","50-59","60+"],
                        right=False)
                    out = (d.groupby(["Age Group","Item Purchased"], observed=True)
                             .size().reset_index(name="Count")
                             .sort_values("Count", ascending=False).head(12))
                    fig = px.bar(out, x="Item Purchased", y="Count",
                                 color="Age Group",
                                 color_discrete_sequence=BLUES)
                    fig.update_xaxes(title="", tickangle=-30)
                    fig.update_yaxes(title="Purchases")
                    return styled_fig(fig)

            with ui.card(full_screen=True):
                ui.card_header("Subscription Status Split")
                @render_widget
                def sub_pie():
                    d = get_filtered().dropna(subset=["Subscription Status"])
                    out = d["Subscription Status"].value_counts().reset_index()
                    out.columns = ["Status","Count"]
                    fig = px.pie(out, names="Status", values="Count",
                                 color_discrete_sequence=[BLUE, "#a8d0f5"],
                                 hole=0.45)
                    fig.update_traces(textinfo="percent+label",
                                      textfont_size=13)
                    return styled_fig(fig)

    # ── 4. Discount & Payment ─────────────────────────────────────────────────
    with ui.nav_panel("💳 Discount & Payment"):

        with ui.layout_columns(col_widths=[4, 4, 4]):

            with ui.card(full_screen=True):
                ui.card_header("Discount vs No Discount")
                @render_widget
                def discount_impact():
                    d = get_filtered().dropna(subset=["Discount Applied"])
                    out = d["Discount Applied"].value_counts().reset_index()
                    out.columns = ["Discount","Count"]
                    fig = px.pie(out, names="Discount", values="Count",
                                 color_discrete_sequence=[BLUE, ACCENT],
                                 hole=0.45)
                    fig.update_traces(textinfo="percent+label")
                    return styled_fig(fig)

            with ui.card(full_screen=True):
                ui.card_header("Promo Code Usage")
                @render_widget
                def promo_usage():
                    d = get_filtered().dropna(subset=["Promo Code Used"])
                    out = d["Promo Code Used"].value_counts().reset_index()
                    out.columns = ["Promo","Count"]
                    fig = px.pie(out, names="Promo", values="Count",
                                 color_discrete_sequence=["#2e75b6", "#74b3e8"],
                                 hole=0.45)
                    fig.update_traces(textinfo="percent+label")
                    return styled_fig(fig)

            with ui.card(full_screen=True):
                ui.card_header("Payment Method Breakdown")
                @render_widget
                def payment_preferences():
                    d = get_filtered().dropna(subset=["Payment Method"])
                    out = d["Payment Method"].value_counts().reset_index()
                    out.columns = ["Method","Count"]
                    fig = px.bar(out, x="Count", y="Method", orientation="h",
                                 color_discrete_sequence=[BLUE])
                    fig.update_yaxes(autorange="reversed", title="")
                    fig.update_xaxes(title="Number of Transactions")
                    return styled_fig(fig)

        with ui.card(full_screen=True):
            ui.card_header("Discount Usage by Category & Gender")
            @render_widget
            def discount_by_category():
                d = get_filtered().dropna(subset=["Category","Discount Applied","Gender"])
                out = d.groupby(["Category","Discount Applied"]).size().reset_index(name="Count")
                fig = px.bar(out, x="Category", y="Count",
                             color="Discount Applied", barmode="group",
                             color_discrete_sequence=[BLUE, ACCENT])
                fig.update_xaxes(title="")
                fig.update_yaxes(title="Number of Purchases")
                return styled_fig(fig)

    # ── 5. Geo ────────────────────────────────────────────────────────────────
    with ui.nav_panel("🗺️ Geography"):

        with ui.layout_columns(col_widths=[8, 4]):

            with ui.card(full_screen=True):
                ui.card_header("Most Popular Shipping Type by U.S. State")
                @render_widget
                def shipping_map():
                    d = get_filtered().dropna(subset=["State_Abbrev","Shipping Type"])
                    grouped = (d.groupby(["Location","State_Abbrev","Shipping Type"])
                                .size().reset_index(name="Count"))
                    grouped = grouped.sort_values(["State_Abbrev","Count"],
                                                  ascending=[True,False])
                    top = grouped.drop_duplicates("State_Abbrev", keep="first")
                    fig = px.choropleth(
                        top, locations="State_Abbrev",
                        locationmode="USA-states",
                        color="Shipping Type",
                        hover_name="Location",
                        hover_data={"Shipping Type":True,"Count":True},
                        scope="usa",
                        color_discrete_sequence=BLUES
                    )
                    fig.update_layout(**LAYOUT, height=440,
                                      margin=dict(l=10,r=10,t=30,b=10))
                    fig._config = {"displayModeBar": False}
                    return fig

            with ui.card(full_screen=True):
                ui.card_header("Revenue by Top 10 States")
                @render_widget
                def state_revenue():
                    d = get_filtered().dropna(subset=["Location","Purchase Amount (USD)"])
                    out = d.groupby("Location")["Purchase Amount (USD)"].sum().reset_index()
                    out = out.sort_values("Purchase Amount (USD)", ascending=False).head(10)
                    fig = px.bar(out, x="Purchase Amount (USD)", y="Location",
                                 orientation="h",
                                 color_discrete_sequence=[BLUE])
                    fig.update_yaxes(autorange="reversed", title="")
                    fig.update_xaxes(title="Revenue (USD)", tickprefix="$")
                    return styled_fig(fig, height=440)

    # ── 6. Satisfaction ───────────────────────────────────────────────────────
    with ui.nav_panel("⭐ Satisfaction"):

        with ui.layout_columns(col_widths=[6, 6]):

            with ui.card(full_screen=True):
                ui.card_header("Avg Review Rating by Category")
                @render_widget
                def rating_by_category():
                    d = get_filtered().dropna(subset=["Category","Review Rating"])
                    out = d.groupby("Category")["Review Rating"].mean().reset_index()
                    out = out.sort_values("Review Rating", ascending=False)
                    fig = px.bar(out, x="Category", y="Review Rating",
                                 color_discrete_sequence=[BLUE],
                                 text_auto=".2f")
                    fig.update_yaxes(range=[0,5.5], title="Avg Rating")
                    fig.update_xaxes(title="")
                    fig.update_traces(textposition="outside")
                    fig.add_hline(y=out["Review Rating"].mean(),
                                  line_dash="dash", line_color=ACCENT,
                                  annotation_text="Overall Avg",
                                  annotation_position="top right")
                    return styled_fig(fig)

            with ui.card(full_screen=True):
                ui.card_header("Avg Review Rating by Age Group")
                @render_widget
                def rating_by_age():
                    d = get_filtered().dropna(subset=["Age","Review Rating"]).copy()
                    d["Age Group"] = pd.cut(d["Age"],
                        bins=[0,20,30,40,50,60,100],
                        labels=["<20","20-29","30-39","40-49","50-59","60+"],
                        right=False)
                    out = d.groupby("Age Group", observed=True)["Review Rating"].mean().reset_index()
                    fig = px.bar(out, x="Age Group", y="Review Rating",
                                 color_discrete_sequence=["#2e75b6"],
                                 text_auto=".2f")
                    fig.update_yaxes(range=[0,5.5], title="Avg Rating")
                    fig.update_xaxes(title="Age Group")
                    fig.update_traces(textposition="outside")
                    return styled_fig(fig)

        with ui.layout_columns(col_widths=[6, 6]):

            with ui.card(full_screen=True):
                ui.card_header("Review Rating vs Purchase History")
                @render_widget
                def rating_vs_loyalty():
                    d = get_filtered().dropna(subset=["Review Rating","Previous Purchases"])
                    fig = px.scatter(d, x="Previous Purchases", y="Review Rating",
                                     color="Category",
                                     color_discrete_sequence=BLUES,
                                     opacity=0.6,
                                     trendline="lowess")
                    fig.update_yaxes(range=[0,5.5], title="Review Rating")
                    fig.update_xaxes(title="Previous Purchases")
                    return styled_fig(fig)

            with ui.card(full_screen=True):
                ui.card_header("Rating Distribution")
                @render_widget
                def rating_hist():
                    d = get_filtered().dropna(subset=["Review Rating"])
                    fig = px.histogram(d, x="Review Rating", nbins=20,
                                       color_discrete_sequence=[BLUE])
                    fig.update_yaxes(title="Count")
                    fig.update_xaxes(title="Review Rating", range=[0,5])
                    return styled_fig(fig)

    # ── 7. Data Table ─────────────────────────────────────────────────────────
    with ui.nav_panel("📋 Data"):
        with ui.card(full_screen=True):
            ui.card_header("Filtered Dataset")
            ui.p("Use the sidebar filters to narrow the view. Click column headers to sort.",
                 style="color:#666; font-size:0.85rem; margin-bottom:8px;")
            @render.data_frame
            def data_table():
                d = get_filtered().drop(columns=["State_Abbrev"], errors="ignore")
                return render.DataGrid(d, filters=True, height="550px")
