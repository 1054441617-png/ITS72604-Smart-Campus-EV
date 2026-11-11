import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load EV charging dataset
df = pd.read_csv("ev_campus_dataset.csv")

# Fill missing numerical values using the median
df["Energy_kWh"] = df["Energy_kWh"].fillna(
    df["Energy_kWh"].median()
)

df["Duration_Mins"] = df["Duration_Mins"].fillna(
    df["Duration_Mins"].median()
)


# Chart 1: Hourly Charging Revenue by Charger Type

# Calculate revenue using an assumed rate
df["Charging_Revenue"] = df["Energy_kWh"] * 0.80

# Group revenue by hour and charger type
hourly_revenue = df.groupby(
    ["Start_Hour", "Charger_Type"]
)["Charging_Revenue"].sum().reset_index()

# Create a multi-bar chart
plt.figure(figsize=(12, 6))

sns.barplot(
    data=hourly_revenue,
    x="Start_Hour",
    y="Charging_Revenue",
    hue="Charger_Type"
)

# Add chart labels
plt.title("Hourly Charging Revenue by Charger Type")
plt.xlabel("Hour of Day")
plt.ylabel("Charging Revenue (RM)")
plt.legend(title="Charger Type")

# Save and display the chart
plt.tight_layout()
plt.savefig("hourly_revenue.png", dpi=300)
plt.show()


# Chart 2: Correlation Heatmap

# Select numerical columns available in the dataset
correlation_data = df[
    ["Battery_Temp_C", "Duration_Mins", "Energy_kWh"]
]

# Calculate correlation coefficients
correlation = correlation_data.corr()

# Create correlation heatmap
plt.figure(figsize=(8, 6))

sns.heatmap(
    correlation,
    annot=True,
    cmap="coolwarm",
    fmt=".2f"
)

# Add chart title
plt.title("Correlation Heatmap of EV Charging Metrics")

# Save and display the heatmap
plt.tight_layout()
plt.savefig("correlation_heatmap.png", dpi=300)
plt.show()
