import pandas as pd

# Read the CSV
df = pd.read_csv("data/campers.csv")

# Replace "nan" strings with empty string
df["activities"] = df["activities"].replace("nan", "")

# Save back to CSV
df.to_csv("data/campers.csv", index=False)

print("Cleaned up campers.csv - all 'nan' strings replaced with empty cells")