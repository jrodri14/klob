from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from direct.showbase.DirectObject import DirectObject


from direct.interval.IntervalGlobal import *
from direct.gui.OnscreenImage import OnscreenImage
import random, sys, os, math
from math import pi, sin, cos

from panda3d.ai import *
from pandac.PandaModules import *
from direct.showbase.RandomNumGen import RandomNumGen

from panda3d.core import Point3, NodePath, PandaNode
from panda3d.core import CollisionTraverser,CollisionNode
from panda3d.core import CollisionHandlerQueue,CollisionRay
from panda3d.core import Vec3,Vec4,BitMask32
from panda3d.core import PandaNode,Camera,TextNode
from direct.gui.DirectGui import *
from panda3d.core import Shader
from direct.filter.CommonFilters import CommonFilters
from direct.showbase.Transitions import Transitions 
from panda3d.core import WindowProperties
from direct.showbase.Audio3DManager import Audio3DManager




from pandac.PandaModules import loadPrcFileData
loadPrcFileData("", "window-title Klob's World")
#loadPrcFileData("", "fullscreen 1") # Set to 1 for fullscreen
loadPrcFileData("", "win-size 1280 700")
loadPrcFileData("", "win-origin -2 -2")

class KlobWorld(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        ## wp = WindowProperties(base.win.getProperties())
        ## wp.setSize(1280,720)
        ## base.win.requestProperties(wp)
        base.setBackgroundColor(255,250,250)
               
        self.listAudio3d = []
        self.allSounds()
        
        self.energyTime = 0
        self.collHandQue = CollisionHandlerQueue()
        self.collHandQueEne = CollisionHandlerQueue()
        
        self.SPEED = .5
        self.speedv = 4
        base.cTrav = CollisionTraverser()
        self.bossLvl = False
        self.bossDead = False
        self.isMoving = False
        self.pause = True
        self.floater = NodePath(PandaNode("floater"))
        self.floater.reparentTo(render)
        
        self.currentLevel = "start"
        
        self.keyMap = {"left":0, "right":0, "forward":0, "backward":0,
                        "cam-left":0, "cam-right":0, "cam-up":0, "cam-down":0,
                        "fire-down":0, "p":0}
        
        
        ###Disable the default camera controls###
        base.disableMouse()
        
        self.pusher = CollisionHandlerPusher()
        base.cTrav.setRespectPrevTransform(True)
        
        #Uncomment to show collisions with environment
        #base.cTrav.showCollisions(render)
        
        self.setAcceptKeys()
        self.MainMenu()

        ## List to keep track of all actors added in each level
        ## to make it easier to cleanup level when destroyed
        self.crAct = []
        self.extraElements = []
        self.laserAmo = []
        self.beamC = []
        self.laserAmoCount = 0
        self.enemyTimer = 0
        self.gunAmmoCount = 0
        self.loaded = []
        self.bulletC = []

    def allSounds(self):
    
        self.audio = Audio3DManager(self.sfxManagerList[0])
        
        self.audio.attachListener(base.camera)
        
        self.heartBeat = base.loadMusic("sounds/heartbeat.wav")
        self.cheer = base.loadMusic("sounds/cheer.wav")
        
        
        self.intro = base.loadMusic("sounds/Mario.wav")
        self.bulletSound = base.loadMusic("sounds/gun_shot.wav")
        self.laserSound = base.loadMusic("sounds/gun_shot.wav")
        self.deadSound = base.loadMusic("sounds/pacman_death.wav")
        self.sound = self.audio.loadSfx("sounds/forest.wav")
        self.gust = base.loadMusic("sounds/gust.wav")
        self.siren = base.loadMusic("sounds/siren_2.wav")
        self.waterfallSound = self.audio.loadSfx("sounds/waterfall.wav")
        self.etSound = base.loadMusic("sounds/et-sound.wav")
        self.walking = base.loadMusic("sounds/running.wav")
        self.mainMenuMusic = base.loadMusic("sounds/intro.wav")
        self.rainforestMusic = self.loader.loadSfx("sounds/rainforest.wav")
        self.egyptMusic = self.loader.loadSfx("sounds/egypt.wav")
        self.asiaMusic = self.loader.loadSfx("sounds/asia.wav")
        self.newyorkMusic = self.loader.loadSfx("sounds/newyork.wav")
        
        self.mainMenuMusic.setLoop(True)
        self.rainforestMusic.setLoop(True)
        self.egyptMusic.setLoop(True)
        self.asiaMusic.setLoop(True)
        self.newyorkMusic.setLoop(True)
        
        self.gust.setLoop(True)
        self.sound.setLoop(True)
        self.siren.setLoop(True)
        
        self.walking.setVolume(5)
        self.heartBeat.setVolume(5)
        self.deadSound.setVolume(.5)
        self.laserSound.setVolume(.2)
        self.bulletSound.setVolume(.2)
        self.sound.setVolume(2)
        self.rainforestMusic.setVolume(.6)
        self.egyptMusic.setVolume(2)
        self.siren.setVolume(.3)
    
    def stopAllSounds(self):
        self.audio.detachSound(self.waterfallSound)
        self.audio.detachSound(self.sound)
        self.audio.detachSound(self.rainforestMusic)
        self.audio.detachSound(self.egyptMusic)
        self.audio.detachSound(self.newyorkMusic)
        
        self.intro.stop()
        self.bulletSound.stop()
        self.laserSound.stop()
        self.deadSound.stop()
        self.sound.stop()
        self.gust.stop()
        self.siren.stop()
        self.waterfallSound.stop()
        self.etSound.stop()
        self.walking.stop()
        self.mainMenuMusic.stop()
        self.rainforestMusic.stop()
        self.egyptMusic.stop()
        self.asiaMusic.stop()
        self.newyorkMusic.stop()
        
        
       
    def MainMenuLevels(self):
        if(self.currentLevel != "start"):
            self.destroyLevel()
            self.stopAllSounds()
            
        self.level1Btn = DirectButton(
                                scale = (0.27,0.1,0.1),
                                command = self.loadRainforestLevel,
                                pos = Vec3(0, 0, 0.4),
                                image = 'GUI/southamericabutton.png', 
                                relief = None)
        self.level2Btn = DirectButton(
                                scale = (0.27,0.1,0.1),
                                command = self.loadAfricaLevel,
                                pos = Vec3(0, 0, 0.15),
                                image = 'GUI/africabutton.png', 
                                relief = None)
        self.level3Btn = DirectButton(
                                scale = (0.27,0.1,0.1),
                                command = self.loadAsiaLevel,
                                pos = Vec3(0, 0, -0.1),
                                image = 'GUI/asiabutton.png', 
                                relief = None)
        self.level4Btn = DirectButton(
                                scale = (0.27,0.1,0.1),
                                command = self.loadNewYorkLevel,
                                pos = Vec3(0, 0, -0.35),
                                image = 'GUI/americabutton.png', 
                                relief = None)    
       
        self.level2Btn.setTransparency(TransparencyAttrib.MAlpha)
        self.level3Btn.setTransparency(TransparencyAttrib.MAlpha)
        self.level4Btn.setTransparency(TransparencyAttrib.MAlpha)
        self.level1Btn.setTransparency(TransparencyAttrib.MAlpha)
    

    def destroyMainMenuLevels(self):
        self.level1Btn.destroy()
        self.level2Btn.destroy()
        self.level3Btn.destroy()
        self.level4Btn.destroy()
        self.mainMenuBtn = DirectButton(
                        text="Main Menu",
                        scale = (0.1,0.1,0.1),
                        command = self.MainMenuLevels,
                        pos = Vec3(0.8, 0, -0.9))
        
    def MainMenu(self):
        if(self.currentLevel == "help"):
            self.destroyHelpMenu()
        elif(self.currentLevel != "start"):
            self.destroyLevel()
            self.mainMenuBtn.destroy()
            self.stopAllSounds()
            
        self.currentLevel="start"
        self.mainMenuImage = OnscreenImage("GUI/mainmenu.png",pos = Vec3(0, 0.0,-0.8), scale=(1.8, 0, 1.8))
        self.mainMenuImage.reparentTo(aspect2d)
        self.mainMenuImage.setTransparency(1)
        self.mainMenuMusic.play()
        mapStart = loader.loadModel('GUI/button_maps.egg') 
        self.startBtn = DirectButton(geom =
                        (mapStart.find('**/start_but'),
                         mapStart.find('**/start_but_click'),
                         mapStart.find('**/start_but_roll'),
                         mapStart.find('**/start_but_disabled')),
                         relief = None,
                         command = self.introScreen,
                         scale = (0.7,0.7,0.7),
                         pos = Vec3(0.6, 0, -0.35))
        self.startBtn.setTransparency(TransparencyAttrib.MAlpha)
        mapHelp = loader.loadModel('GUI/helpbutton_maps.egg') 
        self.helpBtn = DirectButton(geom =
                        (mapHelp.find('**/help_but'),
                         mapHelp.find('**/help_but_click'),
                         mapHelp.find('**/help_but_roll'),
                         mapHelp.find('**/help_but_disabled')),
                         relief = None,
                         command = self.HelpMenu,
                         scale = (0.8,0.65,0.65),
                         pos = Vec3(0.6, 0,-0.65))
        self.helpBtn.setTransparency(TransparencyAttrib.MAlpha)
        
    def destroyMainMenu(self):
        self.startBtn.destroy()
        self.helpBtn.destroy()
        self.mainMenuImage.destroy()
        self.stopAllSounds()
        
    def HelpMenu(self):
        self.destroyMainMenu()
        self.currentLevel="help"
        self.helpMenuImage = OnscreenImage("GUI/helpmenu.png",pos = Vec3(0, 0.0,-0.8), scale=(1.8, 0, 1.8))
        self.helpMenuImage.reparentTo(aspect2d)
        self.helpMenuImage.setTransparency(1)
        
        mapHelp = loader.loadModel('GUI/backbutton_maps.egg') 
        self.backBtn = DirectButton(geom =
                        (mapHelp.find('**/backBtn'),
                         mapHelp.find('**/backBtn_click'),
                         mapHelp.find('**/backBtn_roll'),
                         mapHelp.find('**/backBtn_disabled')),
                         relief = None,
                         command = self.MainMenu,
                         scale = (0.7,0.7,0.7),
                         pos = Vec3(-1.4, 0, 0.8))
        self.backBtn.setTransparency(TransparencyAttrib.MAlpha)
      ###......
      #code missing.
     ### ....
        
    ##Records the state of the arrow keys###
    def setKey(self, key, value):
        if(self.pause is False):
            self.keyMap[key] = value
    
            
            if(self.keyMap["fire-down"] != 0 ):
                if( self.energy['value'] != 0 ):
    
                    if(self.bossDead is False):
                        self.beamC.append( self.loadLaser() )
                        self.laserAmo.append( self.laser() )
                    if(self.laserAmo):    
                        self.laserAmo[self.laserAmoCount].start()
                    self.energy['value'] -= 3
                    self.laserAmoCount = self.laserAmoCount + 1
                    
        
            
    def loadEnviron(self, filename, scale):
        
        self.environ = self.loader.loadModel(filename)
        self.environ.setScale(scale)
        self.environ.reparentTo(self.render)
        self.environ.setPos(0, 0, 0)
        self.environ.setTag('wall','1')
        self.environ.setCollideMask(BitMask32(0x01))
        
        alight = AmbientLight('alight')
        alight.setColor(VBase4(0.8, 0.8, 0.8, 1))
        alnp = render.attachNewNode(alight)
        render.setLight(alnp)
    
    
    def loadAlien(self, point):

        ###Load alien actor###
        self.alien = Actor("models/alien/slugrocket-model",
                           {"walk":"models/alien/slugrocket-anim"})
                           
        self.alien.reparentTo(render)
        self.alien.setScale(3)
        self.alien.setPos(point)
        self.alien.setPlayRate(1.2, "walk")
        self.alien.setBlend(frameBlend = True)
        
        self.dlight = DirectionalLight('my dlight')
        self.dlnp = render.attachNewNode(self.dlight)
        self.dlnp.reparentTo(base.camera)
        self.dlnp.lookAt(self.alien)
        self.dlight.setColor(VBase4(0.8, 0.8, 0.5, 1))
        render.setLight(self.dlnp)
        
        base.camera.setPos(0,-10,2)
        base.camera.reparentTo(self.alien)
        

        self.camGroundRay = CollisionRay()
        self.camGroundRay.setOrigin(0,0,1000)
        self.camGroundRay.setDirection(0,0,-1)
        self.camGroundCol = CollisionNode('camRay')
        self.camGroundCol.addSolid(self.camGroundRay)
        self.camGroundCol.setFromCollideMask(BitMask32.bit(2))
        self.camGroundCol.setIntoCollideMask(BitMask32.allOff())
        self.camGroundColNp = base.camera.attachNewNode(self.camGroundCol)
        self.camGroundHandler = CollisionHandlerQueue()
        base.cTrav.addCollider(self.camGroundColNp, self.camGroundHandler)
        
        
        csAlien = CollisionSphere(0,0,0.6,0.6)
        cnodeAlienPath = self.alien.attachNewNode(CollisionNode('csAlien'))
        cnodeAlienPath.node().addSolid(csAlien)
        self.pusher.addCollider(cnodeAlienPath, self.alien)
        base.cTrav.addCollider(cnodeAlienPath, self.pusher)
        
        ### Uncomment the following comment to show 
        ### the Collision Sphere on the alien
        ## cnodeAlienPath.show()

        self.health = DirectWaitBar(scale = 0.5,
                            range = 100,
                            value = 100,
                            barColor = (0,1,0,1),
                            pos = Vec3(0.75, 0, 0.9))
                                    
        self.energy = DirectWaitBar(scale = 0.5,
                                    range = 100,
                                    value = 100,
                                    barColor = (1,1,0,1),
                                    pos = Vec3(-0.75, 0, 0.9))
        self.energy.reparentTo(aspect2d)
        self.health.reparentTo(aspect2d)
        self.hud = OnscreenImage("GUI/hud.png",scale = Vec3(1.43, 1.0, 1.03),pos = Vec3(0, 0.0,0.045))
        self.hud.reparentTo(aspect2d)
        self.hud.setTransparency(1)
        self.extraElements.append(self.energy)
        self.extraElements.append(self.health)
        self.extraElements.append(self.hud)

        
        
    def alienDie(self, currLvl):
        self.alien.stop()
        self.pause=True
        temp = NodePath(PandaNode("temp"))
        
        base.camera.reparentTo(self.floater)
        base.camera.setZ(base.camera.getZ()+1)
        base.camera.setY(base.camera.getY()-25)
        self.deadSound.play()
        
        fall = LerpHprInterval(nodePath=self.alien, duration=1.5, hpr=(self.alien.getH(),self.alien.getP(), self.alien.getR()-80))
        fall.start()
        
        
        taskMgr.remove("moveTask")
        taskMgr.remove("laterFc")
        transition = Transitions(loader) 
        transition.setFadeColor(0, 0, 0)
        self.dieImage = OnscreenImage("GUI/died.png",scale = Vec3(0.7, 0, 0.2),pos = Vec3(0, 0,-0.5))
        self.dieImage.reparentTo(aspect2d)
        self.dieImage.setTransparency(1)
        if(self.currentLevel == "rainforest"):
            Sequence(Wait(2.0),Func(transition.fadeOut),Wait(2.0),Func(self.destroyLevel),Func(self.loadRainforestLevel),Func(self.dieImage.destroy),Func(transition.fadeIn)).start()
        elif(self.currentLevel == "africa"):
            Sequence(Wait(2.0),Func(transition.fadeOut),Wait(2.0),Func(self.destroyLevel),Func(self.loadAfricaLevel),Func(self.dieImage.destroy),Func(transition.fadeIn)).start()
        elif(self.currentLevel == "asia"):
            Sequence(Wait(2.0),Func(transition.fadeOut),Wait(2.0),Func(self.destroyLevel),Func(self.loadAsiaLevel),Func(self.dieImage.destroy),Func(transition.fadeIn)).start()
        elif(self.currentLevel == "newyork"):
            Sequence(Wait(2.0),Func(transition.fadeOut),Wait(2.0),Func(self.destroyLevel),Func(self.loadNewYorkLevel),Func(self.dieImage.destroy),Func(transition.fadeIn)).start()
        
        
    def collide(self, collEntry):
        collEntry.getFromNodePath().getParent().removeNode()
        
        
        
    def setAcceptKeys(self):
        
        ###Accept the control keys for movement and rotation###
        self.accept("escape", sys.exit)
        self.accept("p", self.setKey, ["p",1])
        
        
        self.accept("arrow_up", self.setKey, ["forward",1])
        self.accept("arrow_up-up", self.setKey, ["forward",0])
        
        self.accept("arrow_down", self.setKey, ["backward", 1])
        self.accept("arrow_down-up", self.setKey, ["backward", 0])
        
        self.accept("arrow_left", self.setKey, ["left",1])
        self.accept("arrow_left-up", self.setKey, ["left",0])
        
        self.accept("arrow_right", self.setKey, ["right",1])
        self.accept("arrow_right-up", self.setKey, ["right",0])

        self.accept("a", self.setKey, ["cam-left",1])
        self.accept("a-up", self.setKey, ["cam-left",0])
        
        self.accept("s", self.setKey, ["cam-right",1])    
        self.accept("s-up", self.setKey, ["cam-right",0])
        
        self.accept("z", self.setKey, ["cam-up",1])
        self.accept("z-up", self.setKey, ["cam-up",0])
        
        self.accept("x", self.setKey, ["cam-down", 1])
        self.accept("x-up", self.setKey, ["cam-down", 0])
        
        # Accept f to fire 
        self.accept("f", self.setKey, ["fire-down",1])
        self.accept("f-up", self.setKey, ["fire-down",0])
        self.cTrav.traverse(render)
    
        
    
    
    #gun / laser code ommitted
    
    def getDistance(self, actor):
       self.vecAlien = Vec3(self.alien.getPos())
       self.vecObj = Vec3(actor.getPos())
       disVec = self.vecObj - self.vecAlien

       return disVec.length()    

    def myFunction(self,task):
        
        self.walking.play()
        
        if(self.pause is False):
            for r in range(0, len(self.crAct)):
                self.crAct[r].setTarget(self.alien)     
                self.bulletC.append( self.createBullet(self.crAct[r]) )
                self.loaded.append( self.loadBullet( self.crAct[r]) )                        
                self.loaded[self.gunAmmoCount].start()
                self.gunAmmoCount += 1
                self.bulletSound.play()
            return task.again    
        
        
    def bossLvlTask(self, dec, task):
        self.crAct[0].setAiPursue(self.alien)
                
        if(self.pause is False):
            self.deleteProjectiles()
            
            self.charcMoveKeys()
            startpos = self.alien.getPos()
            
            self.floater.setPos(self.alien.getPos())
            self.floater.setZ(self.alien.getZ() + 2.0)
            base.camera.lookAt(self.floater)
            
            self.collHandQueEne.sortEntries()
            
            if(self.collHandQueEne.getNumEntries() > 0):
                entryb = self.collHandQueEne.getEntry(0)
              
                if( entryb.getIntoNodePath().getName() == "csAlien"):
                    
                    self.health['value'] -=5
                    if(self.bulletC):
                        self.bulletC[self.gunAmmoCount-1].remove()
                        self.bulletC.pop(self.gunAmmoCount-1)
                        self.loaded.pop(self.gunAmmoCount-1)
                        self.gunAmmoCount -= 1
                    if( self.health['value'] < 20 ):
                        self.heartBeat.play()
                    if(self.health['value'] == 0):
                        self.alienDie(self.currentLevel)
                else:
                    self.bulletC[self.gunAmmoCount-1].remove()
                    self.bulletC.pop(self.gunAmmoCount-1)
                    self.loaded.pop(self.gunAmmoCount-1)
                    self.gunAmmoCount -= 1
                    
                    
            self.collHandQue.sortEntries()
            if( self.collHandQue.getNumEntries() > 0 ):
                
                entry = self.collHandQue.getEntry(0)   
                

                if( entry.getIntoNodePath().getName() == self.crAct[0].getCNP()):
                            
                    self.crAct[0].runAround(self.alien)
                            
                    self.crAct[0].setHitCount(1)
                    self.crAct[0].decreaseHealth(dec)
                            
                    if( self.beamC):
                        self.beamC[self.laserAmoCount-1].remove()
                        self.beamC.pop(self.laserAmoCount-1)
                        if(self.laserAmo):
                            self.laserAmo.pop(self.laserAmoCount-1)
                        self.laserAmoCount -= 1

                    if( self.crAct[0].getHealth()%4 == 0):
                        self.crAct[0].jumpAway(self.alien)
                                
                    if( self.crAct[0].getHealth() == 0 ):
                        ## print x.getDeaths()
                        ## if( x.canRespawn() ):
                            ## x.setDeaths(1)
                            ## x.resetHitCount(0)
                
                                    
                            ## x.setX(random.randint(0, 50))
                            ## x.setY(self.alien.getY()+15)
                        ## else:
                        self.crAct[0].cleanup()
                        self.crAct[0].remove()
                        self.crAct.pop(0)
                        self.cutScene()
                           
        if( self.crAct ):
            self.crAct[0].AIworld.update()
                                
        if( self.keyMap["p"]!= 0):
            self.cutScene()
                    
        return task.cont
    
    
    def move(self, task):
        ##ommmitted
        
               
            return task.cont

    
    def deleteProjectiles(self):
        ## if(self.pause is False):
        if(self.laserAmo):
            for i, x in enumerate(self.laserAmo):
                if( not x.isPlaying() ):
                        
                    self.beamC[i].remove()
                    self.beamC.pop(i)
                    self.laserAmo.pop(i)
                    self.laserAmoCount = self.laserAmoCount -1
                        
        if(self.loaded):
            for i, x in enumerate(self.loaded):
                if(not x.isPlaying()):
                    #self.crAct[i].setTarget(self.alien)
                    self.bulletC[i].remove()
                    self.bulletC.pop(i)
                    self.loaded.pop(i)
                    self.gunAmmoCount = self.gunAmmoCount -1
                        
        self.energyTime = self.energyTime + globalClock.getDt()
            
        if(self.energyTime > 2 ):
            if(self.energy['value'] != 100):
                self.energy['value'] +=5
                self.energyTime = 0
                    

    def charcMoveKeys(self):
        if (self.keyMap["cam-left"]!=0):
            base.camera.setX(base.camera, -20 * globalClock.getDt())
                
        if (self.keyMap["cam-right"]!=0):
            base.camera.setX(base.camera, +20 * globalClock.getDt())
                
        if (self.keyMap["cam-up"]!=0):
            base.camera.setY(base.camera, -20 * globalClock.getDt())
                
        if (self.keyMap["cam-down"]!=0):
            base.camera.setY(base.camera, +20 * globalClock.getDt())
                
        if (self.keyMap["forward"]!=0):
            self.alien.setY(self.alien, 10 * globalClock.getDt())
                
                
        if (self.keyMap["backward"]!=0):
            self.alien.setY(self.alien, -10 * globalClock.getDt())
        
                    
        if (self.keyMap["left"]!=0):
                self.alien.setH(self.alien.getH() + 40 * globalClock.getDt())

                
        if (self.keyMap["right"]!=0):
                self.alien.setH(self.alien.getH() - 40 * globalClock.getDt())

        if (self.keyMap["forward"]!=0) or (self.keyMap["left"]!=0) or (self.keyMap["right"]!=0) or (self.keyMap["backward"] != 0):
            if self.isMoving is False:
                self.alien.loop("walk")
                self.isMoving = True
        else:
            if self.isMoving:
                self.alien.stop()
                self.alien.pose("walk",5)
                self.isMoving = False
                

    def loadingScreen(self):
        self.intro.play()
        transition = Transitions(loader) 
        transition.setFadeColor(0, 0, 0)
        text = TextNode('node name')
        dummy = NodePath(PandaNode("dummy"))
        black = OnscreenImage(image="GUI/black.png",pos=(0,0,0), scale=100)
        black.reparentTo(dummy)
        textNodePath = aspect2d.attachNewNode(text)
        textNodePath.reparentTo(aspect2d, 2)
        textNodePath.setScale(0.07)
        text.setTextColor(1, 1, 1, 1)
        
        if(self.currentLevel=="newyork"):
            Sequence(Func(transition.fadeOut),Func(black.reparentTo, aspect2d),Func(transition.fadeIn),Func(textNodePath.reparentTo,aspect2d, 10),Func(text.setText, "loading"),Wait(1.0),Func(text.setText, "loading."), 
                    Wait(1.0),Func(text.setText, "loading.."), Wait(1.0), Func(text.setText, "loading..."), Func(self.loadNextLevel),Wait(3.0),Func(transition.fadeIn),Func(textNodePath.remove), Func(black.destroy)).start()
        elif(self.currentLevel=="asia"):
            Sequence(Func(transition.fadeOut),Func(black.reparentTo, aspect2d),Func(transition.fadeIn),Func(textNodePath.reparentTo,aspect2d, 10),Func(text.setText, "loading"),Wait(1.0),Func(text.setText, "loading."), 
                    Wait(1.0),Func(text.setText, "loading.."), Wait(1.0), Func(text.setText, "loading..."), Func(self.loadNextLevel),Wait(3.0),Func(transition.fadeIn),Func(textNodePath.remove), Func(black.destroy)).start()
        else:
            Sequence(Func(transition.fadeOut),Func(black.reparentTo, aspect2d),Func(transition.fadeIn),Func(textNodePath.reparentTo,aspect2d, 10),Func(text.setText, "loading"),Wait(0.5),Func(text.setText, "loading."), 
                    Wait(0.5),Func(text.setText, "loading.."), Wait(0.5), Func(text.setText, "loading..."), Func(self.loadNextLevel),Wait(1.5),Func(transition.fadeIn),Func(textNodePath.remove), Func(black.destroy)).start()
        
        
    def cutScene(self):
        self.destroyLevel()
        self.stopAllSounds()
        
        self.cut = OnscreenImage("GUI/bossKilled.png",scale = Vec3(1.6, 0, 1.0),pos = Vec3(0, 0,0))
        self.cut.reparentTo(aspect2d)
        self.cut.setTransparency(1)
        transition = Transitions(loader) 
        transition.setFadeColor(0, 0, 0)
        self.cheer.play()
        if(self.currentLevel=="rainforest"):
            Sequence(Wait(2.0),Func(transition.fadeOut),Wait(1.0),Func(transition.fadeIn),Func(self.cut.setImage,"GUI/map_11.png"),
                     Wait(1.5),Func(self.cut.setImage, "GUI/map_12.png"),Wait(0.5),Func(self.cut.setImage,"GUI/map_13.png"),
                     Wait(0.5),Func(self.cut.setImage,"GUI/map_14.png"),Wait(0.5),Func(self.cut.setImage,"GUI/map_15.png"),
                     Wait(0.5),Func(self.cut.setImage,"GUI/map_16.png"),Wait(3.5),Func(self.cut.destroy), Func(transition.fadeOut), Func(self.loadingScreen), Wait(1.0),Func(transition.fadeIn)).start()
        elif(self.currentLevel=="africa"):
            Sequence(Wait(2.0),Func(transition.fadeOut),Wait(1.0),Func(transition.fadeIn),Func(self.cut.setImage,"GUI/map_21.png"),
                     Wait(1.5),Func(self.cut.setImage, "GUI/map_22.png"),Wait(0.5),Func(self.cut.setImage,"GUI/map_23.png"),
                     Wait(0.5),Func(self.cut.setImage,"GUI/map_24.png"),Wait(0.5),Func(self.cut.setImage,"GUI/map_25.png"),
                     Wait(0.5),Func(self.cut.setImage,"GUI/map_26.png"), Wait(3.5),Func(self.cut.destroy), Func(transition.fadeOut),Func(self.loadingScreen), Wait(1.0),Func(transition.fadeIn)).start()
        elif(self.currentLevel=="asia"):
            Sequence(Wait(2.0),Func(transition.fadeOut),Wait(1.0),Func(transition.fadeIn),Func(self.cut.setImage,"GUI/map_31.png"),
                     Wait(1.5),Func(self.cut.setImage, "GUI/map_32.png"),Wait(0.5),Func(self.cut.setImage,"GUI/map_33.png"),
                     Wait(0.5),Func(self.cut.setImage,"GUI/map_34.png"),Wait(0.5),Func(self.cut.setImage,"GUI/map_35.png"),
                     Wait(0.5),Func(self.cut.setImage,"GUI/map_36.png"),Wait(3.5),Func(self.cut.destroy), Func(transition.fadeOut),Func(self.loadingScreen), Wait(1.0),Func(transition.fadeIn)).start()
        elif(self.currentLevel=="newyork"):
            Sequence(Wait(2.0),Func(transition.fadeOut),Wait(1.0),Func(transition.fadeIn),Func(self.cut.setImage,"GUI/win.png"),
                     Wait(6.5),Func(self.cut.destroy), Func(transition.fadeOut),Func(self.loadingScreen), Wait(1.0),Func(transition.fadeIn)).start()
            
     
    def loadNextLevel(self):
        if(self.currentLevel=="start"):
            self.loadRainforestLevel()
        elif(self.currentLevel=="rainforest"):
            self.loadAfricaLevel()
        elif(self.currentLevel=="africa"):
            self.loadAsiaLevel()
        elif(self.currentLevel=="asia"):
            self.loadNewYorkLevel()
        else:
            self.MainMenu()
  
    def destroyLevel(self):
        self.mainMenuBtn.destroy()
        taskMgr.remove("moveTask")
        taskMgr.remove("bossTask")
        taskMgr.remove("myFunction")
        self.alien.cleanup()
        for enemy in self.crAct:
            enemy.cleanup()
            enemy.remove()
        self.alien.cleanup()
        self.alien.remove()    
        for element in self.extraElements:
            element.removeNode()
        for beam in self.beamC:
            beam.removeNode()
        self.render.clearFog    
        self.laserBeam2.removeNode()
        
        self.environ.removeNode()
        self.crAct[:] = []
        self.extraElements[:] = []

        self.laserAmo[:] =[]
        self.laserAmoCount = 0

        
    def loadBossActor(self):
        self.bossLvl = True
        ###Load Ralph Boss actor###
        difficult = 10
        taskMgr.remove("moveTask")
        taskMgr.remove("myFunction")
        self.health['value'] = 100
        self.energy['value'] = 100
        
        if(self.bossDead is False):
            self.bossImage = OnscreenImage("GUI/bossLoad.png",scale = Vec3(1.6, 0, 1.0),pos = Vec3(0, 0,0))
            self.bossImage.reparentTo(aspect2d)
            self.bossImage.setTransparency(1)
            self.ralphBoss = EnemyActor(1,difficult,True)
            self.ralphBoss.enemy.setScale(2.0)
            self.crAct.append(self.ralphBoss)
            Sequence(Wait(3.0), Func(self.bossImage.destroy), Func(self.crAct[0].showHealthBar)).start()
            
            self.extraElements.append(self.crAct[0].bossHud)
            self.extraElements.append(self.crAct[0].health)
            self.crAct[0].setAiPursue(self.alien)
            self.pusher.addCollider(self.crAct[0].getFromObj(), self.crAct[0].enemy)
            base.cTrav.addCollider(self.crAct[0].getFromObj(), self.pusher)
            gunTex = loader.loadTexture('models/gun_tex.png')
            if(self.currentLevel == "rainforest"):
                dec = 5
                self.ralphBoss.enemy.setPos(0,90,0)
                ralphTex = loader.loadTexture('models/ralph2rainforest.png')
                self.ralphBoss.enemy.setTexture(ralphTex, 1)
                self.ralphBoss.gunPos.setTexture(gunTex, 1)
            elif(self.currentLevel == "africa"):
                dec = 4
                self.ralphBoss.enemy.setPos(-100,-90,0)
                ralphTex = loader.loadTexture('models/ralph2egypt.png')
                self.ralphBoss.enemy.setTexture(ralphTex, 1)
                self.ralphBoss.gunPos.setTexture(gunTex, 1)
            elif(self.currentLevel == "asia"):
                dec = 3
                self.ralphBoss.enemy.setPos(0,0,0)
                ralphTex = loader.loadTexture('models/ralph2asia.png')
                self.ralphBoss.enemy.setTexture(ralphTex, 1)
                self.ralphBoss.gunPos.setTexture(gunTex, 1)
            elif(self.currentLevel == "newyork"):
                dec = 2
                self.ralphBoss.enemy.setPos(120,10,0)
         
        taskMgr.add(self.bossLvlTask,"bossTask", extraArgs = [dec], appendTask=True)
        taskMgr.doMethodLater(1,self.myFunction,"myFunction")
            
    
    
    def loadRainforestLevel(self):
        self.keyMap = {"left":0, "right":0, "forward":0, "backward":0,
                        "cam-left":0, "cam-right":0, "cam-up":0, "cam-down":0,
                        "fire-down":0,  "p":0}
        self.pause = False
        self.currentLevel = "rainforest"
        self.destroyIntro()
        difficulty = 2
        self.bossLvl = False
        self.bossDead = False
        ###Load alien###
        startPos = Point3(0,0,0)
        self.loadAlien(startPos)
        self.rainforestMusic.play()
        ###Load the enemies###
        ralphTex = loader.loadTexture('models/ralph2rainforest.png')
        gunTex = loader.loadTexture('models/gun_tex.png')
        for i in range(0,2):
            enemy = EnemyActor(i, difficulty, False)
            enemy.enemy.setTexture(ralphTex, 1)
            enemy.gunPos.setTexture(gunTex, 1)
            
            enemy.setX(random.randint(-50,50))
            enemy.setY(random.randint(-50,50))
            enemy.setZ(0)
            
            self.crAct.append(enemy)
            self.crAct[i].setAiPursue(self.alien)
            
            self.pusher.addCollider(self.crAct[i].getFromObj(), self.crAct[i].enemy)
            base.cTrav.addCollider(self.crAct[i].getFromObj(), self.pusher)
        
            
        taskMgr.add(self.move,"moveTask")
        taskMgr.doMethodLater(3,self.myFunction,"myFunction")
        self.loadLaser2()
        self.loadLaser()
        
        ###Load the environment###
        self.loadEnviron("models/south_america/rainforest", 5)
        self.plants = self.loader.loadModel("models/south_america/rainforest-nocollision")
        self.plants.reparentTo(self.render)
        self.plants.setScale(4)
        self.plants.setTwoSided(True)
        self.extraElements.append(self.plants)
        
        self.myFog = Fog("FOG")
        self.myFog.setColor(0.5,0.6,0.5)
        self.myFog.setExpDensity(0.005)
        render.setFog(self.myFog)
        self.audio.attachSoundToObject(self.sound, self.environ)
        self.audio.setSoundVelocityAuto(self.sound)
        self.audio.setListenerVelocityAuto()
        
        self.sound.play()
        
    
    def loadAfricaLevel(self):
        self.keyMap = {"left":0, "right":0, "forward":0, "backward":0,
                        "cam-left":0, "cam-right":0, "cam-up":0, "cam-down":0,
                        "fire-down":0, "p":0}
        self.pause = False
        self.currentLevel="africa"
        
        difficulty = 3
        self.bossLvl = False
        self.bossDead = False
        ###Load alien###
        startPos = Point3(-130,-130,0)
        self.loadAlien(startPos)
        self.alien.setH(-40)
        
        ###Load the enemies###
        ralphTex = loader.loadTexture('models/ralph2egypt.png')
        gunTex = loader.loadTexture('models/gun_tex.png')
        for i in range(0,3):
            enemy = EnemyActor(i, difficulty, False)
            enemy.enemy.setTexture(ralphTex, 1)
            enemy.gunPos.setTexture(gunTex, 1)
            enemy.setX(random.randint(-170,-50))
            enemy.setY(random.randint(-170,-50))
            enemy.setZ(0)
        
            self.crAct.append(enemy)
            
            self.crAct[i].setAiPursue(self.alien)
            
            self.pusher.addCollider(self.crAct[i].getFromObj(), self.crAct[i].enemy)
            base.cTrav.addCollider(self.crAct[i].getFromObj(), self.pusher)

        taskMgr.add(self.move,"moveTask")
        taskMgr.doMethodLater(3,self.myFunction,"myFunction")
        
        self.loadLaser2()
        self.loadLaser()
       
        ###Load environment###
        self.loadEnviron("models/africa/egypt", 7)
        self.egypt_nc = self.loader.loadModel("models/africa/egypt-nocollision")
        self.egypt_nc.reparentTo(self.render)
        self.egypt_nc.setPos(0,0,0)
        self.egypt_nc.setScale(7)
        self.extraElements.append(self.egypt_nc)
        self.sphinx = self.loader.loadModel("models/africa/sphinx")
        self.sphinx.setPos(0,80,0)
        self.sphinx.setH(180)
        self.sphinx.setScale(0.12)
        self.sphinx.reparentTo(self.render)
        self.extraElements.append(self.sphinx)
        
        cs = CollisionSphere(0,0,0,200)
        nodePath = self.sphinx.attachNewNode(CollisionNode('nodePath'))
        nodePath.node().addSolid(cs)
        self.gust.play()
        self.audio.attachSoundToObject(self.egyptMusic, self.environ)
        self.audio.setSoundVelocityAuto(self.egyptMusic)
        self.audio.setListenerVelocityAuto()
        self.egyptMusic.play()
        
        
    def loadAsiaLevel(self):
        self.keyMap = {"left":0, "right":0, "forward":0, "backward":0,
                        "cam-left":0, "cam-right":0, "cam-up":0, "cam-down":0,
                        "fire-down":0, "p":0}
        self.pause = False
        self.currentLevel = "asia"

        difficulty = 4
        self.bossLvl = False
        self.bossDead = False
        ###Load alien###
        startPos = Point3(190,-140,0)
        self.loadAlien(startPos)
        ###Load the enemies###
        ralphTex = loader.loadTexture('models/ralph2asia.png')
        gunTex = loader.loadTexture('models/gun_tex.png')
        for i in range(0,4):
            enemy = EnemyActor(i, difficulty, False)
            enemy.enemy.setTexture(ralphTex, 1)
            enemy.gunPos.setTexture(gunTex, 1)
            enemy.setX(random.randint(0,100))
            enemy.setY(random.randint(-150,-50))
            enemy.setZ(0)
      
            self.crAct.append(enemy)
            self.crAct[i].setAiPursue(self.alien)
            
            self.pusher.addCollider(self.crAct[i].getFromObj(), self.crAct[i].enemy)
            base.cTrav.addCollider(self.crAct[i].getFromObj(), self.pusher)
            
        taskMgr.add(self.move,"moveTask")
        taskMgr.doMethodLater(3,self.myFunction,"myFunction")
        
        self.loadLaser2()
        self.loadLaser()
        
        ###Load the environment###
        self.loadEnviron("models/asia/asia2", 5)
        self.asia_nc = self.loader.loadModel("models/asia/asia-nocollision")
        self.asia_nc.reparentTo(self.render)
        self.asia_nc.setPos(0,0,0)
        self.asia_nc.setScale(5)
        self.extraElements.append(self.asia_nc)
        
        self.myFog = Fog("FOG")
        self.myFog.setColor(0.8,0.8,0.8)
        self.myFog.setExpDensity(0.002)
        render.setFog(self.myFog)
        
        self.bonzai = self.loader.loadModel("models/asia/bonzai")
        self.bonzai.reparentTo(self.render)
        self.bonzai.setPos(170,20,0)
        self.bonzai.setScale(0.015)
        self.bonzai.setH(90)
        self.extraElements.append(self.bonzai)
        cs = CollisionSphere(0,0,200,200)
        nodePath = self.bonzai.attachNewNode(CollisionNode('nodePath'))
        nodePath.node().addSolid(cs)
        self.pusher.addCollider(nodePath, self.bonzai)
        
        self.waterfall = self.loader.loadModel("models/asia/waterFall")
        self.waterfall.reparentTo(self.render)
        self.waterfall.setPos(200,80,-.5)
        self.waterfall.setScale(0.25)
        self.waterfall.setH(180)
        self.extraElements.append(self.waterfall)
        cs = CollisionSphere(0,15,-5,130)
        nodePath = self.waterfall.attachNewNode(CollisionNode('nodePath'))
        nodePath.node().addSolid(cs)
        self.pusher.addCollider(nodePath, self.waterfall)
        
        self.waterfallSound.setLoop(True)
        self.audio.attachSoundToObject(self.waterfallSound,self.waterfall)
        self.audio.setSoundVelocityAuto(self.waterfallSound)
        self.audio.setListenerVelocityAuto()
        self.audio.setDistanceFactor(1.5)
        self.waterfallSound.play()
        
        self.tree1 = self.loader.loadModel("models/asia/bamboo")
        self.tree1.reparentTo(self.render)
        self.tree1.setPos(-50,-50,0)
        self.tree1.setScale(0.6,0.6,0.6)
        self.tree1.setBillboardAxis()
        self.extraElements.append(self.tree1)
        
        #Child bamboos scattered around
        placeholder = render.attachNewNode("Bamboo-Placeholder")
        placeholder.setPos(180,-40,0)
        placeholder.setScale(0.8)
        self.tree1.instanceTo(placeholder)
        self.extraElements.append(placeholder)
        
        placeholder = render.attachNewNode("Babmboo-Placeholder")
        placeholder.setPos(-20,-120,0)
        placeholder.setScale(1.0)
        self.tree1.instanceTo(placeholder)
        self.extraElements.append(placeholder)
                
        placeholder = render.attachNewNode("Bamboo-Placeholder")
        placeholder.setPos(-50,180,0)
        placeholder.setScale(1.0)
        self.tree1.instanceTo(placeholder)
        self.extraElements.append(placeholder)
        
        placeholder = render.attachNewNode("Bamboo-Placeholder")
        placeholder.setPos(-60,165,0)
        placeholder.setScale(0.6)
        self.tree1.instanceTo(placeholder)
        self.extraElements.append(placeholder)
        
        placeholder = render.attachNewNode("Bamboo-Placeholder")
        placeholder.setPos(-110,70,0)
        placeholder.setScale(1.0)
        self.tree1.instanceTo(placeholder)
        self.extraElements.append(placeholder)
        
        placeholder = render.attachNewNode("Bamboo-Placeholder")
        placeholder.setPos(-100,-50,0)
        placeholder.setScale(1.6)
        self.tree1.instanceTo(placeholder)
        self.extraElements.append(placeholder)
        
        self.asiaMusic.play()

    
    def loadNewYorkLevel(self):
        self.keyMap = {"left":0, "right":0, "forward":0, "backward":0,
                        "cam-left":0, "cam-right":0, "cam-up":0, "cam-down":0,
                        "fire-down":0,"p":0}
        self.pause = False
        self.currentLevel = "newyork"
        #self.destroyMainMenuLevels()
        difficulty = 5
        ###Load alien###
        startPos = Point3(20,10,0)
        self.loadAlien(startPos)
        self.alien.setH(90)
        
        base.camera.setH(90)
        self.bossLvl = False
        self.bossDead = False
        ###Load the enemies###
        for i in range(0,5):
            enemy = EnemyActor(i, difficulty, False)      
            enemy.setX(random.randint(-100,100))
            enemy.setY(random.randint(8,12))
            enemy.setZ(0)
            
            self.crAct.append(enemy)
            self.crAct[i].setAiPursue(self.alien)
            
            self.pusher.addCollider(self.crAct[i].getFromObj(), self.crAct[i].enemy)
            base.cTrav.addCollider(self.crAct[i].getFromObj(), self.pusher)
            
        taskMgr.add(self.move,"moveTask")
        taskMgr.doMethodLater(2,self.myFunction, "myFunction")
     
        self.loadLaser2()
        self.loadLaser()
        
        ###Load the environment###
        self.loadEnviron("models/america/newyork", 4)
        self.ny_nc = self.loader.loadModel("models/america/newyork-nocollision")
        self.ny_nc.reparentTo(self.render)
        self.ny_nc.setScale(4)
        self.extraElements.append(self.ny_nc)
        
        self.statue = self.loader.loadModel("models/america/statue")
        self.statue.reparentTo(self.render)
        self.statue.setPos(270,-100,13)
        self.statue.setScale(1)
        self.statue.setBillboardAxis()
        self.statue.setTwoSided(True)
        self.extraElements.append(self.statue)
        
        self.myFog = Fog("FOG")
        self.myFog.setColor(0.3,0.3,0.3)
        self.myFog.setExpDensity(0.005)
        render.setFog(self.myFog)
        self.siren.play()
        self.newyorkMusic.play()
        
        
#################################################################


    
w = KlobWorld()
run()
