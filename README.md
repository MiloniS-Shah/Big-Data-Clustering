# Big-Data-Clustering
Implementation of BFR Algorithm - Bradley-Fayyad-Reina

### Dataset : 
Since the BFR algorithm has a strong assumption that the clusters are normally distributed with independent dimensions, we use a synthetic dataset by initializing some random centroids and creating some data points with the centroids and some standard deviations to form the clusters. We also add some other data points as the outliers in the dataset to evaluation the algorithm and their cluster is represented by -1. Figure below shows an example of a part of the dataset. The first column is the data point index (the first column). 
The second column is the cluster that the data point belongs to. The rest columns represent the features/dimensions of the data point.

![Formula](https://github.com/MiloniS-Shah/Big-Data-Clustering/blob/master/input_data.png)

## Implementaion Details:

Bradley-Fayyad-Reina (BFR) algorithm using hw5_clustering.txt.
In BFR, there are three sets of points that you need to keep track of:

Discard set (DS), Compression set (CS), Retained set (RS)

For each cluster in the DS and CS, the cluster is summarized by:

N: The number of points

SUM: the sum of the coordinates of the points

SUMSQ: the sum of squares of coordinates 

### Implementation details of the BFR algorithm: 

Step 1. Load 20% of the data randomly.

Step 2. Run K-Means (e.g., from sklearn) with a large K (e.g., 10 times of the given cluster numbers)
on the data in memory using the Euclidean distance as the similarity measurement.

Step 3. In the K-Means result from Step 2, move all the clusters with only one point to RS (outliers).

Step 4. Run K-Means again to cluster the rest of the data point with K = the number of input clusters.

Step 5. Use the K-Means result from Step 4 to generate the DS clusters (i.e., discard their points and
generate statistics).
The initialization of DS has finished, so far, you have K numbers of DS clusters (from Step 5) and some
numbers of RS (from Step 3).

Step 6. Run K-Means on the points in the RS with a large K to generate CS (clusters with more than one
points) and RS (clusters with only one point).

Step 7. Load another 20% of the data randomly.

Step 8. For the new points, compare them to each of the DS using the Mahalanobis Distance and assign
them to the nearest DS clusters if the distance is < 2√d (d is the number of dimensions).
You cannot use sklearn package for calculating the Mahalanobis Distance. Hint: you will need to compute
variance between the cluster and the point.

Step 9. For the new points that are not assigned to DS clusters, using the Mahalanobis Distance and assign
the points to the nearest CS clusters if the distance is < 2√d

Step 10. For the new points that are not assigned to a DS cluster or a CS cluster, assign them to RS.

Step 11. Run K-Means on the RS with a large K to generate CS (clusters with more than one points) and RS
(clusters with only one point).

Step 12. Merge CS clusters that have a Mahalanobis Distance < 2√d.

Repeat Steps 7 – 12

If this is the last run (after the last chunk of data), merge CS clusters with DS clusters that have a
Mahalanobis Distance < 2√d.
At each run, including the initialization step, you need to count and output the number of the discard
points, the number of the clusters in the CS, the number of the compression points, and the number of
the points in the retained set. 

## Output

The output file is a text file, containing the following information :

a. The intermediate results (the line is named as “The intermediate results”). Then each line should be
started with “Round {i}:” and i is the count for the round (including the initialization, i.e., initialization
would be “Round 1:”. You need to output the numbers in the order of “the number of the discard points”,
“the number of the clusters in the compression set”, “the number of the compression points”, and “the
number of the points in the retained set”.

b. The clustering results (the line is named as “The clustering results”), including the data points index and
their clustering results after the BFR algorithm.The clustering results should be in [0, the number of
clusters). The cluster of outliers should be represented as -1. 

## Execution format
```
python3 filename.py <input_file> <n_cluster> <output_file>
```

Param: input_file_name: the name of the input file (e.g., hw5_clustering.txt), including the file path.
Param: n_cluster: the number of the clusters.
Param: output_file_name: the name of the output txt file, including the file path.
