import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import yfinance as yf


def fetch_historical_data():
    try:
        # Using Yahoo Finance for Gold, S&P 500, and Bitcoin
        gold = yf.Ticker("GC=F")  # Gold futures ticker
        df_gold = gold.history(period="30y", interval="1mo").reset_index()
        if df_gold.empty:
            st.error("Failed to fetch Gold data. Check API limits.")
        df_gold = df_gold.rename(columns={"Date": "date", "Close": "gold_price"})
        df_gold["date"] = df_gold["date"].dt.strftime("%Y-%m-%d")

        sp500 = yf.Ticker("^GSPC")
        df_sp500 = sp500.history(period="30y", interval="1mo").reset_index()
        if df_sp500.empty:
            st.error("Failed to fetch S&P 500 data. Check API limits.")
        df_sp500 = df_sp500.rename(columns={"Date": "date", "Close": "sp500_price"})
        df_sp500["date"] = df_sp500["date"].dt.strftime("%Y-%m-%d")

        # Using Yahoo Finance for Bitcoin
        bitcoin = yf.Ticker("BTC-USD")
        df_bitcoin = bitcoin.history(period="30y", interval="1mo").reset_index()
        if df_bitcoin.empty:
            st.error("Failed to fetch Bitcoin data. Check API limits.")
        df_bitcoin = df_bitcoin.rename(
            columns={"Date": "date", "Close": "bitcoin_price"}
        )
        df_bitcoin["date"] = df_bitcoin["date"].dt.strftime("%Y-%m-%d")

        # Merge all dataframes on date
        # Here doing an inner join to have atleast two assets of data to be compared
        df_merged = pd.merge(
            df_gold[["date", "gold_price"]],
            df_sp500[["date", "sp500_price"]],
            on="date",
            how="inner",
        )
        df_merged = pd.merge(
            df_merged, df_bitcoin[["date", "bitcoin_price"]], on="date", how="outer"
        )
        df_merged["bitcoin_price"] = (
            df_merged["bitcoin_price"].fillna(value=0).reset_index(drop=True)
        )  # Ensure no missing values remain

        return df_merged
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()


def main():
    st.set_page_config(
        page_title="Wealth Storage & Investment", page_icon="📈", layout="wide"
    )

    # Home navigation button
    if st.button("🏠 Home"):
        st.switch_page("Home.py")

    # Title and Introduction
    st.title("📈 Wealth Storage & Investment")
    st.subheader("Explore different ways to store and grow your wealth effectively!")

    st.markdown(
        """
        Understanding wealth storage is crucial for financial security and long-term growth. Here are the major categories of wealth storage:
        
        ### 🔹 Short-term Wealth Storage
        - **Cookie Jar**
          - Similar to keeping money in a checking account
        - **Savings Account**
          - Offers interest but may have withdrawal limitations
        - **Certificate of Deposit (Fixed Deposit)**
          - Higher interest rates but fixed lock-in periods
        - **Precious Metals**
          - Includes Gold or Silver as a hedge against inflation
        - **Government Bonds**
          - Secure investment backed by the government
        
        ### 🔹 Long-term Wealth Storage
        #### 🏠 **Real Estate**
        - Investing in rental properties, land, or commercial real estate
        - Can generate rental income or appreciate in value over time
        
        #### 📈 **Stock Market**
        - (i) **Mutual Funds**
          - Pooled investments managed by professionals
        - (ii) **Picking up Individual Stocks**
          - Direct investment in companies based on research
        
        #### 🌐 **Crypto Market**
        - Example: **Bitcoin**, Ethereum, and other digital assets
        - High volatility but potential for high returns
        """
    )

    # Investment Growth Overview
    st.header("📊 Investment Growth Visualization")
    st.markdown(
        "Understanding the historical returns of different asset classes is crucial in making informed financial decisions."
    )

    df = fetch_historical_data()
    if df.empty:
        st.warning(
            "No data retrieved. Please check your internet connection or API limits."
        )
        return

    # Dynamically determine the min and max years from data
    df["year"] = pd.to_datetime(df["date"]).dt.year
    min_year = df["year"].min()
    max_year = df["year"].max()

    # User selects the start and end years; Slider shows the last 10 year values as placeholder
    start_year, end_year = st.slider(
        "Select the Year Range:", min_year, max_year, (max_year - 10, max_year)
    )
    df_filtered = df[(df["year"] >= start_year) & (df["year"] <= end_year)]

    if df_filtered.empty:
        st.warning(
            "No data available for the selected range. Please choose a different time period."
        )
        return

    # Asset selection checkboxes
    st.subheader("Select Assets to Visualize")
    all_assets = st.checkbox("Select All", value=True)
    gold_selected = st.checkbox("Gold", value=True if all_assets else False)
    sp500_selected = st.checkbox("S&P 500", value=True if all_assets else False)
    bitcoin_selected = st.checkbox("Bitcoin", value=True if all_assets else False)

    # Create a multi-y-axis plot
    fig = go.Figure()

    if gold_selected:
        fig.add_trace(
            go.Scatter(
                x=df_filtered["date"],
                y=df_filtered["gold_price"],
                name="Gold",
                mode="lines",
                line=dict(color="gold"),
            )
        )
    if sp500_selected:
        fig.add_trace(
            go.Scatter(
                x=df_filtered["date"],
                y=df_filtered["sp500_price"],
                name="S&P 500",
                mode="lines",
                line=dict(color="blue"),
            )
        )
    if bitcoin_selected:
        fig.add_trace(
            go.Scatter(
                x=df_filtered["date"],
                y=df_filtered["bitcoin_price"],
                name="Bitcoin",
                mode="lines",
                line=dict(color="orange"),
            )
        )

    fig.update_layout(
        title="Investment Asset Growth Over Time",
        xaxis_title="Year",
        yaxis_title="Price",
        legend_title="Asset Class",
        template="plotly_white",
    )

    # Display chart
    st.plotly_chart(fig)

    # Calculate returns
    initial_values = df_filtered.iloc[0]
    final_values = df_filtered.iloc[-1]

    returns_data = {
        "Asset Class": [],
        "Amount in the Year (USD)": [],
        "Asset Percentage Increase (%)": [],
    }

    if gold_selected:
        returns_data["Asset Class"].append("Gold")
        returns_data["Amount in the Year (USD)"].append(
            f"{initial_values['gold_price']:.2f} → {final_values['gold_price']:.2f}"
        )
        returns_data["Asset Percentage Increase (%)"].append(
            f"{((final_values['gold_price'] - initial_values['gold_price']) / initial_values['gold_price']) * 100:.2f}%"
        )
    if sp500_selected:
        returns_data["Asset Class"].append("S&P 500")
        returns_data["Amount in the Year (USD)"].append(
            f"{initial_values['sp500_price']:.2f} → {final_values['sp500_price']:.2f}"
        )
        returns_data["Asset Percentage Increase (%)"].append(
            f"{((final_values['sp500_price'] - initial_values['sp500_price']) / initial_values['sp500_price']) * 100:.2f}%"
        )
    if bitcoin_selected:
        returns_data["Asset Class"].append("Bitcoin")
        returns_data["Amount in the Year (USD)"].append(
            f"{initial_values['bitcoin_price']:.2f} → {final_values['bitcoin_price']:.2f}"
        )
        returns_data["Asset Percentage Increase (%)"].append(
            f"{((final_values['bitcoin_price'] - initial_values['bitcoin_price']) / initial_values['bitcoin_price']) * 100:.2f}%"
        )

    df_returns = pd.DataFrame(returns_data)

    # Display table
    st.subheader("📋 Investment Summary")
    st.table(df_returns)


if __name__ == "__main__":
    main()
