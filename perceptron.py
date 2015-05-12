#from __future__ import division
import sys, math, operator, random
import numpy as np
import numpy.linalg as la
from signalsmooth import smooth
from sklearn import svm

class Perceptron:

	def __init__(self):
		# per-class weights
		self.weights = {}
		# bias (0 for no bias)
		self.bias = 0
		# maximum epoch
		self.max_epoch = 16
		# training set
 		self.trainSet = []
		# classes
		self.classes = ['Normal', 'Anomaly']
		self.size_normal_train = 0
		self.size_anomaly_train = 0

	def initial_weights(self):
		train_point = self.trainSet[0].keys()[0]
		length = len(train_point)
		for i in self.classes: # only two classes
			# initialize weights as zeros
			w = [0 for x in range(length)]
			self.weights[i] = w

	def learning_rate(self, epoch):
		return 1000. / (1000 + epoch)

	def getLabel_arr(self, sample):
		c = {}
		for label in self.classes:
			c[label] = 0
			for i in range(sample.shape[0]):
				c[label] += self.weights[label][i] * sample[i]
		return max(c.iteritems(), key=operator.itemgetter(1))[0]

	def preProcess(self):
		arr_normal, arr_anomaly = self.smooth()
		for i in range(arr_normal.shape[0]):
			arr_normal[i] = self.feature_scaling(arr_normal[i])
		for i in range(arr_anomaly.shape[0]):
			arr_anomaly[i] = self.feature_scaling(arr_anomaly[i])
		array = np.vstack([arr_normal, arr_anomaly])
		label_normal = [0 for x in range(arr_normal.shape[0])]	
		label_anomaly = [1 for x in range(arr_anomaly.shape[0])]
		#label_normal = ['Normal' for x in range(arr_normal.shape[0])]	
		#label_anomaly = ['Anomaly' for x in range(arr_anomaly.shape[0])]
		label = label_normal + label_anomaly
		#return array, np.array(label)
		self.array = array
		self.label = np.array(label)

	def getLabel(self, sample):
		#return self.getLabel_arr(np.array(sample, dtype=float))
		clf = svm.SVC(kernel='rbf')
		clf.fit(self.array, self.label)
		return clf.predict(sample)[0] 

	def smooth(self):
		# create array of training data
		arr_normal = np.array(self.trainSet[0].keys()[0], dtype=float)
		arr_anomaly = np.array(self.trainSet[0].keys()[0], dtype=float)
		for i in range(0, len(self.trainSet)):
			train_point = self.trainSet[i].keys()[0]
			label = self.trainSet[i][train_point]
			if label == 'Normal':
				arr_normal = np.vstack([arr_normal, np.array(train_point, dtype=float)])
			elif label == 'Anomaly':
				arr_anomaly = np.vstack([arr_anomaly, np.array(train_point, dtype=float)])
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

	def feature_scaling(self, point):
		length = la.norm(point)
		return point / length

	def learn(self):
		"""training and updating the weights"""
		# smooth the training data
		arr_normal, arr_anomaly = self.smooth()
		# initialize weights
		self.initial_weights()
		for epoch in range(1, self.max_epoch):
			decay = self.learning_rate(epoch)
			correct_count = 0
			# loop over normal data
			for i in range(arr_normal.shape[0]):
				train_point = arr_normal[i]
				label = 'Normal'
				# do feature scaling of the train sample
				train_point = self.feature_scaling(train_point)
				#print train_point
				#print type(train_point)
				our_label = self.getLabel_arr(train_point)
				if label != our_label:
					for j in range(train_point.shape[0]):
						self.weights[label][j] = self.weights[label][j] + decay * train_point[j]
						self.weights[our_label][j] = self.weights[our_label][j] + decay * train_point[j]
				else:
					correct_count += 1
			# loop over anomaly data
			for i in range(arr_anomaly.shape[0]):
				train_point = arr_anomaly[i]
				label = 'Anomaly'
				# do feature scaling of the train sample
				train_point = self.feature_scaling(train_point)
				our_label = self.getLabel_arr(train_point)
				if label != our_label:
					for j in range(train_point.shape[0]):
						self.weights[label][j] = self.weights[label][j] + decay * train_point[j]
						self.weights[our_label][j] = self.weights[our_label][j] + decay * train_point[j]
				else:
					correct_count += 1
			#print self.weights
			print "Epoch = ", epoch, ", Accuracy = %g" %(float(correct_count) / len(self.trainSet))

if __name__ == "__main__":
	"""Simple XOR testing using svm """
	X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
	y = np.array([0, 1, 1, 0])
	clf = svm.SVC(kernel='rbf')
	clf.fit(X, y)
	print clf.predict(X)
