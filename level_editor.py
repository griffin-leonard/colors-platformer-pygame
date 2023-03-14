## LOAD MODULES ## 
import pygame
import pickle

pygame.init()

## DECLARE VARIABLES ##
clock = pygame.time.Clock()
FPS = 60

#game window
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 640
LOWER_MARGIN = 100
SIDE_MARGIN = 300

screen = pygame.display.set_mode((SCREEN_WIDTH + SIDE_MARGIN, SCREEN_HEIGHT + LOWER_MARGIN))
pygame.display.set_caption('Level Editor')

MAX_ROWS = 150
MAX_COLS = 150
TILE_SIZE = SCREEN_HEIGHT // 16 #display 16 tiles vertically at a time
TILE_TYPES = 10
MAX_LEVELS = 7

#define colours
WHITE = (255, 255, 255)
GREY = (92, 92, 92)

#background colors
COLOR_SCALAR = 51
RED = (225, 0, 0)
ORANGE = (255, 128, 0)
YELLOW = (225, 225, 0)
GREEN = (0, 225, 0)
BLUE = (0, 0, 255)
INDIGO = (128, 0, 255)
VIOLET = (255, 0, 255)
RAINBOW = (RED, ORANGE, YELLOW, GREEN, BLUE, INDIGO, VIOLET)

level_loaded = 0
level = 0
current_tile = 0
scroll_left = False
scroll_right = False
scroll_up = False
scroll_down = False
scroll_x = 0
scroll_y = (MAX_ROWS * TILE_SIZE) - SCREEN_HEIGHT
scroll_speed = 1

#define font
font = pygame.font.SysFont('Futura', 16)
coord_font = pygame.font.SysFont('Futura', 12)

#store tiles in a list
img_list = []
for x in range(TILE_TYPES):
	img = pygame.image.load(f'img/tile/{x}.png').convert_alpha()
	img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
	img_list.append(img)

save_img = pygame.image.load('img/buttons/save_btn.png').convert_alpha()
load_img = pygame.image.load('img/buttons/load_btn.png').convert_alpha()

#create empty tile list
world_data = []
for row in range(MAX_ROWS):
	r = [-1] * MAX_COLS
	world_data.append(r)


## HELPER FUNCTIONS ##

#function for outputting text onto the screen
def blit_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))

#create function for drawing background
def draw_bg():
	screen.fill(RAINBOW[level_loaded], [0, 0, SCREEN_WIDTH, SCREEN_HEIGHT])

#draw grid
def draw_grid():
	#vertical lines
	for c in range(MAX_COLS + 1):
		pygame.draw.line(screen, WHITE, (c * TILE_SIZE - scroll_x, 0), (c * TILE_SIZE - scroll_x, SCREEN_HEIGHT))
	#horizontal lines
	for c in range(MAX_ROWS + 1):
		pygame.draw.line(screen, WHITE, (0, c * TILE_SIZE - scroll_y), (SCREEN_WIDTH, c * TILE_SIZE - scroll_y))
	screen.fill(GREY, (SCREEN_WIDTH, 0, SIDE_MARGIN, SCREEN_HEIGHT + LOWER_MARGIN)) #side panel for tiles
	screen.fill(GREY, [0, SCREEN_HEIGHT+1, SCREEN_WIDTH, SCREEN_HEIGHT + LOWER_MARGIN]) #botton panel for save and load 

#function for drawing the world tiles
def draw_world():
	for y, row in enumerate(world_data):
		for x, tile in enumerate(row):
			if tile >= 0:
				screen.blit(img_list[tile], (x * TILE_SIZE - scroll_x, y * TILE_SIZE - scroll_y))

#function for drawing text on screen
def draw_text():
	blit_text(f'Selected Level: {level}', font, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 60)
	blit_text('Press UP or DOWN to change selected level', font, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 30)
	for c in range(MAX_COLS + 1):
		loc = c * TILE_SIZE - scroll_x
		if c % 5 == 0 and loc > 0 and loc < SCREEN_WIDTH:
			blit_text(str(c), coord_font, WHITE, loc + 10, SCREEN_HEIGHT + 5)
	for c in range(MAX_ROWS + 1):
		loc = c * TILE_SIZE - scroll_y
		if c % 5 == 0 and loc > 0 and loc < SCREEN_HEIGHT + 10:
			blit_text(str(c), coord_font, WHITE, SCREEN_WIDTH + 5, loc + 10)



## HANDLE BUTTONS (BACKEND) ##
#button class
class Button():
	def __init__(self,x, y, image, scale):
		width = image.get_width()
		height = image.get_height()
		self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		self.clicked = False

	def draw(self, surface):
		action = False

		#get mouse position
		pos = pygame.mouse.get_pos()

		#check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				action = True
				self.clicked = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False

		#draw button
		surface.blit(self.image, (self.rect.x, self.rect.y))

		return action

#create buttons
save_button = Button(SCREEN_WIDTH // 2, SCREEN_HEIGHT + LOWER_MARGIN - 50, save_img, 1)
load_button = Button(SCREEN_WIDTH // 2 + 200, SCREEN_HEIGHT + LOWER_MARGIN - 50, load_img, 1)
#make a button list
button_list = []
button_col = 0
button_row = 0
for i in range(len(img_list)):
	tile_button = Button(SCREEN_WIDTH + (75 * button_col) + 50, 75 * button_row + 50, img_list[i], 1)
	button_list.append(tile_button)
	button_col += 1
	if button_col == 3:
		button_row += 1
		button_col = 0

## GAME LOOP ##

run = True
while run:

	clock.tick(FPS)

	draw_bg()
	draw_world()
	draw_grid()
	draw_text()

	#save and load data
	if save_button.draw(screen):
		#save level data
		pickle_out = open(f'levels/level{level}_data', 'wb')
		pickle.dump(world_data, pickle_out)
		pickle_out.close()
	if load_button.draw(screen):
	    #load in level data
		world_data = []
		pickle_in = open(f'levels/level{level}_data', 'rb')
		world_data = pickle.load(pickle_in)
		level_loaded = level
				
	#choose a tile
	button_count = 0
	for button_count, i in enumerate(button_list):
		if i.draw(screen):
			current_tile = button_count

	#highlight the selected tile
	pygame.draw.rect(screen, RED, button_list[current_tile].rect, 3)

	#scroll the map
	if scroll_left == True and scroll_x > 0:
		scroll_x -= 5 * scroll_speed
	if scroll_right == True and scroll_x < (MAX_COLS * TILE_SIZE) - SCREEN_WIDTH:
		scroll_x += 5 * scroll_speed
	if scroll_up == True and scroll_y > 0:
		scroll_y -= 5 * scroll_speed
	if scroll_down == True and scroll_y < (MAX_ROWS * TILE_SIZE) - SCREEN_HEIGHT:
		scroll_y += 5 * scroll_speed
	

#add new tiles to the screen
	#get mouse position
	pos = pygame.mouse.get_pos()
	x = (pos[0] + scroll_x) // TILE_SIZE
	y = (pos[1] + scroll_y) // TILE_SIZE

	#check that the coordinates are within the tile area
	if pos[0] < SCREEN_WIDTH and pos[1] < SCREEN_HEIGHT:
		#update tile value
		if pygame.mouse.get_pressed()[0] == 1:
			if world_data[y][x] != current_tile:
				world_data[y][x] = current_tile
		if pygame.mouse.get_pressed()[2] == 1:
			world_data[y][x] = -1

#handle key presses
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False
		#keyboard presses
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_UP and level < MAX_LEVELS-1:
				level += 1
			if event.key == pygame.K_DOWN and level > 0:
				level -= 1
			if event.key == pygame.K_a:
				scroll_left = True
			if event.key == pygame.K_d:
				scroll_right = True
			if event.key == pygame.K_w:
				scroll_up = True
			if event.key == pygame.K_s:
				scroll_down = True
			if event.key == pygame.K_RSHIFT:
				scroll_speed *= 2
			if event.key == pygame.K_LSHIFT:
				scroll_speed *= 2

		if event.type == pygame.KEYUP:
			if event.key == pygame.K_a:
				scroll_left = False
			if event.key == pygame.K_d:
				scroll_right = False
			if event.key == pygame.K_w:
				scroll_up = False
			if event.key == pygame.K_s:
				scroll_down = False
			if event.key == pygame.K_RSHIFT:
				scroll_speed /= 2
			if event.key == pygame.K_LSHIFT:
				scroll_speed /= 2

	pygame.display.update()

	if event.type == pygame.QUIT:
		pygame.quit()
		break
	
