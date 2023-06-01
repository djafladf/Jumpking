from vpython import *

# 플레이어의 이동 제어 및 점프 제어
# Space 키를 누름으로써 점프를 차징할 수 있다.
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

# Space 키를 때면 차징한 점프력만큼 점프한다.
def on_keyup(event):
    if event.key == " " and player.WaitForJump:
        player.pos.y = player.pos.y + player.size.y * 0.5
        player.size.y = player.size.y * 2
        player.WaitForJump = False
        player.IsJump = True
        player.OnLand = False
        player.v = vec(player.dx * 0.3 * player.JumpP,player.JumpP,0)
        player.JumpP = 0
    elif event.key == "left" or event.key == "right":
        player.MoveVert = False
        
# 충돌 검사
def DetectCollision():
    for i in CurObjects:
        # Box인 경우
        if i.type == 0:
            if(Collision_Box(i)):
                return True
        # Triangle인 경우
        else:
            if(Collision_Tri(i)):
                return True
    return False
    

# AABB(사각형과 사각형과의 충돌)
# 옆부분에 부딪힌 경우 플레이어가 튕겨져나감
# 윗부분에 부딪힌 경우 해당 Object에 착지함
# 아랫부분에 부딪힌 경우 플레이어가 튕겨져나감
# True 반환시 충돌이며, False반환시 충돌하지 않았음을 반환
# 추후 연산의 편의성을 위해 Collision 연산 후 Object와 Player가 겹치는 부분은 0이다.
def Collision_Box(Object):
    global dt
    # AABB 검사
    OverlapY = (player.size.y + Object.size.y)*0.5 - abs(Object.pos.y - player.pos.y - player.v.y * dt)
    xsub = Object.pos.x - player.pos.x - player.v.x * dt
    OverlapX = (player.size.x + Object.size.x)*0.5 - abs(xsub)
    
    if OverlapY < 0 or OverlapX < 0:
        return False
    
    # Object와 붙어있는 채로 수평으로 이동할때는 연산 무시
    if OverlapY == 0 or OverlapX == 0:
        return True
    
    if OverlapX <= OverlapY:
        # 점프 중 옆부분 충돌
        if player.IsJump:
            if player.v.x != 0:
                player.v.x = player.dx * (-4)
                player.dx = -player.dx
        # 걷는 중 옆부분 충돌
        elif player.dx * xsub >= 0:
            player.pos.x = Object.pos.x - (Object.size.x + player.size.x) * 0.5 * player.dx
            
    else:
        # 윗부분 충돌
        if player.v.y <0:
            player.pos.y = Object.pos.y + (Object.size.y+player.size.y) * 0.5
            player.IsJump = False
            player.OnLand = True
            player.v.x = 0
        # 아랫부분 충돌
        else:
            player.pos.y = Object.pos.y - (Object.size.y+player.size.y) * 0.5
        player.v.y = 0
    return True

# OBB(사각형과 삼각형사이의 충돌)
# 두 다면체를 어떤 축에 투영시켰을 때(이 연산에선 x축 y축), 이 구간이 겹치지 않을 경우 서로 충돌하지 않음
# 빗변에 부딪힌 경우 미끄러짐
# 빗변이 아닌 경우 튕겨져 나감
# 삼각형은 무조건 직각 삼각형이며, x축, y축에 평행한 변이 무조건 있음을 가정
# 충돌 시 True 반환, 충돌하지 않을 시 False 반환
def Collision_Tri(tri):
    global dt
    # SAT
    # x축으로 투영
    cntx = [tri.v0.pos.x,tri.v1.pos.x,tri.v2.pos.x]
    cntx.sort()
    RXmin = player.pos.x - player.size.x/2
    RXmax = player.pos.x + player.size.x/2
    
    if cntx[0] > RXmax or cntx[2] < RXmin:
        return False
    # y축으로 투영
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
    
    print(j)
    # 빗변 충돌 시
    if player.pos.y > tri.line[0].y and j < 0:
        print("!")
        # 이 코드에서 구현된 OBB는 빗변의 충돌 검사 시 모호한 부분이 있어 이를 보충
        # 빗변과의 특정 거리 이상일 경우 충돌로 처리하지 않음
        k = abs(player.pos.x * tri.l + player.pos.y - tri.c) / sqrt(player.pos.x ** 2 + player.pos.y ** 2)
        if k > 0.25 - 0.05 * tri.l:
            return False
        
        # 미끄러지는 듯한 느낌을 주기 위해 회전
        ang = diff_angle(tri.line[1] - tri.line[0],vec(1,0,0))
        grav = norm(tri.line[0] - tri.line[1]) * sin(ang) * 9.8
        player.rotate(angle = ang,axis = vec(0,0,1))
        player.v = vec(0,0,0)
        # 미끄러지는 듯한 느낌을 주기 위한 빗변 이동
        while player.pos.y > tri.line[0].y:
            rate(1/dt)
            player.v = player.v + grav * dt
            player.pos = player.pos + player.v * dt
        player.rotate(angle = -ang,axis = vec(0,0,1))
    # 빗변 외의 부분과 충돌
    else:
        player.pos.y = player.pos.y - 0.1
        player.v.x = -player.v.x
        player.v.y = 0
    return True

# Box Object 초기화
def BoxInit(x,y,sx,sy,cl,st):
    a = box(pos = vec(x,y+st*30,0), size = vec(sx,sy,0.01), color = cl)
    a.type = 0
    return a

# Triangle Object 초기화
def TriInit(a,b,c,cl,st):
    av = vertex(pos = a + vec(0,st*30,0),color = cl)
    bv = vertex(pos = b + vec(0,st*30,0),color = cl)
    cv = vertex(pos = c + vec(0,st*30,0),color = cl)
    d = triangle(v0 = av, v1 = bv, v2 = cv)
    d.type = 1

    # 어떤 부분이 빗변인지 검사
    if dot(norm(b-a),vec(1,0,0)) % 1 != 0:
        d.line = [a,b]
    elif dot(norm(c-a),vec(1,0,0)) %1 != 0:
        d.line = [a,c]
    else:
        d.line = [b,c]
    
    # 추후 거리 계산을 위한 빗변의 방정식 보충 용
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

# 카메라의 위치를 바꿔 마치 스테이지가 넘어가는 듯한 연출
def StageChange(ch):
    player.CurStage = player.CurStage + ch
    scene.center = vec(0,player.CurStage * 30,0)
    del CurObjects[2:]
    CurObjects.extend(Stages[player.CurStage])

# Scene
scene.width = 400
scene.height = 400
scene.center = vec(0,0,0)
scene.range = 15
scene.bind("keydown",on_keydown)
scene.bind("keyup",on_keyup)

# Colors
cg = color.green
cG = vec(0.7,0.7,0.7)

# 현재 Stage의 Object(기본적으로 좌,우의 벽이 존재)
CurObjects = [BoxInit(15.5,0,1,1000,color.black,0),BoxInit(-15.5,0,1,1000,color.black,0)]

# Stage별 Object
# Stage1 = [BoxInit(0,-14.5,30,2,cG,0),BoxInit(11,-10,8,10,cG,0),BoxInit(-11,-10,8,10,cG,0),BoxInit(0,2,8,4,cg,0),BoxInit(8,12,6,3,cg,0)]
Stage1 = [BoxInit(0,-14.5,30,2,cG,0), TriInit(vec(-2,-8,0),vec(4,-8,0),vec(4,-2,0),cg,0)]
Stage2 = [BoxInit(13,-11,4,2,cg,1),BoxInit(4,-11,5,2,cg,1)]
Stages = [Stage1,Stage2]

# Gravity Scale
g = vec(0,-20,0)

# Player
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
StageChange(0)

while True:
    rate(1/dt)    
    
    # 수평 이동 시 낙하를 계산하기 위해 충돌 검사를 따로 뺴놓음
    if player.MoveVert or player.IsJump:
        DJ = DetectCollision()
    
    # 점프 차징
    if player.WaitForJump and player.JumpP <= player.JumpPMax:
        player.JumpP = player.JumpP + 0.005 / dt
    
    # 점프
    if player.IsJump and not player.OnLand:
        player.v = player.v + g * dt
        player.pos = player.pos + player.v * dt
        if player.pos.y > 15 + 30 * player.CurStage:
            StageChange(1)
        elif player.pos.y < -15 + 30 * player.CurStage:
            StageChange(-1)
    
    # 수평 이동
    if player.MoveVert:
        player.pos.x = player.pos.x + dt * player.dx * 10
    
    # 수평 이동 도중 낙하
    if not DJ and player.OnLand:
        player.OnLand = False
        player.IsJump = True
        player.MoveVert = False
    
    
        
    
        