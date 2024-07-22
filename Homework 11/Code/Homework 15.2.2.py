#This question starts with the same code/approach as 15.2.1.
#We just need to add some more constraints

import pandas as pd
from pulp import *

# Read the spreadsheet data
data = pd.read_excel("C:/Users/User/OneDrive/Desktop/Data 15.2/diet.xls")

# Extract the necessary food data
ftable = data[0:64].values.tolist()
foods = [row[0] for row in ftable]
nutrient_names = list(data.columns.values)[3:]
nutrient_data = [{row[0]: row[i+3] for row in ftable} for i in range(11)]

# Extract the daily nutrient requirements
min_daily = [item for sublist in data[65:66].values.tolist() for item in sublist][3:]
max_daily = [item for sublist in data[66:67].values.tolist() for item in sublist][3:]

# Create the optimization problem
problem = LpProblem('Diet_Problem', LpMinimize)

# Create decision variables for the amount of each food and whether it is used or not
foods_used = LpVariable.dicts('IsUsed', foods, lowBound=0, upBound=1, cat=LpBinary)
food_variable = LpVariable.dicts('Food', foods, lowBound=0)

# Set the objective function to minimize the total cost of foods
problem += lpSum([ftable[i][1] * food_variable[foods[i]] for i in range(len(foods))]), 'Total Cost'

# Add constraints for each nutrient's minimum and maximum daily requirements
for i, nutrient_name in enumerate(nutrient_names):
    problem += lpSum([nutrient_data[i][foods[j]] * food_variable[foods[j]] for j in range(len(foods))]) >= min_daily[i], 'Min ' + nutrient_name
    problem += lpSum([nutrient_data[i][foods[j]] * food_variable[foods[j]] for j in range(len(foods))]) <= max_daily[i], 'Max ' + nutrient_name

# If a food is selected, then a minimum of 1/10 serving must be chosen
for food in foods:
    problem += food_variable[food] >= 0.1 * foods_used[food], f"Min {food} serving"

# Many people dislike celery and frozen broccoli. So at most one, but not both, can be selected.
problem += foods_used['Frozen Broccoli'] + foods_used['Celery, Raw'] <= 1, "Either Frozen Broccoli or Celery"

# To get day-to-day variety in protein, at least 3 kinds of meat/poultry/fish/eggs must be selected.
protein_foods = ['Roasted Chicken', 'Beanbacn Soup,W/Watr', 'Chicknoodl Soup', 'New E Clamchwd,W/Mlk', 'Vegetbeef Soup', 'Frankfurter, Beef', 'Splt Pea&Hamsoup', 'Neweng Clamchwd', 'Bologna,Turkey', 'Scrambled Eggs', 'Poached Eggs', 'Ham,Sliced,Extralean', 'Kielbasa,Prk', 'Hamburger W/Toppings', 'Pork', 'Sardines in Oil', 'Pizza W/Pepperoni', 'White Tuna in Water']
problem += lpSum([foods_used[food] for food in protein_foods]) >= 3, "Min 3 protein sources"

# Solve the optimization problem
problem.solve()

# Output the results
for v in problem.variables():
    if v.varValue > 0 and 'IsUsed' not in v.name:
        print('The amount of ' + v.name.replace('Food_', '') + ' to use is: ' + str(v.varValue))

print()
print(f"Total cost of the meal plan is ${value(problem.objective):.2f}")
