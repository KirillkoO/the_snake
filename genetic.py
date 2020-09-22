import random

class Genetic():
	
#-------------------------------------------------------------------------
#my selection method. random pointer in list of snakes population. after calculate probability of selection of specific snake
	def selection_one(snakes, score):
		snake = None #choosed snake
		max_ = max(score) #get maximum value in score list
		while (snake is None):
			index = random.choice(range(0,len(score) - 1)) #choose random pointer
			cur_score = score[index] #get choosed score
			probably = 0.8*(cur_score)/(max_ + 1) #calculate of probability
			if (random.random() < probably):
				snake = snakes[index] #snake was choosed
		return snake
#-----------------------------------------------------------------------
# crossover of two parents
	def crossover_one(snake_1, snake_2):
		offspring_1 = [0 for i in range(len(snake_1))] #every two parents produce two children
		offspring_2 = [0 for i in range(len(snake_1))]
		for i in range(len(snake_1)):
			if (random.random() > 0.5):
				offspring_1[i] = snake_1[i] #with probability 0.5 that offspring_1 get gene from snake_1
				offspring_2[i] = snake_2[i] 
			else:
				offspring_1[i] = snake_2[i]
				offspring_2[i] = snake_1[i]
		return [offspring_1, offspring_2]
#-------------------------------------------------------------------------
# mutation. mutation of random genes
	def mutation_one(snake_1, mut):
		snake_mut = [0 for i in range(len(snake_1))] #create empty snake
		for i in range(len(snake_1)):
			if (random.random() < mut):
				snake_mut[i] = round(random.uniform(-1, 1),1) #replace current gene on random gene
			else:
				snake_mut[i] = snake_1[i]
		return snake_mut
#-------------------------------------------------------------------------
# algorithm of learning
	def gen(population, score, mut):
		random.seed(None)
		offspring = [] #list of offspring snakes
		while (len(offspring) < len(score)):
			parent_1 = Genetic.selection_one(population, score)
			parent_2 = Genetic.selection_one(population, score) #choose two snakes with best fitness score
			[offspring_1, offspring_2] = Genetic.crossover_one(parent_1, parent_2) #calculate offspring snakes
			t = random.random()
			if (t < 0.1):# probability mutate the offspring snakes
				mut_1 = Genetic.mutation_one(offspring_1, mut)
				mut_2 = Genetic.mutation_one(offspring_2, mut/10)
			elif (t >= 0.1 and t < 0.2):
				mut_1 = Genetic.mutation_one(offspring_2, 0.9 * mut) 
				mut_2 = Genetic.mutation_one(offspring_1, 0.9 * mut/10)
			elif (t >= 0.2 and t < 0.3):
				mut_1 = Genetic.mutation_one(offspring_2, 0.8 * mut) 
				mut_2 = Genetic.mutation_one(offspring_1, 0.8 * mut/10)
			elif (t >= 0.3 and t < 0.4):
				mut_1 = Genetic.mutation_one(offspring_2, 0.7 * mut) 
				mut_2 = Genetic.mutation_one(offspring_1, 0.7 * mut/10)
			elif (t >= 0.4 and t < 0.5):
				mut_1 = Genetic.mutation_one(offspring_2, 0.6 * mut) 
				mut_2 = Genetic.mutation_one(offspring_1, 0.6 * mut/10)
			elif (t >= 0.5 and t < 0.6):
				mut_1 = Genetic.mutation_one(offspring_2, 0.5 * mut) 
				mut_2 = Genetic.mutation_one(offspring_1, 0.5 * mut/10)
			elif (t >= 0.6 and t < 0.7):
				mut_1 = Genetic.mutation_one(offspring_2, 0.4 * mut) 
				mut_2 = Genetic.mutation_one(offspring_1, 0.4 * mut/10)
			elif (t >= 0.8 and t < 0.9):
				mut_1 = Genetic.mutation_one(offspring_2, 0.3 * mut) 
				mut_2 = Genetic.mutation_one(offspring_1, 0.3 * mut/10)
			elif (t >= 0.9 and t < 1):
				mut_1 = Genetic.mutation_one(offspring_2, 0.2 * mut) 
				mut_2 = Genetic.mutation_one(offspring_1, 0.2 * mut/10)
			else:
				mut_1 = offspring_1
				mut_2 = offspring_2
			offspring.append(mut_1)
			offspring.append(mut_2) #append offspring snakes to list until it have number population
		return offspring
#-------------------------------------------------------------------------
#snakes = [[round(random.uniform(-1,1),2) for i in range(696)] for j in range(500)]
#score = [round(random.uniform(0, 398),2) for i in range(500)]			
#print(Genetic.selection_one(snakes, score))
#snake_1 = [round(random.random(),2) for i in range(696)]
#snake_2 = [round(random.random(),2) for i in range(696)]
#snake_3 = [round(random.uniform(-1,1),2) for i in range(696)]
#print(Genetic.gen(snakes, score, len(score), 0.05))
#print(Genetic.crossover_one(snake_1, snake_2))
#print(Genetic.mutation_one(snake_1, 0.05))
#print(random.choice(range(0, 100)))
