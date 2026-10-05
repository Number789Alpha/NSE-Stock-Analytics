import sqlite3
import pandas as pd

conn = sqlite3.connect('stock_market.db')

query_t13 = """
WITH adjusted AS (
  SELECT 
    'TCS' AS stock, 
    date,
    CASE WHEN date < '2018-05-31' THEN close_price / 2.0 ELSE close_price END AS adj_close
  FROM tcs
  UNION ALL
  SELECT 
    'Infosys' AS stock, 
    date,
    CASE WHEN date < '2015-06-15' THEN close_price / 2.0 ELSE close_price END AS adj_close
  FROM infosys
),
summarized AS (
  SELECT
    stock,
    MAX(CASE WHEN date = '2015-01-01' THEN adj_close END) AS first_adj_close,
    MAX(CASE WHEN date = '2018-07-31' THEN adj_close END) AS last_adj_close
  FROM adjusted
  GROUP BY stock
)
SELECT 
  stock,
  first_adj_close,
  last_adj_close,
  ROUND(100.0 * ((last_adj_close / first_adj_close) - 1.0), 1) AS adjusted_pct_change
FROM summarized
ORDER BY stock;
"""

df13 = pd.read_sql(query_t13, conn)
print("=== TASK 13 RESULTS ===")
print(df13)

# Stretch challenge: Rebuild TCS moving averages and signals on adjusted prices
query_tcs_adj_signals = """
WITH tcs_adj AS (
  SELECT 
    date,
    CASE WHEN date < '2018-05-31' THEN close_price / 2.0 ELSE close_price END AS adj_close
  FROM tcs
),
ma AS (
  SELECT
    date,
    adj_close,
    ROW_NUMBER() OVER (ORDER BY date) AS rn,
    AVG(adj_close) OVER (ORDER BY date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) AS ma20_raw,
    AVG(adj_close) OVER (ORDER BY date ROWS BETWEEN 49 PRECEDING AND CURRENT ROW) AS ma50_raw
  FROM tcs_adj
),
ma_guarded AS (
  SELECT
    date,
    adj_close,
    CASE WHEN rn >= 20 THEN ma20_raw END AS ma20,
    CASE WHEN rn >= 50 THEN ma50_raw END AS ma50
  FROM ma
),
lagged AS (
  SELECT
    date,
    adj_close,
    ma20,
    ma50,
    LAG(ma20) OVER (ORDER BY date) AS prev_ma20,
    LAG(ma50) OVER (ORDER BY date) AS prev_ma50
  FROM ma_guarded
),
sig AS (
  SELECT
    date,
    adj_close,
    CASE
      WHEN ma20 IS NULL OR ma50 IS NULL OR prev_ma20 IS NULL OR prev_ma50 IS NULL THEN 'Hold'
      WHEN ma20 > ma50 AND prev_ma20 <= prev_ma50 THEN 'Buy'
      WHEN ma20 < ma50 AND prev_ma20 >= prev_ma50 THEN 'Sell'
      ELSE 'Hold'
    END AS signal
  FROM lagged
)
SELECT signal, COUNT(*) AS count FROM sig GROUP BY signal ORDER BY signal;
"""
df_tcs_signals = pd.read_sql(query_tcs_adj_signals, conn)
print("\n=== TCS ADJUSTED SIGNALS ===")
print(df_tcs_signals)
