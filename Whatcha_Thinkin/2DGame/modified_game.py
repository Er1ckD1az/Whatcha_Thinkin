import sys
import pygame as pg
import random
import math
import time
import os

from scripts.entities import PhysicsEntity, Player
from scripts.utilities import load_image, load_picture, Animation
from scripts.tilemap import Tilemap
from scripts.particles import Particle

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the shared data bridge
from shared_data import EEGDataBridge

class Game:
    def __init__(self):
        pg.init()

        pg.display.set_caption('EEG Controlled 2D Scroller')
        self.screen = pg.display.set_mode((800, 600))
        self.display = pg.Surface((400, 300)) 

        self.clock = pg.time.Clock()

        # Create data bridge instance
        self.data_bridge = EEGDataBridge()
        self.data_bridge.set_game_status(True)

        # Movement is set to False since the eeg will be doing the work
        self.movement = [False, False]
        
        self.beta_threshold = 400  # For movement
        self.gamma_threshold = 400  # For jumping
        
        # Control mode
        self.use_eeg_control = True
        self.last_jump_time = 0
        self.jump_cooldown = 1.0  

        self.assets = {
            'decor': load_picture('tiles/decor'),
            'grass': load_picture('tiles/grass'),
            'large_decor': load_picture('tiles/large_decor'),
            'stone': load_picture('tiles/stone'),
            'player': pg.transform.scale(load_image('entities/IDLETESTING.png'), (16, 16)),
            'background1': load_image('layer_backgrounds/background_layer_1.png'),
            'background2': load_image('layer_backgrounds/background_layer_2.png'),
            'background3': load_image('layer_backgrounds/background_layer_3.png'),
            'particles1/leaf': Animation(load_picture('particles1/leaf'), img_dur=20, loop=False),
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

        self.player = Player(self, (50, 50), (8, 15))

        self.tilemap = Tilemap(self, tile_size=16)
        self.tilemap.load('map.json')

        self.leaf_spawners = []
        for tree in self.tilemap.extract([('large_decor', 2)], keep=True):
            self.leaf_spawners.append(pg.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))

        self.particles = []

        self.scroll = [0, 0] 
        
        # Setup font for EEG info display
        self.font = pg.font.SysFont(None, 24)

    def process_eeg_input(self):
        if not self.use_eeg_control:
            return
            
        # Get the latest EEG data
        eeg_data = self.data_bridge.read_eeg_data()
        beta_power = eeg_data['beta_power']
        gamma_power = eeg_data['gamma_power']
        
        # Set movement based on beta power
        self.movement[0] = beta_power < self.beta_threshold * 0.3  # Low beta = move left
        self.movement[1] = beta_power > self.beta_threshold  # High beta = move right
        
        # Handle jumping with gamma power and cooldown
        current_time = time.time()
        if gamma_power > self.gamma_threshold and current_time - self.last_jump_time > self.jump_cooldown:
            self.player.jump()
            self.last_jump_time = current_time

    def display_eeg_info(self):
        eeg_data = self.data_bridge.read_eeg_data()
        beta = eeg_data['beta_power']
        gamma = eeg_data['gamma_power']
        is_eeg_connected = eeg_data['is_eeg_running']
        
        # Background for info panel
        pg.draw.rect(self.display, (0, 0, 0, 150), (5, 5, 150, 65))
        
        # Status indicator
        status_text = "EEG: Connected" if is_eeg_connected else "EEG: Disconnected"
        status_color = (0, 255, 0) if is_eeg_connected else (255, 0, 0)
        status_surface = self.font.render(status_text, True, status_color)
        self.display.blit(status_surface, (10, 10))
        
        # Control mode
        mode_text = "Mode: EEG" if self.use_eeg_control else "Mode: Keyboard"
        mode_surface = self.font.render(mode_text, True, (255, 255, 255))
        self.display.blit(mode_surface, (10, 30))

    def run(self):
        try:
            while True:
                # Process EEG input if available
                self.process_eeg_input()
                
                scaled_background1 = pg.transform.scale(self.assets['background1'], self.display.get_size())
                scaled_background2 = pg.transform.scale(self.assets['background2'], self.display.get_size())
                scaled_background3 = pg.transform.scale(self.assets['background3'], self.display.get_size())

                self.display.blit(scaled_background1, (0, 0)) 
                self.display.blit(scaled_background2, (0, 0)) 
                self.display.blit(scaled_background3, (0, 0)) 

                self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30
                self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 30
                render_scroll = (int(self.scroll[0]), int(self.scroll[1])) 

                # Handle leaf particles
                for rect in self.leaf_spawners:
                    if random.random() * 49999 < rect.width * rect.height:
                        pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                        self.particles.append(Particle(self, 'leaf', pos, velocity=[-0.1, 0.3], frame=random.randint(0, 20)))

                # Render tilemap
                self.tilemap.render(self.display, offset=render_scroll)

                # Update and render player
                self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
                self.player.render(self.display, offset=render_scroll)

                # Update and render particles
                for particle in self.particles.copy():
                    kill = particle.update()
                    particle.render(self.display, offset=render_scroll)
                    if particle.type == 'leaf':
                        particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3
                    if kill:
                        self.particles.remove(particle) 

                # Display EEG info
                self.display_eeg_info()

                # Handle pygame events
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        self.data_bridge.set_game_status(False)
                        pg.quit()
                        sys.exit()
                    # Toggle between EEG and keyboard control with Tab key
                    if event.type == pg.KEYDOWN:
                        if event.key == pg.K_TAB:
                            self.use_eeg_control = not self.use_eeg_control
                            print(f"Control mode: {'EEG' if self.use_eeg_control else 'Keyboard'}")
                        
                        # Keyboard controls (only work when EEG control is off)
                        if not self.use_eeg_control:
                            if event.key == pg.K_LEFT:
                                self.movement[0] = True
                            if event.key == pg.K_RIGHT:
                                self.movement[1] = True
                            if event.key == pg.K_UP:
                                self.player.jump()
                    
                    if event.type == pg.KEYUP and not self.use_eeg_control:
                        if event.key == pg.K_LEFT:
                            self.movement[0] = False
                        if event.key == pg.K_RIGHT:
                            self.movement[1] = False

                # Scale and draw the display on the screen
                self.screen.blit(pg.transform.scale(self.display, self.screen.get_size()), (0, 0))
                pg.display.update()
                self.clock.tick(60)
        finally:
            self.data_bridge.set_game_status(False)

if __name__ == "__main__":
    Game().run()