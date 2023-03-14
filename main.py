#!/usr/bin/env python
#
# Author: Griffin Leonard
# Title: colors game
# Genres: metroidvainia, 2d platformer

# LOAD MODULES
try:
    import sys
    import pygame
    sys.path.append('scripts')
    import file_handling
    import physics_obj
    from globals import * # initializes game
except Exception as exc:
    print("ERROR: couldn't load modules.",exc)
    sys.exit()

# HELPER FUNCTIONS
def load_level(lvl):
    global level, world_data, tiles, entities, special_tiles
    level = lvl
    world_data = file_handling.load_pickle(level)
    tiles, entities, special_tiles = create_room_objects(world_data)

def draw_bg():
    screen.fill(LIGHT_RAINBOW[level])

def draw_tiles():
    ''' Draw tile objects on the screen '''
    for y, row in enumerate(world_data):
        for x, tile in enumerate(row):
            if tile >= 0: # if there's a tile
                if tile == 0:
                    screen.blit(img_dict[DARK_RAINBOW_STR[level]]['floor'], \
                        (x * TILE_SIZE - scroll_x, y * TILE_SIZE - scroll_y))
                elif tile == 9:
                    screen.blit(img_dict[DARK_RAINBOW_STR[level]]['spike'], \
                        (x * TILE_SIZE - scroll_x, y * TILE_SIZE - scroll_y))
                elif tile not in ENTITY_TILES:
                    screen.blit(img_list[tile], \
                        (x * TILE_SIZE - scroll_x, y * TILE_SIZE - scroll_y))
                    
def create_room_objects(world_data):
    ''' Create tile objects from world data '''
    tiles, entity, special_tiles = [], [], []
    for y, row in enumerate(world_data):
        for x, tile in enumerate(row):
            if tile >= 0: # if there's a tile
                if tile in range(1,8):
                    c = tile_data[str(tile)]['color']
                    o = physics_obj.Orb(orb_img, x * TILE_SIZE, y * TILE_SIZE, \
                        TILE_SIZE, TILE_SIZE, c)
                    entity.append(o)
                elif tile_data[str(tile)]['collision']:
                    o = physics_obj.Physics_obj(img_list[tile], \
                        x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    tiles.append(o)
                elif tile == 8: # checkpoint
                    o = physics_obj.Checkpoint(img_list[tile], \
                        x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE, level)
                    special_tiles.append(o)
                elif tile_data[str(tile)]['death']:
                    o = physics_obj.Physics_obj(img_list[tile], \
                        x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE, deadly=True)
                    special_tiles.append(o)
    return (tiles,entity,special_tiles)

def scroll_screen(obj):
    ''' Clamps screen scrolling to an object (usually the player) '''
    global scroll_x
    global scroll_y
    # update horizontal screen scrolling
    if obj.x > scroll_x+SCREEN_WIDTH//2+SCROLL_CLAMP_W//2:
        scroll_x += obj.x - (scroll_x+SCREEN_WIDTH//2+SCROLL_CLAMP_W//2)
    elif obj.x < scroll_x+SCREEN_WIDTH//2-SCROLL_CLAMP_W//2:
        scroll_x -= scroll_x+SCREEN_WIDTH//2-SCROLL_CLAMP_W//2 - obj.x
    # update vertical screen scrolling
    if obj.y > scroll_y+SCREEN_HEIGHT//2+SCROLL_CLAMP_H//2:
        scroll_y += obj.y - (scroll_y+SCREEN_HEIGHT//2+SCROLL_CLAMP_H//2)
    elif obj.y < scroll_y+SCREEN_HEIGHT//2-SCROLL_CLAMP_H//2:
        scroll_y -= scroll_y+SCREEN_HEIGHT//2-SCROLL_CLAMP_H//2 - obj.y
    # prevent scrolling past end of room
    if scroll_x < 0: scroll_x = 0
    if scroll_y < 0: scroll_y = 0
    if scroll_x > (MAX_COLS*TILE_SIZE)-SCREEN_WIDTH: scroll_x = (MAX_COLS*TILE_SIZE)-SCREEN_WIDTH
    if scroll_y > (MAX_ROWS*TILE_SIZE)-SCREEN_HEIGHT: scroll_y = (MAX_ROWS*TILE_SIZE)-SCREEN_HEIGHT

def goto_last_checkpoint():
    global save_data, level
    if level != save_data['level']: load_level(save_data['level'])
    if save_data['checkpoint']: player.set_pos(x=save_data['checkpoint'][0],y=save_data['checkpoint'][1])
    else: player.set_pos(x=save_data['player_loc'][0],y=save_data['player_loc'][1])

# load data
save_data = file_handling.load_json('save_data')
level = save_data['level']
world_data = file_handling.load_pickle(level)
scroll_x, scroll_y = 0, (MAX_ROWS * TILE_SIZE) - SCREEN_HEIGHT

# load tile images
tile_data = file_handling.load_json('tile_data')
img_list = [] # list of pygame images
for x in range(TILE_TYPES):
	img = pygame.image.load(f'img/tile/{x}.png').convert_alpha()
	img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
	img_list.append(img)

# create images for color variants of ground
img_dict = {} # dict of pygame images
for i,c in enumerate(DARK_RAINBOW):
    floor = physics_obj.replace_pixels(img_list[0], c)
    spike = physics_obj.replace_pixels(img_list[9], c)
    img_dict[DARK_RAINBOW_STR[i]] = {'floor':floor,'spike':spike}

# other images
orb_img = pygame.image.load(animation_database['Orb']['img_name']).convert_alpha()
orb_img = pygame.transform.scale(orb_img, (TILE_SIZE*animation_database['Orb']['frames'], TILE_SIZE))

tiles, entities, special_tiles = create_room_objects(world_data) # list of Physics_obj

# create player
img = pygame.image.load('img/player/idle.png').convert_alpha()
img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
player = physics_obj.Player(img, save_data['player_loc'][0], \
    save_data['player_loc'][1], TILE_SIZE, TILE_SIZE)


# MAIN GAME LOOP
while 1:
    clock.tick(60) # Update clock

    # draw and update level
    draw_bg()
    draw_tiles()
    for t in special_tiles: 
        if type(t) != physics_obj.Physics_obj: t.draw(screen, scroll_x, scroll_y) 
    for ob in entities:
        ob.draw(screen, scroll_x, scroll_y)
        ob.update(tiles)
    player.draw(screen, scroll_x, scroll_y)
    player.update(tiles)
    scroll_screen(player)

    # check if player hit deadly object
    obj = player.check_special_tiles(special_tiles) 
    if obj != None:
        if obj.deadly: goto_last_checkpoint()
        elif type(obj) == physics_obj.Checkpoint: 
            save_data = obj.set_active(save_data)

    # change level if collided with orb
    lvl = player.check_orbs(entities)
    if lvl != None: load_level(lvl)

    # quit
    if pygame.event.get(pygame.QUIT):
        pygame.quit()
        sys.exit()

    pygame.display.update() # Update screen 

