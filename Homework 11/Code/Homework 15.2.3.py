#This question starts with the same code/approach as 15.2.1.
#We just need to alter a few things

import pandas as pd
import numpy as np
from pulp import *

# Read the spreadsheet data
data = pd.read_excel("C:/Users/User/OneDrive/Desktop/Data 15.2/diet_large.xls")

# Extract the necessary food data
ftable = data[1:7147].values.tolist()
nutrient_names = list(data.loc[0,:].values.flatten().tolist())
number_nutrients = len(nutrient_names) - 1

# There are a few empty values in the table which need to be replaced
for i in range(7146):
    for j in range(1, len(nutrient_names)):
        if np.isnan(ftable[i][j]):
            ftable[i][j] = 0

# Extract the daily nutrient requirements
min_daily = [item for sublist in data[7148:7149].values.tolist() for item in sublist]
max_daily = [item for sublist in data[7150:7151].values.tolist() for item in sublist]

# Get other relevant food data
foods = [row[0] for row in ftable]
cholesterol_data = {row[0]: float(row[nutrient_names.index('Cholesterol')]) for row in ftable}
nutrient_data = [{row[0]: row[i] for row in ftable} for i in range(1, len(nutrient_names))]

# Create the optimization problem
problem = LpProblem('Diet_Problem', LpMinimize)

# Create decision variables for the amount of each food and whether it is used or not
food_variable = LpVariable.dicts('Food', foods, lowBound=0)

# Set the objective function to minimize the total cholesterol
problem += lpSum([cholesterol_data[food] * food_variable[food] for food in foods]), 'Total Cholesterol'

# Add constraints for each nutrient's minimum and maximum daily requirements. Need to be careful here since not all nutrients have an upper or lower bound (e.g., cholesterol and the fatty acids)
counter = 1
for i in range(number_nutrients):
    if (not np.isnan(min_daily[i+1])) and (not np.isnan(max_daily[i+1])):
        problem += lpSum([nutrient_data[i][food] * food_variable[food] for food in foods]) >= min_daily[i+1], 'Min ' + nutrient_names[i+1] + str(counter)
        problem += lpSum([nutrient_data[i][food] * food_variable[food] for food in foods]) <= max_daily[i+1], 'Max ' + nutrient_names[i+1] + str(counter)
        counter += 1

# Solve the optimization problem
problem.solve()

# Output the results
for v in problem.variables():
    if v.varValue > 0:
        print('The amount of ' + v.name.replace('Food_', '') + ' to use is: ' + str(v.varValue))

print()
print(f"The total cholesterol in this meal plan is {value(problem.objective):.2f}")
