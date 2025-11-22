# Input list
data =  [0.0, 0.0, 1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

# Convert all 0.0 to 0
cleaned_data = [0 if x == 0.0 else x for x in data]

print(cleaned_data)
