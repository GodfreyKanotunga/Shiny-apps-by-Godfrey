# 🛒 Shopping Behavior Dashboard

**Godfrey M. Kanotunga** | MSc in Applied Data Science | Clarkson University

An interactive multi-page analytical dashboard built with **Shiny for Python**, enabling dynamic exploration of consumer behavior across 3,900 customer records.

---

## Live Demo

> Deploy via [shinyapps.io](https://www.shinyapps.io/)

---

## Dashboard Tabs

| Tab | Description |
|---|---|
| 📊 Overview | KPI cards + revenue by category + purchase frequency |
| 🛍️ Products | Top items, colors, category treemap, revenue by age group |
| 👥 Segments | Gender breakdown, age spend, subscription split |
| 💳 Discount & Payment | Discount/promo usage, payment methods |
| 🗺️ Geography | U.S. choropleth map + top revenue states |
| ⭐ Satisfaction | Review ratings by category, age group, loyalty |
| 📋 Data | Filterable, sortable raw data table |

---

## Sidebar Filters

All charts respond dynamically to four filters:
- **Season** — Spring / Summer / Fall / Winter
- **Gender** — Male / Female
- **Category** — Clothing / Footwear / Accessories / Outerwear
- **Subscription** — Yes / No

---

## Dataset

3,900 customer records with 18 features including age, gender, location, purchase amount, category, item, color, season, review rating, shipping type, payment method, discount status, and purchase frequency.

---

## Tech Stack

`Python` · `Shiny for Python` · `Plotly Express` · `pandas` · `shinywidgets`

---

## Project Structure

```
Shiny-apps-by-Godfrey/
├── app.py                          # Main dashboard application
├── data/
│   └── shopping_behavior_...xlsx  # Dataset
└── README.md
```

---

## Running Locally

```bash
pip install shiny shinywidgets plotly pandas openpyxl
shiny run app.py
```
