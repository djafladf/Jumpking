# Web vpython 3.2
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
    if tri.l == 1:
        j = (RXmin - tri.line[0].x) * (RXmin - tri.line[1].x)
    else:
        j = (RXmax - tri.line[0].x) * (RXmax - tri.line[1].x)
    if player.pos.y > tri.line[0].y and j < 0:
        k = abs(player.pos.x * tri.l + player.pos.y - tri.c) / sqrt(player.pos.x ** 2 + player.pos.y ** 2)
        if k > 0.25 - 0.05 * tri.l:
            return False
        ang = diff_angle(tri.line[1] - tri.line[0],vec(1,0,0))
        grav = norm(tri.line[0] - tri.line[1]) * sin(ang) * 9.8
        player.rotate(angle = ang,axis = vec(0,0,1))
        player.v = vec(0,0,0)
        while player.pos.y > tri.line[0].y:
            rate(1/dt)
            player.v = player.v + grav * dt
            player.pos = player.pos + player.v * dt
        player.rotate(angle = -ang,axis = vec(0,0,1))
    else:
        player.pos.y = player.pos.y - 0.1
        player.v.x = -player.v.x
        player.v.y = 0
    return True

def BoxInit(x,y,sx,sy,cl,fr,st):
    a = box(pos = vec(x,y+st*30,0), size = vec(sx,sy,0.1), color = cl)
    a.friction = fr
    a.type = 0
    return a

def TriInit(a,b,c,cl,st):
    av = vertex(pos = a + vec(0,st*30,0),color = cl)
    bv = vertex(pos = b + vec(0,st*30,0),color = cl)
    cv = vertex(pos = c + vec(0,st*30,0),color = cl)
    d = triangle(v0 = av, v1 = bv, v2 = cv)
    d.type = 1
    if dot(norm(b-a),vec(1,0,0)) % 1 != 0:
        d.line = [a,b]
    elif dot(norm(c-a),vec(1,0,0)) %1 != 0:
        d.line = [a,c]
    else:
        d.line = [b,c]
    
    if d.line[0].y > d.line[1].y:
        s = d.line[0]
        d.line[0] = d.line[1]
        d.line[1] = s
    if d.line[0].x > d.line[1].x:
        d.c = d.line[0].x + d.line[0].y
        d.l = 1
    else:
        d.c = d.line[0].y - d.line[0].x
        d.l = -1
    return d

def StageChange(ch):
    player.CurStage = player.CurStage + ch
    scene.center = vec(0,player.CurStage * 30,0)
    scene.background = StageBG[player.CurStage]
    del CurObjects[2:]
    CurObjects.extend(Stages[player.CurStage])


def RGB(r,g,b):
    return vec(r/255,g/255,b/255)

scene.width = 800
scene.height = 600
scene.center = vec(0,0,0)
scene.range = 15

c0 = RGB(22,47,16)
c1 = RGB(30,26,23)
c2 = RGB(85,105,62)
c3 = RGB(66,66,64)
c4 = RGB(64,35,31)

CurObjects = [BoxInit(20.5,0,1,1000,color.black,0,0),BoxInit(-20.5,0,1,1000,color.white,0,0)]
StageBG = [RGB(71,102,66),RGB(71,102,66),RGB(110,149,166),RGB(110,149,166),RGB(110,149,166)]

Stage1 = [BoxInit(0,-14.5,40,2,c1,0,0),BoxInit(15,-7,10,14,c1,0,0),BoxInit(-15,-7,10,14,c1,0,0),BoxInit(0,10,10,4,c0,0,0)]
Stage2 = [BoxInit(9,-12,10,3,c0,0,1),BoxInit(18,-4,4,3,c0,0,1),BoxInit(4,-4,6,3,c0,0,1),BoxInit(-8,2,6,6,c0,0,1),BoxInit(-17,4,6,8,c0,0,1)]
Stage3 = [BoxInit(0,-12,4,1.5,c2,0,2),BoxInit(9,-12,5,1.5,c2,0,2),BoxInit(18.5,-8,3,1.5,c2,0,2),BoxInit(1,-6,10,3,c0,0,2),BoxInit(8,-5.5,4,4,c0,0,2)]
Stage3.extend([BoxInit(-5,3,5,4,c0,0,2),BoxInit(-17.5,7,5,1.5,c2,0,2),BoxInit(-7,14,6,2,c0,0,2)])
Stage4 = [BoxInit(-7,-13.5,6,3,c0,0,3),BoxInit(-7,-2,6,2,c3,0,3),BoxInit(-18,-2,4,2,c2,0,3), BoxInit(4.25,0,2.5,6,c3,0,3)]
Stage4.extend([BoxInit(6,3.5,1,13,c3,0,3),BoxInit(-8,6,1.5,6,c3,0,3),BoxInit(-9.25,9,1,12,c3,0,3)])
Stage5 = [BoxInit(-9.5,-13.5,3,3,c3,0,4),BoxInit(7,-13.5,2.5,3,c3,0,4),BoxInit(7,-8,2.5,1,c4,0,4),BoxInit(19.5,0,1,1.5,c4,0,4)]
g = vec(0,-15,0)

scene.bind("keydown",on_keydown)
scene.bind("keyup",on_keyup)

Stages = [Stage1,Stage2,Stage3,Stage4,Stage5]

player = box(pos = vec(0,-12.8,0), size = vec(1,1,0.01), color = color.white)
player.v = vec(0,0,0)
player.dx = 1
player.WaitForJump = False
player.IsJump = False
player.JumpP = 0
player.JumpPMax = 20
player.MoveVert = False
player.OnLand = True
player.CurStage = 0

dt = 0.01
t = 0
DJ = DetectCollision()
StageChange(4)

while True:
    rate(100)

    # player.pos = scene.mouse.pos

    # if player.pos.y > 15 + 30 * player.CurStage:
    #     StageChange(1)
    # elif player.pos.y < -15 + 30 * player.CurStage:
    #     StageChange(-1)
    
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

