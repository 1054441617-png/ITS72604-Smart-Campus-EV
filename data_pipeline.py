import pandas as pd


# Step 1: Load Dataset

def load_data():
    """Read the original EV charging dataset."""

    df = pd.read_csv("ev_campus_dataset.csv")

    print("Original Dataset Shape:", df.shape)

    return df


# Step 2: Data Cleaning

def clean_data(df):
    """Fill missing values and validate categorical data."""

    print("\nMissing Values Before Cleaning:")
    print(df.isnull().sum())

    # Fill missing numerical values using the median
    numeric_columns = df.select_dtypes(include="number").columns

    for column in numeric_columns:
        if df[column].isnull().all():
            raise ValueError(f"No valid values in {column}")

        df[column] = df[column].fillna(df[column].median())

    # Validate charger types
    if not df["Charger_Type"].isin(["AC", "DC"]).all():
        raise ValueError("Invalid charger type found")

    # Validate user types
    valid_users = ["Student", "Staff", "Visitor"]

    if not df["User_Type"].isin(valid_users).all():
        raise ValueError("Invalid user type found")

    # Validate grid status
    valid_status = ["Normal", "Grid_Surge", "Overheated"]

    if not df["Grid_Status_Label"].isin(valid_status).all():
        raise ValueError("Invalid grid status found")

    print("\nMissing Values After Cleaning:")
    print(df.isnull().sum())

    return df


# Step 3: Feature Engineering

def add_features(df):
    """Calculate charging power, carbon savings and fees."""

    # Convert charging duration to hours
    df["Duration_Hours"] = df["Duration_Mins"] / 60

    # Validate charging duration and energy
    if (df["Duration_Hours"] <= 0).any():
        raise ValueError("Invalid charging duration")

    if (df["Energy_kWh"] < 0).any():
        raise ValueError("Invalid energy value")

    # Calculate average charging power
    df["Power_Rate_kW"] = (
        df["Energy_kWh"] / df["Duration_Hours"]
    )

    # Calculate carbon savings
    df["Carbon_Savings_kgCO2"] = (
        df["Energy_kWh"] * 0.475
    )

    # Assign assumed hourly charging rates
    df["Base_Rate_MYR"] = df["Charger_Type"].map({
        "AC": 6.0,
        "DC": 15.0
    })

    # Calculate base charging fee
    df["Base_Fee_MYR"] = (
        df["Duration_Hours"] * df["Base_Rate_MYR"]
    ).round(2)

    # Calculate peak-hour surcharge
    peak_hours = df["Start_Hour"].between(12, 17)

    df["Peak_Surge_MYR"] = (
        df["Base_Fee_MYR"] * 0.25
    ).where(peak_hours, 0.0)

    # Calculate overstay fee
    df["Overstay_Fee_MYR"] = (
        (df["Overstay_Mins"] - 15).clip(lower=0) * 0.50
    )

    # Calculate total billable amount
    df["Net_Billable_MYR"] = (
        df["Base_Fee_MYR"]
        + df["Peak_Surge_MYR"]
        + df["Overstay_Fee_MYR"]
    ).round(2)

    return df


# Step 4: Export Dataset

def export_data(df):
    """Save the cleaned dataset and display summary statistics."""

    # Export cleaned dataset
    df.to_csv("cleaned_energy_sales_data.csv", index=False)

    # Display summary statistics
    print("\nSummary Statistics:")
    print(df.describe().round(2))

    # Display total charging revenue
    print("\nTotal Revenue: RM",
          round(df["Net_Billable_MYR"].sum(), 2))

    print("\nCleaned dataset exported successfully!")


# Step 5: Main Program

def main():
    """Run the complete EV data processing pipeline."""

    df = load_data()

    df = clean_data(df)

    df = add_features(df)

    export_data(df)


# Step 6: Exception Handling

if __name__ == "__main__":
    try:
        main()

    except (FileNotFoundError, pd.errors.ParserError,
            ValueError, KeyError) as error:
        print("Data processing error:", error)
