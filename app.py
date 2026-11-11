import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns


# Step 1: Configure Streamlit Application

st.set_page_config(
    page_title="Smart Campus EV Dashboard",
    layout="wide"
)


# Step 2: Load Cleaned Dataset

@st.cache_data
def load_data():
    """Load the cleaned EV dataset and create demonstration dates."""

    # Read cleaned EV charging dataset
    df = pd.read_csv("cleaned_energy_sales_data.csv")

    # Create demonstration dates for the date filter
    # The original dataset does not contain actual dates
    df["Demo_Date"] = (
        pd.Timestamp("2026-09-01")
        + pd.to_timedelta(df.index // 24, unit="D")
    )

    return df


try:
    df = load_data()

except (FileNotFoundError, pd.errors.ParserError) as error:
    st.error(f"Unable to load dataset: {error}")
    st.stop()


# Step 3: Create Interactive Sidebar

st.title("Smart Campus Energy & EV Dashboard")

st.caption(
    "Date values are simulated for demonstration. "
    "Charging and billing metrics use the processed dataset."
)

st.sidebar.header("Interactive Filters")

# Date range filter
date_range = st.sidebar.date_input(
    "Select Demo Date Range",
    value=(
        df["Demo_Date"].min().date(),
        df["Demo_Date"].max().date()
    )
)

# Minimum energy threshold
min_energy = st.sidebar.slider(
    "Minimum Energy (kWh)",
    min_value=0.0,
    max_value=float(df["Energy_kWh"].max()),
    value=0.0,
    step=1.0
)

# Charger type selection
charger_types = st.sidebar.multiselect(
    "Select Charger Type",
    options=["AC", "DC"],
    default=["AC", "DC"]
)

# Battery temperature threshold
temp_threshold = st.sidebar.slider(
    "Battery Temperature Alert (°C)",
    min_value=30,
    max_value=60,
    value=40
)


# Step 4: Filter Dataset

# Check that both dates are selected
if len(date_range) != 2:
    st.info("Please select a start date and end date.")
    st.stop()

# Apply date, energy and charger filters
filtered_df = df[
    (df["Demo_Date"].dt.date >= date_range[0])
    & (df["Demo_Date"].dt.date <= date_range[1])
    & (df["Energy_kWh"] >= min_energy)
    & (df["Charger_Type"].isin(charger_types))
].copy()

# Identify high-risk charging sessions
alerts = filtered_df[
    (filtered_df["Overstay_Mins"] > 20)
    & (filtered_df["Battery_Temp_C"] > temp_threshold)
]


# Step 5: Display Executive KPI Metrics

total_energy = filtered_df["Energy_kWh"].sum()
total_carbon = filtered_df["Carbon_Savings_kgCO2"].sum()
total_revenue = filtered_df["Net_Billable_MYR"].sum()
alert_count = len(alerts)

# Calculate comparison values for KPI delta indicators
base_energy = df["Energy_kWh"].sum()
base_carbon = df["Carbon_Savings_kgCO2"].sum()
base_revenue = df["Net_Billable_MYR"].sum()

base_alerts = len(df[
    (df["Overstay_Mins"] > 20)
    & (df["Battery_Temp_C"] > temp_threshold)
])

# Calculate KPI percentage change
def percentage_delta(value, total):
    """Calculate percentage change against the unfiltered total."""

    if total == 0:
        return "N/A"

    return f"{(value / total - 1) * 100:.1f}% vs all data"


col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Energy",
        f"{total_energy:,.2f} kWh",
        delta=percentage_delta(total_energy, base_energy),
        delta_color="off"
    )

with col2:
    st.metric(
        "Carbon Savings",
        f"{total_carbon:,.2f} kg",
        delta=percentage_delta(total_carbon, base_carbon),
        delta_color="off"
    )

with col3:
    st.metric(
        "Total Revenue",
        f"RM {total_revenue:,.2f}",
        delta=percentage_delta(total_revenue, base_revenue),
        delta_color="off"
    )

with col4:
    st.metric(
        "Active Alerts",
        alert_count,
        delta=percentage_delta(alert_count, base_alerts),
        delta_color="off"
    )


# Step 6: Overview Page

def overview():
    """Display charging revenue and battery temperature charts."""

    st.header("Charging Overview")

    if filtered_df.empty:
        st.warning("No records match the selected filters.")
        return

    # Calculate hourly revenue
    hourly_revenue = filtered_df.groupby(
        ["Start_Hour", "Charger_Type"]
    )["Net_Billable_MYR"].sum().reset_index()

    # Create hourly charging revenue chart
    fig, ax = plt.subplots(figsize=(10, 5))

    sns.barplot(
        data=hourly_revenue,
        x="Start_Hour",
        y="Net_Billable_MYR",
        hue="Charger_Type",
        ax=ax
    )

    ax.set_title("Hourly Charging Revenue")
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Revenue (RM)")

    st.pyplot(fig)
    plt.close(fig)

    # Create battery temperature scatter chart
    fig2, ax2 = plt.subplots(figsize=(10, 5))

    sns.scatterplot(
        data=filtered_df,
        x="Battery_Temp_C",
        y="Energy_kWh",
        hue="Charger_Type",
        ax=ax2
    )

    ax2.set_title("Battery Temperature vs Energy")
    ax2.set_xlabel("Battery Temperature (°C)")
    ax2.set_ylabel("Energy Delivered (kWh)")

    st.pyplot(fig2)
    plt.close(fig2)


# Step 7: High-Risk Alert Center

# Display the high-risk alert center
def alert_center():
    """Display high-risk charging sessions and alert messages."""

    st.header("High-Risk Overstay & Alert Center")

    # Display alerts based on selected temperature
    if alerts.empty:
        st.success("No high-risk sessions detected.")

    else:
        st.warning(
            f"{len(alerts)} high-risk sessions detected!"
        )

        if len(alerts) >= 10:
            st.error("High number of risk alerts!")

        # Display high-risk charging sessions
        st.dataframe(
            alerts[
                [
                    "Session_ID",
                    "Charger_Type",
                    "Overstay_Mins",
                    "Battery_Temp_C",
                    "Net_Billable_MYR"
                ]
            ],
            use_container_width=True
        )


# Step 8: Filtered Data Viewer

# Display and export filtered charging data
def data_viewer():
    """Display filtered charging data and provide CSV download."""

    st.header("Filtered EV Charging Data")


    # Display the filtered dataset
    st.dataframe(
        filtered_df,
        use_container_width=True
    )

    # Convert filtered data to CSV
    csv = filtered_df.drop(
        columns=["Demo_Date"]
    ).to_csv(index=False).encode("utf-8-sig")

    # Download CSV file
    st.download_button(
        label="Download Filtered CSV",
        data=csv,
        file_name="filtered_ev_data.csv",
        mime="text/csv"
    )


# Step 9: Create Multiple Pages

page = st.navigation([
    st.Page(overview, title="Overview", default=True),
    st.Page(alert_center, title="Alert Center"),
    st.Page(data_viewer, title="Data Viewer")
])

page.run()
