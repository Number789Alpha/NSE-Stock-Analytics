# 📈 NSE Stock Market SQL Analysis Dashboard

[![Live Dashboard](https://img.shields.io/badge/Streamlit%20Cloud-Live%20App-FF4B4B?style=for-the-badge&logo=streamlit)](https://nse-stock-analytics-imhwvkroyqxn4z64e4hpva.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)](https://python.org)
[![SQLite](https://img.shields.io/badge/Database-SQLite%203-lightblue?logo=sqlite)](https://sqlite.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)

> 🚀 **Live Interactive Dashboard:** [https://nse-stock-analytics-imhwvkroyqxn4z64e4hpva.streamlit.app/](https://nse-stock-analytics-imhwvkroyqxn4z64e4hpva.streamlit.app/)

A comprehensive **SQL-driven stock market analysis project** covering **6 NSE blue-chip equities** over **889 trading days** (Jan 2015 – Jul 2018). Built with **SQLite**, **Python**, and **Streamlit**.

---

## 🏢 Stocks Covered

| Stock | Sector |
|---|---|
| Bajaj Auto | Automobile |
| TCS | Information Technology |
| TVS Motors | Automobile |
| Infosys | Information Technology |
| Eicher Motors | Automobile |
| Hero Motocorp | Automobile |

---

## 🔍 What This Project Does

### ✅ 18 SQL Questions — All Using CTEs & Window Functions

| # | Task |
|---|---|
| 1 | Trading history horizon (COUNT, MIN, MAX) |
| 2 | Peak closing prices (ORDER BY, LIMIT) |
| 3 | Year-by-year average close (GROUP BY, strftime) |
| 4 | **NULL audit** on `deliverable_qty` (UNION ALL across 6 tables) |
| 5 | **Moving averages** — 20-day (short) vs 50-day (long) with boundary guards |
| 6 | **Merged Master View** — 6-table INNER JOIN on date |
| 7 | **Golden Cross / Death Cross** signals using LAG() |
| 8 | Signal frequency distribution |
| 9 | Signal lookup on a specific date |
| 10 | All 6 stocks in one partitioned CTE pipeline |
| 11 | Unadjusted portfolio returns |
| 12 | **The Data Trap** — worst single-day price drops detected |
| 13 | **Corporate Action adjustment** — 1:1 bonus share correction (TCS & Infosys) |
| 14 | **Best BUY candidate** — composite signal strength ranking |
| 15 | **Best SELL candidate** — downside risk composite ranking |
| 16 | BUY stocks classification (composite score ≥ 50) |
| 17 | SELL stocks classification (composite score < 10) |
| 18 | HOLD stocks classification (composite score 10–49) |

---

## 🧠 Key SQL Concepts Used

- **Common Table Expressions (CTEs)** — chained multi-step pipelines
- **Window Functions** — `AVG() OVER`, `LAG()`, `ROW_NUMBER()`, `RANK()`
- **Multi-table INNER JOIN** — cross-stock master view on trading date
- **UNION ALL** — combining 6 stock tables for portfolio-wide queries
- **CASE expressions** — signal detection, bonus adjustment, score bucketing
- **Subqueries** — nested return calculations

---

## 📊 Dashboard Pages (Streamlit)

| Page | Description |
|---|---|
| 🏠 Executive Overview | Project summary, KPIs, key findings |
| 🔍 Data Quality & Null Audit | NULL detection across 5,334 records |
| 📈 Moving Averages & Signals | 20-day vs 50-day MA crossover charts |
| 🔀 Master View & Merge | 889×7 consolidated price matrix |
| 📊 Trend & Performance | Return benchmarking, trend direction |
| ⚠️ Data Trap & Corporate Actions | Bonus issue detection & adjustment |
| 💡 Buy & Sell Decisions | Claim–Evidence–Caveat framework |
| 💻 SQL Code & Live Sandbox | Run live SQL queries against the DB |
| 📑 Submission PDF & Report | Downloadable PDF + all 18 queries |

---

## 🔑 Key Findings

| Finding | Detail |
|---|---|
| NULL rows in `deliverable_qty` | 6 rows across 2 dates (exchange feed downtime) |
| Golden Cross signals (total) | 56 across all 6 stocks |
| Death Cross signals (total) | 57 across all 6 stocks |
| Master table size | 889 rows × 7 columns |
| TCS true return (adjusted) | **+52.4%** (after 1:1 bonus correction) |
| Infosys true return (adjusted) | **+38.2%** (after 1:1 bonus correction) |
| **🟢 BUY** | Bajaj Auto · Infosys |
| **🟡 HOLD** | Hero Motocorp · TCS |
| **🔴 SELL** | Eicher Motors · TVS Motors |

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| SQLite 3 / MySQL 8 | Database engine |
| Python 3.x | Data processing & scripting |
| Pandas | DataFrame operations |
| Streamlit | Interactive dashboard |
| Plotly | Charts & visualizations |
| ReportLab | PDF report generation |

---

## 🚀 Getting Started

```bash
# 1. Clone the repository
git clone https://github.com/Number789Alpha/NSE-Stock-Analytics.git
cd NSE-Stock-Analytics

# 2. Install dependencies
pip install streamlit pandas plotly reportlab

# 3. Build the SQLite database from CSVs
python build_database.py

# 4. Launch the dashboard
streamlit run app.py
```

Then open **http://localhost:8501** in your browser.

---

## 📥 Downloads Available (from Dashboard)

- 📄 `NSE_Stock_Market_SQL_Analysis_Report.pdf` — Full 18-question submission PDF
- 💾 `stock_market_analysis.sql` — Production SQL script (SQLite / MySQL compatible)
- 🔀 `master_table_consolidated.csv` — 889-day merged price matrix

---

## 📁 Project Structure

```
NSE-Stock-Analytics/
├── app.py                            # Streamlit dashboard (9 pages)
├── build_database.py                 # CSV → SQLite database builder
├── generate_pdf_report.py            # ReportLab PDF generator (18 questions)
├── stock_market_analysis.sql         # All 18 SQL queries (CTE + Window Functions)
├── verify_all_tasks.py               # Automated checkpoint verification
├── Bajaj Auto.csv                    # Raw NSE data
├── TCS.csv
├── TVS Motors.csv
├── Infosys.csv
├── Eicher Motors.csv
└── Hero Motocorp.csv
```

---

## 📜 License

MIT License — free to use for academic and educational purposes.
