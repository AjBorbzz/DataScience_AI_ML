import pandas as pd

file = 'Motor_Vehicle_Collisions_-_Crashes.csv'

df = pd.read_csv(file, nrows=100000)

df.to_csv("Motor_Vehicle_Collisions_slim_version.csv", index=False)