import random
import pickle
import os.path
import math

class FeedForward():
	
#-------------------------------------------------------------------------
	def __init__(self, population):
		super().__init__()
		self.weights_1 = None
		self.weights_2 = None
		self.weights_3 = None 
		self.vector = None
		self.quantity = population #quantity of snakes in the file (population)
	
#-------------------------------------------------------------------------
# 24 items in the inputs (8 looking directions), 3 layers in neural network (24x18, 18x12, 12x4)
	def feed_forward(self, mat, inputs, dir):
		(w_1, w_2, w_3) = mat
		second_layer = []
		third_layer = []
		output_layer = []
		for i in range(18): #calculate the second layer output
			sum = 0
			for j in range(24):
				sum += inputs[j] * w_1[i][j]
			y = self.relu(sum)
			second_layer.append(y)
		for i in range(12): #calculate the third layer output
			sum = 0
			for j in range(18):
				sum += second_layer[j] * w_2[i][j]
			y = self.relu(sum)
			third_layer.append(y)
		for i in range(4): #calculate the output layer
			sum = 0
			for j in range(12):
				sum += third_layer[j] * w_3[i][j]
			y = self.sigma(sum)
			output_layer.append(y)
		maximum = max(output_layer) #find the maximum in the output layer
		index_max = output_layer.index(maximum) #find index of the maximum
		#let's assume that the index 0 is the direction left, 1 - right, 2 - down, 3 - up
		if (index_max == 0 and dir != (1, 0)): #left
			return (-1, 0)
		elif (index_max == 1 and dir != (-1, 0)): #right
			return (1, 0)
		elif (index_max == 2 and dir != (0, 1)): #down
			return (0, -1)
		elif (index_max == 3 and dir != (0, -1)): #up
			return (0, 1)
		else:
			return dir
#-------------------------------------------------------------------------
# ReLU
	def relu(self, x):
		if (x > 0):
			return x
		else:
			return 0
#-------------------------------------------------------------------------
# sigma
	def sigma(self, x):
		return 1/(1 + math.exp(-x))
#-------------------------------------------------------------------------
# transformation a vector (696) to matrices (24x18, 18x12, 12x4)
	def vector_to_matrices(self, vec):
		w_1 = [[0 for i in range(24)] for j in range(18)] #24x18 
		w_2 = [[0 for i in range(18)] for j in range(12)] #18x12
		w_3 = [[0 for i in range(12)] for j in range(4)] #12x4
		for i in range(696):
			if (i < 432): #24x18 = 432
				w_1[int(i/24)][i%24] = vec[i]
			elif (i >= 432 and i < 648): #432 + 18x12 = 648
				w_2[int((i-432)/18)][i%18] = vec[i]
			elif (i >= 648):
				w_3[int((i-648)/12)][i%12] = vec[i]
		return (w_1, w_2, w_3)
		
#-------------------------------------------------------------------------
# transformation matrices to the vector
	def matrices_to_vector(self, mat):
		(w_1, w_2, w_3) = mat
		x = [0 for i in range(696)] #vector of zeros
		k = 0 #iteration var for vector
		for i in range(len(w_1)): #first wieghts (w_1) is in beginning of the vector 
			for j in range(len(w_1[i])):
				x[k] = w_1[i][j]
				k += 1
		for i in range(len(w_2)):
			for j in range(len(w_2[i])):
				x[k] = w_2[i][j]
				k += 1
		for i in range(len(w_3)):
			for j in range(len(w_3[i])):
				x[k] = w_3[i][j]
				k +=1
		return x
#-------------------------------------------------------------------------
# load snakes (self.quantity snakes in file)	
	def load_snakes(self):
		file = 'snakes.txt'
		if (os.path.exists(file)):
			f = open(file, 'rb')
			snakes = pickle.load(f)
			return snakes
		else:
			x = [[round(random.uniform(-1, 1), 2) for i in range(696)] for j in range(self.quantity)]
			f = open(file, 'wb')
			pickle.dump(x, f)
			f.close()
			return x
#-------------------------------------------------------------------------
# save snakes in the file
	def save_snakes(self, snakes):
		file = 'snakes.txt'
		f = open(file, 'wb')
		pickle.dump(snakes, f)
		f.close()
#-------------------------------------------------------------------------
#--------------------------tests---------------------------------------
#-------------------------------------------------------------------------
# test of the vector to matrices function
	def test_vec_to_mat(self):
		x = [random.random() for i in range(696)]
		t = FeedForward().vector_to_matrices(x)
		if (x[0] == t[0][0][0]):
			print("first element passed")
		if (x[695] == t[2][3][11]):
			print("last element passed")
			
#-------------------------------------------------------------------------
# test of the matrices to vector funtion
	def test_mat_to_vec(self):
		w_1 = [[random.random() for i in range(24)] for j in range(18)]
		w_2 = [[random.random() for i in range(18)] for j in range(12)]
		w_3 = [[random.random() for i in range(12)] for j in range(4)]
		mat = (w_1, w_2, w_3)
		t = FeedForward().matrices_to_vector(mat)
		if (w_1[0][0] == t[0]):
			print("first element passed")
		if (w_2[0][0] == t[432]):
			print("matrix 2 correspond to element in vector")
		if (w_3[0][0] == t[648]):
			print("matrix 3 correspond to element in vector")
		if (w_3[3][11] == t[695]):
			print("last element passed")
#-------------------------------------------------------------------------
# test of relu
	def test_relu(self):
		if (1 == FeedForward().relu(1) and 0 == FeedForward().relu(-3)):
			print("relu test passed")
#-------------------------------------------------------------------------
# test of feed forward
	def test_feed_forward(self):
		inputs = [random.random() for i in range(24)]
		w_1 = [[random.uniform(-1, 1) for i in range(24)] for j in range(18)]
		w_2 = [[random.uniform(-1, 1) for i in range(18)] for j in range(12)]
		w_3 = [[random.uniform(-1, 1) for i in range(12)] for j in range(4)]
		mat = (w_1, w_2, w_3)
		FeedForward().feed_forward(mat, inputs, (0, 1))
		
