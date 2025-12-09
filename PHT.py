import streamlit as st
import pandas as pd
import datetime
import requests
import json
import numpy as np
import plotly.graph_objects as go
from io import StringIO
from urllib.parse import urlencode

# --- Configuration ---
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent"
# Note: The API Key is expected to be provided by the environment,
# hence it is set to an empty string as per instructions.
API_KEY = ""
MAX_ATTEMPTS = 3

# --- Date Utilities ---
def get_formatted_date(date_obj):
    """Gets a date string in YYYY-MM-DD format."""
    return date_obj.strftime("%Y-%m-%d")

def add_days(date_string, days):
    """Adds days to a date string (YYYY-MM-DD)."""
    date = datetime.datetime.strptime(date_string, "%Y-%m-%d")
    date += datetime.timedelta(days=days)
    return get_formatted_date(date)

# --- State Management and Initialization ---

INITIAL_TRACKER_DATA = {
    'config': {
        'startDate': get_formatted_date(datetime.datetime.now()),
        'totalDays': 7,
    },
    'tasks': [
        {'id': 'task-1', 'name': 'Drink 8 Glasses of Water'},
        {'id': 'task-2', 'name': '30 Minutes of Exercise'},
    ],
    'dailyStatus': {}, # { 'YYYY-MM-DD': { 'task-id': boolean, ... } }
    'lastMotivationDate': None,
    'dailyMotivation': None,
}

def init_state():
    """Initializes Streamlit session state."""
    if 'tracker_data' not in st.session_state:
        st.session_state.tracker_data = INITIAL_TRACKER_DATA
    if 'new_task_name' not in st.session_state:
        st.session_state.new_task_name = ''
    if 'new_total_days' not in st.session_state:
        st.session_state.new_total_days = st.session_state.tracker_data['config']['totalDays']
    if 'graph_view' not in st.session_state:
        st.session_state.graph_view = 'week'
    if 'is_generating' not in st.session_state:
        st.session_state.is_generating = False

init_state()
tracker_data = st.session_state.tracker_data
today = get_formatted_date(datetime.datetime.now())

# --- Gemini LLM Integration ---

@st.cache_data(ttl=datetime.timedelta(hours=24), show_spinner=False)
def generate_daily_motivation(task_list, current_date):
    """
    Calls the Gemini API to get a daily motivational tip.
    Uses Streamlit caching to ensure it runs only once per day.
    """
    st.session_state.is_generating = True

    system_prompt = "You are a positive and insightful personal coach for habit building. Your goal is to provide a single, concise, and highly motivating tip or quote (maximum two sentences) based on the user's current habits. Focus on the value of consistency and overcoming daily resistance. Do not include titles or prefixes like 'Tip: ' or 'Quote: '."

    user_query = f"Generate a daily motivational tip or quote for the following habits: {task_list}" if task_list else "Generate a general tip about starting a new habit and the power of small steps."

    # Construct the API URL with API Key (if provided)
    query_params = {}
    if API_KEY:
        query_params['key'] = API_KEY
    api_url = f"{GEMINI_API_URL}?{urlencode(query_params)}"

    payload = {
        "contents": [{"parts": [{"text": user_query}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]},
    }

    result_text = "Couldn't connect to the habit coach. Try again later."

    for i in range(MAX_ATTEMPTS):
        try:
            response = requests.post(api_url, headers={'Content-Type': 'application/json'}, json=payload)
            response.raise_for_status()

            result = response.json()
            text = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text')

            if text:
                result_text = text
                break

        except Exception as e:
            # print(f"Attempt {i + 1} failed: {e}") # Suppressing console logs as per instructions
            if i < MAX_ATTEMPTS - 1:
                delay = 2 ** i
                import time; time.sleep(delay)
            else:
                result_text = "Failed to get motivation after several retries."


    # Update session state with the result and the date it was generated
    st.session_state.tracker_data['dailyMotivation'] = result_text
    st.session_state.tracker_data['lastMotivationDate'] = current_date
    st.session_state.is_generating = False
    st.rerun() # Rerun to update the main app UI with the new motivation

    return result_text # Must return a value for st.cache_data

# --- Data Processing and Calculation ---

def calculate_completion_data(data):
    """Calculates the daily completion percentage history."""
    tasks = data['tasks']
    daily_status = data['dailyStatus']
    start_date_str = data['config']['startDate']
    total_days = data['config']['totalDays']

    history = []

    current_date = start_date_str
    days_count = 0

    while current_date <= today and days_count < total_days:
        status = daily_status.get(current_date, {})
        completed_count = sum(1 for task in tasks if status.get(task['id']) is True)

        completion_rate = (completed_count / len(tasks) * 100) if tasks else 0

        history.append({
            'Date': datetime.datetime.strptime(current_date, "%Y-%m-%d"),
            'Completion (%)': round(completion_rate),
        })

        current_date = add_days(current_date, 1)
        days_count += 1

    df = pd.DataFrame(history)

    if df.empty:
        return df, []

    df['Date'] = pd.to_datetime(df['Date'])

    # Filter based on graph_view state
    if st.session_state.graph_view == 'week':
        days = 7
    elif st.session_state.graph_view == 'month':
        days = 30
    else: # 'all'
        days = len(df)

    # Get the last 'days' rows
    filtered_df = df.tail(days).reset_index(drop=True)

    return df, filtered_df

df_full, df_filtered = calculate_completion_data(tracker_data)

# --- UI Functions ---

def render_completion_chart(df):
    """Renders the interactive Plotly line chart."""
    if df.empty:
        st.warning("No tracking data available for the selected period.")
        return

    # Determine the time period for the title
    if st.session_state.graph_view == 'week':
        period = "Last 7 Days"
    elif st.session_state.graph_view == 'month':
        period = "Last 30 Days"
    else:
        period = "All Time"

    fig = go.Figure()

    # Shaded Area (Fill)
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['Completion (%)'],
        fill='tozeroy',
        mode='lines',
        line_color='#818CF8',
        fillcolor='rgba(99, 102, 241, 0.2)',
        name='Completion Rate',
        hoverinfo='skip'
    ))

    # Line
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['Completion (%)'],
        mode='lines+markers',
        line=dict(color='#4F46E5', width=3),
        marker=dict(size=8, color='#4F46E5', line=dict(width=2, color='White')),
        name='Completion Rate',
        hoverinfo='text',
        hovertext=[f"{date.strftime('%b %d')}<br>{comp}%" for date, comp in zip(df['Date'], df['Completion (%)'])]
    ))

    fig.update_layout(
        title=f'Daily Habit Completion ({period})',
        xaxis_title="Date",
        yaxis_title="Completion Percentage",
        yaxis=dict(range=[0, 100], ticksuffix="%"),
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=40, r=40, t=40, b=40),
        hovermode="x unified",
    )

    # Add a horizontal line at 75% for a target visualization
    fig.add_hline(y=75, line_width=1, line_dash="dash", line_color="green", opacity=0.5,
                  annotation_text="Target 75%", annotation_position="top right")

    st.plotly_chart(fig, use_container_width=True)

def handle_add_task():
    """Adds a new task to the tracker data."""
    if st.session_state.new_task_name.strip():
        new_id = f'task-{datetime.datetime.now().timestamp()}'
        st.session_state.tracker_data['tasks'].append({
            'id': new_id,
            'name': st.session_state.new_task_name.strip()
        })
        st.session_state.new_task_name = ''
    else:
        st.warning("Please enter a task name.")

def handle_remove_task(task_id):
    """Removes a task and its history from the tracker data."""
    st.session_state.tracker_data['tasks'] = [
        t for t in st.session_state.tracker_data['tasks'] if t['id'] != task_id
    ]
    # Clean up daily status
    new_daily_status = {}
    for date, status_map in st.session_state.tracker_data['dailyStatus'].items():
        new_daily_status[date] = {
            k: v for k, v in status_map.items() if k != task_id
        }
    st.session_state.tracker_data['dailyStatus'] = new_daily_status
    st.rerun()

def handle_update_task_status(date, task_id, is_complete):
    """Updates the completion status of a task for a given day."""
    if date > today:
        st.warning("Cannot check off future tasks.")
        return

    # Initialize nested dictionaries if they don't exist
    if date not in st.session_state.tracker_data['dailyStatus']:
        st.session_state.tracker_data['dailyStatus'][date] = {}

    st.session_state.tracker_data['dailyStatus'][date][task_id] = is_complete

    # Delete status if unchecked to keep data clean, though setting to False works too
    if not is_complete and task_id in st.session_state.tracker_data['dailyStatus'][date]:
         del st.session_state.tracker_data['dailyStatus'][date][task_id]

    # Rerun to update the graph immediately
    st.rerun()

def handle_update_config():
    """Updates the tracking period configuration."""
    try:
        new_days = int(st.session_state.new_total_days)
        if 1 <= new_days <= 365:
            st.session_state.tracker_data['config']['totalDays'] = new_days
            st.session_state.tracker_data['config']['startDate'] = get_formatted_date(datetime.datetime.now())
        else:
            st.error("Total days must be between 1 and 365.")
    except ValueError:
        st.error("Please enter a valid number for total days.")


# --- Application Layout ---

st.set_page_config(layout="wide", page_title="Habit Master Streamlit")

st.markdown("""
    <style>
        .stButton>button {
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: 600;
        }
        .stProgress > div > div > div > div {
            background-color: #4F46E5;
        }
    </style>
""", unsafe_allow_html=True)

st.title(" Habit Master Tracker")
st.caption("Track your consistency. Build your habits using Streamlit and Gemini.")

# --- Automatic Daily Motivation ---
current_date = get_formatted_date(datetime.datetime.now())
task_names = [t['name'] for t in tracker_data['tasks']]
task_list_str = ", ".join(task_names)

if current_date != tracker_data['lastMotivationDate'] and not st.session_state.is_generating:
    # Trigger motivation generation
    generate_daily_motivation(task_list_str, current_date)

st.subheader("Daily Boost ✨")
motivation_container = st.container(border=True)

with motivation_container:
    if st.session_state.is_generating:
        st.info("Generating your daily dose of motivation...", icon="⏳")
    elif tracker_data['dailyMotivation']:
        st.markdown(f"**💡 Insight:** *{tracker_data['dailyMotivation']}*")
    else:
        st.info("Your daily motivation will appear here automatically!")

# --- Configuration Section ---
st.subheader("Tracker Setup")
with st.expander("Change Tracker Length", expanded=False):
    col1, col2 = st.columns([3, 1])
    with col1:
        st.slider(
            "Total Days to Track (Resets Start Date to Today)",
            min_value=1,
            max_value=365,
            value=st.session_state.new_total_days,
            key='new_total_days',
            label_visibility='collapsed'
        )
    with col2:
        st.button("Set Length", on_click=handle_update_config, use_container_width=True)

    st.markdown(f"""
        <p style='font-size: small; color: grey;'>
            Currently tracking {tracker_data['config']['totalDays']} days starting from {tracker_data['config']['startDate']}.
        </p>
    """, unsafe_allow_html=True)


# --- Task Creation Section ---
st.subheader("Manage Tasks")
col_task_input, col_task_button = st.columns([4, 1])

with col_task_input:
    st.text_input(
        "Add a new habit:",
        placeholder="e.g., Read 10 pages, Meditate for 5 min",
        key='new_task_name',
        label_visibility='collapsed'
    )

with col_task_button:
    st.button(
        "Add Task",
        on_click=handle_add_task,
        use_container_width=True,
        type="primary"
    )

st.divider()

# --- Graph Section ---
st.subheader("Completion Rate Visualization")

col_view, col_download = st.columns([3, 1])

with col_view:
    st.radio(
        "Select Time Period",
        ['week', 'month', 'all'],
        index=['week', 'month', 'all'].index(st.session_state.graph_view),
        key='graph_view',
        format_func=lambda x: x.capitalize(),
        horizontal=True,
        label_visibility='collapsed'
    )

with col_download:
    # Prepare CSV data for download
    csv = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name=f"habit_tracker_completion_{st.session_state.graph_view}.csv",
        mime='text/csv',
        use_container_width=True
    )

render_completion_chart(df_filtered)

# --- Tracker Grid Section (Daily Checklist) ---
st.subheader("Daily Checklist")

if not tracker_data['tasks']:
    st.info("Add tasks above to start tracking your habits!", icon="📝")
else:
    # Create the header row for the table
    header_cols = st.columns([3] + [1] * df_full.shape[0])
    header_cols[0].markdown("**Task**", unsafe_allow_html=True)

    # Calculate headers: we only show days from start_date up to today
    for i, date_obj in enumerate(df_full['Date']):
        date_str = date_obj.strftime("%Y-%m-%d")
        day_label = date_obj.strftime("%a %d")

        style = f"font-weight: bold; color: {'#4F46E5' if date_str == today else '#6B7280'};"

        header_cols[i + 1].markdown(f"<div style='text-align: center; {style}'>{day_label}</div>", unsafe_allow_html=True)

    st.divider()

    # Create task rows
    for task in tracker_data['tasks']:
        cols = st.columns([3] + [1] * df_full.shape[0])

        # Column 1: Task Name and Remove Button
        with cols[0]:
            col_name, col_remove = st.columns([4, 1])
            col_name.markdown(f"**{task['name']}**")
            col_remove.button(
                "🗑️",
                key=f"remove_{task['id']}",
                on_click=handle_remove_task,
                args=(task['id'],),
                help="Remove this task",
                use_container_width=True
            )

        # Remaining Columns: Checkboxes for each day
        for i, date_obj in enumerate(df_full['Date']):
            date_str = date_obj.strftime("%Y-%m-%d")

            is_checked = tracker_data['dailyStatus'].get(date_str, {}).get(task['id'], False)

            with cols[i + 1]:
                # Use a unique key for each checkbox
                st.checkbox(
                    label=task['name'], # Provide a non-empty label
                    value=is_checked,
                    key=f"check_{task['id']}_{date_str}",
                    on_change=handle_update_task_status,
                    args=(date_str, task['id'], not is_checked),
                    disabled=date_str > today,
                    label_visibility='collapsed'
                )
