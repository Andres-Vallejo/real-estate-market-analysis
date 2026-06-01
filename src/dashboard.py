from pathlib import Path
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "market_listings.csv"

st.set_page_config(page_title="Real Estate Market Dashboard", layout="wide")
st.title("Real Estate Market Dashboard")

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    df["price_per_sqm"] = (df["price_usd"] / df["size_sqm"]).round(2)
    df["property_age"] = 2026 - df["year_built"]
    return df

df = load_data()
neighborhoods = st.multiselect("Neighborhood", sorted(df["neighborhood"].unique()), default=sorted(df["neighborhood"].unique()))
property_types = st.multiselect("Property type", sorted(df["property_type"].unique()), default=sorted(df["property_type"].unique()))
filtered = df[df["neighborhood"].isin(neighborhoods) & df["property_type"].isin(property_types)]

k1, k2, k3, k4 = st.columns(4)
k1.metric("Listings", len(filtered))
k2.metric("Median price", "$" + format(filtered['price_usd'].median(), ",.0f"))
k3.metric("Median $/sqm", "$" + format(filtered['price_per_sqm'].median(), ",.0f"))
k4.metric("Median days on market", format(filtered['days_on_market'].median(), ".0f"))

st.subheader("Neighborhood scorecard")
scorecard = filtered.groupby("neighborhood").agg(
    listings=("listing_id", "count"),
    median_price=("price_usd", "median"),
    median_price_per_sqm=("price_per_sqm", "median"),
    median_days_on_market=("days_on_market", "median"),
    avg_transit_score=("transit_score", "mean"),
).round(2).sort_values("median_price_per_sqm", ascending=False)
st.dataframe(scorecard, use_container_width=True)

st.subheader("Listings")
st.dataframe(filtered.sort_values("price_per_sqm", ascending=False), use_container_width=True)
