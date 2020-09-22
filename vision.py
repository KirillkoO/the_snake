class Vision():

#-------------------------------------------------------------------------
	def __init__(self, directions, sourceX, sourceY, width_x, height_y):
		super().__init__()
		self.dir = directions #takes setted directions
		self.sourceX = sourceX #source left point (x axis)
		self.sourceY = sourceY #source left point (y axis)
		self.width_x = width_x #get width_x of field
		self.height_y = height_y #get height_y of field
		self.coef = width_x if width_x > height_y else height_y #coefficient for calculating of distance to wall
#-------------------------------------------------------------------------
# 8 directions of vision
	def dist_to_wall(self, head):
		list_of_dist = [] #list of the calculated distancies
		(x_head, y_head) = head #get x and y of head
		(x, y) = (x_head - self.sourceX, y_head - self.sourceY) #bring x and y to zero
		for i in range(len(self.dir)):
			dir = self.dir[i] #get current direction
			(x_cur, y_cur) = (x + dir[0]*20, y + dir[1]*20) #calc position in front of the head
			k = 0 #count cells to wall
			while (x_cur >= 0 and y_cur >= 0 and x_cur < self.width_x*20 and y_cur < self.height_y*20): #increment var while within playing field
				k += 1
				x_cur += dir[0]*20
				y_cur += dir[1]*20
			dist = round(k/(self.coef), 1) #divide on coef 
			list_of_dist.append(dist)
		return list_of_dist
#-------------------------------------------------------------------------
# check if the fruit is looked by vision
	def fruit_in_vision(self, head, fruit):
		vision_fruits = [0 for i in range(len(self.dir))] #list of visions
		(x_head, y_head) = head #get x and y of the head
		(x_fruit, y_fruit) = fruit #get x and y of the fruit
		for i in range(len(self.dir)):
			dir = self.dir[i] #get current direction
			(cur_x, cur_y) = (x_head + dir[0], y_head + dir[1]) #calculate next cell for current dir
			while(cur_y >= self.sourceY and cur_y <= self.sourceY + self.height_y*20 and cur_x >= self.sourceX and cur_x <= self.sourceX + self.width_x*20): #check all cells for current dir if fruit is stayed on the way
				if (y_fruit == cur_y and x_fruit == cur_x): #check if current x and y equal fruit position
					vision_fruits[i] = 1 #set 1 if vision is seeing fruit
				cur_x += dir[0] #step over to next cell 
				cur_y += dir[1] #step over to next cell
		return vision_fruits
#-------------------------------------------------------------------------
# check if the tail of the snake is looked by vision
	def tail_in_vision(self, snake):
		vision_tail = [0 for i in range(len(self.dir))] #list of visible parts of the tail
		(x_head, y_head) = snake[0].get_pos() #get position of the snake's head
		for i in range(len(self.dir)):
			dir = self.dir[i]
			count = 0 #var for calculate distance to the tail
			(cur_x, cur_y) = (x_head + dir[0], y_head + dir[1]) #current position
			while(cur_y >= self.sourceY and cur_y < self.sourceY + self.height_y*20 and cur_x >= self.sourceX and cur_x < self.sourceX + self.width_x*20):
				for j in range(1, len(snake)):
					(x_cell, y_cell) = snake[j].get_pos() #get x and y of every cell
					if (cur_y == y_cell and cur_x == x_cell):
						vision_tail[i] = round((self.height_y * self.width_x - count)/(self.height_y * self.width_x), 1) #dist to the tail's cell
						break
				count += 1 #add one as next step
				cur_x += dir[0] #next cur pos
				cur_y += dir[1] #next cur pos
		return vision_tail
#------------------------------------------------------------------------
# collect all data as inputs for neural network
	def inputs(self, head, fruit, snake):
		inputs = self.dist_to_wall(head) + self.fruit_in_vision(head, fruit) + self.tail_in_vision(snake) #union all data
		return inputs
#------------------------------------------------------------------------