import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(layout="wide", page_title='🚀 Startup Funding Analysis')

# ---------------- Load and preprocess data ----------------
@st.cache_data
def load_data():
    df = pd.read_csv('startup_funding_cleaned_final 2.csv')
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    df.dropna(subset=['amount'], inplace=True)
    return df

df = load_data()

# ---------------- Sidebar ----------------
st.sidebar.title('🧭 Navigation')
option = st.sidebar.radio('Choose View', ['Overall Analysis', 'StartUp Analysis', 'Investor Analysis'])

years = sorted(df['year'].dropna().unique())
cities = sorted(df['city'].dropna().unique())
verticals = sorted(df['vertical'].dropna().unique())

# ---------------- Overall Analysis ----------------
def load_overall_analysis():
    st.title('📊 Overall Startup Funding Analysis')
    selected_year = st.selectbox("Filter by Year (Optional)", options=["All"] + years, index=0)

    data = df if selected_year == "All" else df[df['year'] == selected_year]

    total = round(data['amount'].sum())
    max_funding = data.groupby('startup')['amount'].sum().max()
    avg_funding = round(data.groupby('startup')['amount'].sum().mean())
    num_startups = data['startup'].nunique()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric('💰 Total Funding', f'{total} Cr')
    col2.metric('🏆 Max Funding by Startup', f'{max_funding} Cr')
    col3.metric('📊 Avg Funding per Startup', f'{avg_funding} Cr')
    col4.metric('🚀 Unique Startups', num_startups)

    # Month-on-Month Trend
    st.subheader('📈 Month-on-Month Funding Trend')
    selected_type = st.selectbox('Select Metric', ['Total Amount', 'Funding Count'])
    temp_df = data.groupby(['year', 'month'])['amount'].agg('sum' if selected_type == 'Total Amount' else 'count').reset_index()
    temp_df['Period'] = temp_df['month'].astype(str) + '-' + temp_df['year'].astype(str)

    fig, ax = plt.subplots()
    sns.lineplot(data=temp_df, x='Period', y='amount', ax=ax)
    ax.set_xticklabels(temp_df['Period'], rotation=45)
    st.pyplot(fig)

    # Top Startups
    st.subheader('🏅 Top 10 Startups by Total Funding')
    top_startups = data.groupby('startup')['amount'].sum().sort_values(ascending=False).head(10)
    st.bar_chart(top_startups)

    # Top Investors
    st.subheader('💸 Top 10 Investors by Total Investment')
    investor_df = data[data['investors'].notnull()].copy()
    investor_df = investor_df.assign(investors=investor_df['investors'].str.split(',')).explode('investors')
    investor_df['investors'] = investor_df['investors'].str.strip()
    top_investors = investor_df.groupby('investors')['amount'].sum().sort_values(ascending=False).head(10)
    st.bar_chart(top_investors)

    # City-wise funding
    st.subheader('🏙️ Top 10 Cities by Total Funding')
    city_funding = data.groupby('city')['amount'].sum().sort_values(ascending=False).head(10)
    st.bar_chart(city_funding)

    # Download filtered data
    st.subheader("⬇️ Download Filtered Data")
    csv_data = data.to_csv(index=False)
    st.download_button("Download CSV", csv_data, file_name='filtered_funding_data.csv', mime='text/csv')

# ---------------- Startup Analysis ----------------
def load_startup_details(startup):
    st.title(f'📌 Detailed Analysis for Startup: {startup}')
    startup_df = df[df['startup'] == startup].copy()

    st.subheader('🧾 Recent Funding Rounds')
    st.dataframe(startup_df[['date', 'investors', 'vertical', 'city', 'round', 'amount']].sort_values(by='date', ascending=False).head(5))

    col1, col2 = st.columns(2)
    with col1:
        st.subheader('📆 Funding Over Time')
        yearly = startup_df.groupby('year')['amount'].sum()
        st.line_chart(yearly)
    with col2:
        st.subheader('📊 Funding by Round')
        round_data = startup_df.groupby('round')['amount'].sum()
        st.bar_chart(round_data)

    st.subheader('🤝 Investor Contributions')
    investor_series = startup_df['investors'].dropna().str.split(',').explode().str.strip()
    startup_df = startup_df.reset_index(drop=True)
    investor_series = investor_series.reset_index(drop=True)
    startup_df = startup_df.assign(investor=investor_series)
    top_investors = startup_df.groupby('investor')['amount'].sum().sort_values(ascending=False)
    st.bar_chart(top_investors)
    st.dataframe(top_investors.reset_index().rename(columns={'investor': 'Investor', 'amount': 'Total Investment'}))

# ---------------- Investor Analysis ----------------
def load_investor_details(investor):
    st.title(f'💼 Investor Analysis: {investor}')
    investor_df = df[df['investors'].str.contains(investor, na=False)]

    st.subheader('🕒 Recent Investments')
    st.dataframe(investor_df[['date', 'startup', 'vertical', 'city', 'round', 'amount']].sort_values(by='date', ascending=False).head(5))

    col1, col2 = st.columns(2)
    with col1:
        st.subheader('📆 Investments Over Time')
        yearly = investor_df.groupby('year')['amount'].sum()
        st.line_chart(yearly)
    with col2:
        st.subheader('📊 Investments by Round')
        round_data = investor_df.groupby('round')['amount'].sum()
        st.bar_chart(round_data)

    st.subheader('🚀 Top Startups Funded')
    top_startups = investor_df.groupby('startup')['amount'].sum().sort_values(ascending=False).head(10)
    st.bar_chart(top_startups)

    st.subheader('🌐 Sector Distribution')
    sector_data = investor_df.groupby('vertical')['amount'].sum()
    fig, ax = plt.subplots()
    wedges, texts, autotexts = ax.pie(sector_data, labels=sector_data.index, autopct='%1.1f%%', startangle=140)
    ax.axis('equal')
    st.pyplot(fig)

# ---------------- Page Routing ----------------
if option == 'Overall Analysis':
    load_overall_analysis()

elif option == 'StartUp Analysis':
    selected_startup = st.sidebar.selectbox('Select Startup', sorted(df['startup'].dropna().unique()))
    if st.sidebar.button('Analyze Startup'):
        load_startup_details(selected_startup)

elif option == 'Investor Analysis':
    all_investors = sorted(set(df['investors'].dropna().str.split(',').sum()))
    selected_investor = st.sidebar.selectbox('Select Investor', all_investors)
    if st.sidebar.button('Analyze Investor'):
        load_investor_details(selected_investor)
