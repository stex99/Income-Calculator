
# 📈 Dividend Income Target Simulator

This Streamlit app models dividend income growth over time, prioritizing investments in the highest-yielding stocks that have not yet reached their income goals. It stops reinvesting dividends once each stock meets its inflation-adjusted target income, helping you visualize a goal-based investment strategy.

---

## 🚀 Features

- Upload your own CSV file of dividend-paying stocks
- Specify investment horizon, quarterly contributions, and how many stocks to invest in per year
- Automatically prioritizes top-yielding, under-target investments
- Stops reinvestment after goal is met
- Shows:
  - Year-by-year portfolio income
  - Cumulative income vs. target charts
  - Target achievement summaries
- Export results to CSV

---

## 📊 Sample Input Format

```csv
Symbol,Starting Shares,Share Price,Dividend,Payout Frequency,Div Growth %,Price Growth %,Reinvest %,Target Income,Inflation %
OXLC,1000,5.00,0.90,M,2,3,100,2000,2
XFLT,500,7.50,0.72,Q,3,4,100,1500,2
NLY,400,15.00,1.20,Q,1,2,100,1200,2
```

---

## 💻 How to Run Locally

```bash
pip install streamlit pandas matplotlib
streamlit run streamlit_dividend_prioritized_stop_reinvest.py
```

---

## ☁️ Deploy on Streamlit Cloud

1. Push this repo to GitHub
2. Go to [streamlit.io/cloud](https://streamlit.io/cloud)
3. Click **New App**
4. Select your repo and set the app file to:
   ```
   streamlit_dividend_prioritized_stop_reinvest.py
   ```

---

## 📁 Included Files

- `streamlit_dividend_prioritized_stop_reinvest.py` – main app
- `requirements.txt` – dependencies for Streamlit Cloud
- `sample_input.csv` – ready-to-use example file

---

## 📬 Contact

Feel free to reach out for improvements or feature requests!

