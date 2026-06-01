-- Premium Real Estate Market Analysis
-- Assumed table: market_listings

-- 1. Neighborhood price scorecard
SELECT
  neighborhood,
  COUNT(*) AS listings,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price_usd) AS median_price,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price_usd / NULLIF(size_sqm, 0)) AS median_price_per_sqm,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY days_on_market) AS median_days_on_market
FROM market_listings
GROUP BY neighborhood
ORDER BY median_price_per_sqm DESC;

-- 2. Liquidity by property type
SELECT
  property_type,
  COUNT(*) AS listings,
  AVG(days_on_market) AS avg_days_on_market,
  SUM(CASE WHEN days_on_market <= 25 THEN 1 ELSE 0 END) * 1.0 / COUNT(*) AS fast_sale_rate
FROM market_listings
GROUP BY property_type;

-- 3. Potentially overpriced listings versus neighborhood benchmark
WITH benchmarks AS (
  SELECT neighborhood, AVG(price_usd / NULLIF(size_sqm, 0)) AS avg_price_per_sqm
  FROM market_listings
  GROUP BY neighborhood
)
SELECT
  l.listing_id,
  l.neighborhood,
  l.property_type,
  l.price_usd,
  l.price_usd / NULLIF(l.size_sqm, 0) AS price_per_sqm,
  b.avg_price_per_sqm,
  (l.price_usd / NULLIF(l.size_sqm, 0)) / b.avg_price_per_sqm - 1 AS premium_vs_neighborhood
FROM market_listings l
JOIN benchmarks b USING (neighborhood)
WHERE (l.price_usd / NULLIF(l.size_sqm, 0)) > b.avg_price_per_sqm * 1.12
ORDER BY premium_vs_neighborhood DESC;
