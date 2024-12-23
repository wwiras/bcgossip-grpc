# from sklearn.cluster import AgglomerativeClustering
# import numpy as np
#
# # Sample data
# X = np.array([[1, 2], [1, 4], [1, 0],
#               [4, 2], [4, 4], [4, 0]])
#
# # Create an AgglomerativeClustering object
# clustering = AgglomerativeClustering(n_clusters=2, linkage='ward')
#
# # Fit the model to the data
# clustering.fit(X)
#
# # Get cluster labels for each data point
# labels = clustering.labels_
# print(labels)


import numpy as np

# Sample 2D array
data = np.array([[10, 1, 8],
                 [2, 7, 1],
                 [9, 3, 6]])

# Find the minimum value in the entire array
# min_value = np.min(data)
# print(f"Minimum value in the array: {min_value}")

# Find the minimum value in each row
# min_values_row = np.min(data, axis=1)
# print(f"Minimum values in each row: {min_values_row}")

# Find the minimum value in each column
# min_values_col = np.min(data, axis=0)
# print(f"Minimum values in each column: {min_values_col}")

# Sample 2D array
data = np.array([[10, 1, 8],
                 [5, 7, 3],
                 [9, 3, 6]])

# Find the index of the minimum value in the flattened array
flat_index = np.argmin(data)
print(f"flat_index = {flat_index}")

# Convert the flat index to row and column indices
row_index, col_index = np.unravel_index(flat_index, data.shape)

print(f"Row index of minimum value: {row_index}")
print(f"Column index of minimum value: {col_index}")

print(f"minimum value from np({row_index}, {col_index}): {data[row_index,col_index]}")

