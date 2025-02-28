I have designed a basic problem statement to tested out CP solving NP problem. Here is the problem statement for our assignment problem:

## Problem Statement: Exam Center Assignment
Assign candidates to exam centers for a multi-day exam. We assume each district only have one center. There are serve preferences and constraints for center allowcation:

1. **Capacity Constraints**:   
    For each exam day, there are maximum capacity for each center and it could be different in different day.
2. **District Perference**:  
   Each candidate has a preferred exam district. Ideally, a candidate should be assigned to their preferred center on every day.
3. **Move Distance Penalty**:  
    If a candidate is assigned to a different center on consecutive days, a penalty is incurred. This penalty reflects the inconvenience and potential cost of traveling between different centers.  
4. **Inconsistency Allocation Penalty**:
   To reduce candidate inconvenience, a candidate should ideally be assigned to the same center on every exam day as much as possible.

## Objective:
Minimize the total penalty, which includes penalties for not being assigned to the preferred center and penalties for moving between different centers on consecutive days, while satisfying the capacity constraints for each center on each day.

## Input Files:
- **students.csv**: Contains the list of students and their preferred centers.
- **centers.csv**: Contains the list of centers and their capacities for each day.

## Output:
- **output.csv**: Contains the assignment of students to centers for each day along with the penalties incurred.

## Example:
Given the following input files:

**students.csv**:
```
StudentID,PreferredCenter
1,A
2,B
3,C
```

**centers.csv**:
```
Center,Day1,Day2
A,2,2
B,2,2
C,2,2
```

The output file `output.csv` will contain the assignment of students to centers for each day and the penalties incurred for each assignment.