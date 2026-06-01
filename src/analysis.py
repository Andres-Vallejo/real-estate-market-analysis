from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "market_listings.csv"
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)


def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df["price_per_sqm"] = (df["price_usd"] / df["size_sqm"]).round(2)
    df["property_age"] = 2026 - df["year_built"]
    df["liquidity_segment"] = pd.cut(df["days_on_market"], bins=[0, 25, 45, 999], labels=["fast", "normal", "slow"])
    df["premium_listing"] = df["price_per_sqm"] >= df["price_per_sqm"].quantile(0.75)
    return df


def build_model(df: pd.DataFrame):
    features = ["neighborhood", "property_type", "bedrooms", "bathrooms", "size_sqm", "property_age", "parking", "transit_score", "condition_score"]
    X = df[features]
    y = df["price_usd"]
    categorical = ["neighborhood", "property_type"]
    numeric = [c for c in features if c not in categorical]
    preprocessor = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
        ("num", "passthrough", numeric),
    ])
    model = Pipeline([
        ("prep", preprocessor),
        ("model", RandomForestRegressor(n_estimators=250, random_state=42, min_samples_leaf=2)),
    ])
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    metrics = pd.DataFrame({
        "metric": ["mae_usd", "r2"],
        "value": [round(mean_absolute_error(y_test, preds), 2), round(r2_score(y_test, preds), 3)],
    })
    return model, metrics


def make_outputs(df: pd.DataFrame, model, metrics: pd.DataFrame) -> None:
    market = df.groupby("neighborhood").agg(
        listings=("listing_id", "count"),
        median_price=("price_usd", "median"),
        median_price_per_sqm=("price_per_sqm", "median"),
        median_days_on_market=("days_on_market", "median"),
        avg_transit_score=("transit_score", "mean"),
    ).round(2).reset_index().sort_values("median_price_per_sqm", ascending=False)
    market.to_csv(OUT / "neighborhood_scorecard.csv", index=False)
    metrics.to_csv(OUT / "model_metrics.csv", index=False)

    scored = df.copy()
    features = ["neighborhood", "property_type", "bedrooms", "bathrooms", "size_sqm", "property_age", "parking", "transit_score", "condition_score"]
    scored["predicted_price_usd"] = model.predict(scored[features]).round(0)
    scored["pricing_gap_pct"] = ((scored["price_usd"] - scored["predicted_price_usd"]) / scored["predicted_price_usd"] * 100).round(1)
    scored["pricing_signal"] = np.select(
        [scored["pricing_gap_pct"] > 8, scored["pricing_gap_pct"] < -8],
        ["overpriced", "undervalued"],
        default="fairly_priced",
    )
    scored.to_csv(OUT / "listing_price_signals.csv", index=False)

    plt.figure(figsize=(9, 5))
    sns.barplot(data=market, x="median_price_per_sqm", y="neighborhood", color="#2f6f9f")
    plt.title("Median price per sqm by neighborhood")
    plt.tight_layout()
    plt.savefig(OUT / "price_per_sqm_by_neighborhood.png", dpi=160)


def main() -> None:
    df = load_data()
    model, metrics = build_model(df)
    make_outputs(df, model, metrics)
    print("Premium real estate analysis complete.")
    print(metrics)


if __name__ == "__main__":
    main()
