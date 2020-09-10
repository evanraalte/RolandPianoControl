import pygame
import threading
import random








class Canvas(threading.Thread):
    velocities = {}

    def velocities_handler(self):
        for k,v in self.velocities.items():
            if v > 0 : self.velocities[k]-= 1

    def __init__(self,randomize = False):
        super().__init__()
        self.killed = False
        self.randomize = randomize
        # initial values
        
        for i in range(0,88):
            self.velocities[i] = 0
        self.screen = pygame.display.set_mode((880, 300))
        self.screen.fill((0, 0, 0))
        self.clock = pygame.time.Clock()
        self.start()

    def kill(self): 
        self.killed = True


    def draw_bar(self,num,velocity):
        pygame.draw.rect(self.screen,pygame.Color('white'),(num*10+1,300-velocity,8,velocity))

    def draw_rect(self, x, y, width, height, color):
        pygame.draw.rect(self.screen, pygame.Color(color), (x, y, width, height))

    def clear(self):
        self.screen.fill((50, 50, 50))

    def run(self):
        timer = 0
        while True:
            for e in pygame.event.get():
                # print(e)
                if e.type == pygame.QUIT:
                    return
            if self.killed:
                raise SystemExit()
            self.clear()
            for i in range(0,88):
                self.draw_bar(i,(300/127)*self.velocities[i])

            pygame.display.update()
            self.clock.tick(60)
            if self.randomize:
                self.velocities_handler()
                if timer == 6:
                    timer = 0
                    key = random.randint(0,88)
                    self.velocities[key] = random.randint(60,127)

                else:
                    timer += 1

if __name__ == "__main__":
    canvas = Canvas(True)
