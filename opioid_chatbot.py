import streamlit as st
import pandas as pd
import plotly.express as px
import time

file_path= "C://Users//nalla//OneDrive//Desktop//ML Project//Cleaned_Opioid_Risk_Dataset.xlsx"
df = pd.read_excel(file_path, sheet_name="Sheet1")

# Preprocessing
df['Year'] = df['Year'].astype(int)
df['State'] = df['State'].astype(str)

# Initialize session state for memory
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Sidebar
st.sidebar.title("🧠 Opioid Risk Assistant (with Memory)")
st.sidebar.write("Ask me about forecasts, risks, state comparisons, maps, and more!")

# Main App
st.title("Opioid Risk Chatbot - Smart Version 🤖✨")
st.write("👋 Hi! I'm your Smart Opioid Risk Assistant. Ask me anything about opioid trends!")

# Input
query = st.text_input("Ask your question:", "")

# Thinking animation
def thinking():
    with st.spinner('Thinking deeply... 🤔'):
        time.sleep(1.5)

# Helper Functions
def get_state_risk(state):
    avg_crude_rate = df[df['State'] == state]['Crude Rate'].mean()
    if avg_crude_rate < 10:
        return "Low Risk"
    elif avg_crude_rate < 20:
        return "Medium Risk"
    else:
        return "High Risk"

def plot_deaths_map(year=None):
    if year:
        df_year = df[df['Year'] == year]
    else:
        df_year = df
    fig = px.choropleth(df_year, locations='State', locationmode="USA-states",
                        color='Deaths', scope="usa", title=f"Opioid Deaths {'in '+str(year) if year else '(All Years)'}",
                        color_continuous_scale="Reds")
    return fig

def compare_states(state_list):
    filtered = df[df['State'].isin(state_list)]
    fig = px.line(filtered, x='Year', y='Crude Rate', color='State', markers=True,
                  title="Crude Rate Comparison Between States")
    return fig

# Chatbot logic
if query:
    thinking()

    query_lower = query.lower()
    response = ""

    # Save history
    st.session_state.chat_history.append(f"🧑‍💻 You: {query}")

    if "forecast" in query_lower or "future" in query_lower:
        st.subheader("📈 Forecasted Deaths")
        fig = px.line(df.groupby('Year')['Deaths'].sum().reset_index(), x='Year', y='Deaths', title="Forecasted Opioid Deaths")
        st.plotly_chart(fig)
        response = "Here’s the forecast based on past trends."

    elif "risk" in query_lower:
        st.subheader("🚨 Risk Level")
        matched_states = []
        for state in df['State'].unique():
            if state.lower() in query_lower:
                matched_states.append(state)

        if matched_states:
            for state in matched_states:
                risk = get_state_risk(state)
                st.success(f"{state}: {risk}")
            response = "Here are the risk levels you asked about!"
        else:
            response = "Please mention a valid state name for risk information."
            
    elif "severity" in query_lower or "severity index" in query_lower:
        st.subheader("🩺 Opioid Severity by State")
        severity = df.groupby('State')['Crude Rate'].mean().reset_index()
        fig = px.bar(severity, x='State', y='Crude Rate', title="Average Crude Rate by State", color='Crude Rate', color_continuous_scale="Reds")
        st.plotly_chart(fig)
        response = "Here’s the opioid severity across states."

    elif "map" in query_lower:
        st.subheader("🗺️ Opioid Deaths Map")
        fig = plot_deaths_map()
        st.plotly_chart(fig)
        response = "Here’s the map showing opioid deaths across states."

    elif "compare" in query_lower or "comparison" in query_lower:
        st.subheader("📊 Compare States")
        if "and" in query_lower:
            parts = query.split("compare")[-1].split("and")
            state1 = parts[0].strip().title()
            state2 = parts[1].strip().title()
            if state1 in df['State'].values and state2 in df['State'].values:
                fig = compare_states([state1, state2])
                st.plotly_chart(fig)
                response = f"Here’s the comparison between {state1} and {state2}."
            else:
                response = "One or both states not found. Please check the names."
        else:
            response = "Please specify two states to compare."

    elif "deaths" in query_lower:
        st.subheader("⚰️ Total Deaths Over Time")
        deaths = df.groupby('Year')['Deaths'].sum().reset_index()
        fig = px.line(deaths, x='Year', y='Deaths', markers=True, title="Total Opioid Deaths per Year")
        st.plotly_chart(fig)
        response = "Here’s the opioid deaths trend."

    elif "data for" in query_lower:
        st.subheader("📋 State Data")
        state = query.split("for")[-1].strip().title()
        if state in df['State'].values:
            st.dataframe(df[df['State'] == state])
            response = f"Here’s the data for {state}."
        else:
            response = f"Couldn't find data for {state}."

    elif "help" in query_lower or "what can you do" in query_lower:
        response = """
        You can ask me:
        - "Forecast future opioid deaths"
        - "Risk level for Ohio"
        - "Show opioid deaths map"
        - "Compare Texas and California"
        - "Deaths over years"
        - "Show severity index"
        """

    else:
        response = "😕 I’m not sure how to answer that. Try asking about forecasts, deaths, maps, or comparisons!"

    # Save bot response
    st.session_state.chat_history.append(f"🤖 Bot: {response}")

# Show chat history
st.subheader("📝 Conversation History")
for chat in st.session_state.chat_history:
    st.write(chat)
