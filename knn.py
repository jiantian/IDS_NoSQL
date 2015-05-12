#from commands import division
import numpy as np
import numpy.linalg as la
import sys, math, operator
from signalsmooth import smooth

"""
 k-nearest neighbor for outlier dectection in mongoDB workflow.
"""
class KNN:

	def __init__(self):
		"""
		Training set. Each entry in trainSet is a {(point):flag} pair.
		Need to use a list in case of duplicated points
		"""
		self.trainSet = []
		"""
		Count for the size of the normal training data
		"""
		self.size_normal_train = 0
		"""
		Count for the size of the anomaly training data
		"""
		self.size_anomaly_train = 0

	"""
	Normalize a vector (point) by converting it to a unit vector
	by dividing each value by the length of the vector.
	The normarlized values are between [0,1].
	@param point: vector
	"""
	def feature_scaling(self, point):
		length = la.norm(np.array(point))
		return tuple([x / length for x in point])

	"""
	Calculate the Euclidean distance between two points
	@param point1: vector
	@param point2: vector
	"""
	def Euclidean_distance(self, point1, point2):
		return la.norm(np.array(point1) - np.array(point2))

	"""
	Smooth the training data. 
	Apply a boxcar smoothing (moving average) with n point.
	"""
	def smooth(self):
		# create array of training data
		arr_normal = np.array(self.trainSet[0].keys()[0], dtype=float)
		arr_anomaly = np.array(self.trainSet[0].keys()[0], dtype=float)
		for i in range(0, len(self.trainSet)):
			train_point = self.trainSet[i].keys()[0]
			label = self.trainSet[i][train_point]
			if label == 'Normal':
				arr_normal = np.vstack([arr_normal, np.array(train_point)])
			elif label == 'Anomaly':
				arr_anomaly = np.vstack([arr_anomaly, np.array(train_point)])
			else:
				sys.exit("Error in the training data!")
		# delete first row
		arr_normal = np.delete(arr_normal,(0),axis=0)
		arr_anomaly = np.delete(arr_anomaly,(0),axis=0)
		# do smoothing for each of columns
		for col in range(arr_normal.shape[1]):
			arr_normal[:,col] = smooth(arr_normal[:,col])
		for col in range(arr_anomaly.shape[1]):
			arr_anomaly[:,col] = smooth(arr_anomaly[:,col])
		return arr_normal, arr_anomaly
	
	"""
	Get k nearest neighbors
	@param test_point: a vector point
	"""
	def getNeighbors(self, test_point):
		distances = []
		test_point = self.feature_scaling(test_point)
		arr_normal, arr_anomaly = self.smooth()
		for i in range(arr_normal.shape[0]):
			train_point = tuple(arr_normal[i])
			label = 'Normal'
			train_point = self.feature_scaling(train_point)
			dist = self.Euclidean_distance(train_point, test_point)
			distances.append((train_point, label, dist))
		for i in range(arr_anomaly.shape[0]):
			train_point = tuple(arr_anomaly[i])
			label = 'Anomaly'
			train_point = self.feature_scaling(train_point)
			dist = self.Euclidean_distance(train_point, test_point)
			distances.append((train_point, label, dist))
		"""
		for i in range(len(self.trainSet)):
			train_point = self.trainSet[i].keys()[0]
			label = self.trainSet[i][train_point]
			train_point = self.feature_scaling(train_point)
			dist = self.Euclidean_distance(train_point, test_point)
			distances.append((train_point, label, dist))
		"""
		distances.sort(key=operator.itemgetter(2))
		neighbors = []
		# set the k value in KNN algorithm based on the size of training set
		#self.k = min(self.size_normal_train, self.size_anomaly_train)
		self.k = 5
		for i in range(self.k):
			neighbors.append((distances[i][0], distances[i][1]))
		return neighbors

	"""
	Get the label of the test_point by kNN
	@param test_point: the tuple (vector) being tested
	"""
	def getLabel(self, test_point):
		neighbors = self.getNeighbors(test_point)
		votes = {}
		for i in range(len(neighbors)):
			label = neighbors[i][1]
			votes[label] = 1 + votes.get(label, 0)
		sortedVotes = sorted(votes.iteritems(), key=operator.itemgetter(1), reverse=True)
		return sortedVotes[0][0]

if __name__ == "__main__":
	knn_class = KNN()
	print knn_class.feature_scaling((8000,-2,2,6000))
	print knn_class.feature_scaling((8000,0,0,6000))
	print knn_class.Euclidean_distance((0,0),(3,4))
	arr = np.array([[1,2,3],[1,3,4],[2,4,3],[3,2,3]], dtype=float)
	print arr
	arr[:,0] = smooth(arr[:,0])
	print arr
