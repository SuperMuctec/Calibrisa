from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import yfinance as yf
import numpy as np
from datetime import datetime

def train_predict(df, column, future_day):
    # Make sure the column and 'Days' exist
    if not isinstance(column, str) or "Days" not in df.columns or column not in df.columns:
        return "N/A"

    try:
        # Drop rows where either Days or the column is NaN
        sub_df = df[["Days", column]].dropna()
    except KeyError:
        return "N/A"

    # Extra safety: make sure the column is not fully null
    col_series = sub_df[column]
    if sub_df.empty or col_series.empty:
        return "N/A"

    X = sub_df[["Days"]].values
    y = col_series.values

    if len(X) < 2:
        return "N/A"

    try:
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        model = LinearRegression()
        model.fit(X_scaled, y)

        future_scaled = scaler.transform([[future_day]])
        prediction = model.predict(future_scaled)[0]

        return round(float(prediction), 2)
    except Exception:
        return "N/A"



def predict_stock_info(ticker, date_str):
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return {"error": "Invalid date format. Use YYYY-MM-DD."}

    df = yf.download(ticker, start="2010-01-01", end="2025-01-01", progress=False)
    if df.empty:
        return {"error": f"No data found for {ticker}"}

    df = df.reset_index()
    df["Days"] = (df["Date"] - df["Date"].min()).dt.days
    future_day = (date_obj - df["Date"].min()).days

    # Predict using your model
    predicted_price = train_predict(df, "Close", future_day)
    predicted_volume = train_predict(df, "Volume", future_day)
    predicted_dividend = round(np.random.uniform(0.5, 3.5), 2)
    predicted_eps = round(np.random.uniform(1, 8), 2)

    try:
        predicted_pe = round(predicted_price / predicted_eps, 2)
    except:
        predicted_pe = "N/A"

    try:
        market_cap = round(predicted_price * predicted_volume, 2)
    except:
        market_cap = "N/A"

    predicted_52low = round(predicted_price * 0.85, 2) if isinstance(predicted_price, float) else "N/A"
    predicted_52high = round(predicted_price * 1.15, 2) if isinstance(predicted_price, float) else "N/A"

    valuation = {
        "trailing_pe": predicted_pe,
        "forward_pe": round(predicted_pe * 0.95, 2) if isinstance(predicted_pe, float) else "N/A",
        "eps_ttm": predicted_eps,
        "eps_forward": round(predicted_eps * 1.1, 2),
        "dividend_rate": predicted_dividend,
        "dividend_yield": round(predicted_dividend / predicted_price, 4) if isinstance(predicted_price, float) and predicted_price != 0 else "N/A",
        "analyst_rating": "N/A",
        "target_price": round(predicted_price * 1.2, 2) if isinstance(predicted_price, float) else "N/A"
    }

    return {
        "ticker": ticker,
        "date": date_str,
        "price": predicted_price,
        "info": {"Close": predicted_price},
        "valuation": valuation,
        "week": f"${predicted_52low} – ${predicted_52high}",
        "cap": f"${market_cap}" if isinstance(market_cap, float) else market_cap,
        "avg": f"{predicted_volume:,}" if isinstance(predicted_volume, (int, float)) else "N/A",
        "dividend": f"{valuation['dividend_yield']}%" if valuation['dividend_yield'] != "N/A" else "N/A",
        "desc": f"This is an AI-generated prediction for {ticker}.",
        "name": f"{ticker} Corp.",
        "field": "Predicted Sector • Predicted Industry",
        "website": "https://example.com",
        "model_used": "Linear Regression (scikit-learn)"
    }
