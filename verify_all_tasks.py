import sqlite3
import pandas as pd

def run_verification():
    conn = sqlite3.connect('stock_market.db')
    cursor = conn.cursor()

    print("=================== TASK 1 ===================")
    df1 = pd.read_sql("""
    SELECT COUNT(*) AS trading_days, MIN(date) AS first_day, MAX(date) AS last_day FROM bajaj_auto;
    """, conn)
    print(df1)

    print("\n=================== TASK 2 ===================")
    df2 = pd.read_sql("""
    SELECT date, close_price FROM eicher_motors ORDER BY close_price DESC LIMIT 5;
    """, conn)
    print(df2)

    print("\n=================== TASK 3 ===================")
    df3 = pd.read_sql("""
    SELECT strftime('%Y', date) AS year, ROUND(AVG(close_price), 2) AS avg_close 
    FROM tcs 
    GROUP BY year 
    ORDER BY year;
    """, conn)
    print(df3)

    print("\n=================== TASK 4 ===================")
    df4 = pd.read_sql("""
    SELECT 'bajaj_auto' AS stock, date FROM bajaj_auto WHERE deliverable_qty IS NULL
    UNION ALL
    SELECT 'eicher_motors' AS stock, date FROM eicher_motors WHERE deliverable_qty IS NULL
    UNION ALL
    SELECT 'hero_motocorp' AS stock, date FROM hero_motocorp WHERE deliverable_qty IS NULL
    UNION ALL
    SELECT 'infosys' AS stock, date FROM infosys WHERE deliverable_qty IS NULL
    UNION ALL
    SELECT 'tcs' AS stock, date FROM tcs WHERE deliverable_qty IS NULL
    UNION ALL
    SELECT 'tvs_motors' AS stock, date FROM tvs_motors WHERE deliverable_qty IS NULL;
    """, conn)
    print(df4)

    print("\n=================== TASK 5 ===================")
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
    conn.commit()
    print("First non-null ma20:")
    print(pd.read_sql("SELECT * FROM bajaj1 WHERE ma20 IS NOT NULL ORDER BY date LIMIT 1;", conn))
    print("First non-null ma50:")
    print(pd.read_sql("SELECT * FROM bajaj1 WHERE ma50 IS NOT NULL ORDER BY date LIMIT 1;", conn))
    print("On 2018-07-31:")
    print(pd.read_sql("SELECT * FROM bajaj1 WHERE date = '2018-07-31';", conn))

    print("\n=================== TASK 6 ===================")
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
    conn.commit()
    print("Master Table check (Row count, columns, sample 2018-07-31):")
    print("Total rows:", pd.read_sql("SELECT COUNT(*) FROM master_table;", conn).iloc[0,0])
    print(pd.read_sql("SELECT * FROM master_table WHERE date = '2018-07-31';", conn))

    print("\n=================== TASK 7 ===================")
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
    conn.commit()
    print("First Buy signal:")
    print(pd.read_sql("SELECT * FROM bajaj2 WHERE signal = 'Buy' ORDER BY date LIMIT 1;", conn))
    print("First Sell signal:")
    print(pd.read_sql("SELECT * FROM bajaj2 WHERE signal = 'Sell' ORDER BY date LIMIT 1;", conn))

    print("\n=================== TASK 8 ===================")
    df8 = pd.read_sql("""
    SELECT signal, COUNT(*) AS count FROM bajaj2 GROUP BY signal ORDER BY signal;
    """, conn)
    print(df8)

    print("\n=================== TASK 9 ===================")
    df9 = pd.read_sql("""
    SELECT signal FROM bajaj2 WHERE date = '2018-06-21';
    """, conn)
    print(df9)

    print("\n=================== TASK 10 ===================")
    query_t10 = """
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
        CASE WHEN rn >= 20 THEN ma20_raw END AS ma20,
        CASE WHEN rn >= 50 THEN ma50_raw END AS ma50
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
    ),
    sig AS (
      SELECT
        stock,
        date,
        close_price,
        CASE
          WHEN ma20 IS NULL OR ma50 IS NULL OR prev_ma20 IS NULL OR prev_ma50 IS NULL THEN 'Hold'
          WHEN ma20 > ma50 AND prev_ma20 <= prev_ma50 THEN 'Buy'
          WHEN ma20 < ma50 AND prev_ma20 >= prev_ma50 THEN 'Sell'
          ELSE 'Hold'
        END AS signal
      FROM lagged
    ),
    latest AS (
      SELECT
        stock,
        date AS last_signal_date,
        signal AS last_signal,
        ROW_NUMBER() OVER (PARTITION BY stock ORDER BY date DESC) AS rank
      FROM sig
      WHERE signal != 'Hold'
    )
    SELECT
      s.stock,
      SUM(CASE WHEN s.signal = 'Buy' THEN 1 ELSE 0 END) AS buys,
      SUM(CASE WHEN s.signal = 'Sell' THEN 1 ELSE 0 END) AS sells,
      l.last_signal_date,
      l.last_signal
    FROM sig s
    JOIN latest l ON s.stock = l.stock AND l.rank = 1
    GROUP BY s.stock
    ORDER BY s.stock;
    """
    df10 = pd.read_sql(query_t10, conn)
    print(df10)
    print("Total buys across stocks:", df10['buys'].sum())
    print("Total sells across stocks:", df10['sells'].sum())

    print("\n=================== TASK 11 ===================")
    query_t11 = """
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
    ends AS (
      SELECT stock, MIN(date) AS min_date, MAX(date) AS max_date
      FROM prices
      GROUP BY stock
    )
    SELECT 
      e.stock,
      p1.close_price AS first_close,
      p2.close_price AS last_close,
      ROUND(((p2.close_price - p1.close_price) / p1.close_price) * 100.0, 1) AS pct_change
    FROM ends e
    JOIN prices p1 ON e.stock = p1.stock AND e.min_date = p1.date
    JOIN prices p2 ON e.stock = p2.stock AND e.max_date = p2.date
    ORDER BY pct_change DESC;
    """
    df11 = pd.read_sql(query_t11, conn)
    print(df11)

    print("\n=================== TASK 12 ===================")
    query_t12 = """
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
    moves AS (
      SELECT 
        stock, 
        date, 
        close_price,
        ROUND(((close_price / LAG(close_price) OVER (PARTITION BY stock ORDER BY date)) - 1) * 100.0, 1) AS pct_move
      FROM prices
    ),
    ranked AS (
      SELECT 
        stock, 
        date, 
        close_price, 
        pct_move,
        ROW_NUMBER() OVER (PARTITION BY stock ORDER BY pct_move ASC) AS rn
      FROM moves
      WHERE pct_move IS NOT NULL
    )
    SELECT stock, date, close_price, pct_move
    FROM ranked
    WHERE rn = 1
    ORDER BY pct_move ASC;
    """
    df12 = pd.read_sql(query_t12, conn)
    print(df12)

    print("\n=================== TASK 13 ===================")
    query_t13 = """
    WITH adjusted AS (
        SELECT 'TCS' AS stock, date,
            CASE WHEN date < '2018-05-31' THEN close_price / 2.0 ELSE close_price END AS adj_close
        FROM tcs
        UNION ALL
        SELECT 'Infosys' AS stock, date,
            CASE WHEN date < '2015-06-15' THEN close_price / 2.0 ELSE close_price END AS adj_close
        FROM infosys
    ),
    summarized AS (
        SELECT stock,
            MAX(CASE WHEN date = '2015-01-01' THEN adj_close END) AS first_adj_close,
            MAX(CASE WHEN date = '2018-07-31' THEN adj_close END) AS last_adj_close
        FROM adjusted GROUP BY stock
    )
    SELECT stock, first_adj_close, last_adj_close,
        ROUND(100.0 * ((last_adj_close / first_adj_close) - 1.0), 1) AS adjusted_pct_change
    FROM summarized ORDER BY stock;
    """
    df13 = pd.read_sql(query_t13, conn)
    print(df13)
    conn.close()

if __name__ == '__main__':
    run_verification()
