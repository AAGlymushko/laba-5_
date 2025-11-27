import pygame
import random

pygame.init()

WORLD_WIDTH = 5000
WORLD_HEIGHT = 1250

CAMERA_OFFSET_X = 400
CAMERA_OFFSET_Y = 300

SIZE_X = 1280
SIZE_Y = 720

STEP_ALONG_Y = 5
STEP_FALL = 30
STEP_ALONG_X = 5

MAX_ADD_SPEED = 10
START_SPEED_JUMP = 50
READUCTION_FACTOR = 15

screen = pygame.display.set_mode((SIZE_X, SIZE_Y))
clock = pygame.time.Clock()

class GameObject:
    def __init__(self, id, x, y, w, h):
        self.id = id
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def get_coord(self):
        return self.x, self.y

    def get_size(self):
        return self.w, self.h

    def set_coord(self, x, y):
        self.x = x
        self.y = y

    def paint(self, surface):
        pass

class Hero(GameObject):
    def __init__(self, x, y):
        super().__init__("id/hero/", x, y, 100, 100)
        self.sprite = pygame.image.load("hero.png")
        self.sprite = pygame.transform.scale(self.sprite, (100, 100))
        self.vect = False

    def paint(self, surface):
        if not self.vect:
            surface.blit(self.sprite, (self.x, self.y))
        else:
            flipped = pygame.transform.flip(self.sprite, True, False)
            surface.blit(flipped, (self.x, self.y))

class Cubs(GameObject):
    def __init__(self, x, y, w, h):
        super().__init__("id/cubs/", x, y, w, h)
        self.tile = pygame.image.load("floor.png")

    def paint(self, surface):
        tile = pygame.transform.scale(self.tile, (600, 600))
        clip_rect = pygame.Rect(self.x, self.y, self.w, self.h)
        old_clip = surface.get_clip()
        surface.set_clip(clip_rect)
        for yy in range(0, self.h, 600):
            for xx in range(0, self.w, 600):
                surface.blit(tile, (self.x + xx, self.y + yy))
        surface.set_clip(old_clip)

class Wall(GameObject):
    def __init__(self):
        super().__init__("id/wall/", 0, 0, WORLD_WIDTH, WORLD_HEIGHT)
        self.tile = pygame.image.load("fon.png")

    def paint(self, surface):
        tile = pygame.transform.scale(self.tile, (600, 300))
        for yy in range(0, WORLD_HEIGHT, 300):
            for xx in range(0, WORLD_WIDTH, 600):
                surface.blit(tile, (xx, yy))

class Enemy(GameObject):
    def __init__(self, x, y, step=2, radius=50):
        super().__init__("id/Enemy/", x, y, 200, 200)
        self.step = step
        self.is_right = True
        self.radius_plus = x + abs(radius)
        self.radius_minus = x - abs(radius)
        self.frames = [
            pygame.image.load("Ninja 2.png"),
            pygame.image.load("Ninja 1.png"),
            pygame.image.load("Ninja 3.png"),
            pygame.image.load("Ninja 1.png"),
        ]
        self.frames = [pygame.transform.scale(f, (200, 200)) for f in self.frames]
        self.cadr = 0
        self.animation_speed = 0.1

    def update(self):
        self.x += self.step if self.is_right else -self.step
        if self.x >= self.radius_plus:
            self.x = self.radius_plus
            self.is_right = False
        if self.x <= self.radius_minus:
            self.x = self.radius_minus
            self.is_right = True
        self.cadr += self.animation_speed
        if self.cadr >= len(self.frames):
            self.cadr = 0

    def paint(self, surface):
        frame = self.frames[int(self.cadr)]
        if self.is_right:
            surface.blit(frame, (self.x, self.y))
        else:
            surface.blit(pygame.transform.flip(frame, True, False), (self.x, self.y))

class MovingPlatform(GameObject):
    def __init__(self, x, y, w, h, step=2, radius=200):
        super().__init__("id/moving_platform/", x, y, w, h)
        self.step = step
        self.is_right = True
        self.radius_plus = x + radius
        self.radius_minus = x - radius
        self.tile = pygame.image.load("platform.png")

    def update(self):
        self.x += self.step if self.is_right else -self.step
        if self.x >= self.radius_plus:
            self.is_right = False
        if self.x <= self.radius_minus:
            self.is_right = True

    def paint(self, surface):
        tile = pygame.transform.scale(self.tile, (600, 600))
        clip_rect = pygame.Rect(self.x, self.y, self.w, self.h)
        old_clip = surface.get_clip()
        surface.set_clip(clip_rect)
        for yy in range(0, self.h, 600):
            for xx in range(0, self.w, 600):
                surface.blit(tile, (self.x + xx, self.y + yy))
        surface.set_clip(old_clip)

class Portal(GameObject):
    def __init__(self, x, y, w, h):
        super().__init__("id/portal/", x, y, w, h)
        self.tile = pygame.image.load("portal.png")

    def paint(self, surface):
        tile = pygame.transform.scale(self.tile, (100, 100))    
        clip_rect = pygame.Rect(self.x, self.y, self.w, self.h)
        old_clip = surface.get_clip()
        surface.set_clip(clip_rect)    
        for yy in range(0, self.h, 100):
            for xx in range(0, self.w, 100):
                surface.blit(tile, (self.x + xx, self.y + yy))    
        surface.set_clip(old_clip)

class Portals:
    def __init__(self, p1, p2):
        self.id = "id/portals/"
        (x1, y1, w1, h1) = p1
        (x2, y2, w2, h2) = p2
        self.portal1 = Portal(x1, y1, w1, h1)
        self.portal2 = Portal(x2, y2, w2, h2)

    def paint(self, surf):
        self.portal1.paint(surf)
        self.portal2.paint(surf)

class Finish(GameObject):
    def __init__(self, x, y):
        super().__init__("id/finish/", x, y, 110, 200)
        self.sprite = pygame.image.load("flag.png")
        self.sprite = pygame.transform.scale(self.sprite, (110, 200))

    def paint(self, surf):
        surf.blit(self.sprite, (self.x, self.y))

def intersection(a, b):
    return (
        a.x < b.x + b.w and
        a.x + a.w > b.x and
        a.y < b.y + b.h and
        a.y + a.h > b.y
    )


def collision(a, b):
    if not intersection(a, b):
        return False

    overlapX = min(a.x + a.w - b.x, b.x + b.w - a.x)
    overlapY = min(a.y + a.h - b.y, b.y + b.h - a.y)

    if overlapX < overlapY:
        if b.x + b.w / 2 < a.x + a.w / 2:
            b.x = a.x - b.w
        else:
            b.x = a.x + a.w
    else:
        if b.y + b.h / 2 < a.y + a.h / 2:
            b.y = a.y - b.h
        else:
            b.y = a.y + a.h
    return True

class Round:
    def __init__(self):
        self.objects = []

        self.hero = Hero(100, WORLD_HEIGHT - 350)

        self.left = False
        self.right = False
        self.jump = False
        self.jump_permit = True
        self.fall = 0

        self.y_minus_add = 0
        self.x_plus_add = 0
        self.x_minus_add = 0

        self.camera_x = 0
        self.camera_y = 0

        self.victory = False

        self.objects.append(Wall())
        self.objects.append(Cubs(0, WORLD_HEIGHT - 300, 5000, 300))
        self.objects.append(Cubs(0, 0, 5000, 300))
        self.objects.append(Cubs(750, WORLD_HEIGHT - 700, 500, 400))
        self.objects.append(Cubs(500, WORLD_HEIGHT - 450, 250, 50))
        self.objects.append(Cubs(600, WORLD_HEIGHT - 600, 150, 50))

        self.objects.append(Portals(
            (0, WORLD_HEIGHT - 700, 75, 75),
            (1250, WORLD_HEIGHT - 400, 1000, 100)
        ))

        self.objects.append(Cubs(1700, WORLD_HEIGHT - 700, 150, 50))
        self.objects.append(Cubs(2250, WORLD_HEIGHT - 700, 500, 500))

        self.objects.append(Enemy(2850, WORLD_HEIGHT - 500, 1, 70))

        self.objects.append(MovingPlatform(3000, WORLD_HEIGHT - 700, 600, 100, 2, 200))

        self.objects.append(Cubs(3500, WORLD_HEIGHT - 400, 500, 100))

        self.objects.append(Finish(4800, WORLD_HEIGHT - 500))

    def update_camera(self):
        cx = self.hero.x + self.hero.w / 2 - CAMERA_OFFSET_X
        cy = self.hero.y + self.hero.h / 2 - CAMERA_OFFSET_Y

        self.camera_x = max(0, min(cx, WORLD_WIDTH - SIZE_X))
        self.camera_y = max(0, min(cy, WORLD_HEIGHT - SIZE_Y))

    def movement(self):
        x, y = self.hero.x, self.hero.y

        if self.jump and self.jump_permit:
            self.jump_permit = False
            self.fall = START_SPEED_JUMP
        else:
            self.fall -= self.fall / READUCTION_FACTOR

        y += STEP_FALL
        y -= self.fall + self.y_minus_add
        x += self.x_plus_add + (STEP_ALONG_X if self.right else 0)
        x -= self.x_minus_add + (STEP_ALONG_X if self.left else 0)

        def adjust(active, value):
            return min(value + 1, MAX_ADD_SPEED) if active else max(value - 1, 0)
        self.y_minus_add = adjust(self.jump, self.y_minus_add)
        self.x_plus_add = adjust(self.right, self.x_plus_add)
        self.x_minus_add = adjust(self.left, self.x_minus_add)
        x = max(0, min(x, WORLD_WIDTH - self.hero.w))
        y = max(0, min(y, WORLD_HEIGHT - self.hero.h))

        self.hero.set_coord(x, y)

    def hero_check(self):
        for obj in self.objects:
            self.handle_collision(obj, self.hero)

    def handle_collision(self, first, second):
        if isinstance(first, Portals):
            p1 = first.portal1
            p2 = first.portal2
            if intersection(p1, second):
                second.x = p2.x + p2.w + 50
            elif intersection(p2, second):
                second.x = p1.x + p1.w + 50
            return

        if isinstance(first, Enemy):
            if collision(first, second):
                if second.y + second.h < first.y + first.h:
                    self.objects.remove(first)
                    self.fall = START_SPEED_JUMP / 2
            return

        if isinstance(first, Finish):
            if collision(first, second):
                self.victory = True
            return

        if isinstance(first, Cubs) or isinstance(first, MovingPlatform):
            old_y = second.y
            if collision(first, second):
                if second.y < old_y:
                    self.jump_permit = True
                    self.fall = min(self.fall, 0)

    def update(self):
        for obj in self.objects:
            if isinstance(obj, Enemy) or isinstance(obj, MovingPlatform):
                obj.update()

        self.movement()
        self.update_camera()
        self.hero_check()

    def draw(self):
        screen.fill((0, 0, 0))
        temp = pygame.Surface((WORLD_WIDTH, WORLD_HEIGHT), pygame.SRCALPHA)
        for obj in self.objects:
            if isinstance(obj, Portals):
                obj.paint(temp)
            else:
                obj.paint(temp)

        self.hero.paint(temp)

        screen.blit(temp, (-self.camera_x, -self.camera_y))

        if self.victory:
            font = pygame.font.SysFont("Times New Roman", 60)
            text = font.render("Victory!!!", True, (255, 255, 255))
            screen.blit(text, (SIZE_X // 2 - text.get_width() // 2,
                               SIZE_Y // 2 - text.get_height() // 2))

round = Round()

running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                round.left = True
                round.hero.vect = True
            if event.key == pygame.K_d:
                round.right = True
                round.hero.vect = False
            if event.key == pygame.K_w:
                round.jump = True

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                round.left = False
            if event.key == pygame.K_d:
                round.right = False
            if event.key == pygame.K_w:
                round.jump = False

    round.update()
    round.draw()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()