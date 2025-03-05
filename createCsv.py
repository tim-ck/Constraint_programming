import csv
import random

# Constants
num_students = 21500
center_codes = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']
len_center_codes = len(center_codes)
preferences = []
for i in range(len_center_codes):
	preferences += [center_codes[i]] * (num_students // len_center_codes)
num_students = len(preferences)

random.shuffle(preferences)  # Shuffle to randomize the order of preferences
print(f"Generated preferences for {num_students // len_center_codes} students per center")
# # Filepath
output_file = 'problem3/students.csv'

# Write to CSV
with open(output_file, mode='w', newline='') as file:
	writer = csv.writer(file)
	writer.writerow(['StudentID', 'PreferredCenter'])
	for student_id in range(num_students):
		writer.writerow([student_id, preferences[student_id]])

print(f"Data for {num_students} students has been written to {output_file}")

# # Verify the CSV file
# center_counts = {center: 0 for center in center_codes}
# student_count = 0

# with open(output_file, mode='r', newline='') as file:
# 	reader = csv.reader(file)
# 	next(reader)  # Skip the header row
# 	for row in reader:
# 		student_count += 1
# 		center_counts[row[1]] += 1

# print(f"Verification: Found {student_count} students in the CSV")
# print(f"Center counts: A: {center_counts['A']} (expected 6500), B: {center_counts['B']} (expected 7000), C: {center_counts['C']} (expected 7500)")

# # Create centers.csv with capacity for each day
# num_days = 2  # Multiple days scenario
# centers = ['A', 'B', 'C']
# # Capacities for each center for each day
# capacities = {
# 	'A': [7700, 7700],  # Day 1 and Day 2 capacities
# 	'B': [6800, 6800],
# 	'C': [7000, 7000]
# }

# # Filepath for centers data
# centers_file = 'problem2/centers.csv'

# # Write centers data to CSV
# with open(centers_file, mode='w', newline='') as file:
# 	writer = csv.writer(file)
# 	# Write each center's information
# 	for center in centers:
# 		row = [center] + capacities[center]
# 		writer.writerow(row)
