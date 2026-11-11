import numpy as np
import pandas as pd

# Load EV charging dataset
df = pd.read_csv("ev_campus_dataset.csv")

# NumPy Operation 1: 2D Array Slicing

# Select two numerical columns and convert to NumPy
telemetry = df[["Start_Hour", "Energy_kWh"]].to_numpy()

# Display array shape
print("Array shape:", telemetry.shape)

# 2D array slicing: first five rows, both columns
print("\nFirst five records:")
print(telemetry[:5, :])


# NumPy Operation 2: Boolean Masking

# Convert battery temperature column to NumPy array
temperatures = df["Battery_Temp_C"].to_numpy()

# Select battery temperatures exceeding 45 degrees
high_temperatures = temperatures[temperatures > 45]

# Display high battery temperatures
print("\nBattery temperatures above 45°C:")
print(high_temperatures)


# Pandas Operation 1: Median Imputation

# Fill missing energy values using the median
df["Energy_kWh"] = df["Energy_kWh"].fillna(
    df["Energy_kWh"].median()
)

# Fill missing charging duration values using the median
df["Duration_Mins"] = df["Duration_Mins"].fillna(
    df["Duration_Mins"].median()
)

# Display remaining missing values
print("\nMissing values after cleaning:")
print(df.isnull().sum())


# Pandas Operation 2: GroupBy

# Calculate charging revenue using an assumed rate
df["Charging_Revenue"] = df["Energy_kWh"] * 0.80

# Calculate total revenue by charger type
revenue = df.groupby("Charger_Type")["Charging_Revenue"].sum()

# Display charging revenue
print("\nRevenue by charger type:")
print(revenue)
