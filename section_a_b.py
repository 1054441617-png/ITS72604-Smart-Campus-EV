import pandas as pd
from functools import reduce

# Load EV charging dataset
df = pd.read_csv("ev_campus_dataset.csv")

# Fill missing energy values using the median
df["Energy_kWh"] = df["Energy_kWh"].fillna(
    df["Energy_kWh"].median()
)

# Calculate base energy fee using an assumed rate
df["Base_Energy_Fee"] = df["Energy_kWh"] * 0.80

# Convert DataFrame into a list of session records
sessions = df.to_dict("records")


# Step 1: Filter High-Risk Sessions

# Select sessions with overstay above 20 minutes
# AND battery temperature above 40 degrees
high_risk = filter(
    lambda x: x["Overstay_Mins"] > 20
    and x["Battery_Temp_C"] > 40,
    sessions
)


# Step 2: Apply 15% Surcharge

# Apply a 1.15 multiplier to each base energy fee
# Calculate the additional surcharge amount
surcharge_sessions = map(
    lambda x: {
        "Session_ID": x["Session_ID"],
        "Base_Fee": x["Base_Energy_Fee"],
        "Final_Fee": x["Base_Energy_Fee"] * 1.15,
        "Surcharge": x["Base_Energy_Fee"] * 0.15
    },
    high_risk
)

# Convert the mapped results into a list
# filter() and map() process records lazily
results = list(surcharge_sessions)


# Step 3: Calculate Total Surcharge Revenue

# Reduce all surcharge amounts into one total
total_surcharge = reduce(
    lambda total, x: total + x["Surcharge"],
    results,
    0
)


# Display Results

print("Total High-Risk Sessions:", len(results))

print("\nFirst Five High-Risk Sessions:")
for session in results[:5]:
    print(session)

print("\nTotal Surcharge Revenue: RM",
      round(total_surcharge, 2))
