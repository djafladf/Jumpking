#Web vpython 3.2
from vpython import *

def on_keydown(event):
    if not(player.IsJump or player.WaitForJump):
        if event.key == "left":
            player.dx = -1
            player.MoveVert = True
        elif event.key == "right":
            player.dx = 1
            player.MoveVert = True
        elif event.key == " " and not player.MoveVert:
            player.WaitForJump = True
            player.size.y = player.size.y * 0.5
            player.pos.y = player.pos.y - player.size.y * 0.5
        
def on_keyup(event):
    if event.key == " " and player.WaitForJump:
        player.pos.y = player.pos.y + player.size.y * 0.5
        player.size.y = player.size.y * 2
        player.WaitForJump = False
        player.IsJump = True
        player.OnLand = False
        player.v = vec(player.dx * 0.5 * player.JumpP,player.JumpP,0)
        player.color = color.red
        player.JumpP = 0
    elif event.key == "left" or event.key == "right":
        player.MoveVert = False
        

def DetectCollision():
    l = 0
    for i in CurObjects:
        # Box
        if i.type == 0:
            z = Collision_Box(i)
            if(z == 1):
                return True
            elif(z== 2):
                l = 1
        # Triangle
        else:
            if(Collision_Tri(i)):
                return True
    if l == 1:
        return True
    return False
    

# AABB
def Collision_Box(Object):
    global dt
    OverlapY = (player.size.y + Object.size.y)*0.5 - abs(Object.pos.y - player.pos.y - player.v.y * dt)
    xsub = Object.pos.x - player.pos.x - player.v.x * dt
    OverlapX = (player.size.x + Object.size.x)*0.5 - abs(xsub)
    
    if OverlapY < 0 or OverlapX < 0:
        return 0
    
    if OverlapY == 0 or OverlapX == 0:
        return 2
    
    if OverlapX < OverlapY:
        if player.IsJump:
            if player.v.x != 0:
                player.v.x = player.dx * player.v.x * 0.8
                player.dx = -player.dx
        elif player.dx * xsub >= 0:
            player.pos.x = Object.pos.x - (Object.size.x + player.size.x * 1.4) * 0.5 * player.dx
            
    else:
        if player.pos.y > Object.pos.y:
            player.pos.y = Object.pos.y + (Object.size.y+player.size.y) * 0.5
            player.IsJump = False
            player.OnLand = True
            player.color = color.white
            player.v.x = 0
        else:
            player.pos.y = Object.pos.y - (Object.size.y+player.size.y) * 0.5
        player.v.y = 0
    return 1

# OBB(SAT)
def Collision_Tri(tri):
    global dt
    # To X
    cntx = [tri.v0.pos.x,tri.v1.pos.x,tri.v2.pos.x]
    cntx.sort()
    RXmin = player.pos.x - player.size.x/2
    RXmax = player.pos.x + player.size.x/2
    
    if cntx[0] > RXmax or cntx[2] < RXmin:
        return False
    # To Y
    cnty = [tri.v0.pos.y,tri.v1.pos.y,tri.v2.pos.y]
    cnty.sort()
    RYmin = player.pos.y - player.size.y/2
    RYmax = player.pos.y + player.size.y/2
    if cnty[0] > RYmax or cnty[2] < RYmin:
        return False
    
    if tri.IsReverse:
        j2 = player.pos.y < tri.line[0].y
        if tri.l > 0:
            j = RXmin >= tri.line[0].x and RXmax <= tri.line[1].x
        else:
            j = RXmin >= tri.line[1].x and RXmax <= tri.line[0].x
    else:
        j2 = player.pos.y > tri.line[0].y
        j = True
        
    if j2 and j:
        k = abs(-player.pos.x * tri.l + player.pos.y - tri.c) / sqrt(player.pos.x ** 2 + player.pos.y ** 2)
        if k > 0.005:
            return False
        if player.v.y > 0:
            player.v.x = -player.v.x
            player.v.y = -1
            return True
        ang = diff_angle(tri.line[1] - tri.line[0],vec(1,0,0))
        grav = norm(tri.line[0] - tri.line[1]) * sin(ang) * 9.8
        player.rotate(angle = ang,axis = vec(0,0,1))
        if player.dx * tri.l > 0:
            player.dx = -1
            player.v = vec(0,0,0)
        else:
            player.dx = 1
            player.v = vec(player.v.x,player.v.x * grav.y / grav.x,0)
        while player.pos.y > tri.line[0].y:
            rate(1/dt)
            player.v = player.v + grav * dt
            player.pos = player.pos + player.v * dt
        player.rotate(angle = -ang,axis = vec(0,0,1))
    else:
        player.v.x = -player.v.x
        player.v.y = -1
    return True

def BoxInit(x,y,sx,sy,cl,fr,st):
    a = box(pos = vec(x,y+st*30,0), size = vec(sx,sy,0.001), color = cl)
    a.friction = fr
    a.type = 0
    return a

def TriInit(a,b,c,cl,st):
    av = vertex(pos = a + vec(0,st*30,0),color = cl)
    bv = vertex(pos = b + vec(0,st*30,0),color = cl)
    cv = vertex(pos = c + vec(0,st*30,0),color = cl)
    d = triangle(v0 = av, v1 = bv, v2 = cv)
    d.type = 1
    d.IsReverse = False
    if dot(norm(b-a),vec(1,0,0)) % 1 != 0:
        d.line = [av.pos,bv.pos]
        left = cv.pos
    elif dot(norm(c-a),vec(1,0,0)) %1 != 0:
        d.line = [av.pos,cv.pos]
        left = bv.pos
    else:
        d.line = [bv.pos,cv.pos]
        left = av.pos
    
    if d.line[0].y > d.line[1].y:
        s = d.line[0]
        d.line[0] = d.line[1]
        d.line[1] = s
        
    if d.line[0].y < left.y or d.line[1].y < left.y:
        d.Isreverse = True
        
    d.l = (d.line[1].y - d.line[0].y) / (d.line[1].x - d.line[0].x)
    d.c = d.line[0].y - d.l * d.line[0].x
    
    return d

def StageChange(ch):
    if player.CurStage == len(Stages)-1 and ch == 1:
        print("Clear")
        return
    player.CurStage = player.CurStage + ch
    scene.center = vec(0,player.CurStage * 30,0)
    scene.background = StageBG[player.CurStage]
    del CurObjects[2:]
    CurObjects.extend(Stages[player.CurStage])


def RGB(r,g,b):
    return vec(r/255,g/255,b/255)

scene.width = 1600
scene.height = 1200
scene.center = vec(0,0,0)
scene.range = 15

c0 = RGB(22,47,16)
c1 = RGB(30,26,23)
c2 = RGB(85,105,62)
c3 = RGB(66,66,64)
c4 = RGB(64,35,31)
c5 = RGB(41,66,67)
c6 = RGB(56,42,48)

CurObjects = [BoxInit(20.5,0,1,1000,color.black,0,0),BoxInit(-20.5,0,1,1000,color.white,0,0)]
StageBG = [RGB(71,102,66),RGB(71,102,66),RGB(110,149,166),RGB(110,149,166),RGB(110,149,166),RGB(56,53,53),RGB(56,53,53)]

Stage1 = [BoxInit(0,-14.5,40,2,c1,0,0),BoxInit(15,-7,10,14,c1,0,0),BoxInit(-15,-7,10,14,c1,0,0),BoxInit(0,10,10,4,c0,0,0)]
Stage2 = [BoxInit(9,-12,10,3,c0,0,1),BoxInit(18,-4,4,3,c0,0,1),BoxInit(4,-4,6,3,c0,0,1),BoxInit(-8,2,6,6,c0,0,1),BoxInit(-17,4,6,8,c0,0,1)]
Stage3 = [BoxInit(0,-12,4,1.5,c2,0,2),BoxInit(9,-12,5,1.5,c2,0,2),BoxInit(18.5,-8,3,1.5,c2,0,2),BoxInit(1,-6,10,3,c0,0,2),BoxInit(8,-5.5,4,4,c0,0,2)]
Stage3.extend([BoxInit(-5,3,5,4,c0,0,2),BoxInit(-17.5,7,5,1.5,c2,0,2),BoxInit(-7,14,6,2,c0,0,2)])
Stage4 = [BoxInit(-7,-13.5,6,3,c0,0,3),BoxInit(-7,-2,6,2,c3,0,3),BoxInit(-18,-2,4,2,c2,0,3), BoxInit(8.25,0,2.5,6,c3,0,3)]
Stage4.extend([BoxInit(10,3.5,1,13,c3,0,3),BoxInit(-8,6,1.5,6,c3,0,3),BoxInit(-9.25,9,1,12,c3,0,3)])
Stage5 = [BoxInit(-9.5,-13.5,3,3,c3,0,4),BoxInit(11,-13.5,2.5,3,c3,0,4),BoxInit(11,-7,2.5,1,c4,0,4),BoxInit(19,0,2,2,c4,0,4),BoxInit(6,8,2.75,1,c4,0,4)]
Stage5.extend([BoxInit(0,9.5,2.75,1,c4,0,4),BoxInit(-6,11,2.75,1,c4,0,4),BoxInit(0,14.5,16,1,c4,0,4),BoxInit(-15,7,2.75,1,c4,0,4)])
Stage6 = [BoxInit(0,-13,16,4,c4,0,5),BoxInit(12.5,1,15,12,c5,0,5),BoxInit(-8,-4.75,4,1.5,c5,0,5),BoxInit(-18,0,4,1.5,c5,0,5),BoxInit(-14.5,7,3,4,c5,0,5)]
Stage6.extend([BoxInit(-12,14.25,16,1.5,c5,0,5),BoxInit(-8.5,5.75,9,1.5,c5,0,5),BoxInit(10.5,13.5,11,3,c5,0,5)])
Stage7 = [BoxInit(8,-8.5,6,13,c5,0,6),BoxInit(13.5,-14.25,5,1.5,c5,0,6),BoxInit(13.5,-2.75,5,1.5,c5,0,6),BoxInit(16,10,8,10,c5,0,6),TriInit(vec(12,14,0),vec(12,5,0),vec(5,5,0),c5,6)]
Stage7.extend([BoxInit(-3,10,6,10,c5,0,6),BoxInit(-5.5,-6,5,1.5,c6,0,6),TriInit(vec(-4,-15,0),vec(-11,-15,0),vec(-11,-8,0),c5,6),TriInit(vec(-11,-6,0),vec(-18.5,-6,0),vec(-18.5,2,0),c5,6)])

Stage8 = []
g = vec(0,-15,0)


def process():
    global TE
    TE = False

scene.bind("keydown",on_keydown)
scene.bind("keyup",on_keyup)
scene.bind('click keydown', process)

Stages = [Stage1,Stage2,Stage3,Stage4,Stage5,Stage6,Stage7,Stage8]

player = box(pos = vec(0,-12.8,0), size = vec(1,1,0.01), color = color.white)
player.v = vec(0,0,0)
player.dx = 1
player.WaitForJump = False
player.IsJump = True
player.JumpP = 0
player.JumpPMax = 20
player.MoveVert = False
player.OnLand = True
player.CurStage = 0

dt = 0.01
t = 0
DJ = DetectCollision()
StageChange(6)

def Normal():
    global DJ
    if player.MoveVert or player.IsJump:
        DJ = DetectCollision()
        
    if player.WaitForJump and player.JumpP <= player.JumpPMax:
        player.JumpP = player.JumpP + 0.005 / dt
        
    if player.IsJump and not player.OnLand:
        player.v = player.v + g * dt
        player.pos = player.pos + player.v * dt
        if player.pos.y > 15 + 30 * player.CurStage:
            StageChange(1)
        elif player.pos.y < -15 + 30 * player.CurStage:
            StageChange(-1)
    
    if player.MoveVert:
        player.pos.x = player.pos.x + dt * player.dx * 10

    if not DJ and player.OnLand:
        player.OnLand = False
        player.IsJump = True
        player.color = color.red
        player.MoveVert = False

def test():
    player.pos = scene.mouse.pos

TE = True
    

while True:
    rate(100)
    if TE:
        test()
    else:
        Normal()

