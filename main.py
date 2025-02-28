from ortools.sat.python import cp_model
import csv
import os
prefex_path = ['problem1']
problem_index = 0
student_csv_path = os.path.join(os.path.dirname(__file__), prefex_path[problem_index], 'students.csv')
center_csv_path = os.path.join(os.path.dirname(__file__), prefex_path[problem_index], 'centers.csv')

preferred_center = []
with open(student_csv_path, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        preferred_center.append(row['PreferredCenter'])

num_students = len(preferred_center)
print(f"Read data for {num_students} students.")

centers = []
capacity_day = []
num_days = 0

with open(center_csv_path, newline='') as csvfile:
    reader = csv.reader(csvfile)
    center_capacities = []
    for row in reader:
        center_name = row[0]
        centers.append(center_name)
        day_capacities = [int(cap) for cap in row[1:]]
        center_capacities.append((center_name, day_capacities))
    num_days = len(center_capacities[0][1]) if center_capacities else 0
    for d in range(num_days):
        day_dict = {}
        for center, caps in center_capacities:
            day_dict[center] = caps[d]
        capacity_day.append(day_dict)

num_centers = len(centers)
center_to_index = {center: idx for idx, center in enumerate(centers)}
center_counts = {'A': 0, 'B': 0, 'C': 0}
for pref in preferred_center:
    center_counts[pref] += 1
print(f"Student preference distribution: {center_counts}")
for d in range(num_days):
    print(f"Day {num_days}: Center capacities: {capacity_day[d]}")
    print(f"Day {num_days}: Difference: A={capacity_day[d]['A']-center_counts['A']}, B={capacity_day[d]['B']-center_counts['B']}, C={capacity_day[d]['C']-center_counts['C']}")
model = cp_model.CpModel()
# Decision variables
assignment = {}
for s in range(num_students):
    for d in range(num_days):
        assignment[(s, d)] = model.NewIntVar(0, num_centers - 1, f'student_{s}_day_{d}')

# Soft constraint
penalty_diff = {}
for s in range(num_students):
    for d in range(num_days - 1):
        penalty_diff[(s, d)] = model.NewBoolVar(f'penalty_diff_student_{s}_between_day_{d}_and_{d+1}')
        model.Add(assignment[(s, d)] != assignment[(s, d+1)]).OnlyEnforceIf(penalty_diff[(s, d)])
        model.Add(assignment[(s, d)] == assignment[(s, d+1)]).OnlyEnforceIf(penalty_diff[(s, d)].Not())

# Soft constraint
penalty_pref = {}
for s in range(num_students):
    for d in range(num_days):
        penalty_pref[(s, d)] = model.NewBoolVar(f'penalty_pref_student_{s}_day_{d}')
        pref_index = center_to_index[preferred_center[s]]
        model.Add(assignment[(s, d)] != pref_index).OnlyEnforceIf(penalty_pref[(s, d)])
        model.Add(assignment[(s, d)] == pref_index).OnlyEnforceIf(penalty_pref[(s, d)].Not())


# Soft constraint
penalty_table = [
    [0, 0, 2],  # preferred = A(0) -> assigned = A(0):0, B(1):0, C(2):2
    [0, 0, 0],  # preferred = B(1) -> assigned = A(0):0, B(1):0, C(2):0
    [2, 0, 0],  # preferred = C(2) -> assigned = A(0):2, B(1):0, C(2):0
]
flattened_penalty_table = []
for pref_row in penalty_table:
    flattened_penalty_table.extend(pref_row)
penalty_move = {}
for s in range(num_students):
    for d in range(num_days):
        # Get the preferred center index
        pref_idx = center_to_index[preferred_center[s]]
        # assignment[(s, d)] is the assigned center index
        index_in_table = model.NewIntVar(0, num_centers*num_centers - 1, f'table_index_s{s}_d{d}')
        model.Add(index_in_table == pref_idx * num_centers + assignment[(s, d)])
        penalty_move[(s, d)] = model.NewIntVar(0, max(flattened_penalty_table), f'penalty_move_s{s}_d{d}')
        # AddElement(target_var=penalty_move[(s, d)], index=index_in_table, values=flattened_penalty_table)
        model.AddElement(index_in_table, flattened_penalty_table, penalty_move[(s, d)])


# Capacity hard constraints: 
for d in range(num_days):
    for center, cap in capacity_day[d].items():
        center_idx = center_to_index[center]
        # For each student, create an indicator: 1 if student s is assigned to center center_idx on day d.
        assigned_indicators = []
        for s in range(num_students):
            is_assigned = model.NewBoolVar(f'student_{s}_day_{d}_is_{center}')
            model.Add(assignment[(s, d)] == center_idx).OnlyEnforceIf(is_assigned)
            model.Add(assignment[(s, d)] != center_idx).OnlyEnforceIf(is_assigned.Not())
            assigned_indicators.append(is_assigned)
        model.Add(sum(assigned_indicators) <= cap)

total_diff_penalty = sum(penalty_diff[(s, d)] for s in range(num_students) for d in range(num_days - 1))
total_pref_penalty = sum(penalty_pref[(s, d)] for s in range(num_students) for d in range(num_days))
total_move_penalty = sum(penalty_move[(s, d)] for s in range(num_students) for d in range(num_days))
# model.Minimize(total_pref_penalty)
# model.Minimize(2*total_pref_penalty + total_move_penalty)
model.Minimize(total_diff_penalty + 2*total_pref_penalty + total_move_penalty)


# Solve the model.
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 300
status = solver.Solve(model)

# Output the results.
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    # Create output file path
    output_path = os.path.join(os.path.dirname(__file__), prefex_path[problem_index], 'output.csv')
    with open(output_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        header = ['StudentID', 'PreferredCenter']
        for d in range(num_days):
            header.append(f'AssignedCenterDay{d}')
        for d in range(num_days):
            header.append(f'PenaltyDay{d}')
        writer.writerow(header)
        for s in range(num_students):
            penalty = []
            for d in range(num_days):
                penalty_sum = solver.Value(penalty_pref[(s, d)]) + solver.Value(penalty_move[(s, d)])
                
                # Only add diff penalty if more than one day
                diff_penalty = 0
                if num_days > 1 and (s, d) in penalty_diff:
                    diff_penalty = solver.Value(penalty_diff[(s, d)])
                penalty.append(penalty_sum + diff_penalty)
            row_values = [s, preferred_center[s]]
            for d in range(num_days):
                row_values.append(centers[solver.Value(assignment[(s, d)])])
            for p in penalty:
                row_values.append(p)
            writer.writerow(row_values)

    # print total number of students assigned to each center
    print(f"Total students assigned to each center:")
    for d in range(num_days):
        center_counts = {center: 0 for center in centers}
        for s in range(num_students):
            center_counts[centers[solver.Value(assignment[(s, d)])]] += 1
        print(f"Day {d}: {center_counts}")
else:
    print("No solution found. Please try again with different parameters.")