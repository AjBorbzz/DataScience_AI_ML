A = [1, 2, 3, 4, 5, 5, 1, 1, 3, 6]
B = [{}, [], ()]

# Process each number in A
for num in A:
    if isinstance(B[0], set):  # Add to the set in the first position
        B[0].add(num)
    if isinstance(B[1], list):  # Add to the list in the second position
        B[1].append(num)
    if isinstance(B[2], tuple):  # Add to the tuple in the third position
        B[2] += (num,)

# Prepare the final result as per the problem's expected format
# Convert the first set to list, the second list remains as is, and the third tuple remains as is
output = [list(B[0]), B[1], B[2]]

print(output)
