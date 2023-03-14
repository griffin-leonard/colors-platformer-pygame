import pygame

from globals import TILE_SIZE, MAX_ROWS, MAX_COLS, WHITE, RAINBOW, animation_database

def collision_test(object_1,object_list):
    ''' Check if an object collides with a list of objects 
    args:
        object_1: rect of object to check collisions
        object_list: list of Physics_obj of objects to check 
    returns:
        list of rects that object_1 collides with
    '''
    collision_list = []
    for obj in object_list:
        if obj.rect.colliderect(object_1):
            collision_list.append(obj)
    return collision_list

def replace_pixels(img, color, replace=(0,0,0)):
    ''' Replace all pixels in img (pygame image) with the RGB values replace 
        with the RGB values color, preserve transparency '''
    img = img.copy()
    w, h = img.get_size()
    r, g, b = color
    for x in range(w):
        for y in range(h):
            pixel = img.get_at((x, y))
            if pixel[:3] == replace:
                img.set_at((x, y), pygame.Color(r, g, b, pixel[3]))
    return img

class Physics_obj(object):
    ''' Collidable object '''
    def __init__(self,img,x,y,x_size,y_size,deadly=False):
        self.img = img
        self.width = x_size
        self.height = y_size
        self.rect = pygame.Rect(x,y,self.width,self.height)
        self.x = x
        self.y = y
        self.deadly = deadly

    def draw(self, surface, scroll_x, scroll_y):
        surface.blit(self.img, (self.rect.x - scroll_x, self.rect.y - scroll_y))

    def move(self,movement,tiles):
        ''' Handle collisions when moving
        args:
            movement: tup (x,y) of pixels to move
            platforms: list of rects to check for collisions with
        returns:
            collision_data: dict containing data about direction of collisions
        '''
        # check for horizontal collisions
        self.x += movement[0]
        self.rect.x = int(self.x)
        block_hit_list = collision_test(self.rect,tiles) # get list of platforms collided with
        block_hit_list = [obj.rect for obj in block_hit_list]
        collision_data = {'top':False,'bottom':False,'right':False,'left':False,'slant_bottom':False,'data':[]}
        for block in block_hit_list:
            markers = [False,False,False,False]
            if movement[0] > 0:
                self.rect.right = block.left
                collision_data['right'] = True
                markers[0] = True
            elif movement[0] < 0:
                self.rect.left = block.right
                collision_data['left'] = True
                markers[1] = True
            collision_data['data'].append([block,markers])
            self.x = self.rect.x

        # check for vertical collisions
        self.y += movement[1]
        self.rect.y = int(self.y)
        block_hit_list = collision_test(self.rect,tiles) # get list of platforms collided with
        block_hit_list = [obj.rect for obj in block_hit_list]
        for block in block_hit_list:
            markers = [False,False,False,False]
            if movement[1] > 0:
                self.rect.bottom = block.top
                collision_data['bottom'] = True
                markers[2] = True
            elif movement[1] < 0:
                self.rect.top = block.bottom
                collision_data['top'] = True
                markers[3] = True
            collision_data['data'].append([block,markers])
            self.y = self.rect.y

        return collision_data

    def set_pos(self, x=None, y=None):
        if x != None:
            self.x = x
            self.rect.x = x
            self.move_x = 0
        if y != None:
            self.y = y
            self.rect.y = y
            self.move_y = 0

class Entity(Physics_obj):
    ''' Object with animation '''
    def __init__(self,img,x,y,x_size,y_size,animation_len=0,frame_len=0,gravity=TILE_SIZE//12,term_vel=TILE_SIZE//2):
        super().__init__(img,x,y,x_size,y_size)
        # variables for motion
        self.move_x = 0
        self.move_y = 0
        self.acc_y = 0
        self.gravity = gravity
        self.term_vel = term_vel
        self.animated = False

        # animation 
        if animation_len != 0:
            self.animated = True
            self.frame_len = frame_len
            self.load_animation(img,animation_len)

    def update(self,tiles):
        # movement
        if self.gravity:
            test = self.rect.copy()
            test.y += 1
            if not collision_test(test, tiles):
                self.acc_y = self.gravity # apply gravity

            self.move_y = min(self.term_vel, self.move_y+self.acc_y)
            self.move((self.move_x,self.move_y), tiles)

        self.keep_in_bounds() # stop entity from leaving screen

        # animation
        if self.animated:
            if self.frame_time == 0:
                self.frame_time = self.frame_len
                if self.animation_frame < self.animation_len: 
                    self.animation_frame += 1
                else:
                    self.animation_frame = 0
                self.get_image()
            else:
                self.frame_time -= 1
    
    def get_image(self):
        self.img = pygame.Surface((self.width, self.height)).convert_alpha()
        self.img.blit(self.sprite_sheet, (0,0), area=(self.animation_frame*self.width, 0, (self.animation_frame+1)*self.width-1, self.height))

    def load_animation(self, img, animation_len):
        self.sprite_sheet = img
        self.animation_len = animation_len
        self.animation_frame = 0
        self.frame_time = self.frame_len
        self.get_image()

    def keep_in_bounds(self):
        if self.rect.left < 0:
            self.set_pos(x=0)
        elif self.rect.right > TILE_SIZE*MAX_COLS:
            self.set_pos(x=TILE_SIZE*MAX_COLS-self.width)
        if self.rect.top < 0:
            self.set_pos(y=0)
        elif self.rect.bottom > TILE_SIZE*MAX_ROWS:
            self.set_pos(y=TILE_SIZE*MAX_ROWS-self.height)

class Player(Entity):
    ''' Controllable player entity '''
    def __init__(self,img,x,y,x_size,y_size):
        super().__init__(img,x,y,x_size,y_size)

        # varialbes for movement
        self.speed = TILE_SIZE//32
        self.maxSpeed = TILE_SIZE//6
        self.friction = TILE_SIZE//16
        self.is_jumping = False
        self.jump_height = TILE_SIZE//6
        self.maxJumpCount = 10
        self.jumpCount = self.maxJumpCount

    def update(self,tiles):
        test = self.rect.copy()
        test.y += 1
        on_ground = collision_test(test, tiles)

        # bonk head, end jump
        test.y -= 2
        on_ceiling = collision_test(test, tiles)
        if on_ceiling:
            self.move_y = 0
            self.is_jumping = False

        # Handle player inputs
        pressed = pygame.key.get_pressed()

        # horizontal acceleration
        if pressed[pygame.K_a]:
            # if on_ground: self.move_x = max(-self.maxSpeed, self.move_x-self.speed)
            # else: self.move_x = max(-self.maxSpeed, self.move_x-self.speed//2) # adjust direction slower in air
            self.move_x = max(-self.maxSpeed, self.move_x-self.speed)
        if pressed[pygame.K_d]:
            # if on_ground: self.move_x = min(self.maxSpeed, self.move_x+self.speed)
            # else: self.move_x = min(self.maxSpeed, self.move_x+self.speed//2) # adjust direction slower in air
            self.move_x = min(self.maxSpeed, self.move_x+self.speed)

        # horizontal decceleration
        if self.move_x < 0 and not pressed[pygame.K_a]:
            # if on_ground: self.move_x = min(0, self.move_x+self.friction)
            # else: self.move_x = min(0, self.move_x+self.friction//2) # less friction in air 
            self.move_x = min(0, self.move_x+self.friction)
        if self.move_x > 0 and not pressed[pygame.K_d]:
            # if on_ground: self.move_x = max(0, self.move_x-self.friction)
            # else: self.move_x = max(0, self.move_x-self.friction//2) # less friction in air 
            self.move_x = max(0, self.move_x-self.friction)

        # vertical movement
        if on_ground:
            self.move_y = 0 # set velocity to 0 if on platform
            if not self.is_jumping and pressed[pygame.K_w]: # initiate jump
                self.jumpCount = self.maxJumpCount
                self.is_jumping = True
                self.acc_y = -self.jump_height
        else:
            self.acc_y = self.gravity # apply gravity
            if self.is_jumping:  
                # extend jump when holding jump button
                if pressed[pygame.K_w]:
                    if self.jumpCount > 0:
                        self.jumpCount -= 1
                        self.acc_y = -self.jumpCount//4
                    else:
                        self.is_jumping = False
                # end jump
                else:
                    self.is_jumping = False
        self.move_y = min(self.term_vel, self.move_y+self.acc_y)

        self.move((self.move_x,self.move_y), tiles)
        self.keep_in_bounds()

    def check_orbs(self, objects):
        obj_collided = collision_test(self.rect, objects)
        for obj in obj_collided:
            if type(obj) == Orb: return obj.color_index
        return None

    def check_special_tiles(self, objects):
        obj_collided = collision_test(self.rect, objects)
        for obj in obj_collided:
            return obj
        return None

class Orb(Entity):
    ''' Collectable orb '''
    def __init__(self,img,x,y,x_size,y_size,color,animation_len=animation_database['Orb']['frames'],frame_len=animation_database['Orb']['len']):
        super().__init__(img,x,y,x_size,y_size,animation_len=animation_len,frame_len=frame_len)
        self.gravity = 0
        self.color_index = color
        self.color = RAINBOW[color]
        self.sprite_sheet = replace_pixels(self.sprite_sheet,self.color,(255,255,255))
        self.get_image()

class Checkpoint(Physics_obj):
    def __init__(self,img,x,y,x_size,y_size,level,active=False):
        super().__init__(img,x,y,x_size,y_size)
        self.active = active
        self.level = level

    def set_active(self, save_data):
        if not self.active: self.activate()
        save_data['checkpoint'] = (self.x,self.y)
        save_data['level'] = self.level
        return save_data

    def activate(self):
        self.active = True
        self.img = replace_pixels(self.img, RAINBOW[self.level], WHITE)

