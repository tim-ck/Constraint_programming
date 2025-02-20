from ortools.sat.python import cp_model

# Create the model.
model = cp_model.CpModel()

# Data: 6 students, 3 centers ('A', 'B', 'C'), 2 exam days.
num_students = 7
centers = ['A', 'B', 'C']
num_centers = len(centers)
num_days = 2

# Capacity constraints by day:
capacity_day = [
    {'A': 3, 'B': 3, 'C': 3},   # Day 1 capacities.
    {'A': 1, 'B': 2, 'C': 4}    # Day 2 capacities.
]

# Student preferences: two students prefer each center.
preferred_center = ['A', 'A', 'A', 'B', 'B', 'C', 'C']
center_to_index = {center: idx for idx, center in enumerate(centers)}

# Decision variables: assignment[(s, d)] is the center (as an index) assigned to student s on day d.
assignment = {}
for s in range(num_students):
    for d in range(num_days):
        assignment[(s, d)] = model.NewIntVar(0, num_centers - 1, f'student_{s}_day_{d}')

# Soft constraint: Prefer that a student stays in the same center across both days.
# We introduce a penalty variable for each student that is 1 if the centers differ.
penalty_diff = {}
for s in range(num_students):
    for d in range(num_days - 1):
        penalty_diff[(s, d)] = model.NewBoolVar(f'penalty_diff_student_{s}_between_day_{d}_and_{d+1}')
        model.Add(assignment[(s, d)] != assignment[(s, d+1)]).OnlyEnforceIf(penalty_diff[(s, d)])
        model.Add(assignment[(s, d)] == assignment[(s, d+1)]).OnlyEnforceIf(penalty_diff[(s, d)].Not())

# Soft constraint: Prefer that a student gets their preferred center on every day.
penalty_pref = {}
for s in range(num_students):
    for d in range(num_days):
        penalty_pref[(s, d)] = model.NewBoolVar(f'penalty_pref_student_{s}_day_{d}')
        pref_index = center_to_index[preferred_center[s]]
        model.Add(assignment[(s, d)] != pref_index).OnlyEnforceIf(penalty_pref[(s, d)])
        model.Add(assignment[(s, d)] == pref_index).OnlyEnforceIf(penalty_pref[(s, d)].Not())



# Capacity constraints: For each center and day, ensure the number of students assigned doesn't exceed capacity.
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

# Objective: Minimize the total penalties (for switching centers and not meeting preferences).
total_diff_penalty = sum(penalty_diff[(s, d)] for s in range(num_students) for d in range(num_days - 1))
total_pref_penalty = sum(penalty_pref[(s, d)] for s in range(num_students) for d in range(num_days))
model.Minimize(total_diff_penalty + total_pref_penalty)

# Solve the model.
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Output the results.
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    for s in range(num_students):
        day_assignments = []
        diff_penalties = []
        pref_penalties = []
        for d in range(num_days):
            center_assigned = centers[solver.Value(assignment[(s, d)])]
            day_assignments.append(f"Day {d} = {center_assigned}")
            pref_penalties.append(f"PrefPenalty Day {d} = {solver.Value(penalty_pref[(s, d)])}")
            if d < num_days - 1:
                diff_penalties.append(f"DiffPenalty {d}-{d+1} = {solver.Value(penalty_diff[(s, d)])}")
    
        print(f"Student {s}: " + ", ".join(day_assignments) +
              f", Preferred = {preferred_center[s]}, " +
              ", ".join(diff_penalties) + ", " +
              ", ".join(pref_penalties))
else:
    print("No solution found.")
