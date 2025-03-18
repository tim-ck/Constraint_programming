from ortools.sat.python import cp_model
import csv
import os
prefex_path = ['problem1', 'problem2', 'problem3']
problem_index = 1
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
center_counts = {center: 0 for center in centers}
for pref in preferred_center:
    center_counts[pref] += 1
print(f"Student preference distribution: {center_counts}")
for d in range(num_days):
    print(f"Day {num_days}: Center capacities: {capacity_day[d]}")
    center_diff_string = ', '.join([f"{center}: {capacity_day[d][center]-center_counts[center]}" for center in centers])
    print(f"Day {num_days}: Difference: {center_diff_string}")
    # print(f"Day {num_days}: Difference: A={capacity_day[d]['A']-center_counts['A']}, B={capacity_day[d]['B']-center_counts['B']}, C={capacity_day[d]['C']-center_counts['C']}")
model = cp_model.CpModel()
# Decision variables
assignment = {}
for s in range(num_students):
    for d in range(num_days):
        assignment[(s, d)] = model.NewIntVar(0, num_centers - 1, f'student_{s}_day_{d}')

# Capacity hard constraints: 
for d in range(num_days):
    for center, cap in capacity_day[d].items():
        center_idx = center_to_index[center]
        assigned_indicators = []
        for s in range(num_students):
            is_assigned = model.NewBoolVar(f'student_{s}_day_{d}_is_{center}')
            model.Add(assignment[(s, d)] == center_idx).OnlyEnforceIf(is_assigned)
            model.Add(assignment[(s, d)] != center_idx).OnlyEnforceIf(is_assigned.Not())
            assigned_indicators.append(is_assigned)
        model.Add(sum(assigned_indicators) <= cap)


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
penalty_table = []
for pref in range(num_centers):
    row = []
    for assigned in range(num_centers):
        if pref == assigned:
            row.append(0)
        elif abs(pref - assigned) == 1:
            row.append(0)
        else:
            row.append(2)
    penalty_table.append(row)
flattened_penalty_table = []
for pref_row in penalty_table:
    flattened_penalty_table.extend(pref_row)
penalty_move = {}
for s in range(num_students):
    for d in range(num_days):
        pref_idx = center_to_index[preferred_center[s]]
        index_in_table = model.NewIntVar(0, num_centers*num_centers - 1, f'table_index_s{s}_d{d}')
        model.Add(index_in_table == pref_idx * num_centers + assignment[(s, d)])
        penalty_move[(s, d)] = model.NewIntVar(0, max(flattened_penalty_table), f'penalty_move_s{s}_d{d}')
        model.AddElement(index_in_table, flattened_penalty_table, penalty_move[(s, d)])
        # penalty_move[(s, d)] = model.NewIntVar(0, 2 * max(flattened_penalty_table), f'penalty_move_s{s}_d{d}')
        # model.AddElement(index_in_table, [2 * val for val in flattened_penalty_table], penalty_move[(s, d)])

total_pref_penalty = sum(penalty_pref[(s, d)] for s in range(num_students) for d in range(num_days))
total_diff_penalty = sum(penalty_diff[(s, d)] for s in range(num_students) for d in range(num_days - 1))
total_move_penalty = sum(penalty_move[(s, d)] for s in range(num_students) for d in range(num_days))
# model.Minimize(total_/pref_penalty)
# model.Minimize(total_pref_penalty + total_move_penalty)
model.Minimize(2*total_diff_penalty + total_pref_penalty + total_move_penalty)


print("Solving model...")
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 30
status = solver.Solve(model)
print(f"Solver status: {solver.StatusName(status)}")

if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    print("\n=== Individual Student Assignments ===")
    for s in range(num_students):
        print(f"\nStudent {s} (Preferred: {preferred_center[s]}):")
        for d in range(num_days):
            assigned_center = centers[solver.Value(assignment[(s, d)])]
            pref_penalty = solver.Value(penalty_pref[(s, d)])
            move_penalty = solver.Value(penalty_move[(s, d)])
            diff_penalty = solver.Value(penalty_diff[(s, d)]) if (s, d) in penalty_diff else 0
            
            penalties = []
            if pref_penalty:
                penalties.append(f"Preference Penalty: {pref_penalty}")
            if move_penalty:
                penalties.append(f"Move Penalty: {move_penalty}")
            if diff_penalty:
                penalties.append(f"Day-change Penalty: {diff_penalty}")
            
            penalty_str = ", ".join(penalties) if penalties else "No Penalties"
            
            print(f"  Day {d + 1}: Assigned Center: {assigned_center} [{penalty_str}]")

    print("\n=== Daily Center Summary ===")
    for d in range(num_days):
        print(f"\nDay {d + 1}:")
        center_counts = {center: 0 for center in centers}
        for s in range(num_students):
            assigned_center = centers[solver.Value(assignment[(s, d)])]
            center_counts[assigned_center] += 1
        for center, count in center_counts.items():
            capacity = capacity_day[d][center]
            print(f"  Center {center}: {count}/{capacity} students assigned")
else:
    print("No solution found. Please adjust constraints or parameters.")
