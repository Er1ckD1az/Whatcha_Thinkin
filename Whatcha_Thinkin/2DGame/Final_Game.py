import sys
import pygame as pg
import random
import math

from scripts.entities import PhysicsEntity, Player
from scripts.utilities import load_image, load_picture, Animation
from scripts.tilemap import Tilemap
from scripts.particles import Particle

class Game:
    def __init__(self):

        pg.init()

        pg.display.set_caption('2d scroller')
        self.screen = pg.display.set_mode((800,600))
        self.display = pg.Surface((400,300)) 

        self.clock = pg.time.Clock()

        self.movement = [False,False]

        self.assets = {
            'decor': load_picture('tiles/decor'),
            'grass': load_picture('tiles/grass'),
            'large_decor': load_picture('tiles/large_decor'),
            'stone': load_picture('tiles/stone'),
            'player': pg.transform.scale(load_image('entities/IDLETESTING.png'), (16, 16)),  # Scale here
            'background1': load_image('layer_backgrounds/background_layer_1.png'),
            'background2': load_image('layer_backgrounds/background_layer_2.png'),
            'background3': load_image('layer_backgrounds/background_layer_3.png'),
            'particles1/leaf': Animation(load_picture('particles1/leaf'), img_dur=20,loop=False),
            'player/idle': Animation(
                [pg.transform.scale(img, (16, 16)) for img in load_picture('entities/Knight/120x80_PNGSheets/IDLETESTING1')],
                img_dur=6
            ),
            'player/jump': Animation(
                [pg.transform.scale(img, (16, 16)) for img in load_picture('entities/Knight/120x80_PNGSheets/JUMP')]
            ),
            'player/run': Animation(
                [pg.transform.scale(img, (16, 16)) for img in load_picture('entities/Knight/120x80_PNGSheets/RUNNING')]
            ),
            'player/fall': Animation(
                [pg.transform.scale(img, (16, 16)) for img in load_picture('entities/Knight/120x80_PNGSheets/FALL')]
            ),
            'player/wall_slide': Animation(
                [pg.transform.scale(img, (16, 16)) for img in load_picture('entities/Knight/120x80_PNGSheets/WALLSLIDE')]
            ),
        }

        self.player = Player(self, (50,50), (8,15))

        self.tilemap = Tilemap(self, tile_size = 16)
        self.tilemap.load('map.json')

        self.leaf_spawners = []
        for tree in self.tilemap.extract([('large_decor', 2)], keep = True): #if we wanted to search for other tiles we could
            self.leaf_spawners.append(pg.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))

        self.particles = []

        self.scroll = [0,0] 

    def run(self):
        while True:
            scaled_background1 = pg.transform.scale(self.assets['background1'], self.display.get_size())
            scaled_background2 = pg.transform.scale(self.assets['background2'], self.display.get_size())
            scaled_background3 = pg.transform.scale(self.assets['background3'], self.display.get_size())

            self.display.blit(scaled_background1, (0, 0)) 
            self.display.blit(scaled_background2, (0, 0)) 
            self.display.blit(scaled_background3, (0, 0)) 

            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 30
            render_scroll = (int(self.scroll[0]), int(self.scroll[1])) 

            for rect in self.leaf_spawners:
                #this scales the density of the spawn rate by making it porportional to the hitbox
                if random.random() * 49999 < rect.width * rect.height:
                    #makes sure that the leaves spawn inside the hitbox
                    pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                    self.particles.append(Particle(self,'leaf',pos,velocity=[-0.1,0.3], frame=random.randint(0,20)))

            self.tilemap.render(self.display, offset = render_scroll)

            self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
            self.player.render(self.display, offset = render_scroll)

            for particle in self.particles.copy(): #removes the particle as soon as the animation is finished
                kill = particle.update()
                particle.render(self.display, offset=render_scroll)
                if particle.type == 'leaf':
                    #with the use of sin and its altneration between -1 & 1 creates an smooth oscillating pattern
                    particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3 #the 0.035 slows down the alternating
                if kill:
                    self.particles.remove(particle) 

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_LEFT:
                        self.movement[0] = True
                    if event.key == pg.K_RIGHT:
                        self.movement[1] = True
                    if event.key == pg.K_UP:
                        self.player.jump()
                if event.type == pg.KEYUP:
                    if event.key == pg.K_LEFT:
                        self.movement[0] = False
                    if event.key == pg.K_RIGHT:
                        self.movement[1] = False

            self.screen.blit(pg.transform.scale(self.display, self.screen.get_size()),(0,0))#drawing the display onto the screen gives the pixelated look
            pg.display.update()
            self.clock.tick(60)

Game().run()