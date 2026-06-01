-- Real Estate Market Analysis
-- Business KPI query examples. Adjust table and column names for a warehouse implementation.

SELECT * FROM sample_data LIMIT 20;

SELECT dimension_column, COUNT(*) AS records
FROM sample_data
GROUP BY dimension_column
ORDER BY records DESC;

SELECT dimension_column, SUM(metric_column) AS total_metric, AVG(metric_column) AS average_metric
FROM sample_data
GROUP BY dimension_column
ORDER BY total_metric DESC;

SELECT dimension_column, SUM(metric_column) AS total_metric, RANK() OVER (ORDER BY SUM(metric_column) DESC) AS metric_rank
FROM sample_data
GROUP BY dimension_column;
