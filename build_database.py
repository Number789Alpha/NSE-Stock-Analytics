import sqlite3
import pandas as pd

def build_db():
    conn = sqlite3.connect('stock_market.db')
    cursor = conn.cursor()

    files = {
        'bajaj_auto': 'Bajaj Auto.csv',
        'eicher_motors': 'Eicher Motors.csv',
        'hero_motocorp': 'Hero Motocorp.csv',
        'infosys': 'Infosys.csv',
        'tcs': 'TCS.csv',
        'tvs_motors': 'TVS Motors.csv'
    }

    for table_name, file_name in files.items():
        df = pd.read_csv(file_name)
        df.columns = df.columns.str.strip()
        df.rename(columns={
            'Date': 'date',
            'Open Price': 'open_price',
            'High Price': 'high_price',
            'Low Price': 'low_price',
            'Close Price': 'close_price',
            'WAP': 'wap',
            'No.of Shares': 'no_of_shares',
            'No. of Trades': 'no_of_trades',
            'Total Turnover (Rs.)': 'total_turnover',
            'Deliverable Quantity': 'deliverable_qty',
            '% Deli. Qty to Traded Qty': 'pct_deli_qty',
            'Spread High-Low': 'spread_high_low',
            'Spread Close-Open': 'spread_close_open'
        }, inplace=True)
        
        df['date'] = pd.to_datetime(df['date'], format='%d-%B-%Y').dt.strftime('%Y-%m-%d')
        df.sort_values('date', ascending=True, inplace=True)
        df.to_sql(table_name, conn, if_exists='replace', index=False)

    print("Loaded 6 raw stock tables.")

    # Create bajaj1 (Task 5)
    cursor.execute("DROP TABLE IF EXISTS bajaj1;")
    cursor.execute("""
    CREATE TABLE bajaj1 AS
    SELECT
      date,
      close_price,
      CASE WHEN ROW_NUMBER() OVER (ORDER BY date) >= 20
           THEN ROUND(AVG(close_price) OVER (ORDER BY date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW), 2)
      END AS ma20,
      CASE WHEN ROW_NUMBER() OVER (ORDER BY date) >= 50
           THEN ROUND(AVG(close_price) OVER (ORDER BY date ROWS BETWEEN 49 PRECEDING AND CURRENT ROW), 2)
      END AS ma50
    FROM bajaj_auto;
    """)

    # Create master_table (Task 6)
    cursor.execute("DROP TABLE IF EXISTS master_table;")
    cursor.execute("""
    CREATE TABLE master_table AS
    SELECT 
      b.date,
      b.close_price AS bajaj,
      t.close_price AS tcs,
      tvs.close_price AS tvs,
      inf.close_price AS infosys,
      e.close_price AS eicher,
      h.close_price AS hero
    FROM bajaj_auto b
    JOIN tcs t ON b.date = t.date
    JOIN tvs_motors tvs ON b.date = tvs.date
    JOIN infosys inf ON b.date = inf.date
    JOIN eicher_motors e ON b.date = e.date
    JOIN hero_motocorp h ON b.date = h.date
    ORDER BY b.date;
    """)

    # Create bajaj2 (Task 7)
    cursor.execute("DROP TABLE IF EXISTS bajaj2;")
    cursor.execute("""
    CREATE TABLE bajaj2 AS
    WITH t AS (
      SELECT 
        date, 
        close_price, 
        ma20, 
        ma50,
        LAG(ma20) OVER (ORDER BY date) AS prev_ma20,
        LAG(ma50) OVER (ORDER BY date) AS prev_ma50
      FROM bajaj1
    )
    SELECT 
      date, 
      close_price,
      CASE
        WHEN ma20 IS NULL OR ma50 IS NULL OR prev_ma20 IS NULL OR prev_ma50 IS NULL THEN 'Hold'
        WHEN ma20 > ma50 AND prev_ma20 <= prev_ma50 THEN 'Buy'
        WHEN ma20 < ma50 AND prev_ma20 >= prev_ma50 THEN 'Sell'
        ELSE 'Hold'
      END AS signal
    FROM t;
    """)

    # Create signals_master view/table for all 6 stocks
    cursor.execute("DROP TABLE IF EXISTS signals_master;")
    cursor.execute("""
    CREATE TABLE signals_master AS
    WITH prices AS (
      SELECT 'Bajaj Auto' AS stock, date, close_price FROM bajaj_auto
      UNION ALL
      SELECT 'Eicher Motors' AS stock, date, close_price FROM eicher_motors
      UNION ALL
      SELECT 'Hero Motocorp' AS stock, date, close_price FROM hero_motocorp
      UNION ALL
      SELECT 'Infosys' AS stock, date, close_price FROM infosys
      UNION ALL
      SELECT 'TCS' AS stock, date, close_price FROM tcs
      UNION ALL
      SELECT 'TVS Motors' AS stock, date, close_price FROM tvs_motors
    ),
    ma AS (
      SELECT 
        stock,
        date,
        close_price,
        ROW_NUMBER() OVER (PARTITION BY stock ORDER BY date) AS rn,
        AVG(close_price) OVER (PARTITION BY stock ORDER BY date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) AS ma20_raw,
        AVG(close_price) OVER (PARTITION BY stock ORDER BY date ROWS BETWEEN 49 PRECEDING AND CURRENT ROW) AS ma50_raw
      FROM prices
    ),
    ma_guarded AS (
      SELECT
        stock,
        date,
        close_price,
        CASE WHEN rn >= 20 THEN ROUND(ma20_raw, 2) END AS ma20,
        CASE WHEN rn >= 50 THEN ROUND(ma50_raw, 2) END AS ma50
      FROM ma
    ),
    lagged AS (
      SELECT
        stock,
        date,
        close_price,
        ma20,
        ma50,
        LAG(ma20) OVER (PARTITION BY stock ORDER BY date) AS prev_ma20,
        LAG(ma50) OVER (PARTITION BY stock ORDER BY date) AS prev_ma50
      FROM ma_guarded
    )
    SELECT
      stock,
      date,
      close_price,
      ma20,
      ma50,
      CASE
        WHEN ma20 IS NULL OR ma50 IS NULL OR prev_ma20 IS NULL OR prev_ma50 IS NULL THEN 'Hold'
        WHEN ma20 > ma50 AND prev_ma20 <= prev_ma50 THEN 'Buy'
        WHEN ma20 < ma50 AND prev_ma20 >= prev_ma50 THEN 'Sell'
        ELSE 'Hold'
      END AS signal
    FROM lagged;
    """)

    # Create adjusted_prices table for TCS & Infosys + raw for others
    cursor.execute("DROP TABLE IF EXISTS adjusted_prices;")
    cursor.execute("""
    CREATE TABLE adjusted_prices AS
    SELECT 'Bajaj Auto' AS stock, date, close_price AS adj_close FROM bajaj_auto
    UNION ALL
    SELECT 'Eicher Motors' AS stock, date, close_price AS adj_close FROM eicher_motors
    UNION ALL
    SELECT 'Hero Motocorp' AS stock, date, close_price AS adj_close FROM hero_motocorp
    UNION ALL
    SELECT 'Infosys' AS stock, date, CASE WHEN date < '2015-06-15' THEN close_price / 2.0 ELSE close_price END AS adj_close FROM infosys
    UNION ALL
    SELECT 'TCS' AS stock, date, CASE WHEN date < '2018-05-31' THEN close_price / 2.0 ELSE close_price END AS adj_close FROM tcs
    UNION ALL
    SELECT 'TVS Motors' AS stock, date, close_price AS adj_close FROM tvs_motors;
    """)

    conn.commit()
    conn.close()
    print("Database built successfully!")

if __name__ == '__main__':
    build_db()
