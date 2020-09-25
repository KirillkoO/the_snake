from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import *
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.core.window import Window
import random
import vision
import neural
import genetic

#-------------------------------------------------------------------------
#-------------------------------------------------------------------------
# cell of snakes
class Cell(Widget):
	def __init__(self, x, y):
		super().__init__()
		self.pos = (x, y)
		self.size = (20, 20)
#-------------------------------------------------------------------------
	def get_pos(self):
		return self.pos
#-------------------------------------------------------------------------
	def set_pos(self, x, y):
		self.pos = (x, y)
#-------------------------------------------------------------------------
#-------------------------------------------------------------------------
# worm, basic object for game
# directions of the snake moving: (1, 0) - right, (-1, 0) - left, (0, 1) - up, (0, -1) - down
class Worm(Widget):
	def __init__(self, sourceX, sourceY, width_x, height_y):
		super().__init__()
		self.sourceX = sourceX #source point x
		self.sourceY = sourceY #source point y
		self.width_x = width_x #width_x of playing field
		self.height_y = height_y #height_y of playing field
		self.snake = [] #list of cells of the snake
		self.init_snake(sourceX, sourceY, width_x, height_y) #init starting snake
		self.eated_state = None
#-------------------------------------------------------------------------
# build the start snake
	def init_snake(self, sourceX, sourceY, width_x, height_y):
		cell_1 = Cell(sourceX + int(width_x/2)*20, sourceY + int(height_y/2)*20) #create cell in the center of playing field
		cell_2 = Cell(sourceX + int(width_x/2)*20 - 20, sourceY + int(height_y/2)*20) #the snake is turning on to the right
		self.add_widget(cell_1) 
		self.add_widget(cell_2)
		self.snake.append(cell_1)
		self.snake.append(cell_2)
#-------------------------------------------------------------------------
# return snake
	def get_snake(self):
		return self.snake
#-------------------------------------------------------------------------
# return eated state
	def get_eated_state(self):
		return self.eated_state
#-------------------------------------------------------------------------
# calculate new position
	def new_pos(self, dir):
		(x_head, y_head) = self.snake[0].get_pos() #get head position
		(x_new, y_new) = (x_head + dir[0]*20, y_head + dir[1]*20) #calc new head position
		return (x_new, y_new)
#-------------------------------------------------------------------------
# check if the snake has left the playing field
	def is_leave(self, dir):
		(x_new, y_new) = self.new_pos(dir) #calc new position
		if (x_new < self.sourceX or y_new < self.sourceY or x_new >= self.sourceX + self.width_x*20 or y_new >= self.sourceY + self.height_y*20):
			return True
		return False
#-------------------------------------------------------------------------
# check if the snake has bitten itself
	def is_bite(self, dir):
		(x_new, y_new) = self.new_pos(dir) #calc new position
		(x_head, y_head) = self.snake[0].get_pos() #get x and y of the snake
		for i in range(2, len(self.snake)):
			(x_cell, y_cell) = self.snake[i].get_pos() #get x and y every cell beginning from 2 index of the snake
			if (x_head == x_cell and y_head == y_cell): #if coordinates match that means the snake has bitten itself
				return True
			return False
#-------------------------------------------------------------------------
# union two methods (is_leave and is_bite) to one 
	def is_alive(self, dir):
		if (not self.is_leave(dir) and not self.is_bite(dir)):
			return True
		return False
#-------------------------------------------------------------------------
# the snake can move. The last cell removes and becomes to the new position 
	def move(self, dir, fruit):
		(x_fruit, y_fruit) = fruit.get_pos() #get pos of the fruit
		(x_new, y_new) = self.new_pos(dir) #calc new pos
		if (x_fruit == x_new and y_fruit == y_new): #if snake eated the fruit
			new_cell = Cell(x_new, y_new) #create new cell of the snake
			self.snake.insert(0, new_cell) #add new cell to the snake list
			self.add_widget(new_cell) #add new widget
			self.eated_state = True
		else:
			last_cell = self.snake[-1] #get last cell
			self.snake.remove(last_cell) #remove cell
			last_cell.set_pos(x_new, y_new) #move it to the new position
			self.snake.insert(0, last_cell) #insert last cell to begin of the list
			self.eated_state = False
#-------------------------------------------------------------------------
#-------------------------------------------------------------------------
class Form(Widget):
	def __init__(self, width_x, height_y):
		super().__init__()
		#---------------------canvas---------------------------------
		with self.canvas: #paint playing field
			Color(1, 1, 1) #white color
			(init_x, init_y) = (Window.size[0] / 2 - width_x * 10, Window.size[1] / 2 - height_y * 10)
			Rectangle(pos = (init_x, init_y), size=(width_x * 20, height_y * 20)) #adaptive playing field with fix cell (20 px)
			Color(0, 0, 0) #black color
			for i in range(height_y):
				Line(points=[init_x, init_y + i*20, init_x + width_x * 20, init_y + i*20])
			for i in range(width_x):
				Line(points=[init_x + i*20, init_y, init_x + i*20, init_y + height_y * 20])
		#----------------------------------------------------------------
		self.width_x = width_x #width_x of playing field
		self.height_y = height_y #height_y of playing field
		self.sourceX = int(Window.size[0] / 2) - width_x * 10 #left edge point (x axes)
		self.sourceY = int(Window.size[1] / 2) - height_y * 10 #left edge point (y axes)
		self.worm = None #instance of the snake
		self.fruit = None #instance of the fruit
		self.count_start = -1 #count of game start
		self.population = 250 #number of snakes in population
		self.vision_dir = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)] #set of the vision directions
		self.vision = vision.Vision(self.vision_dir, self.sourceX, self.sourceY, self.width_x, self.height_y) #instance for vision
		self.dir = (1, 0) #start direction
		self.ff = neural.FeedForward(self.population) #instance for neural network
		t = self.ff.load_snakes() #load all snakes from file
		self.snakes = t[0]
		self.random_seed = t[1]
		self.snakes_offspring = None #instance for offspring snakes
		self.mutation_rank = 0.1 #rank of mutation
		self.cur_snake = None #instance for current playing snake
		self.matrices = None #instance of matrix for current snake
		self.count_moves = 0 #count of the snake moves
		self.count_fruit = 0 #count of fruit that was eatten by snake
		self.fitness_source = [0 for i in range(self.population)] #var for save fitness score every snake in source population
		self.fitness_offspring = [0 for i in range(self.population)] #var for save fitness score every snake in offspring population
		self.count_try = 2 #number of attemps to play the game of the population
		self.current_try = 1 #current try
		self.queue_population = False #queue population (if false - queue of source population, true - offspring)
		self.generation = 0 #count generation
		self.sum_fruit = 0 
		#-----------------------------------------------------------------
		self.text1 = Label(pos=(self.sourceX + 70, self.sourceY - 100), text='Count start:') 
		self.text2 = Label(pos=(self.sourceX + 240, self.sourceY - 100), text='0')
		self.add_widget(self.text1)
		self.add_widget(self.text2) #labels for display count start
		self.text3 = Label(pos=(self.sourceX + 70, self.sourceY + self.height_y*20 + 30), text="Generation:")
		self.text4 = Label(pos=(self.sourceX + 240, self.sourceY + self.height_y*20 + 30), text="0")
		self.add_widget(self.text3)
		self.add_widget(self.text4) #labels for display generation
		
		self.text5 = Label(pos=(self.sourceX + 70, self.sourceY - 250), text='0')
		self.add_widget(self.text5)
		self.text6 = Label(pos=(self.sourceX + 70, self.sourceY - 175), text='0')
		self.add_widget(self.text6)
		self.text7 = Label(pos=(self.sourceX + 240, self.sourceY - 250), text='0')
		self.add_widget(self.text7)
#-------------------------------------------------------------------------
# calculate and return empty position to place the fruit
	def get_empty_pos(self, width_x, height_y):
		snake_pos = [] #list of position of the snake's cells 
		empty_pos = [] #list for empty positions
		for i in range(len(self.worm.get_snake())):
			(x_pos, y_pos) = self.worm.get_snake()[i].get_pos() #get coordinates of snake's cells
			snake_pos.append((x_pos, y_pos)) #add it to the list
		matrix = [[0 for x in range(self.height_y)] for y in range(self.width_x)] #create empty matrix with our width_x and height_y
		for i in range(self.width_x):
			for j in range(self.height_y):
				for k in range(len(snake_pos)):
					if (self.sourceY + i*20 == snake_pos[k][0] and self.sourceX + j*20 == snake_pos[k][1]): #fill matrix 
						matrix[i][j] = 1
		for i in range(self.width_x):
			for j in range(self.height_y):
				if (matrix[i][j] != 1): #if current position empty add it to the list
					empty_pos.append((i, j))
		(x, y) = random.choice(empty_pos) #choice random position from the list
		return (self.sourceX + x*20, self.sourceY+y*20)
#-------------------------------------------------------------------------
# fitness function
	def fitness(self):
		return self.count_fruit
#-------------------------------------------------------------------------
# compare two population
# length of source population and their offspring is equal
	def compare_population(self, source, offspring):
		source_sum = max(source)
		offspring_sum = max(offspring)
		#for i in range(len(source)):
			#source_sum += source[i]**2 #than bigger number fruit the snake has eaten, than bigger score it getting
			#offspring_sum += offspring[i]**2
		self.text6.text =str([source_sum, offspring_sum])
		#if (offspring_sum >= source_sum): #if offspring population has got more score than source return true
		if (source_sum <= offspring_sum):
			return True
		return False
#-------------------------------------------------------------------------
# snakes play in turn
	def queue_game(self):
		self.current_try +=1 #plus one try
		if (self.current_try == self.count_try and not self.queue_population): #as all snakes in population has played in game self.count_try times
			self.current_try = 1 #reset current try to 1 for offspring population
			self.queue_population = True #source population finished its tries
			self.learning_offspring()
		elif (self.current_try == self.count_try and self.queue_population): #queue of source population
			self.current_try = 1
			self.queue_population = False
			if (self.compare_population(self.fitness_source, self.fitness_offspring)): #compare source and offspring populations
				self.snakes = self.snakes_offspring #set to self.snakes its offspring
				self.ff.save_snakes((self.snakes, self.random_seed)) #and save in the file
				self.learning_offspring()
				self.queue_population = True
				self.fitness_source = self.fitness_offspring #reset fitness score
				self.fitness_offspring = [0 for i in range(len(self.snakes))] #offspring fitness score too
				self.generation += 1 #one generation has passed
				self.text4.text = str(self.generation) #display current generation
			else:
				self.learning_offspring() #learning offspring again
				self.queue_population = True
				self.fitness_offspring = [0 for i in range(len(self.snakes))]
#-------------------------------------------------------------------------
# learning neural network
	def learning_offspring(self):
		self.snakes_offspring = genetic.Genetic.gen(self.snakes, self.fitness_source, self.mutation_rank)
#-------------------------------------------------------------------------
	def update(self, _):
		inputs = self.vision.inputs(self.worm.get_snake()[0].get_pos(), self.fruit.get_pos(), self.worm.get_snake()) #get input layer from vision
		self.dir = self.ff.feed_forward(self.matrices, inputs, self.dir) #calculate direction for snake moving
		if self.worm.is_alive(self.dir): #if the current snake is alive keep going
			self.worm.move((self.dir), self.fruit) #make a move
			self.count_moves += 1 #add one to move count 
			if (self.worm.get_eated_state()): #if the snake ate the fruit
				self.count_fruit += 1 #add one to fruit count
				if (self.count_fruit == self.width_x * self.height_y - 3):
					self.full_stop()
				(x, y) = self.get_empty_pos(self.width_x, self.height_y) #get new empty position to place fruit
				self.fruit.set_pos(x, y) #set new position of the fruit
			if (self.count_moves/(self.count_fruit + 1) > 100): #if the snake begin moving round 
				self.stop() #interrupt game after 100 moves
		else: #if the snake died 
			self.stop() #reset game
#-------------------------------------------------------------------------
	def start(self):
		self.dir = (1, 0) #reset start direction
		self.count_moves = 0 #reset count moves
		self.count_fruit = 0 #reset count fruit
		self.count_start += 1 #each start plus one, for load neccesery snake
		self.text7.text = str(self.random_seed)
		if (self.count_start < self.population - 1):
			if (not self.queue_population):
				self.cur_snake = self.snakes[self.count_start] #number of snake that playing in game
				self.matrices = self.ff.vector_to_matrices(self.cur_snake) #transform vector to weight matrices
			elif (self.queue_population):
				self.cur_snake = self.snakes_offspring[self.count_start]
				self.matrices = self.ff.vector_to_matrices(self.cur_snake)
			self.worm = Worm(self.sourceX, self.sourceY, self.width_x, self.height_y) #create the snake 
			self.add_widget(self.worm) # add widget on the form
			random.seed(self.random_seed)
			(x, y) = self.get_empty_pos(self.width_x, self.height_y) #get emtpy position to place the fruit
			self.fruit = Cell(x, y) #create the fruit
			self.add_widget(self.fruit) #add widget
		elif (self.count_start == self.population - 1):
			self.sum_fruit = 0 #reset 
			self.count_start = -1 #reset count
			self.queue_game() #define whose of queue
			self.random_seed = random.choice(range(-1000000, 1000000))
			#self.learning() #when all snakes has tried gather fruit
		self.text2.text = str(self.count_start) #display count start
		Clock.schedule_interval(self.update, 0.001) #start the clock
#-------------------------------------------------------------------------
# stop game, reset all play objects
	def stop(self):
		self.sum_fruit += self.count_fruit ** 2
		self.text5.text = str(self.sum_fruit)
		if (self.queue_population):
			self.fitness_offspring[self.count_start] += self.count_fruit #if offspring population has queue to play, count number of the fruit to fitness_offspring
		else:
			self.fitness_source[self.count_start] += self.count_fruit #correspondly with source population
		self.remove_widget(self.worm) #remove snake
		self.remove_widget(self.fruit) #remove fruit
		Clock.unschedule(self.update) #stop the clock
		self.start() #start again
#-------------------------------------------------------------------------
	def full_stop(self):
		Clock.unschedule(self.update)
		self.ff.save_snakes((self.snakes_offspring, self.random_seed))
#-------------------------------------------------------------------------
#-------------------------------------------------------------------------
class SnakeApp(App):
	def build(self):
		self.form = Form(4, 4)
		self.form.start()
		return self.form

if __name__ == '__main__':
	SnakeApp().run()