
from typing import List
import numpy as np
import cv2
import time
import math

counter = int(0)

def count(times:int):
	global counter
	if counter < times:
		counter += 1
		return False
	counter = 0
	return True


class Snake_Particle:
	def __init__(self, p:np.ndarray, v:int):
		self.p = p
		self.v = v
		self.count = 0
		self.dir = 'empty'
		self.head = p
		self.body = []
		# 生成食物
		self.food_generate()
		# print("snake init success, head = ", self.head, ' food = ', self.food)
	def move(self, dir):
		if self.count >= self.v:
			self.count = 0
		else:
			self.count += 1
			return True

		if self.dir == 'empty':
			self.dir = dir
		if self.dir == 'left':
			if dir != 'right':
				self.dir = dir
		if self.dir == 'right':
			if dir != 'left':
				self.dir = dir
		if self.dir == 'up':
			if dir != 'down':
				self.dir = dir
		if self.dir == 'down':
			if dir != 'up':
				self.dir = dir


		tmp_head = self.next_head()		 # 更新临时头部

		if (tmp_head == self.food).all():   # 吃到食物
			self.body_change(True)
			# 更新食物，并且去除在身上或者头上的食物
			self.food_generate()
		elif self.EatSelf(tmp_head):  # 吃到自己
			return False			# 游戏结束
		else:						# 正常移动
			self.body_change()

		self.head = tmp_head
		info = '[SnakeIn]\t' + 'food' + str(self.food) + '\t' +	'head' + str(self.head) + '\t' +'body' + str(self.body) + '\t' +'dir' + self.dir + '\t' +'\n'
		# print(info)
		return True

	# 生成食物
	def food_generate(self):
		self.food = np.array([np.random.randint(0, 16), np.random.randint(0, 16)])
		while (self.food == self.head).all() or self.inBody(self.food):
			self.food = np.array([np.random.randint(0, 16), np.random.randint(0, 16)])
	
	# 计算移动中身体变换的坐标
	def body_change(self, isEatFood = False):
		if isEatFood:		# 吃到食物了
			# 头部前进，身体加1
			self.body.insert(0, self.head)
		else:				# 没有吃到食物
			# 如果身体不是空的，则删除最后一个节点，并且头部前进
			if len(self.body) > 0:
				self.body.insert(0, self.head)
				self.body.pop()
		

	def inBody(self, tmp):
		return self.EatSelf(tmp)

	def EatSelf(self, tmp):
		for node in self.body:
			if (node == tmp).all() == True:
				return True
		return False

	def next_head(self):
		tmp = self.head + self.move_snake()
		if tmp[0] < 0:
			tmp[0] = 15
		elif tmp[0] > 15:
			tmp[0] = 0
		
		if tmp[1] < 0:
			tmp[1] = 15
		elif tmp[1] > 15:
			tmp[1] = 0
		return tmp

	def draw(self, img):
		for i in self.body:
			img[int(i[1]), int(i[0])] = (255,0,0)
		img[int(self.head[1]), int(self.head[0])] = (203,192,255)
		img[int(self.food[1]), int(self.food[0])] = (0,255,0)
			

	def move_snake(self):
		step = np.array([0,0])
		if self.dir == 'left':
			step = np.array([-1,0])
		elif self.dir == 'right':
			step = np.array([1,0])
		elif self.dir == 'up':
			step = np.array([0,-1])
		elif self.dir == 'down':
			step = np.array([0,1])
		# print('[stepInfo]\tstep:',step,'\tdir:',self.dir)
		return step

class Particle:
	def __init__(self, p: np.ndarray, v: np.ndarray, color: tuple):
		self.p = p
		self.v = v
		self.color = color
	def copy(self,color = None):
		if color is None:
			return Particle(self.p, self.v, self.color)
		return Particle(self.p, self.v, color)
	def update(self, p: np.ndarray, v: np.ndarray, dt, dv, kp = 0.5):  # kp 是速度衰减率
		p = p + v * dt
		v = v + dv * dt
		# while not self.inrange(p):
		if (p[0] - 16) > 0:
			p[0] = 16 - (p[0] - 16) * kp		# 判断位置是否符合要求
			v[0] = -v[0] * kp
		if p[0] < 0:
			p[0] = -p[0] * kp
			v[0] = -v[0] * kp
		if (p[1] - 16) > 0:
			p[1] = 16 - (p[1] - 16) * kp
			v[1] = -v[1] * kp
		if p[1] < 0:
			p[1] = -p[1] * kp
			v[1] = -v[1] * kp
		self.p = p
		self.v = v
		# print("self.p = ", self.p)

	def inrange(self, p: np.ndarray):
		return p[0] < 16 and p[1] < 16 and p[0] > 0 and p[1] > 0

	def draw(self, img: np.ndarray):
		if self.inrange(self.p):
			(px_tmp, py_tmp) = (int(self.p[1]), int(self.p[0]))
			tmp_color = self.color + img[px_tmp, py_tmp]
			for channel in tmp_color:
				if channel > 255:
					channel = 255
			img[px_tmp, py_tmp] = tmp_color
			# img[int(self.p[0]), int(self.p[1])] += self.color


plist = List[Particle]
class God:
	def __init__(self, particleList: plist):
		self.particleList = particleList
		# print("particlist",self.particleList[0].v)
	def add(self, p: np.ndarray, v: np.ndarray, color: tuple):
		self.particleList.append(Particle(p, v, color))
	def update(self, dt, da, dv, img, kp = 0.5):
		for p in self.particleList:
			# print("p", p.p + p.v * dt)
			p.update(p.p + p.v * dt, p.v + da * dt, dt, dv, kp)
			p.draw(img)


ball = [[8, 8], 1, (255, 0, 0)]

# 初始化粒子群


def init_particle(n, color = None):
	# 初始化粒子群
	particleList = []

	for i in range(n):
		# 初始化粒子的位置
		p = np.array([np.random.randint(0, 16), np.random.randint(0, 16)])
		# 初始化粒子的速度
		# v = np.array([np.random.randint(-1, 1), np.random.randint(-1, 1)])
		v = np.array([0, 0])
		# 初始化粒子的颜色
		if color is None:
			color = (np.random.randint(0, 255), np.random.randint(0, 255), np.random.randint(0, 255))
		# color = (np.random.randint(0, 255), np.random.randint(0, 255), np.random.randint(0, 255))
		# 初始化粒子
		if n > 1:
			particleList.append(Particle(p, v, color))
		elif n == 1:
			return Particle(p, v, color)
	# print("particleList",particleList[0].p)

	return particleList


# 这个函数才是重中之重
# 这个是物理引擎函数
# 上 -
# 下 +
# 左 -
# 右 +
# _____
# |   |
# |   |
# |   |
# ------
# 其中roll是ax， pitch是ay


# 多粒子模式
god = God(init_particle(1, (50, 10, 20)))
def mutilParticle(roll, pitch, yaw, last_time, src: np.ndarray, color = None):
	global god
	if last_time < 0:	# 需要初始化
		god = God(init_particle(40, color))
		return time.time()
	# 计算上一次到现在的时间
	dt = time.time() - last_time
	g = 6
	# 计算全部粒子的加速度
	dax = g*math.sin(math.radians(roll))
	day = g*math.sin(math.radians(pitch))
	if abs(dax) < 1:
		dax = 0
	if abs(day) < 1:
		day = 0
	da = np.array([dax,day])
	# info = '[Mul1Info]:\tda:({:.3f},{:.3f})'.format(dax, day)
	# print(info)
	dv = da * dt
	# info = '[MulPInfo]:\tdt:{:<.3f}\tg:{:<.3f}\tda:{:<.3f}\tdv:{:<.3f}'.format(
    #         dt, g, da, dv)
	god.update(dt, da, dv, src)
	return time.time()


# 多粒子模式2
god2 = God(init_particle(1, (50, 10, 20)))
def mutilParticle2(roll, pitch, yaw, last_time, src: np.ndarray):
	global god2
	if last_time < 0:  # 需要初始化
		god2 = God(init_particle(40))
		return time.time()
	dt = time.time() - last_time
	g = 6
	# 计算全部粒子的加速度
	dax = g*math.sin(math.radians(roll))
	day = g*math.sin(math.radians(pitch))
	if abs(dax) < 1:
		dax = 0
	if abs(day) < 1:
		day = 0
	da = np.array([dax, day])
	dv = da * dt
	god2.update(dt, da, dv, src)
	return time.time()


asnake = Snake_Particle(np.array([9,9]),3)
# 贪吃蛇模式
def snake(roll,pitch,yaw,last_time,src:np.ndarray):
	global asnake
	if last_time < 0:  # 需要初始化
		asnake = Snake_Particle(np.array([np.random.randint(
			0, 16), np.random.randint(0, 16)]), np.random.randint(1, 5))
		return time.time()
	# 获取方向
	# 判断左右或者前后
	dir = asnake.dir
	if abs(roll) > abs(pitch):
		if roll > 25:
			dir = 'right'
		elif roll < -25:
			dir = 'left'
	else:
		if pitch > 25:
			dir = 'down'
		elif pitch < -25:
			dir = 'up'
	# print('[dir Info]\t',dir)
	ret = asnake.move(dir)
	if not ret:
		return -1
	asnake.draw(src)
	return time.time()

myParticle = Particle(np.array([8, 8]), np.array([0, 0]), (255, 0, 0))
# 流影模式
flows = list()
# file = open('flow.txt', 'w')
def flowShadow(roll, pitch, yaw, last_time, src: np.ndarray):
	global myParticle
	global flows
	num = 15	# 流影数量

	# 单位颜色
	unitColor = (17,0,0)
	if last_time < 0:  # 需要初始化
		myParticle = init_particle(1, (unitColor[0] * num, unitColor[1] * num, unitColor[2] * num))
		for i in range(num):
			flows.append(myParticle.p)
		return time.time()

	dt = time.time() - last_time
	g = 6
	# 计算全部粒子的加速度
	dax = g*math.sin(math.radians(roll))
	day = g*math.sin(math.radians(pitch))
	if abs(dax) < 1:
		dax = 0
	if abs(day) < 1:
		day = 0
	da = np.array([dax, day])
	dv = da * dt

	# 模拟粒子运动，更新位置
	myParticle.update(myParticle.p + myParticle.v * dt, myParticle.v + da * dt, dt, dv)
	myParticle.draw(src)

	# 更新流影
	# if count(3):
	# 	# 循环右移flows列表
	# 	for i in range(len(flows) - 1):
	# 		flows[i] = flows[i + 1]
	# 	flows[-1] = myParticle.p

	# 将flows右移一位
	length = len(flows)
	for i in range(length - 1, -1, -1):
		flows[i] = flows[i - 1]

	flows[0] = myParticle.p
	# file.write( str(myParticle.p) + " --> " + str(flows) + '\n\n')
	# 画流影
	for i in range(num):
		(px_tmp, py_tmp) = (int(flows[i][1]), int(flows[i][0]))
		tmp_color = (unitColor[0] * i, unitColor[1] * i,
		             unitColor[2] * i) + src[px_tmp, py_tmp]
		for channel in tmp_color:
			if channel > 255:
				channel = 255
		src[px_tmp, py_tmp] = tmp_color
	return time.time()


# 新概念贪吃蛇模式
snakehead = Particle(np.array([8, 8]), np.array([0, 0]), (255, 0, 0))
food = np.array([np.random.randint(0, 16), np.random.randint(0, 16)])
snake_flow = list()
def newSnake(roll, pitch, yaw, last_time, src: np.ndarray):
	global snakehead
	global food
	global snake_flow
	if last_time < 0:  # 需要初始化
		snakehead = init_particle(1, (203, 192, 255))
		food = np.array([np.random.randint(0, 16), np.random.randint(0, 16)])
		headaxis = np.array([int(snakehead.p[0]), int(snakehead.p[1])])
		# 初始化流影5次
		for i in range(5):
			snake_flow.append(headaxis)
		while (food == headaxis).all():
			food = np.array([np.random.randint(0, 16), np.random.randint(0, 16)])
		return time.time()
	dt = time.time() - last_time
	g = 6
	# 计算全部粒子的加速度
	dax = g*math.sin(math.radians(roll))
	day = g*math.sin(math.radians(pitch))
	if abs(dax) < 1:
		dax = 0
	if abs(day) < 1:
		day = 0
	da = np.array([dax, day])
	dv = da * dt
	snakehead.update(snakehead.p + snakehead.v * dt, snakehead.v + da * dt, dt, dv)
	snakehead.draw(src)

	# 画出食物位置
	src[food[1], food[0]] = (0, 255, 0)

	# 头部坐标
	headaxis = np.array([int(snakehead.p[0]), int(snakehead.p[1])])

	# 判断是否吃到食物
	if (headaxis == food).all():	# 吃到食物了
		snake_flow.append(snake_flow[-1])
		# 更新食物
		food = np.array([np.random.randint(0, 16), np.random.randint(0, 16)])
		while (food == headaxis).all():
			food = np.array([np.random.randint(0, 16), np.random.randint(0, 16)])
	
	# 将流影右移一位
	length = len(snake_flow)
	for i in range(length - 1, -1, -1):
		snake_flow[i] = snake_flow[i - 1]
	snake_flow[0] = headaxis


	# 画流影
	for i in range(len(snake_flow)):
		(px_tmp, py_tmp) = (int(snake_flow[i][1]), int(snake_flow[i][0]))
		# if (px_tmp, py_tmp) == (headaxis[1], headaxis[0]):
		# 	continue
		tmp_color = (255 - i * 20, 0, 0) + src[px_tmp, py_tmp]
		for channel in tmp_color:
			if channel > 255:
				channel = 255
			if channel < 0:
				channel = 0
		src[px_tmp, py_tmp] = tmp_color
	if len(snake_flow) > 25:
		snake_flow = snake_flow[0:5]
	# 输出蛇头坐标，食物坐标
	# info = '[flowsnake]\t' + 'head:' + str(headaxis) + '\tfood:' + str(food) + '\tlength:' + str(len(snake_flow))
	# print(info)

	return time.time()
	

def update_information(roll, pitch, yaw, last_time, src: np.ndarray, mode : int):
	if last_time < 0:  # 需要初始化
		counter = int(0)
	if mode == 1:	# 多粒子模式
		return mutilParticle(roll, pitch, yaw, last_time, src,(100,0,0))
	elif mode == 2:	# 流影模式
		return flowShadow(roll, pitch, yaw, last_time, src)
	elif mode == 3:	# 烟花模式
		return mutilParticle2(roll, pitch, yaw, last_time, src)
	elif mode == 4:	# 贪吃蛇模式
		return snake(roll, pitch, yaw, last_time, src)
	elif mode == 5:	# 新概念贪吃蛇模式
		return newSnake(roll, pitch, yaw, last_time, src)
	elif mode == 6: # 蓝粒子模式
		return mutilParticle(roll, pitch, yaw, last_time, src,(100,0,10))
