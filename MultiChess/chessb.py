import pygame # pygame 라이브러리 사용
import glob
import copy
import time
import os
import sys
import socket # 소켓 라이브러리 사용

if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)

'''

20-09-28
v1.0 - 게임 완성
v1.1 - 스테일메이트, 시간 제한 버그 수정

'''

s_ip = input("\n서버의 아이피를 입력해 주세요.\n") # 서버 아이피 설정
s_port = 12345 # 서버 포트 설정

print("서버에 연결중입니다.")
c_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # socket.AF_INET : IPv4 주소 사용, socket.SOCK_STREAM : 전송계층 프로토콜 TCP 사용
c_sock.connect((s_ip, s_port)) # 해당 주소의 서버에 연결한다.


pygame.init() # pygame 초기화

size = (1100, 700) # 크기 설정
board = pygame.display.set_mode(size) # 크기를 기반으로 게임판 설정
pygame.display.set_caption("Chess Game") # 게임 이름 설정

backg = pygame.image.load("image\\back.jpg") # 이미지 업로드

piecesi = glob.glob("image\\pieces\\*.png")

sel = [] # 클릭한 칸을 담는 배열
history = []
prom = 0
angpa = -1
stak = 0
castl = [[True, True], [True, True]]
moveche = []
font = pygame.font.Font("image\\acharismaBk.ttf", 30) # 폰트 설정
font2 = pygame.font.Font("image\\acharismaBk.ttf", 25) # 폰트 설정
font3 = pygame.font.Font("image\\acharismaBk.ttf", 50) # 폰트 설정
btime = 0
wtime = 0
stime = 0
timer = 0
sec = 0
fir = True

promarr = ["", "", "룩", "나이트", "비숍", "퀸"] # 프로모션 출력 배열
seq = "백" # 순서
chemes = " " # 체크상태 출력

# 기물은 흑색 폰이 1, 룩이 2, 나이트가 3, 비숍이 4, 퀸이 5, 킹이 6
# 백색은 음수로 표기

# 판 초기화 함수
def clearboard():
    global timer, btime, wtime, stime

    timer = 0
    btime = 0
    wtime = 0
    stime = 0

    board = []
    board.append([2, 3, 4, 5, 6, 4, 3, 2])
    board.append([1, 1, 1, 1, 1, 1, 1, 1])
    board.append([0, 0, 0, 0, 0, 0, 0, 0])
    board.append([0, 0, 0, 0, 0, 0, 0, 0])
    board.append([0, 0, 0, 0, 0, 0, 0, 0])
    board.append([0, 0, 0, 0, 0, 0, 0, 0])
    board.append([-1, -1, -1, -1, -1, -1, -1, -1])
    board.append([-2, -3, -4, -5, -6, -4, -3, -2])
    return board


# 남은 기물을 확인하는 함수
def checkpie(sta):
    whi = [0, 0, 0, 0, 0, 0] # 폰/룩/나이트/비숍/퀸/킹
    bla = [0, 0, 0, 0, 0, 0] # 폰/룩/나이트/비숍/퀸/킹

    for y in sta:
        for x in y:
            if x>0:
                bla[x-1] += 1
            elif x<0:
                whi[(x*-1)-1] += 1
    return whi, bla


# 몇 번째 칸을 클릭했는지 감지하는 함수
def selboard(x, y, selarr, boardstat):
    xy = (int(event.pos[0]//87.5), int(event.pos[1]//87.5))
    if len(selarr) == 1:
        if sel[0] == xy:
            del(selarr[0])
        else:
            selarr.append(xy)
    elif boardstat[xy[1]][xy[0]] != 0 : 
        selarr.append(xy)
    return selarr


# 현재 판 상황을 출력하는 함수
def prtboard(board, sta):
    for i in range(0, len(sta)):
        for j in range(0, len(sta[i])):
            img = sta[i][j]
            if img != 0:
                if img>0: img -= 1
                board.blit(pygame.image.load(piecesi[img+6]), (j*87.5, i*87.5))


# 기물의 자리를 변경하는 함수
def change(sel, sta, seq):
    global moveche, stak
    
    if ((seq == "백" and sta[sel[0][1]][sel[0][0]]<0) or (seq == "흑" and sta[sel[0][1]][sel[0][0]]>0)) and ruleche(sta[sel[0][1]][sel[0][0]], sel, sta, seq):
        moveche = [sta[sel[0][1]][sel[0][0]], (sel[0][0], sel[0][1]), (sel[1][0], sel[1][1])]
        pre = sel[0]
        sus = sel[1]
        if sta[sus[1]][sus[0]] != 0 or sta[pre[1]][pre[0]] == 1 or sta[pre[1]][pre[0]] == -1:
            stak = 0
        sta[sus[1]][sus[0]] = int(sta[pre[1]][pre[0]])
        sta[pre[1]][pre[0]] = 0
        return sta
    else:
        return sta


# 판 상황을 기록하는 함수
def saveboard(sta):
    global history
    
    history.append([])
    for i in sta:
        history[len(history)-1].append(copy.deepcopy(i))


# 순서를 바꾸는 함수
def changeseq(seq):
    if seq == "흑":
        seq = "백"
    else:
        seq = "흑"
    return seq


# 기물의 이동 조건을 확인하는 함수
def ruleche(piece, sel, sta, seq):
    x1 = sel[0][0]
    x2 = sel[1][0]
    y1 = sel[0][1]
    y2 = sel[1][1]
    if abs(piece) == 1: # 폰
        return pawn(x1, x2, y1, y2, seq, sta) or angp(x1, x2, y1, y2, seq, sta)
    elif abs(piece) == 2: # 룩
        return rook(x1, x2, y1, y2, seq, sta)
    elif abs(piece) == 3: # 나이트
        return knight(x1, x2, y1, y2, seq, sta)
    elif abs(piece) == 4: # 비숍
        return bishop(x1, x2, y1, y2, seq, sta)
    elif abs(piece) == 5: # 퀸
        return queen(x1, x2, y1, y2, seq, sta)
    elif abs(piece) == 6: # 킹
        return king(x1, x2, y1, y2, seq, sta)


# 폰의 이동 조건
def pawn(x1, x2, y1, y2, seq, sta):
    if seq == "백":
        if (x1 == x2 and ((y1-1 == y2 and sta[y2][x2] == 0) or (y1 == 6 and y2 == 4 and sta[5][x2] == 0 and sta[4][x2] == 0))) or (abs(x1-x2) == 1 and y1-1 == y2 and sta[y2][x2]>0):
            return True
        else:
            return False
    else:
        if (x1 == x2 and ((y1+1 == y2 and sta[y2][x2] == 0) or (y1 == 1 and y2 == 3 and sta[2][x2] == 0 and sta[3][x2] == 0))) or (abs(x1-x2) == 1 and y1+1 == y2 and sta[y2][x2]<0):
            return True
        else:
            return False
  

# 앙파상 함수
def angp(x1, x2, y1, y2, seq, sta):
    global angpa

    if seq == "백":
        if abs(x1-x2) == 1 and y2 == 2 and y1 == 3 and sta[y1][x2] == 1 and angpa == x2:
            sta[y1][x2] = 0
            return True
        else: 
            return False
    else:
        if abs(x1-x2) == 1 and y2 == 5 and y1 == 4 and sta[y1][x2] == -1 and angpa == x2:
            sta[y1][x2] = 0
            return True
        else: 
            return False


# 룩의 이동 조건
def rook(x1, x2, y1, y2, seq, sta):
    if (x1 == x2 and y1 != y2) or (x1 != x2 and y1 == y2):
        if (x1 == x2 and y1 != y2):
            if y1-y2>0:
                for i in range(y1-1, y2, -1):
                    if sta[i][x2] != 0: 
                        return False
                if (seq == "백" and sta[y2][x2]<0) or (seq == "흑" and sta[y2][x2]>0):
                    return False
            else:
                for i in range(y1+1, y2, 1):
                    if sta[i][x2] != 0: 
                        return False
                if (seq == "백" and sta[y2][x2]<0) or (seq == "흑" and sta[y2][x2]>0):
                    return False
        else:
            if x1-x2>0:
                for i in range(x1-1, x2, -1):
                    if sta[y2][i] != 0: 
                        return False
                if (seq == "백" and sta[y2][x2]<0) or (seq == "흑" and sta[y2][x2]>0):
                    return False
            else:
                for i in range(x1+1, x2, 1):
                    if sta[y2][i] != 0: 
                        return False
                if (seq == "백" and sta[y2][x2]<0) or (seq == "흑" and sta[y2][x2]>0):
                    return False
        return True
    else:
        return False

 
# 나이트의 이동 조건
def knight(x1, x2, y1, y2, seq, sta):
    if abs(x1-x2)+abs(y1-y2) == 3 and abs(x1-x2) != 0 and abs(y1-y2) != 0:
        if (seq == "백" and sta[y2][x2]<0) or (seq == "흑" and sta[y2][x2]>0):
            return False
        return True
    else:
        return False
    

# 비숍의 이동 조건
def bishop(x1, x2, y1, y2, seq, sta):
    if abs(x1-x2) == abs(y1-y2):
        if x1-x2>0 and y1-y2>0:
            for i in range(1, x1-x2):
                if sta[y1-i][x1-i] != 0: 
                    return False
            if (seq == "백" and sta[y2][x2]<0) or (seq == "흑" and sta[y2][x2]>0):
                return False
        elif x1-x2>0 and y1-y2<0:
            for i in range(1, x1-x2):
                if sta[y1+i][x1-i] != 0: 
                    return False
            if (seq == "백" and sta[y2][x2]<0) or (seq == "흑" and sta[y2][x2]>0):
                return False
        elif x1-x2<0 and y1-y2>0:
            for i in range(1, x2-x1):
                if sta[y1-i][x1+i] != 0: 
                    return False
            if (seq == "백" and sta[y2][x2]<0) or (seq == "흑" and sta[y2][x2]>0):
                return False
        elif x1-x2<0 and y1-y2<0:
            for i in range(1, x2-x1):
                if sta[y1+i][x1+i] != 0: 
                    return False
            if (seq == "백" and sta[y2][x2]<0) or (seq == "흑" and sta[y2][x2]>0):
                return False
        return True
    else:
        return False


# 퀸의 이동 조건
def queen(x1, x2, y1, y2, seq, sta):
    if rook(x1, x2, y1, y2, seq, sta) or bishop(x1, x2, y1, y2, seq, sta):
        return True
    else:
        return False


# 킹의 이동 조건
def king(x1, x2, y1, y2, seq, sta):
    global chemes

    if abs(x1-x2)<=1 and abs(y1-y2)<=1 and ((seq == "백" and sta[y2][x2]>=0) or (seq == "흑" and sta[y2][x2]<=0)):
        return True
    elif y1 == y2 and abs(x1-x2) == 2 and chemes == " ":
        return castle(x1, x2, seq, sta)
    else:
        return False


# 캐슬링 함수
def castle(x1, x2, seq, sta):
    if seq == "백" and x1 < x2 and sta[7][5] == sta[7][6] == 0 and castl[0][1]:
        sta[7][5] = -2
        sta[7][7] = 0
        return True
    elif seq == "백" and x1 > x2 and sta[7][1] == sta[7][2] == sta[7][3] == 0 and castl[0][0]:
        sta[7][0] = 0
        sta[7][3] = -2
        return True
    elif seq == "흑" and x1 < x2 and sta[0][5] == sta[0][6] == 0 and castl[1][1]:
        sta[0][5] = 2
        sta[0][7] = 0
        return True
    elif seq == "흑" and x1 > x2 and sta[0][1] == sta[0][2] == sta[0][3] == 0 and castl[1][0]:
        sta[0][0] = 0
        sta[0][3] = 2
        return True
    else:
        return False


# 킹의 현재 위치 탐색 함수
def kingpos(seq, sta):
    if seq == "백":
        for i in range(0, len(sta)):
            for j in range(0, len(sta[i])):
                if sta[i][j] == -6:
                    return (j, i)
    else:
        for i in range(0, len(sta)):
            for j in range(0, len(sta[i])):
                if sta[i][j] == 6:
                    return (j, i)
    return (-1, -1)


# 체크 확인 함수
def checkche(seq, sta, kp):
    able = knightche(seq, sta, kp) + eightche(seq, sta, kp)
    if len(able)>0:
        return True
    else:
        return False
        

# 메이트 감지 함수(체크메이트/스테일메이트) [모든 경우 감지 - 비효율적]
def mateche(seq, sta):
    global moveche

    templist = moveche[:]

    if seq == "백":
        for y1 in range(0, 8):
            for x1 in range(0, 8):
                if sta[y1][x1]<0:
                    for y2 in range(0, 8):
                        for x2 in range(0, 8):
                            tempsel = [(x1, y1), (x2, y2)]
                            sta = change(tempsel, sta, seq)
                            if sta == history[len(history)-1]:
                                continue
                            if not checkche(seq, sta, kingpos(seq, sta)):
                                sta = copy.deepcopy(history[len(history)-1])
                                moveche = templist[:]
                                return False, sta
                            sta = copy.deepcopy(history[len(history)-1])

    elif seq == "흑":
        for y1 in range(0, 8):
            for x1 in range(0, 8):
                if sta[y1][x1]>0:
                    for y2 in range(0, 8):
                        for x2 in range(0, 8):
                            tempsel = [(x1, y1), (x2, y2)]
                            sta = change(tempsel, sta, seq)
                            if sta == history[len(history)-1]:
                                continue
                            if not checkche(seq, sta, kingpos(seq, sta)):
                                sta = copy.deepcopy(history[len(history)-1])
                                moveche = templist[:]
                                return False, sta
                            sta = copy.deepcopy(history[len(history)-1])

    moveche = templist[:]
    return True, sta


# 나이트 체크 확인 함수
def knightche(seq, sta, kp):
    able = []
    if seq == "백": kn = 3
    else: kn = -3
    kmovex = [2, 2, -2, -2, 1, 1, -1, -1]
    kmovey = [1, -1, 1, -1, 2, -2, 2, -2]
    for i in range(0, 8):
        x = kp[0]+kmovex[i]
        y = kp[1]+kmovey[i]
        if x>7 or x<0 or y>7 or y<0: 
            continue
        if sta[y][x] == kn: 
            able.append((x, y))
    return able


# 8방향 체크 확인 함수 (8방향, 왼쪽위부터 시계방향)
def eightche(seq, sta, kp):
    able = []
    if seq == "백": seqt = 1
    else: seqt = -1
    movex = [-1, 0, 1, 1, 1, 0, -1, -1]
    movey = [-1, -1, -1, 0, 1, 1, 1, 0]
    for i in range(0, 8):
        pixel = 1
        while 0<=kp[0]+(movex[i]*pixel)<=7 and 0<=kp[1]+(movey[i]*pixel)<=7:
            x = kp[0]+(movex[i]*pixel)
            y = kp[1]+(movey[i]*pixel)
            if sta[y][x] != 0:
                pic = sta[y][x]
                if pixel == 1 and pic*seqt == 6: # 킹
                    able.append((x, y))
                elif pixel == 1 and seqt == 1 and i in [0, 2] and pic == 1: # 폰
                    able.append((x, y))
                elif pixel == 1 and seqt == -1 and i in [4, 6] and pic == -1: # 폰
                    able.append((x, y))
                elif i in [0, 2, 4, 6] and pic*seqt in [4, 5]: # 대각선 (비숍, 퀸)
                    able.append((x, y))
                elif i in [1, 3, 5, 7] and pic*seqt in [2, 5]: # 직선 (룩, 퀸)
                    able.append((x, y))
                break
            pixel += 1
    return able


# 무승부 판정 함수
def draw(whi, bla, sta):
    global stak

    total = 0
    for i in whi:
        total += i
    for i in bla:
        total += i
    if total == 2:
        return "무승부 (킹만 존재)"

    elif total == 3 and (whi[2] == 1 or whi[3] == 1 or bla[2] == 1 or bla[3] == 1):
        return "무승부 (기물 부족)"

    elif total == 4 and whi[3] == bla[3] == 1:
        wb = findpie(-4, sta)
        bb = findpie(4, sta)
        if ((wb[0]%2)+(wb[1]%2))%2 == ((bb[0]%2)+(bb[1]%2))%2:
            return "무승부 (같은 색의 비숍)"

    elif stak >= 50:
        return "무승부 (50수 규칙)"

    elif len(history)>=9:
        if history[len(history)-1] == history[len(history)-5] == history[len(history)-9]:
            return "무승부 (3회 동형반복)"

    if stak >= 30:
        return "50수 규칙 위험("+str(stak)+"/50)"

    if len(history)>=5:
        if history[len(history)-1] == history[len(history)-5]:
            return "3회 동형반복 위험"

    return " "
        

# 특정 기물의 위치를 찾는 함수
def findpie(pie, sta):
    for y in range(0, len(sta)):
        for x in range(0, len(sta[y])):
            if sta[y][x] == pie:
                return (x, y)
    return (-1, -1)


def listencode(sta):
    prt = ""
    for i in sta:
        for j in i:
            prt += str(j)
            prt += "*"
        prt = prt[:-1]
        prt += "+"
    prt = prt[:-1]
    return prt


def decry(prt):
    templist = prt.split("/")
    templist[0] = templist[0].split("+")
    for i in range(0, len(templist[0])):
        templist[0][i] = templist[0][i].split("*")
    for i in range(0, len(templist[0])):
        for j in range(0, len(templist[0][i])):
            templist[0][i][j] = int(templist[0][i][j])
    return templist


boardstat = clearboard()
# boardstat = [[0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 6, 5, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, -6, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0]]

done = True # 무한 반복을 위한 done 변수를 True로 설정

while done : # done이 True일 경우 (무한 반복)
    for event in pygame.event.get() : # 이벤트 인식
        if event.type == pygame.QUIT : # 종료 버튼을 누른 경우
            done = False # done을 False로 설정
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if 0<=event.pos[0]<=700 and 0<=event.pos[1]<=700 and len(sel)<2: # 기물 이동
                sel = selboard(event.pos[0], event.pos[1], sel, boardstat)
                if len(sel) == 2:
                    saveboard(boardstat)
                    boardstat = change(sel, boardstat, seq)
                    if checkche(seq, boardstat, kingpos(seq, boardstat)): # 움직였을 때 체크인 경우 움직임 취소
                        boardstat = history[len(history)-1][:]
                        del(history[len(history)-1])
                        moveche = []
                    elif boardstat == history[len(history)-1]: # 제자리를 클릭한 경우 취소
                        del(history[len(history)-1])
                        moveche = []
                    else:
                        stak += 1
                        angpa = -1
                        if timer>0: # 차례 변경에 의한 시간 초기화
                            stime = 30
                        else:
                            stime = 0
                        if len(moveche) > 0: # 앙파상/캐슬링 가능여부 판단
                            if moveche[0] == -1:
                                if moveche[1][1] == 6 and moveche[2][1] == 4:
                                    angpa = moveche[1][0]
                            elif moveche[0] == 1:
                                if moveche[1][1] == 1 and moveche[2][1] == 3:
                                    angpa = moveche[1][0]
                            elif moveche[0] == -2 and moveche[1][1] == 7:
                                if moveche[1][0] == 0:
                                    castl[0][0] = False
                                elif moveche[1][0] == 7:
                                    castl[0][1] = False
                            elif moveche[0] == 2 and moveche[1][1] == 0:
                                if moveche[1][0] == 0:
                                    castl[1][0] = False
                                elif moveche[1][0] == 7:
                                    castl[1][1] = False
                            elif moveche[0] == -6:
                                castl[0][0] = False
                                castl[0][1] = False
                            elif moveche[0] == 6:
                                castl[1][0] = False
                                castl[1][1] = False

                        seq = changeseq(seq)

                        if checkche(seq, boardstat, kingpos(seq, boardstat)): # 체크/체크메이트 확인
                            saveboard(boardstat)
                            tf, boardstat = mateche(seq, boardstat)
                            del(history[len(history)-1])
                            if tf:
                                chemes = changeseq(seq)+"의 승리(체크메이트)"
                            else:
                                chemes = changeseq(seq)+"의 체크"
                        else: # 스테일메이트/무승부 확인
                            saveboard(boardstat)
                            tf, boardstat = mateche(seq, boardstat)
                            del(history[len(history)-1])
                            if tf:
                                chemes = "무승부(스테일메이트)"
                            else:
                                wpie, bpie = checkpie(boardstat)
                                chemes = draw(wpie, bpie, boardstat)
                    sel = []

            elif 725<=event.pos[0]<=875 and 475<=event.pos[1]<=550: # 판 초기화 버튼
                saveboard(boardstat)
                boardstat = clearboard()
                seq = "백"

            elif 925<=event.pos[0]<=1075 and 575<=event.pos[1]<=650: # 타임 어택 버튼
                timer += 1
                if timer == 4:
                    timer = 0
                if timer >= 1:
                    wtime = 300*timer
                    btime = 300*timer
                    stime = 30
                    sec = time.time()
                elif timer == 0:
                    wtime = 0
                    btime = 0
                    stime = 0

            elif 725<=event.pos[0]<=875 and 575<=event.pos[1]<=650 and len(history)>0: # 이전 버튼
                boardstat = copy.deepcopy(history[len(history)-1])
                seq = changeseq(seq)
                del(history[len(history)-1])
                chemes = " "
                stime = 30

            elif 925<=event.pos[0]<=1075 and 475<=event.pos[1]<=550 and len(sel)==1: # 프로모션(진급) 버튼
                if 2<=prom<=5 and ((boardstat[sel[0][1]][sel[0][0]] == 1 and sel[0][1] == 7) or (boardstat[sel[0][1]][sel[0][0]] == -1 and sel[0][1] == 0)):
                    boardstat[sel[0][1]][sel[0][0]] *= int(prom)
                    if checkche(seq, boardstat, kingpos(seq, boardstat)): # 체크/체크메이트 확인
                        saveboard(boardstat)
                        tf, boardstat = mateche(seq, boardstat)
                        del(history[len(history)-1])
                        if tf:
                            chemes = changeseq(seq)+"의 승리(체크메이트)"
                        else:
                            chemes = changeseq(seq)+"의 체크"
                    else: # 스테일메이트/무승부 확인
                        saveboard(boardstat)
                        tf, boardstat = mateche(seq, boardstat)
                        del(history[len(history)-1])
                        if tf:
                            chemes = "무승부(스테일메이트)"
                        else:
                            wpie, bpie = checkpie(boardstat)
                            chemes = draw(wpie, bpie, boardstat)
                    sel = []
                else:
                    sel = []

        elif event.type == pygame.KEYUP and (50<=event.key<=53 or 258<=event.key<=261): # 진급할 기물 선택
            if event.key<=53:
                prom = event.key-48
            else:
                prom = event.key-256

    # 시간 경과 표시
    if time.time() >= sec+1 and timer > 0 and btime > 0 and wtime > 0:
        sec = time.time()
        if stime <= 0:
            if seq == "흑":
                btime -= 1
            elif seq == "백":
                wtime -= 1
        else:
            stime -= 1

    # 시간 초과 감지
    if timer > 0:
        if btime <= 0:
            chemes = "백의 승리(시간 초과)"
        elif wtime <= 0:
            chemes = "흑의 승리(시간 초과)"
        elif chemes == "백의 승리(시간 초과)" or chemes == "흑의 승리(시간 초과)":
            chemes = " "


    board.fill((255,255,255)) # 배경을 흰색으로 채운다

    board.blit(backg, (0, 0)) # 이미지를 그린다

    # 프로모션(진급) 기물 표시
    promf = font.render(promarr[prom], True, (0, 0, 0))
    promr = promf.get_rect();
    promr.center = (1000, 425)
    board.blit(promf, promr)

    # 백 남은시간 표시
    seqf = font.render("백 : "+str(wtime)+"초", True, (0, 0, 0))
    seqr = seqf.get_rect();
    seqr.center = (800, 310)
    board.blit(seqf, seqr)

    # 흑 남은시간 표시
    seqf = font.render("흑 : "+str(btime)+"초", True, (0, 0, 0))
    seqr = seqf.get_rect();
    seqr.center = (800, 360)
    board.blit(seqf, seqr)

    # 해당 순서의 남은 시간 표시
    seqf = font3.render(str(stime)+"초", True, (0, 0, 0))
    seqr = seqf.get_rect();
    seqr.center = (980, 335)
    board.blit(seqf, seqr)

    # 체크/무승부 메시지 표시
    seqf = font.render(chemes, True, (0, 0, 0))
    seqr = seqf.get_rect();
    seqr.center = (900, 270)
    board.blit(seqf, seqr)

    # 순서 표시
    seqf = font.render(seq+"의 차례입니다.", True, (0, 0, 0))
    seqr = seqf.get_rect();
    seqr.center = (900, 230)
    board.blit(seqf, seqr)

    wpie, bpie = checkpie(boardstat)

    # 백의 남은 기물 표시
    seqf = font2.render("wP:"+str(8-wpie[0])+"/wL:"+str(2-wpie[1])+"/wK:"+str(2-wpie[2])+"/wB:"+str(2-wpie[3])+"/wQ:"+str(1-wpie[4]), True, (0, 0, 0))
    seqr = seqf.get_rect();
    seqr.center = (900, 160)
    board.blit(seqf, seqr)

    # 흑의 남은 기물 표시
    seqf = font2.render("bP:"+str(8-bpie[0])+"/bL:"+str(2-bpie[1])+"/bK:"+str(2-bpie[2])+"/bB:"+str(2-bpie[3])+"/bQ:"+str(1-bpie[4]), True, (0, 0, 0))
    seqr = seqf.get_rect();
    seqr.center = (900, 190)
    board.blit(seqf, seqr)

    # 죽은 기물 메시지 표시
    seqf = font.render("죽은 기물", True, (0, 0, 0))
    seqr = seqf.get_rect();
    seqr.center = (900, 120)
    board.blit(seqf, seqr)

    # 제작자 표시
    seqf = font.render("Made by eun01210", True, (0, 0, 0))
    seqr = seqf.get_rect();
    seqr.center = (900, 50)
    board.blit(seqf, seqr)

    prtboard(board, boardstat)

    # 선택한 칸 표시
    if len(sel) > 0:
        pygame.draw.rect(board, (255, 0, 0), (sel[0][0]*87.5, sel[0][1]*87.5, 87.5, 87.5), 5)

    if seq == "백":
        if fir == True:
            fir = False
        else:
            byte = listencode(boardstat) + "/" + str(wtime) + "/" + str(btime) + "/" + str(stime) + "/" + str(chemes) + "/" + str(seq) + "/" + str(timer)
            c_sock.send(bytes(byte, 'UTF-8'))
        
        seqf = font3.render("상대가 수를 두고 있습니다.", True, (255, 0, 0))
        seqr = seqf.get_rect();
        seqr.center = (550, 350)
        board.blit(seqf, seqr)
        pygame.display.flip()
        
        rec = c_sock.recv(1024).decode('UTF-8')
        rec = decry(rec)
        boardstat = copy.deepcopy(rec[0])
        wtime = int(copy.deepcopy(rec[1]))
        btime = int(copy.deepcopy(rec[2]))
        stime = int(copy.deepcopy(rec[3]))
        chemes = copy.deepcopy(rec[4])
        seq = copy.deepcopy(rec[5])
        timer = int(copy.deepcopy(rec[6]))
    else:
        pygame.display.flip()

    pygame.time.delay(10) # 딜레이 설정 (0.01초)

c_sock.close() # 클라이언트 소켓을 졸료한다.
# 725,575 ~ 875,650 // 925,575 ~ 1075,650 //// 475 ~ 550
