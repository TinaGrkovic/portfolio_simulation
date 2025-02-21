import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import glob

# Load the dataset
df = pd.read_csv("clean_withSMP500_withForestFunds_Jan22.csv")

# Convert the 'Day' column to datetime
df['Day'] = pd.to_datetime(df['Day'])

# Streamlit page configuration
st.set_page_config(page_title="Portfolio Performance Dashboard", layout="wide")

# Title
st.title("Portfolio Performance Simulation")

# Show the raw data
st.subheader("Portfolio Data Overview (Dec 9 - Jan 22)")
st.dataframe(df)

# Multi-select filter for portfolio columns
portfolio_columns = df.columns[1:]  # Exclude the date column
selected_portfolios = st.multiselect("Select portfolios to visualize", portfolio_columns, default=portfolio_columns)

# Prepare data for Plotly Express by melting the DataFrame
df_melted = df.melt(id_vars=['Day'], value_vars=selected_portfolios, var_name='Portfolio', value_name='Value')

# Create an interactive line plot using Plotly Express
fig = px.line(df_melted, x='Day', y='Value', color='Portfolio', 
              title="Portfolio Performance Over Time",
              labels={'Day': 'Date', 'Value': 'Portfolio Value', 'Portfolio': 'Portfolio'},
              markers=True)


# Customize the plot
fig.update_layout(hovermode="x unified", legend_title="Portfolio Names")

# Show the chart in Streamlit
st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------
# Additional Insights
# ----------------------------------------

# Calculate final values
final_values = df.iloc[-1, 1:]
initial_values = df.iloc[0, 1:]

# Portfolio rankings
best_performer = final_values.idxmax()
worst_performer = final_values.idxmin()
highest_growth = final_values.max() - initial_values[best_performer]
highest_loss = final_values.min() - initial_values[worst_performer]

# Calculate volatility (standard deviation of returns)
volatility = df[selected_portfolios].pct_change().std().sort_values(ascending=False)
most_volatile = volatility.idxmax()
least_volatile = volatility.idxmin()

# Show final rankings as a poll-style display with centered alignment and a box
st.subheader("Portfolio Rankings for now...")

# Sort portfolios from highest to lowest value
ranked_portfolios = final_values.sort_values(ascending=False)

# Define styling and emojis for top 3 ranks
medal_emojis = ["🥇", "🥈", "🥉"]
colors = ["#FFD700", "#C0C0C0", "#CD7F32"]  # Gold, Silver, Bronze colors

# Create HTML content for rankings
rankings_html = "<div style='text-align: center; border: 2px solid #ddd; padding: 20px; width: 50%; margin: auto; background-color: #f9f9f9; border-radius: 10px;'>"

for idx, (portfolio, value) in enumerate(ranked_portfolios.items(), start=1):
    portfolio_name = portfolio.title()
    formatted_value = f"${value:,.2f}"

    if idx <= 3:
        rankings_html += (
            f"<p style='font-size:28px; font-weight:bold; color:{colors[idx-1]}; margin: 10px 0;'>"
            f"{medal_emojis[idx-1]} {portfolio_name} - {formatted_value}</p>"
        )
    else:
        rankings_html += (
            f"<p style='font-size:22px; font-weight:bold; color:#333; margin: 5px 0;'>"
            f"{idx}. {portfolio_name} - {formatted_value}</p>"
        )

rankings_html += "</div>"

# Display rankings in Streamlit
st.markdown(rankings_html, unsafe_allow_html=True)

# Insights Display
st.markdown(f"""
- 🏆 **Best Performer:** {best_performer.title()} with a final value of **{final_values[best_performer]:,.2f}**, growing by **{highest_growth:,.2f}**.
- 📉 **Worst Performer:** {worst_performer.title()} with a final value of **{final_values[worst_performer]:,.2f}**, losing **{highest_loss:,.2f}**.
- 📊 **Most Volatile Portfolio:** {most_volatile.title()} with a standard deviation of **{volatility[most_volatile]:.2%}**.
- 🛡️ **Least Volatile Portfolio:** {least_volatile.title()} with a standard deviation of **{volatility[least_volatile]:.2%}**.
""")

# Show volatility chart
fig_volatility = px.bar(volatility, x=volatility.index, y=volatility.values,
                        title="Portfolio Volatility",
                        labels={'x': 'Portfolio', 'y': 'Volatility (Standard Deviation)'}
                        )
st.plotly_chart(fig_volatility)

###################################################################################

# Title
st.title("Portfolio Competition Insights")

# Most Popular Stocks Section
st.subheader("🏅 Most Popular Stocks Across Portfolios")

popular_stocks = {
    "AAPL (Apple Inc.)": 5,
    "MSFT (Microsoft Corp.)": 4,
    "NVDA (NVIDIA Corp.)": 4,
    "TGT (Target Corp.)": 3,
    "LLY (Eli Lilly & Co.)": 3
}

popular_df = pd.DataFrame(list(popular_stocks.items()), columns=["Stock", "Number of Portfolios"])
st.table(popular_df.style.set_properties(**{'text-align': 'left'}).set_table_styles(
    [{'selector': 'th', 'props': [('text-align', 'center')]}]
))

#######################

# Load the CSV file containing stock prices since the competition started
stock_prices = pd.read_csv("all_stock_prices_since_competition_start.csv")

# Calculate stock performance over the competition period
stock_prices.set_index("Date", inplace=True)
stock_performance = (stock_prices.iloc[-1] - stock_prices.iloc[0]) / stock_prices.iloc[0] * 100

# Identify top 5 best-performing stocks
best_performing_stocks = stock_performance.nlargest(5)
best_stocks_dict = best_performing_stocks.to_dict()

# Identify top 5 worst-performing stocks
worst_performing_stocks = stock_performance.nsmallest(5)
worst_stocks_dict = worst_performing_stocks.to_dict()

# Best Performing Stocks Section
st.subheader("🚀 Best Performing Stocks During Competition")

best_stocks_df = pd.DataFrame(
    list(best_stocks_dict.items()), 
    columns=["Stock", "Performance Change (%)"]
)

st.table(best_stocks_df.style.set_properties(**{'text-align': 'left'}).set_table_styles(
    [{'selector': 'th', 'props': [('text-align', 'center')]}]
))

# Worst Performing Stocks Section
st.subheader("📉 Worst Performing Stocks During Competition")

worst_stocks_df = pd.DataFrame(
    list(worst_stocks_dict.items()), 
    columns=["Stock", "Performance Change (%)"]
)

st.table(worst_stocks_df.style.set_properties(**{'text-align': 'left'}).set_table_styles(
    [{'selector': 'th', 'props': [('text-align', 'center')]}]
))

# Summary Section
st.subheader("🔍 Key Observations")
st.markdown(f"""
- **{best_stocks_df.iloc[0]['Stock']}** was the best-performing stock with a growth of **{best_stocks_df.iloc[0]['Performance Change (%)']:.2f}%**.
- **{worst_stocks_df.iloc[0]['Stock']}** faced the biggest losses with a decline of **{worst_stocks_df.iloc[0]['Performance Change (%)']:.2f}%**.
- **AAPL** and **MSFT** were the most popular stocks, appearing in multiple portfolios.
- **The recent U.S. elections, with Donald Trump being selected, have influenced market trends, particularly in sectors such as energy, defense, and financials.**
- **The holiday season likely contributed to fluctuations in consumer retail stocks, such as Target (TGT) and Amazon (AMZN), as spending patterns shifted.**
""")

# Footer
st.caption("Data collected from competition portfolios and analyzed using Yahoo Finance data.")
