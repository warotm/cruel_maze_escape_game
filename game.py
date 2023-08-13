import pygame as pg
from pathlib import Path
import random

window_w = 1280
window_h = 1024

map_paths = list(Path("maps").glob("*.png"))


class Instruction(pg.sprite.Sprite):
    def __init__(self, pos):
        super(Instruction, self).__init__()
        self.image = pg.image.load("instruction.png").convert_alpha()
        self.rect = self.image.get_rect(center=pos)


class Player(pg.sprite.Sprite):
    def __init__(self, pos):
        super(Player, self).__init__()
        self.image = pg.image.load("player.png").convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.mask = pg.mask.from_surface(self.image)
        self.speed = 1

    def move(self, direction, step=None):
        if not step:
            step = self.speed
        self.direction = direction
        pos_x = self.rect.center[0]
        pos_y = self.rect.center[1]
        if self.direction == "UP":
            pos_y -= step
        if self.direction == "DOWN":
            pos_y += step
        if self.direction == "LEFT":
            pos_x -= step
        if self.direction == "RIGHT":
            pos_x += step
        self.rect.center = (pos_x, pos_y)


class Map(pg.sprite.Sprite):
    def __init__(self, pos, img_path):
        super(Map, self).__init__()
        self.image = pg.image.load(img_path).convert_alpha()
        self.original_image = self.image
        self.rect = self.image.get_rect(center=pos)
        self.mask = pg.mask.from_surface(self.image)
        self.counter = 0
        self.current_degree = 0

    def rotate(self, degree=1, time=10):
        self.counter += 1
        if self.counter > time:
            self.current_degree += degree
            self.image = pg.transform.rotate(self.original_image, self.current_degree)
            self.rect = self.image.get_rect(center=(window_w / 2, window_h / 2))
            self.mask = pg.mask.from_surface(self.image)
            self.counter = 0


class Game:
    map_index = None
    rotation_speed = 20
    is_instruction = True

    def __init__(self):
        self.screen = pg.display.set_mode((window_w, window_h))
        self.instruction = Instruction((window_w / 2, window_h / 2))
        self.instruction_sprite = pg.sprite.Group(self.instruction)
        if not self.map_index:
            self.map_index = 0
        self.map = pg.sprite.Group(
            Map(
                (window_w / 2, window_h / 2), map_paths[self.map_index % len(map_paths)]
            )
        )
        self.player = Player((window_w / 2, window_h / 2))
        while pg.sprite.spritecollide(
            self.player, self.map, False, pg.sprite.collide_mask
        ):
            self.player.move("DOWN", 10)
        self.all_sprites = pg.sprite.Group(self.player, self.map)
        self.done = False
        self.clock = pg.time.Clock()
        self.direction = ""
        self.start_time = None
        self.current_time = None
        self.is_game_end = False
        self.is_game_win = False

    def run(self):
        while not self.done:
            self.event_loop()
            self.update()
            self.draw()
            pg.display.flip()
            self.clock.tick(60)

    def event_loop(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    self.direction = "UP"
                if event.key == pg.K_DOWN:
                    self.direction = "DOWN"
                if event.key == pg.K_LEFT:
                    self.direction = "LEFT"
                if event.key == pg.K_RIGHT:
                    self.direction = "RIGHT"
                if event.key == pg.K_SPACE:
                    self.reset()
                if event.key == pg.K_RETURN:
                    self.change_map()
                if event.key == pg.K_RIGHTBRACKET:
                    self.rotation_speed += 1
                if event.key == pg.K_LEFTBRACKET:
                    self.rotation_speed -= 1

    def game_over(self):
        self.is_game_end = True

    def game_win(self):
        self.is_game_end = True
        self.is_game_win = True

    def change_map(self):
        self.map_index += 1
        self.__init__()

    def reset(self):
        self.__init__()

    def update(self):
        if pg.sprite.spritecollide(
            self.player, self.map, False, pg.sprite.collide_mask
        ):
            self.game_over()

        pos_x = self.player.rect.center[0]
        pos_y = self.player.rect.center[1]

        if (pos_x < 0 or pos_x > window_w) or (pos_y < 0 or pos_y > window_h):
            self.game_win()

        # Start timer
        if self.direction != "" and self.start_time == None:
            self.is_instruction = False
            self.start_time = pg.time.get_ticks()

        if not self.is_game_end:
            if self.direction != "":
                self.map.sprites()[0].rotate(1, self.rotation_speed)
                self.player.move(self.direction)

    def draw_text(self):
        FONT = pg.font.SysFont("notosans", 42)
        BIG_FONT = pg.font.SysFont("notosans", 84)
        TEXT_COLOR = (42, 42, 42)
        BG_COLOR = (200, 200, 200)
        if self.start_time and not self.is_game_end:
            if not self.is_game_end:
                self.current_time = pg.time.get_ticks()
            time_since_enter = self.current_time - self.start_time
            message = "Timer: {}".format(time_since_enter / 1000)
            self.screen.blit(FONT.render(message, True, TEXT_COLOR), (200, 20))
        if self.is_game_end:
            if self.is_game_win:
                message = "(~^^)~ Yay you WIN in {}s | SPD {} ~(^^~)".format(
                    (self.current_time - self.start_time) / 1000,
                    self.rotation_speed,
                )
                text = BIG_FONT.render(message, True, TEXT_COLOR, BG_COLOR)
                text_rect = text.get_rect(center=(window_w / 2, window_h / 2))
                self.screen.blit(text, text_rect)
            else:
                message = "(~^^)~ Nah you LOSE ~(^^~)"
                text = BIG_FONT.render(message, True, TEXT_COLOR, BG_COLOR)
                text_rect = text.get_rect(center=(window_w / 2, window_h / 2))
                self.screen.blit(text, text_rect)
        else:
            message = "Speed: {}".format(self.rotation_speed)
            self.screen.blit(FONT.render(message, True, TEXT_COLOR), (20, 20))
        if self.is_instruction:
            self.instruction_sprite.draw(self.screen)

    def draw(self):
        self.screen.fill((255, 255, 255))
        self.all_sprites.draw(self.screen)
        self.draw_text()


if __name__ == "__main__":
    pg.init()
    pg.display.set_caption('CRUEL MAZE ESCAPE')
    game = Game()
    game.run()
    pg.quit()
