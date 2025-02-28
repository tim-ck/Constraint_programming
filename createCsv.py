import csv
import random

# Constants
num_students = 21500
preferences = ['A'] * 7500 + ['B'] * 7000 + ['C'] * 7000
random.shuffle(preferences)  # Shuffle to randomize the order of preferences

# # Filepath
output_file = 'problem2/students.csv'

# Write to CSV
with open(output_file, mode='w', newline='') as file:
	writer = csv.writer(file)
	writer.writerow(['StudentID', 'PreferredCenter'])
	for student_id in range(1, num_students + 1):
		writer.writerow([student_id, preferences[student_id - 1]])

print(f"Data for {num_students} students has been written to {output_file}")

# Verify the CSV file
center_counts = {'A': 0, 'B': 0, 'C': 0}
student_count = 0

with open(output_file, mode='r', newline='') as file:
	reader = csv.reader(file)
	next(reader)  # Skip the header row
	for row in reader:
		student_count += 1
		center_counts[row[1]] += 1

print(f"Verification: Found {student_count} students in the CSV")
print(f"Center counts: A: {center_counts['A']} (expected 6500), B: {center_counts['B']} (expected 7000), C: {center_counts['C']} (expected 7500)")

# Create centers.csv with capacity for each day
num_days = 2  # Multiple days scenario
centers = ['A', 'B', 'C']
# Capacities for each center for each day
capacities = {
	'A': [7700, 7700],  # Day 1 and Day 2 capacities
	'B': [6800, 6800],
	'C': [7000, 7000]
}

# Filepath for centers data
centers_file = 'problem2/centers.csv'

# Write centers data to CSV
with open(centers_file, mode='w', newline='') as file:
	writer = csv.writer(file)
	# Write each center's information
	for center in centers:
		row = [center] + capacities[center]
		writer.writerow(row)
