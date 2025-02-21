import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

# Load the portfolio data
file_path = 'clean_withSMP500_Jan22.csv'  # Update with your file path
df = pd.read_csv(file_path)

# Convert 'Day' column to datetime format
df['Day'] = pd.to_datetime(df['Day'])

# Extract Isaiah's portfolio and relevant data
isaiah_portfolio = df[['Day', 'isaiah', 'SMP-500']]

# Calculate percentage change in portfolio value over time
isaiah_portfolio['Portfolio Change (%)'] = isaiah_portfolio['isaiah'].pct_change() * 100

# Isaiah's portfolio allocations
allocations = {
    'ISRG': 1.00  # 100% allocation
}

# Simulate the investment distribution based on allocation percentages
initial_investment = 10000  # Assuming initial investment amount
impact_data = {stock: (allocations[stock] * initial_investment) for stock in allocations}

# Create a DataFrame for visualization
impact_df = pd.DataFrame(list(impact_data.items()), columns=['Stock', 'Investment'])
impact_df['Deviation from Avg'] = impact_df['Investment'] - impact_df['Investment'].mean()
impact_df = impact_df.sort_values(by='Deviation from Avg', ascending=False)

# Streamlit app
st.title("Isaiah's Portfolio Analysis")

# Tabs for different visualizations
tab1, tab2 = st.tabs(["Portfolio Performance", "Individual Stock Performance"])

with tab1:
    # Portfolio Performance Over Time
    st.subheader("Portfolio Performance Over Time")
    fig1 = px.line(isaiah_portfolio, x='Day', y=['isaiah', 'SMP-500'], 
                labels={'value': 'Portfolio Value ($)'}, 
                title="Isaiah's Portfolio vs S&P 500")
    st.plotly_chart(fig1)

    # Key Portfolio Metrics
    st.subheader("Key Portfolio Metrics")
    initial_value = isaiah_portfolio['isaiah'].iloc[0]
    current_value = isaiah_portfolio['isaiah'].iloc[-1]
    growth = ((current_value - initial_value) / initial_value) * 100
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Starting Value ($)", value=f"{initial_value:,.2f}")
    with col2:
        st.metric(label="Current Value ($)", value=f"{current_value:,.2f}")
    with col3:
        st.metric(label="Growth (%)", value=f"{growth:.2f}%")

    # Best and Worst Days
    isaiah_portfolio['Daily Change'] = isaiah_portfolio['isaiah'].diff()
    best_day = isaiah_portfolio.loc[isaiah_portfolio['Daily Change'].idxmax()]
    worst_day = isaiah_portfolio.loc[isaiah_portfolio['Daily Change'].idxmin()]

    st.write(f"**Best Day:** {best_day['Day'].date()} with an increase of ${best_day['Daily Change']:.2f}")
    st.write(f"**Worst Day:** {worst_day['Day'].date()} with a decrease of ${worst_day['Daily Change']:.2f}")

    #___________________________________________________________________________________________________________________________

    # Investment Contribution Breakdown Pie Chart
    st.subheader("Investment Contribution Breakdown")
    fig2 = px.pie(impact_df, values='Investment', names='Stock', 
                title="Contribution of Each Investment")
    st.plotly_chart(fig2)

##############################################################################################################################

with tab2:
    # Stock Analysis Section
    st.subheader("Stock Analysis")

    # Load additional stock analysis data
    stock_prices = pd.read_csv('isaiah_individual_stock_prices.csv')
    stock_returns = pd.read_csv('isaiah_stock_daily_returns.csv')

    # Convert 'Date' column to datetime
    stock_prices['Date'] = pd.to_datetime(stock_prices['Date'])

    # Timeframe selection
    timeframe_options = {
        "Last 5 Days": stock_prices[stock_prices['Date'] >= stock_prices['Date'].max() - pd.DateOffset(days=5)],
        "Last Month": stock_prices[stock_prices['Date'] >= stock_prices['Date'].max() - pd.DateOffset(months=1)],
        "Last 6 Months": stock_prices[stock_prices['Date'] >= stock_prices['Date'].max() - pd.DateOffset(months=6)],
        "Last Year": stock_prices[stock_prices['Date'] >= stock_prices['Date'].max() - pd.DateOffset(years=1)]
    }

    selected_timeframe = st.radio("Select Timeframe:", list(timeframe_options.keys()), index=3, horizontal=True)
    filtered_data = timeframe_options[selected_timeframe]

    # Select stock to analyze
    selected_stock = st.selectbox("Select a stock to analyze:", stock_prices.columns.drop(['Index', 'Date']))

    # Plot stock performance with selected timeframe
    fig = px.line(filtered_data, x='Date', y=selected_stock, 
                  title=f"{selected_stock} Performance Over {selected_timeframe}",
                  labels={'x': 'Date', 'y': 'Stock Price ($)'})
    st.plotly_chart(fig)
    st.caption("This chart shows the stock price movement of the selected stock over the chosen timeframe.")

    #______________________________________________________________________________________________________________

    # Waterfall chart for cash flow analysis
    st.subheader(f"Cash Flow Waterfall Chart for {selected_stock}")

    # Calculate deviation from initial investment
    initial_investment_value = stock_returns[selected_stock].iloc[0]
    stock_returns['Adjusted Return'] = stock_returns[selected_stock] - initial_investment_value

    # Filter returns data for the selected stock
    selected_stock_returns = stock_returns[['Date', 'Adjusted Return']].copy()

    # Calculate summary statistics
    current_value = selected_stock_returns['Adjusted Return'].iloc[-1]
    peak_value = selected_stock_returns['Adjusted Return'].max()
    lowest_value = selected_stock_returns['Adjusted Return'].min()
    average_performance = selected_stock_returns['Adjusted Return'].mean()
    volatility = selected_stock_returns['Adjusted Return'].std()

    # Create a waterfall chart using Plotly
    fig_waterfall = px.bar(
        selected_stock_returns, 
        x='Date', 
        y='Adjusted Return', 
        title=f"{selected_stock} Daily Cash Flows Relative to Initial Investment",
        labels={'x': 'Date', 'y': 'Cash Flow Change ($)'},
        text=selected_stock_returns['Adjusted Return'].round(2),
    )

    fig_waterfall.update_traces(marker_color=['green' if x >= 0 else 'red' for x in selected_stock_returns['Adjusted Return']])
    st.plotly_chart(fig_waterfall)
    st.caption("This chart shows the daily cash flow changes for the selected stock relative to its initial investment, with positive values in green and negative values in red.")

    # Display summary statistics
    st.markdown(f"""You started with an initial investment of **{initial_investment_value:,.2f}**, which is now worth **{current_value + initial_investment_value:,.2f}**.""")

    st.markdown(f"""
    **Stock Summary for {selected_stock}:**  
    - **Current Gain/Loss:** ${current_value:,.2f}  
    - **Peak Value:** ${peak_value:,.2f}  
    - **Lowest Value:** ${lowest_value:,.2f}  
    - **Average Performance:** ${average_performance:,.2f}  
    - **Volatility:** ${volatility:,.2f}
    """)

    #_______________________________________________________________________________________________________________________
    
    # Calculate volatility (standard deviation of daily returns) for each stock

    # Exclude 'Adjusted Return' column if it exists in the DataFrame
    if 'Adjusted Return' in stock_returns.columns:
        stock_returns = stock_returns.drop(columns=['Adjusted Return'])

    volatility = stock_returns.iloc[:, 2:].std().sort_values(ascending=False).reset_index()
    volatility.columns = ['Stock', 'Volatility']

    # Plot volatility comparison
    st.subheader("Stock Volatility Comparison")
    fig = px.bar(volatility, x='Stock', y='Volatility',
                title="Stock Volatility Comparison",
                labels={'Volatility': 'Volatility (Standard Deviation)'})

    st.plotly_chart(fig)

    st.caption("This chart compares the volatility of different stocks based on the standard deviation of their daily returns.")
