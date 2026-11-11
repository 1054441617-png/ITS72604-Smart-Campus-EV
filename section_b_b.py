import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load cleaned EV charging dataset
df = pd.read_csv("cleaned_energy_sales_data.csv")

# Set visualization style
sns.set_theme(style="whitegrid")

# Create three visualization panels
fig, axes = plt.subplots(3, 1, figsize=(12, 16))


# Panel 1: Charging Load vs Solar Generation

# Calculate total charging power by session start hour
hours = np.arange(24)

charging_load = df.groupby(
    "Start_Hour"
)["Power_Rate_kW"].sum().reindex(hours, fill_value=0)

# Create an illustrative solar generation curve
# Solar generation is simulated, not measured
solar_generation = np.maximum(
    0, np.sin((hours - 6) * np.pi / 12)
) * charging_load.max() * 0.6

# Plot charging load
axes[0].plot(
    hours,
    charging_load,
    marker="o",
    label="Charging Load Proxy"
)

# Plot simulated solar generation
axes[0].plot(
    hours,
    solar_generation,
    linestyle="--",
    label="Simulated Solar Generation"
)

# Add chart labels
axes[0].set_title(
    "Hourly Charging Load Proxy vs Simulated Solar Generation"
)
axes[0].set_xlabel("Hour of Day")
axes[0].set_ylabel("Aggregate Power (kW)")
axes[0].set_xticks(hours)
axes[0].legend()


# Panel 2: Charging Cost by User Type

# Create a box plot comparing charging costs
sns.boxplot(
    data=df,
    x="User_Type",
    y="Net_Billable_MYR",
    order=["Student", "Staff", "Visitor"],
    ax=axes[1]
)

# Add chart labels
axes[1].set_title("Charging Session Cost by User Type")
axes[1].set_xlabel("User Type")
axes[1].set_ylabel("Charging Cost (RM)")


# Panel 3: Battery Temperature vs Energy Delivered

# Create scatter plot with regression trendline
sns.regplot(
    data=df,
    x="Battery_Temp_C",
    y="Energy_kWh",
    scatter_kws={"alpha": 0.4},
    line_kws={"linewidth": 2},
    ax=axes[2]
)

# Add chart labels
axes[2].set_title(
    "Battery Temperature vs Energy Delivered"
)
axes[2].set_xlabel("Battery Temperature (°C)")
axes[2].set_ylabel("Energy Delivered (kWh)")


# Save and display all three panels
plt.tight_layout()

plt.savefig(
    "section_b_visualizations.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print("Three visualization panels created successfully!")
