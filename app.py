import pygame
import neat
import time
import os
import random
import PySimpleGUI as sg
pygame.font.init()

from pyrsistent import b

WIN_WIDTH = 500
WIN_HEIGHT = 800
DRAW_LINES = True

GEN = 0

BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]

PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))
STAT_FONT = pygame.font.SysFont('arial.ttf', 30)
SCORE_FONT = pygame.font.SysFont('arial.ttf', 40)

class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]
        self.color = (random.randrange(0, 255), random.randrange(0, 255), random.randrange(0, 255))

    def jump(self):
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1

        d = self.vel * self.tick_count + 1.5*self.tick_count**2

        if d >= 16:
             d = 16
        if d < 0:
            d -= 2

        self.y = self.y + d

        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, win):
        self.img_count += 1

        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME * 4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2

        rotated_image = pygame.transform.rotate(self.img, self.tilt) 
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft = (self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)

class Pipe:
    GAP = 200
    VEL = 5

    def __init__(self, x):
        self.x = x
        self.height = 0

        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        ### if no collisions with top or bottom pipes
        if t_point or b_point:
            return True
        return False


class Base:
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH


    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))



sg.theme('LightPurple')

def main_menu():

    font = ("Arial", 14)

    layout = [[sg.Text('Main Menu')],
            [sg.Button('Run Simulation')],
            [sg.Button('Play Yourself')],
            [sg.Button('Exit', size=6)]]

    window = sg.Window('Main Menu', layout, element_justification='c', font=font, size=(200, 250))

    while True:  # Event Loop
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Exit':
            window.close()
            return "Exit"
        if event == 'Run Simulation':
            window.close()
            return 'Run Simulation'
        if event == 'Play Yourself':
            window.close()
            return 'Play Yourself'


def main_menu2():

    font = ("Arial", 14)

    layout = [[sg.Text('Main Menu')],
            [sg.Button('Play Again?')],
            [sg.Button('Exit', size=6)]]

    window = sg.Window('Main Menu', layout, element_justification='c', font=font, size=(200, 250))

    while True:  # Event Loop
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Exit':
            window.close()
            return "Exit"
        if event == 'Play Again?':
            window.close()
            return 'Play Yourself'

def draw_window2(win, bird, pipes, base, score):
    pygame.font.init()
    SCORE_FONT = pygame.font.SysFont('arial.ttf', 40)

    win.blit(BG_IMG, (0,0))

    for pipe in pipes:
        pipe.draw(win)


    text = SCORE_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))
    
    base.draw(win)

    bird.draw(win)
    pygame.display.update()


def main2(play):

    while play == "Play Yourself":

        bird = Bird(230, 350)
        base = Base(730)
        pipes = [Pipe(700)]
        run = True
        win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        clock = pygame.time.Clock()
        score = 0

        while run:
            clock.tick(30)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if pygame.mouse.get_pressed()[0]:
                    bird.jump()

            bird.move()
            add_pipe = False
            rem = []
            for pipe in pipes:
                if pipe.collide(bird):
                    run = False
                
                if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                    rem.append(pipe)
                    
                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True
                pipe.move()

            if add_pipe:
                score += 1
                pipes.append(Pipe(550))

            for r in rem:
                pipes.remove(r)

            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                run = False

            base.move()
            draw_window2(win, bird, pipes, base, score)

        pygame.quit()

        check = main_menu2()
        if check == "Play Yourself":
            main2('Play Yourself')
        elif check == 'Exit':
            quit()

    
play = None

while not play:
    play = main_menu()

if play == "Run Simulation":
    def draw_window(win, birds, pipes, base, score, gen, pipe_ind):
        win.blit(BG_IMG, (0,0))

        for pipe in pipes:
            pipe.draw(win)

        text = SCORE_FONT.render("Score: " + str(score), 1, (255, 255, 255))
        win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))
        text = STAT_FONT.render("Generation: " + str(gen), 1, (255, 255, 255))
        win.blit(text, (10, 10))
        text = STAT_FONT.render("Alive: " + str(len(birds)), 1, (255, 255, 255))
        win.blit(text, (10, 35))

        base.draw(win)

        for bird in birds:
            # draw lines from bird to pipe
            if len(birds) == 1:
                if DRAW_LINES:
                    try:
                        pygame.draw.line(win, (random.randrange(0, 255), random.randrange(0, 255), random.randrange(0, 255)), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_TOP.get_width()/2, pipes[pipe_ind].height), 5)
                        pygame.draw.line(win, (random.randrange(0, 255), random.randrange(0, 255), random.randrange(0, 255)), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_BOTTOM.get_width()/2, pipes[pipe_ind].bottom), 5)
                    except:
                        pass
            else:
                if DRAW_LINES:
                    try:
                        pygame.draw.line(win, bird.color, (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_TOP.get_width()/2, pipes[pipe_ind].height), 5)
                        pygame.draw.line(win, bird.color, (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_BOTTOM.get_width()/2, pipes[pipe_ind].bottom), 5)
                    except:
                        pass
            # draw bird
            bird.draw(win)

        pygame.display.update()

    def main(genomes, config):

        global GEN
        GEN += 1

        nets = []
        ge = []
        birds = []

        for _, g in genomes:
            net = neat.nn.FeedForwardNetwork.create(g, config)
            nets.append(net)
            birds.append(Bird(230, 350))
            g.fitness = 0
            ge.append(g)

        base = Base(730)
        pipes = [Pipe(700)]
        
        pygame.display.set_caption('Flappy Bird')
        win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        clock = pygame.time.Clock()
        score = 0
        run = True

        while run:
            clock.tick(1000000)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    pygame.quit()
                    quit()

            pipe_ind = 0
            if len(birds) > 0:
                if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                    pipe_ind = 1
            else:
                run = False
                break

            for x, bird in enumerate(birds):
                bird.move()
                ge[x].fitness += 0.05
                if bird.y < 10:
                    ge[x].fitness -= 0.5

                output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

                if output[0] > 0.5:
                    bird.jump()

            add_pipe = False
            rem = []

            for pipe in pipes:

                for x, bird in enumerate(birds):
                    if pipe.collide(bird):
                        ge[x].fitness = -5
                        birds.pop(x)
                        nets.pop(x)
                        ge.pop(x)
                    
                    if not pipe.passed and pipe.x < bird.x:
                        pipe.passed = True
                        add_pipe = True

                if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                    rem.append(pipe)
                
                pipe.move()

            if add_pipe:
                score += 1
                for g in ge:
                    g.fitness += 5

                pipes.append(Pipe(550))

            for r in rem:
                pipes.remove(r)
            
            for x, bird in enumerate(birds):
                if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)
                    

            base.move()
            draw_window(win, birds, pipes, base, score, GEN, pipe_ind)

    def run(config_path):
            config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)

            p = neat.Population(config)

            p.add_reporter(neat.StdOutReporter(True))
            stats = neat.StatisticsReporter()
            p.add_reporter(stats)

            winner = p.run(main ,50)

    if __name__ == '__main__':
        local_dir = os.path.dirname(__file__)
        config_path = os.path.join(local_dir, 'neat_config.txt')
        run(config_path)


elif play == "Play Yourself":
    main2(play)
