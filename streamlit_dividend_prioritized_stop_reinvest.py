
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# App config
st.set_page_config(page_title="Dividend Target Simulator", layout="wide")
st.title("🎯 Dividend Income Target Simulator")

# Sidebar inputs
st.sidebar.header("Simulation Settings")
investment_horizon = st.sidebar.number_input("Investment Horizon (Years)", min_value=1, max_value=100, value=25)
quarterly_contribution = st.sidebar.number_input("Quarterly Contribution ($)", min_value=0, step=50, value=250)
top_n_stocks = st.sidebar.number_input("Max Stocks to Invest In Per Year", min_value=1, max_value=20, value=5)

uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])

# Only proceed if a file is uploaded
if uploaded_file:
    df = pd.read_csv(uploaded_file)

    def simulate_prioritized_investment_stop_reinvest(stock_df, quarterly_contribution, years, top_n_stocks):
        tracking = {}
        for _, row in stock_df.iterrows():
            symbol = row['Symbol']
            tracking[symbol] = {
                "shares": row['Starting Shares'],
                "share_price": row['Share Price'],
                "dividend": row['Dividend'],
                "div_growth": row['Div Growth %'] / 100,
                "price_growth": row['Price Growth %'] / 100,
                "reinvest_pct": row['Reinvest %'] / 100,
                "target_income": row['Target Income'],
                "inflation": row['Inflation %'] / 100,
                "payout_freq": row['Payout Frequency'].upper(),
                "met_target": False
            }

        records = []

        for year in range(1, years + 1):
            under_target_stocks = []
            for symbol, data in tracking.items():
                annual_div = data['dividend'] * data['shares']
                target = data['target_income'] * ((1 + data['inflation']) ** (year - 1))
                if annual_div < target:
                    yield_pct = data['dividend'] / data['share_price']
                    under_target_stocks.append((symbol, yield_pct))
                else:
                    tracking[symbol]["met_target"] = True

            prioritized = [x[0] for x in sorted(under_target_stocks, key=lambda x: x[1], reverse=True)[:top_n_stocks]]
            per_stock_contribution = (quarterly_contribution * 4) / len(prioritized) if prioritized else 0

            for symbol in tracking:
                data = tracking[symbol]
                annual_div = data['dividend'] * data['shares']
                target = data['target_income'] * ((1 + data['inflation']) ** (year - 1))
                reinvested_income = 0

                if symbol in prioritized:
            reinvested_income = annual_div * data['reinvest_pct']
            data['shares'] += reinvested_income / data['share_price']
                    data['shares'] += reinvested_income / data['share_price']
                    new_shares = per_stock_contribution / data['share_price']
                    data['shares'] += new_shares

                records.append({
                    'Year': year,
                    'Symbol': symbol,
                    'Shares': round(data['shares'], 2),
                    'Price': round(data['share_price'], 2),
                    'Dividend/Share': round(data['dividend'], 2),
                    'Annual Dividend': round(data['dividend'] * data['shares'], 2),
                    'Reinvested Income': round(reinvested_income, 2),
                    'Actual Income': round(data['dividend'] * data['shares'], 2),
                    'Inflation-Adj Target': round(target, 2),
                    'Met Target?': data['dividend'] * data['shares'] >= target
                })

                data['dividend'] *= (1 + data['div_growth'])
                data['share_price'] *= (1 + data['price_growth'])

        return pd.DataFrame(records)

    # Run simulation
    results = simulate_prioritized_investment_stop_reinvest(df, quarterly_contribution, investment_horizon, top_n_stocks)
    results['Cumulative Income'] = results.groupby('Symbol')['Actual Income'].cumsum()
    results['Cumulative Target'] = results.groupby('Symbol')['Inflation-Adj Target'].cumsum()

    # Show table
    st.subheader("📊 Simulation Results")
    st.dataframe(results)

    # Summary
    st.subheader("📘 Target Achievement Summary")
    summary = (
        results[results["Met Target?"] == True]
        .groupby("Symbol")
        .agg(FirstYearMetTarget=("Year", "min"))
        .reset_index()
    )
    all_symbols = pd.DataFrame(results["Symbol"].unique(), columns=["Symbol"])
    summary_full = all_symbols.merge(summary, on="Symbol", how="left")
    summary_full["EverMetTarget"] = summary_full["FirstYearMetTarget"].notna()
    summary_full["FirstYearMetTarget"] = summary_full["FirstYearMetTarget"].fillna("Never")
    st.dataframe(summary_full)

    # Chart
    st.subheader("📈 Total Portfolio Income by Year")
    income_by_year = results.groupby('Year')['Actual Income'].sum().reset_index()
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(income_by_year['Year'], income_by_year['Actual Income'], color='skyblue')
    ax.set_xlabel("Year")
    ax.set_ylabel("Total Income ($)")
    ax.set_title("Total Dividend Income by Year")
    ax.grid(True, linestyle='--', alpha=0.5)
    st.pyplot(fig)

    # Download
    csv = results.to_csv(index=False).encode('utf-8')

    # Final Total Portfolio Income
    st.subheader("💰 Total Portfolio Income at Horizon")
    final_year = results['Year'].max()
    final_income = results[results['Year'] == final_year]['Actual Income'].sum()
    st.metric(label="Total Income in Final Year", value=f"${final_income:,.2f}")

    # Final Year Income Table
    # Final Year Value Table
    st.subheader("📋 Final Year Value by Stock")
    final_year_data = results[results['Year'] == investment_horizon]
    value_table = final_year_data[['Symbol', 'Shares', 'Price', 'Dividend/Share', 'Annual Dividend']].copy()
    value_table['Final Year Value'] = value_table['Shares'] * value_table['Price']
    value_table = value_table.rename(columns={
        'Dividend/Share': 'Dividend per Share',
        'Annual Dividend': 'Total Dividends'
    })
    value_table = value_table[['Symbol', 'Final Year Value', 'Shares', 'Price', 'Dividend per Share', 'Total Dividends']]
    value_table = value_table.sort_values(by='Final Year Value', ascending=False)
    st.dataframe(value_table)
    st.download_button("📥 Download Results CSV", data=csv, file_name="income_projection_results.csv", mime="text/csv")
else:
    st.info("Upload a CSV with your portfolio to begin.")
