import sys
from sklearn.cluster import KMeans

import bfr

input_file = sys.argv[1]
no_of_clusters = int(sys.argv[2])
data = bfr.get_data(input_file)
n_sample = len(data)

percent = 0.2

X = []
index = []
for i in range(len(data)):
	X.append(data[i][1])
	index.append(data[i][0])

init_data = X[:int(n_sample * percent)]
init_index = index[:int(n_sample * percent)]

kmeans = KMeans(n_clusters=(no_of_clusters * 10), random_state=0).fit(init_data)

# CREATING RETAINED SET
rs = []
dict_labels = {}
dict_indexes = {}
for i in range(len(kmeans.labels_)):
	try:
		dict_labels[kmeans.labels_[i]].append(init_data[i])
		dict_indexes[kmeans.labels_[i]].append(init_index[i])
	except:
		dict_labels[kmeans.labels_[i]] = [init_data[i]]
		dict_indexes[kmeans.labels_[i]] = [init_index[i]]

to_be_clusters = []
rs_index = []
to_be_clusters_index = []
for i in range(no_of_clusters * 10):
	if len(dict_labels[i]) == 1:
		rs.append(dict_labels[i][0])
		rs_index.append(dict_indexes[i][0])
	else:
		points_i = dict_labels[i]
		indexes_i = dict_indexes[i]
		for j in range(len(points_i)):
			to_be_clusters.append(points_i[j])
			to_be_clusters_index.append(indexes_i[j])

# CREATING DISCARD SET
ds = {}
points_in_ds = {}

kmeans_ds = KMeans(n_clusters=no_of_clusters, random_state=0).fit(to_be_clusters)
for i in range(len(kmeans_ds.labels_)):
	try:
		cluster_statistics = ds[kmeans_ds.labels_[i]]
		cluster_statistics[0] += 1
		for j in range(len(to_be_clusters[i])):
			cluster_statistics[1][j] += to_be_clusters[i][j]
			cluster_statistics[2][j] += to_be_clusters[i][j] ** 2
		ds[kmeans_ds.labels_[i]] = cluster_statistics
		points_in_ds[kmeans_ds.labels_[i]].append(to_be_clusters_index[i])

	except:
		cluster_statistics = list()

		cluster_statistics.append(1)
		cluster_statistics.append(to_be_clusters[i])
		cluster_statistics.append([d ** 2 for d in to_be_clusters[i]])

		ds[kmeans_ds.labels_[i]] = cluster_statistics
		points_in_ds[kmeans_ds.labels_[i]] = [to_be_clusters_index[i]]

k = int(len(rs) * 0.8)
kmeans_for_cs = KMeans(n_clusters=k, random_state=0).fit(rs)
cs_labels = {}
points_in_cs = {}
for i in range(len(kmeans_for_cs.labels_)):
	try:
		cs_labels[kmeans_for_cs.labels_[i]].append(rs[i])
		points_in_cs[kmeans_for_cs.labels_[i]].append(rs_index[i])
	except:
		cs_labels[kmeans_for_cs.labels_[i]] = [rs[i]]
		points_in_cs[kmeans_for_cs.labels_[i]] = [rs_index[i]]

ur = 0
retained_set = []
clusters_of_new_rs = []

retained_set_index = []

for i in cs_labels:
	if len(cs_labels[i]) == 1:
		retained_set.append(cs_labels[i][0])
		retained_set_index.append(points_in_cs[i][0])
		clusters_of_new_rs.append(i)

for i in clusters_of_new_rs:
	del (cs_labels[i])
	del (points_in_cs[i])

cs = {}
# creating statistics for compressed_set
for i in cs_labels:
	points_in_i = cs_labels[i]
	# print(len(points_in_i))
	for point in points_in_i:
		try:
			cluster_statistics = cs[i]
			cluster_statistics[0] += 1
			for j in range(len(point)):
				cluster_statistics[1][j] += point[j]
				cluster_statistics[2][j] += point[j] ** 2
			cs[i] = cluster_statistics
		except:
			cluster_statistics = list()
			cluster_statistics.append(1)
			cluster_statistics.append(point)
			cluster_statistics.append([d ** 2 for d in point])

			cs[i] = cluster_statistics

output_file = sys.argv[3]
output = "Miloni_shah_output.txt"
f1 = open(output, "w+")

f1.write("The intermediate results:\n")
f1.write("Round 1: " + str(bfr.count_points(ds)) + "," + str(len(cs)) + "," + str(bfr.count_points(cs)) + "," + str(len(retained_set)) + "\n")

# work with cs = points_in_cs, retained_set = retained_set_index, ds = points_in_ds
def mahalanobis(dict1, point, forcemerge=False):
	ref = {}
	for key in dict1:

		std_dev = []
		mean = []

		features = dict1[key]
		for i in range(len(features[1])):
			sd = (features[2][i] / features[0] - (features[1][i] / features[0]) ** 2) ** 0.5
			std_dev.append(sd)
			m = features[1][i] / features[0]
			mean.append(m)

		distances = []
		for i in range(len(point)):
			yi = ((point[i] - mean[i]) / std_dev[i]) ** 2
			distances.append(yi)
		root_of_d = sum(distances) ** 0.5
		ref[key] = root_of_d
		# print(key, ref[key])
		# print(std_dev)
		# print("======")

	max_d = max(ref.values())
	clus = -1
	for key in ref:
		if ref[key] < max_d:
			max_d = ref[key]
			clus = key

	if not forcemerge:
		if max_d < 2 * (len(point) ** 0.5):
			return clus
		return -1
	else:
		return clus


def update_stat(dic, point, label):
	try:
		cluster_statistics = dic[label]
		cluster_statistics[0] += 1
		for j in range(len(point)):
			cluster_statistics[1][j] += point[j]
			cluster_statistics[2][j] += point[j] ** 2
		dic[label] = cluster_statistics
	except:
		cluster_statistics = list()

		cluster_statistics.append(1)
		cluster_statistics.append(point)
		cluster_statistics.append([d ** 2 for d in point])

		dic[label] = cluster_statistics
	return dic


# debug
start = 0.2  # 0.2
end = 0.4  # 0.4
roundvalue = 2
while True:

	#print(start, end)
	if start == 1.0:
		break
	new_data = X[int(len(X) * start):int(len(X) * end)]
	new_data_indexes = index[int(len(X) * start):int(len(X) * end)]
	not_assigned_to_ds = []
	not_assigned_to_ds_index = []
	for i in range(len(new_data)):
		eachpoint = new_data[i]
		point_index = new_data_indexes[i]
		cluster_no = mahalanobis(ds, eachpoint)
		if cluster_no == -1:
			not_assigned_to_ds.append(eachpoint)
			not_assigned_to_ds_index.append(point_index)
		else:
			ds = update_stat(ds, eachpoint, cluster_no)
			points_in_ds[cluster_no].append(point_index)

	not_assigned_to_cs = []
	not_assigned_to_cs_index = []
	for i in range(len(not_assigned_to_ds)):
		eachpoint = not_assigned_to_ds[i]
		point_index = not_assigned_to_ds_index[i]
		cluster_no = mahalanobis(cs, eachpoint)
		if cluster_no == -1:
			not_assigned_to_cs.append(eachpoint)
			not_assigned_to_cs_index.append(point_index)
		else:
			cs = update_stat(cs, eachpoint, cluster_no)
			points_in_cs[cluster_no].append(point_index)

	retained_set = retained_set + not_assigned_to_cs
	retained_set_index += not_assigned_to_cs_index

	k = int(len(retained_set) * 0.8)

	kmeans_for_cs = KMeans(n_clusters=k, random_state=0).fit(retained_set)
	newcs_labels = {}
	newcs_index = {}

	for i in range(len(kmeans_for_cs.labels_)):
		try:
			newcs_labels[kmeans_for_cs.labels_[i]].append(retained_set[i])
			newcs_index[kmeans_for_cs.labels_[i]].append(retained_set_index[i])
		except:
			newcs_labels[kmeans_for_cs.labels_[i]] = [retained_set[i]]
			newcs_index[kmeans_for_cs.labels_[i]] = [retained_set_index[i]]

	clusters_of_new_rs = []
	retained_set = []
	retained_set_index = []
	for i in newcs_labels:
		if len(newcs_labels[i]) == 1:
			retained_set.append(newcs_labels[i][0])
			retained_set_index.append(newcs_index[i][0])
			clusters_of_new_rs.append(i)
	for i in clusters_of_new_rs:
		del (newcs_labels[i])
		del (newcs_index[i])

	new_cs = {}
	new_cs_index = {}
	# creating statistics for compressed_set
	for i in newcs_labels:
		points_in_i = newcs_labels[i]
		points_in_i_indexes = newcs_index[i]
		# print(len(points_in_i))
		for j in range(len(points_in_i)):
			point = points_in_i[j]
			point_index = points_in_i_indexes[j]
			try:
				cluster_statistics = new_cs[i]
				cluster_statistics[0] += 1
				for j in range(len(point)):
					cluster_statistics[1][j] += point[j]
					cluster_statistics[2][j] += point[j] ** 2
				new_cs[i] = cluster_statistics
				new_cs_index[i].append(point_index)
			except:
				cluster_statistics = list()

				cluster_statistics.append(1)
				cluster_statistics.append(point)
				cluster_statistics.append([d ** 2 for d in point])

				new_cs[i] = cluster_statistics
				new_cs_index[i] = [point_index]

	# new_cs and cs both have CS
	# now checking mah dist between them
	unmerged = []
	for i in new_cs:
		fv = new_cs[i]
		centroid = [x / fv[0] for x in fv[1]]

		to_be_label = mahalanobis(cs, centroid)
		if to_be_label == -1:
			unmerged.append(i)
		else:
			cs[to_be_label][0] += fv[0]
			for j in range(len(fv[1])):
				cs[to_be_label][1][j] += fv[1][j]
				cs[to_be_label][2][j] += fv[2][j]
			points_in_cs[to_be_label] += new_cs_index[i]

	max_index = max(cs.keys())
	for i in range(len(unmerged)):
		cs[max_index + i + 1] = new_cs[unmerged[i]]
		points_in_cs[max_index + i + 1] = new_cs_index[unmerged[i]]

	start = end
	end = start + 0.2
	f1.write("Round " + str(roundvalue) +": " + str(bfr.count_points(ds)) + "," + str(len(cs)) + "," + str(bfr.count_points(cs)) + "," + str(len(retained_set)) + "\n")
	roundvalue = roundvalue + 1



for i in cs:

	fv = cs[i]
	centroid = [x / fv[0] for x in fv[1]]

	to_be_label = mahalanobis(ds, centroid, True)
	ds[to_be_label][0] += fv[0]
	for j in range(len(fv[1])):
		ds[to_be_label][1][j] += fv[1][j]
		ds[to_be_label][2][j] += fv[2][j]

	points_in_ds[to_be_label] += points_in_cs[i]

f1.write("Round 6: " + str(bfr.count_points(ds)) + ",0,0," + str(len(retained_set)) + "\n")

f1.write("The clustering results:\n")
kkkk = []

for k in points_in_ds:
	vs = points_in_ds[k]
	for v in vs:
		kkkk.append((v, k))

kkkk = sorted(kkkk, key=lambda x: int(x[0]))

for v, k in kkkk:
	f1.write(str(v) + "," + str(k) + "\n")

for point in retained_set_index:
	f1.write(str(point) + ",-1\n")

f1.close()

