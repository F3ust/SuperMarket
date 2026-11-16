-- Open business_mart.sqlite from the successful run referenced by latest.json.

-- Monthly KPI: observed panel only, not complete store revenue or profit.
SELECT month, sales, baskets, households, aov,
       ROUND(sales_mom * 100, 2) AS sales_mom_percent
FROM monthly_kpis ORDER BY month;

-- Categories driving observed sales in the latest month.
SELECT department, sales
FROM department_monthly
WHERE month = (SELECT MAX(month) FROM department_monthly)
ORDER BY sales DESC;

-- CRM review queue: ranking, not estimated incremental treatment effect.
SELECT a.household_id, a.risk_score, a.recency, a.visits_90, a.sales_90,
       c.segment
FROM customer_risk_actions a
LEFT JOIN customer_segments c ON c.household_id = a.household_id
WHERE a.priority_top20 = 1
ORDER BY a.risk_score DESC;

-- Seven-day category-level panel receipts forecast, not replenishment quantity.
SELECT series, target_start, target_end, forecast,
       lower_heuristic, upper_heuristic
FROM forecast_next_7_days ORDER BY forecast DESC;

-- ABC identifies revenue concentration; no costs or margin implied.
SELECT ABC, COUNT(*) AS products, SUM(sales) AS positive_sales
FROM product_abc GROUP BY ABC ORDER BY ABC;
