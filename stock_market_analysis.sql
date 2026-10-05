-- ============================================================================
-- SQL STOCK MARKET ANALYSIS: MOVING AVERAGES, GOLDEN CROSS & CORPORATE ACTIONS
-- Target Database: SQLite 3.x / MySQL 8.0+
-- Six NSE Stocks Analyzed: Bajaj Auto, Eicher Motors, Hero Motocorp, Infosys, TCS, TVS Motors
-- Time Period: January 1, 2015 to July 31, 2018 (889 Trading Days)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- DDL SCHEMAS & INGESSION REFERENCE (MySQL 8.0+ / SQLite)
-- ----------------------------------------------------------------------------
-- Example Table Creation for MySQL:
/*
CREATE TABLE IF NOT EXISTS bajaj_auto (
    `date` DATE PRIMARY KEY,
    open_price DECIMAL(12,2),
    high_price DECIMAL(12,2),
    low_price DECIMAL(12,2),
    close_price DECIMAL(12,2),
    wap DECIMAL(16,4),
    no_of_shares BIGINT,
    no_of_trades BIGINT,
    total_turnover DECIMAL(20,2),
    deliverable_qty BIGINT,
    pct_deli_qty DECIMAL(6,2),
    spread_high_low DECIMAL(12,2),
    spread_close_open DECIMAL(12,2)
);
*/

-- ============================================================================
-- PART 1: GET TO KNOW THE DATA
-- ============================================================================

-- ----------------------------------------------------------------------------
-- TASK 1: How much history do we have?
-- Goal: Return total trading days, earliest date, and latest date in bajaj_auto.
-- Checkpoint: 889 trading days, 2015-01-01 to 2018-07-31.
-- ----------------------------------------------------------------------------
SELECT 
    COUNT(*) AS trading_days,
    MIN(date) AS first_day,
    MAX(date) AS last_day
FROM bajaj_auto;


-- ----------------------------------------------------------------------------
-- TASK 2: Eicher's five best closes
-- Goal: Return the date and close_price of Eicher Motors' 5 highest closing prices.
-- Checkpoint: 5 rows, top close > ₹32,000 (all 5 fall in Sept 2017).
-- ----------------------------------------------------------------------------
SELECT 
    date,
    close_price
FROM eicher_motors
ORDER BY close_price DESC
LIMIT 5;


-- ----------------------------------------------------------------------------
-- TASK 3: TCS, year by year
-- Goal: Return each year and TCS's average closing price, rounded to 2 decimals.
-- Checkpoint: 4 rows (2015-2018). 2016 average is exactly 2419.00.
-- ----------------------------------------------------------------------------
SELECT 
    strftime('%Y', date) AS year,
    ROUND(AVG(close_price), 2) AS avg_close
FROM tcs
GROUP BY year
ORDER BY year;


-- ----------------------------------------------------------------------------
-- TASK 4: Find the holes (Null deliverable_qty Audit)
-- Goal: Find all rows across all 6 stocks where deliverable_qty is NULL.
-- Checkpoint: 6 rows in total (1 per stock), falling on 2 distinct dates.
-- ----------------------------------------------------------------------------
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


-- ============================================================================
-- PART 2: THE ASSIGNMENT & CORE CALCULATIONS
-- ============================================================================

-- ----------------------------------------------------------------------------
-- TASK 5: Moving averages for Bajaj Auto
-- Goal: Create table bajaj1 with date, close_price, 20-day MA (ma20), 50-day MA (ma50).
-- Guard partial window days with NULL using ROW_NUMBER().
-- Checkpoint: 889 rows, 4 columns. First ma20 non-null on 2015-01-29 (2415.53),
-- first ma50 non-null on 2015-03-13 (2283.80). On 2018-07-31, ma20 is 2918.51.
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS bajaj1;
CREATE TABLE bajaj1 AS
SELECT
    date,
    close_price,
    CASE 
        WHEN ROW_NUMBER() OVER (ORDER BY date) >= 20
        THEN ROUND(AVG(close_price) OVER (ORDER BY date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW), 2)
    END AS ma20,
    CASE 
        WHEN ROW_NUMBER() OVER (ORDER BY date) >= 50
        THEN ROUND(AVG(close_price) OVER (ORDER BY date ROWS BETWEEN 49 PRECEDING AND CURRENT ROW), 2)
    END AS ma50
FROM bajaj_auto;

-- Verification for Task 5
SELECT * FROM bajaj1 ORDER BY date LIMIT 10;


-- ----------------------------------------------------------------------------
-- TASK 6: Master table (Closing prices merged)
-- Goal: Create master_table with date, bajaj, tcs, tvs, infosys, eicher, hero.
-- Checkpoint: 889 rows, 7 columns. On 2018-07-31: bajaj 2700.70, tvs 517.45.
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS master_table;
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

-- Verification for Task 6
SELECT * FROM master_table WHERE date = '2018-07-31';


-- ----------------------------------------------------------------------------
-- TASK 7: Golden Cross signals for Bajaj Auto
-- Goal: Create table bajaj2 with date, close_price, signal (Buy, Sell, Hold).
-- Crossover logic:
-- Buy: ma20 crosses above ma50 (ma20 > ma50 AND prev_ma20 <= prev_ma50)
-- Sell: ma20 crosses below ma50 (ma20 < ma50 AND prev_ma20 >= prev_ma50)
-- Checkpoint: First Buy on 2015-05-18, first Sell on 2015-08-24.
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS bajaj2;
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

-- Verification for Task 7
SELECT * FROM bajaj2 WHERE signal IN ('Buy', 'Sell') ORDER BY date LIMIT 10;


-- ----------------------------------------------------------------------------
-- TASK 8: How often did it trigger? (Bajaj Auto Signal Distribution)
-- Goal: Group bajaj2 by signal and count occurrences.
-- Checkpoint: 3 rows (Buy: 12, Hold: 866, Sell: 11). Total = 889.
-- ----------------------------------------------------------------------------
SELECT 
    signal,
    COUNT(*) AS count
FROM bajaj2
GROUP BY signal
ORDER BY signal;


-- ----------------------------------------------------------------------------
-- TASK 9: Signal on a given day
-- Goal: Return the signal for 2018-06-21 from bajaj2.
-- Checkpoint: Returns 'Buy' for 2018-06-21.
-- ----------------------------------------------------------------------------
SELECT signal 
FROM bajaj2 
WHERE date = '2018-06-21';


-- ----------------------------------------------------------------------------
-- TASK 10: All six stocks in one query (Consolidated Master Query)
-- Goal: Single CTE pipeline returning stock, buys, sells, last_signal_date, last_signal.
-- Partitioned by stock across all moving average and signal calculations.
-- Checkpoint: 6 rows, 5 columns. Total across stocks: 56 Buys, 57 Sells.
-- ----------------------------------------------------------------------------
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


-- ============================================================================
-- PART 3: QUESTION THE RESULT & CORPORATE ACTION ADJUSTMENTS
-- ============================================================================

-- ----------------------------------------------------------------------------
-- TASK 11: Who went up? (Unadjusted Overall Performance)
-- Goal: Compare first and last trading day prices across all stocks.
-- Checkpoint: TVS Motors tops list at 86.9%. TCS (-23.8%) and Infosys (-30.9%)
-- show negative raw returns due to unadjusted corporate actions.
-- ----------------------------------------------------------------------------
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


-- ----------------------------------------------------------------------------
-- TASK 12: The Data Trap (Single Worst Daily Drop per Stock)
-- Goal: Find each stock's single worst percentage daily move.
-- Checkpoint: TCS (-50.4% on 2018-05-31) and Infosys (-49.9% on 2015-06-15)
-- reveal 1:1 bonus issues/splits where price halved overnight.
-- ----------------------------------------------------------------------------
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
SELECT 
    stock, 
    date, 
    close_price, 
    pct_move
FROM ranked
WHERE rn = 1
ORDER BY pct_move ASC;


-- ----------------------------------------------------------------------------
-- TASK 13: Fix it (Adjusted Performance Calculation)
-- Goal: Adjust TCS and Infosys for 1:1 bonus issues by dividing pre-event prices by 2.
-- Corporate Event Dates:
-- TCS: 2018-05-31 (prices before this date divided by 2)
-- Infosys: 2015-06-15 (prices before this date divided by 2)
-- Checkpoint: TCS adjusted change = +52.4%, Infosys adjusted change = +38.2%.
-- ----------------------------------------------------------------------------
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


-- ============================================================================
-- APPENDIX B: STORED FUNCTION FOR MYSQL (REFERENCE)
-- ============================================================================
/*
DELIMITER $$
CREATE FUNCTION bajaj_signal(d DATE)
RETURNS VARCHAR(4) DETERMINISTIC READS SQL DATA
BEGIN
    DECLARE s VARCHAR(4);
    SELECT signal INTO s FROM bajaj2 WHERE date = d;
    RETURN s;
END $$
DELIMITER ;

-- Example invocation:
-- SELECT bajaj_signal('2018-06-21'); -- Returns 'Buy'
*/
