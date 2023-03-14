from matplotlib import animation
import pygame
import file_handling

pygame.init()
clock = pygame.time.Clock()

# Initialise window
screen_info = pygame.display.Info()
window_size = (screen_info.current_w, screen_info.current_h - (screen_info.current_h//5))
screen = pygame.display.set_mode(window_size)
pygame.display.set_caption('colors game') 

# DECLARE GLOBAL VARIABLES
# variables in all caps never change
SCREEN_WIDTH, SCREEN_HEIGHT = window_size[0], window_size[1]
MAX_ROWS, MAX_COLS = 150, 150
SCROLL_CLAMP_W = SCREEN_WIDTH//4
SCROLL_CLAMP_H = SCREEN_HEIGHT//3

TILE_SIZE = SCREEN_HEIGHT // 16
TILE_TYPES = 10
ENTITY_TILES = [1,2,3,4,5,6,7,8]

# colors
BLACK = (0, 0, 0)
GREY = (128, 128, 128)
WHITE = (255, 255, 255)

RED = (225, 0, 0)
ORANGE = (255, 128, 0)
YELLOW = (225, 225, 0)
GREEN = (0, 225, 0)
BLUE = (0, 0, 255)
INDIGO = (128, 0, 255)
VIOLET = (255, 0, 255)
RAINBOW = (RED, ORANGE, YELLOW, GREEN, BLUE, INDIGO, VIOLET)

DARK_RED = (128, 0, 0)
DARK_ORANGE = (128, 64, 0)
DARK_YELLOW = (128, 128, 0)
DARK_GREEN = (0, 128, 0)
DARK_BLUE = (0, 0, 128)
DARK_INDIGO = (64, 0, 128)
DARK_VIOLET = (128, 0, 128)
DARK_RAINBOW = (DARK_RED,DARK_ORANGE,DARK_YELLOW,DARK_GREEN,DARK_BLUE,DARK_INDIGO,DARK_VIOLET)
DARK_RAINBOW_STR = ('dark_red','dark_orange','dark_yellow','dark_green','dark_blue','dark_indigo','dark_violet')

LIGHT_RED = (255, 128, 128)
LIGHT_ORANGE = (255, 178, 128)
LIGHT_YELLOW = (255, 255, 128)
LIGHT_GREEN = (128, 255, 128)
LIGHT_BLUE = (128, 128, 255)
LIGHT_INDIGO = (178, 128, 255)
LIGHT_VIOLET = (255, 128, 255)
LIGHT_RAINBOW = (LIGHT_RED,LIGHT_ORANGE,LIGHT_YELLOW,LIGHT_GREEN,LIGHT_BLUE,LIGHT_INDIGO,LIGHT_VIOLET)

# animations
animation_database = file_handling.load_json('animation_data')