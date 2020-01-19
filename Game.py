import pygame
import math
import random
import sys

sounds = {

    "BackGround" : "sounds/BackGround.mp3",
    "wings" : "sounds/wings.wav",
    "Crash" : "sounds/WoodWhack.wav",
    "sprint": "sounds/sprint.wav",
    "ScorePlus": "sounds/ScorePlus.ogg",
    "GameOver": "sounds/GameOver.mp3"

}

assets = {
    "Background": "assets/backgroundT.png",
    "Floor": "assets/floor.png",
    "PillarUp": "assets/top.png",
    "PillarDown": "assets/bottom.png",
    "Bird": [["assets/0.png", "assets/1.png", "assets/2.png"], ["assets/dead.png"]],
    "GameOver": "assets/Game Over2.png",
}

"""

still have to add rotation _ Done
handle collision & bird Death _ Done

Score Has to be Added // Done
Sound Has to be Added

"""


class FlappyBird:

    def play_sound(self, sound):
        for index, selected_sound in enumerate(self.sounds):
            if sound == selected_sound:             # Problem Solved
                self.channels[index].play(sound)  # we can use channels for simultaneous sounds

    def __init__(self):
        pygame.font.init()
        pygame.mixer.init()

        pygame.mixer.music.load(sounds["BackGround"])
        self.sfxCrash = pygame.mixer.Sound(sounds["Crash"])
        self.sfxWings = pygame.mixer.Sound(sounds["wings"])
        self.scoresfx = pygame.mixer.Sound(sounds["ScorePlus"])
        self.jumpSfx = pygame.mixer.Sound(sounds["sprint"])
        self.sounds = [self.sfxWings, self.scoresfx, self.jumpSfx, self.sfxCrash]
        self.channels = [pygame.mixer.Channel(i) for i in range(len(self.sounds))]

        self.sfxWings.set_volume(3)
        self.jumpSfx.set_volume(0.2)
        self.scoresfx.set_volume(0.1)
        self.font = pygame.font.SysFont("Arial", 80)
        self.gameOverFont = pygame.font.SysFont("Arial", 300)
        self.background = pygame.image.load(assets["Background"])
        self.floor = pygame.image.load(assets["Floor"])
        self.start = False
        self.startText = "Please Press 'S' To Start the Game "
        self.startfont = pygame.font.SysFont("Times new roman", 20)
        self.w = 1300
        self.h = 708
        self.score = 0
        self.isDead = False
        self.screen = pygame.display.set_mode((self.w, self.h))
        self.init_background()
        self.moveBackground = 0
        self.Speed = 5
        self.Gravity = 980
        self.birdMass = 1
        self.BottomPillar = pygame.image.load(assets["PillarDown"]).convert_alpha()  # for transparency
        self.TopPillar = pygame.image.load(assets["PillarUp"]).convert_alpha()
        self.ExistingPillars = []
        self.betweenPillars = 450
        self.pillarMvt = 0
        self.margePillars = 150
        self.birdActualPos = 0
        self.birdAnimFrames = 4
        self.detaTime = 60
        self.birdY = 300
        self.jumpForce = 0
        self.timeDeath = 0
        self.isJump = False
        self.deltaY = 0
        self.jumpForceIntensity = 5000
        self.countedPillars = []
        self.gameOverMusicPlayed = False
        self.downSprint = False
        self.downSprintForce = 0
        self.downSprintForceIntensity = 3000
        self.bird = [
            pygame.image.load(x) for x in assets["Bird"][0]
        ]
        self.birdDead = pygame.image.load(assets["Bird"][1][0])
        self.birdLocalization = {"x", "y", "Rect"}

        self.time = 0
        self.LastTime = 0

    def codeY(self, Y):
        return self.h - Y

    def GameOver(self):
        if self.isDead:
            gameover = pygame.image.load(assets["GameOver"])
            # self.screen.blit(self.gameOverFont.render("GameOver", -1, (255, 0, 0)), (50, self.h/4))
            self.screen.blit(gameover, ((self.w - gameover.get_width())/2, (self.h - gameover.get_height())/2))

    def score_function(self):
        if not self.isDead:

            _, _, w, h = self.birdLocalization["rect"]

            for pillar in self.ExistingPillars:
                _, _, w, h = pillar["Bottom"]

                if pillar not in self.countedPillars and (pillar["x"] < self.birdLocalization["x"] < pillar["x"]+w):
                    self.score += 1
                    self.countedPillars.append(pillar)
                    self.play_sound(self.scoresfx)

        self.screen.blit(self.font.render(str(self.score), -1, (150, 150, 150)), (self.w/2, 50))

    def apply_physics(self):
        if self.isJump:
            self.jumpForce = self.jumpForceIntensity
        else:
            self.jumpForce = 0

        if self.downSprint:
            self.downSprintForce = self.downSprintForceIntensity
        else:
            self.downSprintForce = 0

        mGama= -(self.Gravity*self.birdMass) +self.jumpForce-self.downSprintForce

        deltaYvelocity = (mGama*self.detaTime*10**-3)/self.birdMass
        self.deltaY = deltaYvelocity*self.detaTime*10**-3
        self.birdY = self.codeY(self.birdY)
        self.birdY += self.deltaY
        self.birdY = self.codeY(self.birdY)
        if (self.birdY >= self.h-self.floor.get_height()) and not self.isDead:
            self.Die()
            self.birdY = self.h-self.floor.get_height()
        self.birdLocalization["y"] = self.birdY

        self.isJump = False
        self.downSprint = False

    def actions(self):
        if not self.isDead:
            keys = pygame.key.get_pressed()
            mouse = pygame.mouse.get_pressed()
            if keys[pygame.K_SPACE] or mouse[0]:
                self.bird = [
                    pygame.transform.rotate(pygame.image.load(x), 15) for x in assets["Bird"][0]
                ]
                self.jump()

            elif keys[pygame.K_DOWN] or mouse[2]:
                self.bird = [
                    pygame.transform.rotate(pygame.image.load(x), -15) for x in assets["Bird"][0]
                ]
                self.play_sound(self.jumpSfx)
                self.downSprint = True

            else:
                self.bird = [
                    pygame.image.load(x) for x in assets["Bird"][0]
                ]

    def jump(self):
        self.bird = [
            pygame.transform.rotate(pygame.image.load(x), 30) for x in assets["Bird"][0]
        ]
        self.play_sound(self.jumpSfx)
        self.isJump = True

    def Die(self):

        if not self.isDead:
            self.isDead = True
            pygame.mixer.music.stop()
            self.play_sound(self.sfxCrash)  # still has problems

    def checkCollision(self):
        _, _, w, h = self.birdLocalization["rect"]
        BirdScope = pygame.Rect(self.birdLocalization["x"], self.birdLocalization["y"], w, h)

        for pillar in self.ExistingPillars:
            _, _, w, h = pillar["Bottom"]
            BottomScope = pygame.Rect(pillar["x"], pillar["By"], w, h)

            _, _, w, h = pillar["Top"]
            TopScope = pygame.Rect(pillar["x"], pillar["Ty"], w, h)

            if (BirdScope.colliderect(TopScope) or BirdScope.colliderect(BottomScope)) and not self.isDead:
                self.Die()

    def controlBird(self):
        if self.birdActualPos < self.birdAnimFrames*len(self.bird) - 1:
            self.birdActualPos += 1
        else:
            self.birdActualPos = 0
        if not self.isDead:
            self.play_sound(self.sfxWings)
            pos = self.birdActualPos//self.birdAnimFrames
            self.birdLocalization= {"x": 50, "y": self.birdY,
                                    "rect": self.bird[pos].get_rect()}
            self.screen.blit(self.bird[pos], (50, self.birdY))
        else:
            self.birdLocalization = {"x": 50, "y": self.birdY,
                                     "rect": self.birdDead.get_rect()}
            self.screen.blit(self.birdDead, (50, self.birdY))

    def SpeedControl(self):
        if not self.isDead:
            self.jumpForceIntensity += 3
            self.downSprintForceIntensity += 3
            self.Speed += 0.1  # increase speed after getting score

    def create_Pillars(self):
        # picture = pygame.transform.scale(picture, (1280, 720))

        randomVPos = random.randint(0, 400)

        if self.pillarMvt > self.betweenPillars:
            self.pillarMvt = 0
            self.screen.blit(self.TopPillar, (self.w, -randomVPos))
            self.screen.blit(self.BottomPillar, (self.w, -randomVPos + self.margePillars+self.TopPillar.get_height()))
            pillar = {"Top" : self.TopPillar.get_rect(), "Bottom" : self.BottomPillar.get_rect(), "x" : self.w,
                      "Ty": -randomVPos, "By" : -randomVPos + self.margePillars+self.TopPillar.get_height()}

            self.ExistingPillars.append(pillar)

        for index, pillar in enumerate(self.ExistingPillars):
            pillar["Top"].move((pillar["x"] - self.Speed, pillar["Ty"]))
            pillar["Bottom"].move((pillar["x"] - self.Speed, pillar["By"]))
            self.ExistingPillars[index]["x"] = pillar["x"] - self.Speed
            self.screen.blit(self.TopPillar, (pillar["x"],pillar["Ty"]))
            self.screen.blit(self.BottomPillar, (pillar["x"], pillar["By"]))

        for pillar in self.ExistingPillars:
            if pillar["x"] + self.BottomPillar.get_width() < 0:
                self.ExistingPillars.remove(pillar)
                self.SpeedControl()

    def init_background(self):
        bw, bh = self.background.get_size()
        fw, fh = self.floor.get_size()
        N = math.ceil(self.w/bw)
        for k in range(N):
            self.screen.blit(self.background, (k*bw, 0))
            self.screen.blit(self.floor, (k*fw, self.h-fh))

    def animate_background(self):
        self.screen.fill((255, 255, 255))
        bw, bh = self.background.get_size()
        fw, fh = self.floor.get_size()
        m = math.ceil(self.w / bw)
        N = m*2
        for k in range(N):
            self.screen.blit(self.background, (0 + k * bw - self.moveBackground, 0))
            self.screen.blit(self.floor, (0 + k * fw - self.moveBackground, self.h - fh))
        if self.moveBackground < (m - 1)*bw:
            self.moveBackground += self.Speed
            self.pillarMvt += self.Speed
        else:
            self.moveBackground = 0

    def floor_onforeGround(self):
        fw, fh = self.floor.get_size()
        m = math.ceil(self.w / fw)
        N = m * 2
        for k in range(N):
            self.screen.blit(self.floor, (0 + k * fw - self.moveBackground, self.h - fh))

    def GameOverMusic(self):
        if not self.gameOverMusicPlayed and self.timeDeath*self.detaTime > 1500:
            pygame.mixer.music.load(sounds["GameOver"])
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(0.2)
            self.gameOverMusicPlayed = True

    def start_game(self):
        txt_w, txt_h = self.startfont.size(self.startText)
        delay = 15
        color = (0, 0, 0)
        if not self.start:
            if self.time <= delay+self.LastTime:
                color = (0, 255, 0)
            elif 2*delay+self.LastTime >= self.time > delay+self.LastTime:
                color = (255, 0, 0)
            elif self.time > 2*delay+self.LastTime:
                self.LastTime = self.time

            self.screen.blit(self.startfont.render(self.startText, -1, color),
                             ((self.w - txt_w) / 2, (self.h - txt_h) / 2))

            keys = pygame.key.get_pressed()
            if keys[pygame.K_s]:
                self.start = True

    def run(self):
        clock = pygame.time.Clock()
        pygame.font.init()
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.2)
        while True:

            clock.tick(self.detaTime)
            if self.isDead and not self.gameOverMusicPlayed:
                self.timeDeath += 1
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

            self.start_game()
            if self.start:
                self.animate_background()
                self.create_Pillars()
                self.floor_onforeGround()  # hide the pillars with the Floor as if the pillars comes out from it
                self.controlBird()
                self.checkCollision()
                self.score_function()
                self.actions()
                self.apply_physics()
                self.GameOver()
                self.GameOverMusic()
            else:
                self.time += 1  # each increase means +60 ms (Sample Time)
            pygame.display.update()


f = FlappyBird()
f.run()
