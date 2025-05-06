import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def simulate_reinvest_all(stock_df, quarterly_contribution, years, top_n_stocks):
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
            if annual_div < target and symbol != 'SPAXX':
                yield_pct = data['dividend'] / data['share_price']
                under_target_stocks.append((symbol, yield_pct))
            else:
                tracking[symbol]['met_target'] = True

        prioritized = [x[0] for x in sorted(under_target_stocks, key=lambda x: x[1], reverse=True)[:top_n_stocks]]
        spaxx_contribution = quarterly_contribution * 4

        for symbol in tracking:
            data = tracking[symbol]
            annual_div = data['dividend'] * data['shares']
            reinvested_income = annual_div * data['reinvest_pct']
            data['shares'] += reinvested_income / data['share_price']

            if symbol == 'SPAXX':
                data['shares'] += spaxx_contribution / data['share_price']
            elif symbol in prioritized:
                per_stock_contribution = (quarterly_contribution * 4) / len(prioritized)
                data['shares'] += per_stock_contribution / data['share_price']

            target = data['target_income'] * ((1 + data['inflation']) ** (year - 1))
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

# Streamlit UI
st.title("Dividend Portfolio Simulator")

uploaded_file = st.file_uploader("Upload your portfolio CSV", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("### Uploaded Portfolio", df)

    investment_horizon = st.number_input("Investment Horizon (years)", value=25, min_value=1)
    quarterly_contribution = st.number_input("Quarterly Contribution ($)", value=250.0, min_value=0.0)
    top_n_stocks = st.number_input("Top N Stocks to Prioritize Each Year", value=5, min_value=1)

    if st.button("Run Simulation"):
        results = simulate_reinvest_all(df, quarterly_contribution, investment_horizon, top_n_stocks)

        total_income = results[results['Year'] == investment_horizon]['Actual Income'].sum()
        st.metric(label="Total Portfolio Income in Final Year", value=f"${total_income:,.2f}")

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

        st.subheader("📈 Total Portfolio Income by Year")
        income_by_year = results.groupby('Year')['Actual Income'].sum().reset_index()
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(income_by_year['Year'], income_by_year['Actual Income'], color='skyblue')
        ax.set_xlabel("Year")
        ax.set_ylabel("Total Income ($)")
        ax.set_title("Total Dividend Income by Year")
        ax.grid(True, linestyle='--', alpha=0.5)
        st.pyplot(fig)
