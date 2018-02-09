#NAWON CHOI nawonc
# mode-demo.py
# events-example0.py
# Barebones timer, mouse, and keyboard events
# mouseEventsDemo.py

from tkinter import *
import tkinter as tk
import random
import string
import os

#SOURCES:
#list of scrabble dictionary words downloaded from github
    # jonbcard's "scrabble-bot"
    #https://github.com/jonbcard/scrabble-bot/blob/master/src/dictionary.txt
#letter distribution and scores based off the board game Scrabble
#other sources cited above individual functions
#based on the app "Word Streak" by Zynga

####################################
# init
####################################

highScore = [0,0,0,0,0]

def init(data):
    data.demo = False

    # MODE
    data.mode = "splashScreen"

    data.width = 500
    data.height = 700
    data.rows = 4
    data.cols = 4

    #board always has exactly 5 vowels
    data.consonants = consonants()
    data.vowels = vowels()
    data.letters = [random.choice(data.consonants) for i in range(11)]+[random.choice(data.vowels) for i in range(5)]
    # print(data.letters)
    random.shuffle(data.letters)
    data.board = [data.letters[:4],data.letters[4:8],data.letters[8:12],data.letters[12:]]
    # data.board = [([(data.letters)
    #         for c in range(data.cols)]) for r in range(data.rows)]
    # print(data.board)
    data.letterscores = letterscores()
    data.lines = []

    #dictionary
    data.englishWords = set(readFile("dictionary.txt").splitlines())
    #smaller subset of all englishWords(bc most words are ~7 letters long)
    data.subSet = set()
    for x in data.englishWords:
        if len(x)<=8:
            data.subSet.add(x)
        if len(data.subSet) == 1000:
            break
    # print(len(data.englishWords))
    print("loading... This may take a couple minutes...")

    # margin around grid
    data.xmargin = 50
    data.ymargin = data.height/3
    data.cellSize = 100 # width and height of each cell
    data.m = 7

    #score and timer
    data.score = 0
    data.ticks = 0
    data.isTimeUp = False
    data.timer = 120
    data.newHighScore = False

    #keyboard control
    data.keys = [['1','2','3','4'],
                 ['q','w','e','r'],
                 ['a','s','d','f'],
                 ['z','x','c','v']]
    data.highlight = "yellow"

    #proposed word
    data.propWord = [] #list of tuples (row, col) of key pressed
    data.wordPoints = 0
    data.scoredWords = set()
    data.allPossibleWords = findAllWords(data)
    # print('all words', data.allPossibleWords)
    # print(len(data.allPossibleWords))

    #extra animations and powerups
    data.wordFound = 0
    data.freeze = None
    data.inspire = None
    data.inspiredWords = []
    data.encouragement = None
    data.instructions = False

    #mouse drag and drop
    data.drag = False
    data.boundaries = boundaries(data)

# returns a 2D list: 2 x 1
#first list: tuples of the boundaries of each row (y values)
#second list: tuples of the boundaries for each col (x value)
#boundaries are smaller than drawn cells to make diagonals easier
def boundaries(data):
    m=data.m
    bounds = []
    c, r = [], []
    for row in range(data.rows):
        (x0,y0,x1,y1) = getCellBounds(row, 0, data)
        r1 = tuple([y0+m,y1-m]) #plus/minus 5?
        r.append(r1)
    for col in range(data.cols):
        (x0,y0,x1,y1) = getCellBounds(0, col, data)
        c1 = tuple([x0+m,x1-m])
        c.append(c1)
    bounds.append(r)
    bounds.append(c)
    return bounds

def readFile(path):
    with open(path, "rt") as f:
        return f.read()

def writeFile(path, contents):
    with open(path, "wt") as f:
        f.write(contents)

def vowels():
    vowels = ('A'*9)+('E'*12)+('I'*9)+('O'*8)+('U'*4)
    return vowels

def consonants():
    a =('B'*2)+('C'*2)+('D'*4)+('F'*2)+('G'*3)
    b =('H'*2)+('L'*4)+('M'*2)+('N'*6)
    c =('P'*2)+('R'*6)+('S'*4)+('T'*6)+('V'*2)+('W'*2)
    d =('Y'*2)+'JKQXZ'
    return a+b+c+d

def letterscores():
    d=dict()
    for letter in 'EAIONRTLSU':
        d[letter] = 1
    d['D'] = 2
    d['G'] = 2
    for letter in 'BCMP':
        d[letter] = 3
    for letter in 'FHVWY':
        d[letter] = 4
    d['K'] = 5
    d['J'] = 8
    d['X'] = 8
    d['Q'] = 10
    d['Z'] = 10
    return d

####################################
# mode dispatcher
####################################

def mousePressed(event, data):
    if (data.mode == "splashScreen"): splashScreenMousePressed(event, data)
    elif (data.mode == "playGame"):   playGameMousePressed(event, data)
    elif (data.mode == "help"):       helpMousePressed(event, data)
    elif (data.mode == "gameOver"):   gameOverMousePressed(event, data)

def keyPressed(event, data):
    if (data.mode == "splashScreen"): splashScreenKeyPressed(event, data)
    elif (data.mode == "playGame"):   playGameKeyPressed(event, data)
    elif (data.mode == "help"):       helpKeyPressed(event, data)
    elif (data.mode == "gameOver"):   gameOverKeyPressed(event, data)

def timerFired(data):
    if (data.mode == "splashScreen"): splashScreenTimerFired(data)
    elif (data.mode == "playGame"):   playGameTimerFired(data)
    elif (data.mode == "help"):       helpTimerFired(data)
    elif (data.mode == "gameOver"):   gameOverTimerFired(data)

def redrawAll(canvas, data):
    if (data.mode == "splashScreen"): splashScreenRedrawAll(canvas, data)
    elif (data.mode == "playGame"):   playGameRedrawAll(canvas, data)
    elif (data.mode == "help"):       helpRedrawAll(canvas, data)
    elif (data.mode == "gameOver"):   gameOverRedrawAll(canvas, data)

def leftMoved(event, data):
    #drag and click to create words on the board
    if data.drag==True:
        row = None
        col = None
        for rows in range(len(data.boundaries[0])):
            y0 = data.boundaries[0][rows][0]
            y1 = data.boundaries[0][rows][1]
            if (event.y < y1) and (event.y > y0):
                row = rows
        for cols in range(len(data.boundaries[1])):
            x0 = data.boundaries[1][cols][0]
            x1 = data.boundaries[1][cols][1]
            if (event.x > x0) and (event.x < x1):
                col = cols
        if (row!= None) and (col != None):
            coord = tuple([row, col])
            if (data.propWord ==[]):
                data.propWord.append(coord)
            else:
                if isLegalBlock(coord[0],coord[1],data):
                    data.propWord.append(coord)

def leftReleased(event, data):
    if data.drag == True:
        data.drag = False
        word = makeWord(data.propWord, data)
        if isWord(word, data) and (word not in data.scoredWords):
            getWordPoints(word, data)
            data.score += data.wordPoints
            data.scoredWords.add(word)
            data.encouragement = data.wordPoints
            data.wordFound = 10
            data.wordPoints = 0
        data.propWord = []
        data.lines = []

####################################
# playGame mode
####################################

def playGameMousePressed(event, data):
    #if click is in the board, start the "drag"
    if (data.inspire==None) or (data.inspire== 0):
        if (event.x >= data.xmargin) and (event.x<= data.width-data.xmargin):
            if (event.y >= data.ymargin) and (event.y <= data.ymargin +(data.width-2*data.xmargin)):
                data.drag = True 
    #time freeze powerup
    if (data.freeze == None):
        if (event.x>=data.width-(data.xmargin+50)) and (event.x<=data.width-data.xmargin):
            if (event.y>data.xmargin*2/3+5) and (event.y<data.xmargin*2/3+55):
                data.freeze = 100
    #inspiration powerup
    if (data.inspire == None):
        if (event.x>=data.width-(data.xmargin+110)) and (event.x<=data.width-(data.xmargin+60)):
            if (event.y>data.xmargin*2/3+5) and (event.y<data.xmargin*2/3+55):
                data.inspire = 60
                inspire(data)

def inspire(data):
    #chooses 5 words (len>=5) from the list of possible words
    #displays it for 6 seconds
    for item in data.allPossibleWords:
        if len(item)>= 4:
            if item not in data.scoredWords:
                data.inspiredWords.append(item)
        if len(data.inspiredWords)==5:
            # print(data.inspiredWords)
            break

def playGameKeyPressed(event, data):
    if (event.keysym == 'p'):
        data.mode = "help"
    if (event.keysym == 'l'):
        data.isTimeUp= True
        newHighScore(data)
        data.mode = "gameOver"
    for row in range(len(data.keys)):
        for col in range(len(data.keys[0])):
            if data.keys[row][col] == event.keysym:
                if data.propWord==[]:
                    data.propWord.append(tuple([row, col]))
                else:
                    if (isLegalBlock(row, col, data)):
                        data.propWord.append(tuple([row, col]))
    #space bar indicates that the user has finished creating a word
    if (event.keysym=="space"):
        word = makeWord(data.propWord, data)
        if isWord(word, data) and (word not in data.scoredWords):
            getWordPoints(word, data)
            data.score += data.wordPoints
            data.scoredWords.add(word)
            data.encouragement = data.wordPoints
            data.wordFound = 10
            data.wordPoints = 0
        data.propWord = []
        data.lines = []
    if (event.keysym=="BackSpace"):
        if not (data.propWord==[]):
            return data.propWord.pop()

def isLegalBlock(row, col, data):
    #checks if a move is legal by subtracting the row/col of the move
    #and seeing if its one of the legal directions 
    if (row, col) in data.propWord: return False
    elif (row == None) and (col == None): return False
    directions=[(-1,-1), (-1,0), (-1,+1),
                ( 0,-1),         ( 0,+1),
                (+1,-1), (+1,0), (+1,+1)]
    srow, scol = data.propWord[-1][0], data.propWord[-1][1]
    r, c = srow-row, scol-col
    for direction in directions:
        drow = direction[0]
        dcol = direction[1]
        if (drow==r) and (dcol==c):
            return True

def makeWord(proposedWord, data):
    #converts row/col tuple into a string of the corresponding letters
    proposedWord = ""
    for item in data.propWord:
        row, col = item[0], item[1]
        proposedWord+= str(data.board[row][col])
    return proposedWord

def isWord(word, data):
    #somehow define what a word is and check if its a word
    #import a scrabble dictionary of all possible words??
    if len(word)<=1: return False
    #make sure its a word
    if data.demo == False:
        if word in data.englishWords:
            return True
    else:
        if word in data.subSet:
            return True


def getWordPoints(proposedWord, data):
    for i in proposedWord:
        data.wordPoints+= data.letterscores[i]

#calls "solve" function which returns a list of all possible letter combos
#checks for legitimate words from that list 
def findAllWords(data):
        # Uses backtracking to return a list of all possible combination of letters
    #starting from a given row and col
    def solve(row, col, data):
        #base case: when theres no more directions to go in
        # allCombos = set()
        foundPaths = set()
        def isLegal(row, col, path, data): 
            #legal move: in board, adjacent, unused block
            if (row<0) or (row>(len(data.board)-1)) or (col<0) or (col>(len(data.board[0])-1)):
                return False
            elif (tuple([row, col])) in path:
                return False
            return True
        def isWordBeginning(word, data):
            #only continues to search words in the path if words can be made with the prefix
            #ex) backtracks if the current word is "XYZ" or "AAA"
            l = len(word)
            if word in foundPaths: return True
            if data.demo == False:
                for x in data.englishWords:
                    if x[:l]==word:
                        foundPaths.add(word)
                        return True
            else:
                for x in data.subSet:
                    if x[:l]==word:
                        foundPaths.add(word)
                        return True
            return False
        # backtrack
        def makeCombos(word, row, col, data, path =[]):
            if len(path)==0: path.append(tuple([row, col]))
            directions=[(-1,-1), (-1,0), (-1,+1),
                        ( 0,-1),         ( 0,+1),
                        (+1,-1), (+1,0), (+1,+1)]
            for direction in directions:
                drow, dcol = direction[0], direction[1]
                r, c = row+drow, col+dcol
                if isLegal(r, c, path, data):
                    path.append(tuple([r, c]))
                    newWord = word + data.board[r][c]
                    if isWordBeginning(newWord, data):
                        if isWord(newWord,data):
                            allPossibleWords.add(newWord)
                        makeCombos(newWord, r, c, data, path)
                    path.pop()
            return None
        makeCombos(data.board[row][col], row, col, data)
    board = data.board
    rows, cols = len(board), len(board[0])
    allPossibleWords = set()
    for row in range(rows):
        for col in range(cols):
            # print(row,col)
            solve(row, col, data)
    return allPossibleWords

########################################################
def playGameTimerFired(data):
    #timer fires every second
    if (data.isTimeUp ==False) and ((data.freeze == None) or (data.freeze == 0)) and ((data.inspire== None) or (data.inspire==0)):
        data.ticks += 1
        if data.ticks %10 == 0:
            data.timer-=1
            if data.timer==0: 
                data.isTimeUp = True
                newHighScore(data)
                data.mode = "gameOver"
    if data.wordFound >= 0:
        if data.wordFound == 0:
            data.encouragement = None
        else: data.wordFound -= 1
        if len(data.propWord)>0:
            data.wordFound=0
    if (data.freeze !=None) and (data.freeze > 0):
        data.freeze -= 1
    if (data.inspire != None) and (data.inspire>0):
        data.inspire -=1

def playGameRedrawAll(canvas, data):
    canvas.create_rectangle(0, 0, data.width, data.height, fill="dodger blue", outline="white")
    canvas.create_rectangle(data.xmargin, (5*data.ymargin)/8, data.width-data.xmargin, (data.width - 2*data.xmargin)/2, fill="yellow", outline='yellow')
    canvas.create_text(data.width/2, data.height-(data.height/20), text="Press 'p' to pause game", font="Arial 15")
    drawBoard(canvas, data)
    drawLines(canvas, data)
    drawTimer(canvas, data)
    drawScore(canvas, data)
    drawWord(canvas, data)
    drawPowerups(canvas, data)
    drawEncouragement(canvas, data)

#from lab6 tetris
def drawBoard(canvas, data):
    #draws grid of cells
    for row in range(data.rows):
        for col in range(data.cols):
            drawCell(canvas, data, row, col, data.board[row][col]) 

#adapted from lab6 tetris
def drawCell(canvas, data, row, col, color):
    gridWidth  = data.width - 2*data.xmargin
    (x0, y0, x1, y1) = getCellBounds(row, col, data)
    m = data.m # cell outline margin
    canvas.create_rectangle(x0, y0, x1, y1, fill="dodger blue", outline='dodger blue')
    if tuple([row, col]) in data.propWord:
        canvas.create_rectangle(x0+m, y0+m, x1-m, y1-m, fill= data.highlight, outline='dodger blue')
    else:
        canvas.create_rectangle(x0+m, y0+m, x1-m, y1-m, fill= "white", outline='white')
    canvas.create_text((x0+x1)/2, (y0+y1)/2, text=data.board[row][col], font="Arial 40 bold")
    canvas.create_text(x1-m, y0+m, text= data.letterscores[data.board[row][col]], font= "Arial 20 bold", anchor="ne")

#from lab6 tetris
def getCellBounds(row, col, data):
    # aka "modelToView"
    # returns (x0, y0, x1, y1) corners/bounding box of given cell in grid
    gridWidth  = data.width - 2*data.xmargin
    x0 = data.xmargin + gridWidth * col / data.cols
    x1 = data.xmargin + gridWidth * (col+1) / data.cols
    y0 = int(data.ymargin + gridWidth * row / data.rows)
    y1 = int(data.ymargin + gridWidth * (row+1) / data.rows)
    return (x0, y0, x1, y1)

def getLineValues(data):
    for x in range(len(data.propWord)-1):
        srow, scol = data.propWord[x][0], data.propWord[x][1]
        (x0,y0,x1,y1) = getCellBounds(srow,scol,data)
        trow, tcol = data.propWord[x+1][0], data.propWord[x+1][1]
        (x2,y2,x3,y3) = getCellBounds(trow,tcol,data)
        data.lines.append([(x0+x1)/2,(y0+y1)/2,(x2+x3)/2,(y2+y3)/2])

def drawLines(canvas, data):
    getLineValues(data)
    for item in range(len(data.lines)):
        x0, y0 = data.lines[item][0],data.lines[item][1]
        x1, y1 = data.lines[item][2],data.lines[item][3]
        canvas.create_line(x0,y0,x1,y1, fill ='orange', width = 5)

def drawPowerups(canvas, data):
    drawFreeze(canvas, data)
    drawInspire(canvas, data)

def drawInspire(canvas, data):
    #reveals 5 words that have not yet been found for 7 seconds
    if (data.inspire == None):
        canvas.create_rectangle(data.width-(data.xmargin+110), data.xmargin*2/3+5, data.width-(data.xmargin+60), data.xmargin*2/3+55, fill="violet", outline= 'violet')
        canvas.create_text(data.width-(data.xmargin+110)+17, data.xmargin*2/3+2, text='I', anchor='nw', font="Arial 50 bold", fill='white')
    elif (data.inspire != None) and (data.inspire>0):
        drawInspiration(canvas, data)

def drawFreeze(canvas, data):
    #time freeze
    if (data.freeze == None):
        canvas.create_rectangle(data.width-(data.xmargin+50), data.xmargin*2/3+5, data.width-data.xmargin, data.xmargin*2/3+55, fill="SkyBlue1", outline='SkyBlue1')
        canvas.create_text(data.width-(data.xmargin+50)+10, data.xmargin*2/3+2, text="F", anchor="nw",font="Arial 50 bold", fill="white")

def drawInspiration(canvas,data):
    m = 63
    canvas.create_rectangle(data.width/6, data.height/4, data.width-(data.width/6), data.height-(data.height/4), fill="violet", outline='violet')
    for word in range(len(data.inspiredWords)):
        canvas.create_text(data.width/2, 50+data.height/4+(word*m), text=data.inspiredWords[word], fill="white", font="Arial 30 bold")

def drawTimer(canvas, data):
    color = "white"
    if data.timer<=30: color = "yellow"
    if data.timer<=10: color = "red"
    if (data.freeze!=None) and (data.freeze<=100) and (data.freeze>0): color = 'SkyBlue1'
    if (data.inspire!= None) and (data.inspire<=50) and (data.inspire>0): color = 'violet'
    canvas.create_rectangle(data.xmargin, data.xmargin*2/3+5, data.xmargin+75, data.xmargin+25, fill=color, outline=color)
    canvas.create_text(data.xmargin+20, data.ymargin/5, text=data.timer, 
        font="Arial 20", anchor="nw")

def drawScore(canvas, data):
    canvas.create_text(data.width/2, data.ymargin/3, text=data.score, font="Arial 50 bold")

def drawWord(canvas, data):
    word = makeWord(data.propWord, data)
    canvas.create_text(data.width/2, (3*data.ymargin)/4, text=word, font="Arial 50 bold")

def drawEncouragement(canvas, data):
    if (data.encouragement!=None):
        if (data.encouragement >= 4) and (data.encouragement < 7):
            canvas.create_text(data.width/2, data.ymargin/2, text="Good!", font="Arial 20")
        elif (data.encouragement >= 7) and (data.encouragement < 10):
            canvas.create_text(data.width/2, data.ymargin/2, text="Excellent!", font="Arial 20")
        elif (data.encouragement >= 10) and (data.encouragement < 12):
            canvas.create_text(data.width/2, data.ymargin/2, text="Amazing!", font="Arial 20")
        elif (data.encouragement >= 12):
            canvas.create_text(data.width/2, data.ymargin/2, text="Incredible!", font="Arial 20") 

####################################
# splashScreen mode
####################################

def splashScreenMousePressed(event, data):
    pass
    # data.mode = "playGame"

def splashScreenKeyPressed(event, data):
    if (event.keysym=='i'):
        data.instructions= not data.instructions
    if (event.keysym=='space'): data.mode = "playGame"

def splashScreenTimerFired(data):
    pass

def splashScreenRedrawAll(canvas, data):
    canvas.create_rectangle(0,0,data.width, data.height, fill="dodger blue", outline="white")
    canvas.create_text(data.width/2, data.height/3,
                       text="BOGGLE", font="Arial 75 bold", fill="white")
    canvas.create_text(data.width/2, (7*data.height)/12,
                       text="Press space to start", font="Arial 20")
    canvas.create_text(data.width/2, (8*data.height)/12, text="Press 'i' for instructions", font="Arial 17")
    drawInstructions(canvas, data)

def drawInstructions(canvas, data):
    if data.instructions==True:
        canvas.create_rectangle(data.width/8, data.height/2, data.width-data.width/8, data.height-data.height/6, fill="white", outline="white")
        canvas.create_text(data.width/2, data.height/2+50, font="Arial 15", text="Make as many words as possible in the given time!")
        #blocks
        canvas.create_rectangle(data.width/6+15, data.height/2+100, data.width/6+65, data.height/2+150, fill="violet", outline="violet")
        canvas.create_rectangle(data.width/6+15, data.height/2+165, data.width/6+65, data.height/2+215, fill="SkyBlue1", outline="SkyBlue1")
        canvas.create_text(data.width/6+40, data.height/2+190, text="F", font="Arial 25 bold", fill="white")
        canvas.create_text(data.width-data.width/3-50, data.height/2+190, text="Freezes timer for 10 seconds")
        canvas.create_text(data.width/6+40, data.height/2+125, text="I", font="Arial 25 bold", fill="white")
        canvas.create_text(data.width-data.width/3-50, data.height/2+125, text="Reveals 5 unfound words for 7 seconds")

####################################
# pause mode
####################################

def helpMousePressed(event, data):
    data.mode = 'playGame'

def helpKeyPressed(event, data):
    data.mode = "playGame"

def helpTimerFired(data):
    pass

def helpRedrawAll(canvas, data):
    canvas.create_rectangle(0, 0, data.width, data.height, fill="dodger blue", outline="white")
    canvas.create_text(data.width/2, data.height/2-40,
                       text="GAME PAUSED", font="Arial 50 bold", fill="white")
    canvas.create_text(data.width/2, data.height/2+15,
                       text="Press any key to keep playing!", font="Arial 20")

####################################
# gameOver mode
####################################

def gameOverMousePressed(event, data):
    pass

def gameOverKeyPressed(event, data):
    if (event.keysym == "r"):
        init(data)

def gameOverTimerFired(data):
    pass

def newHighScore(data):
    global highScore
    for score in range(len(highScore)):
        if data.score > highScore[score]:
            highScore.insert(score, data.score)
            if score == 0:data.newHighScore = True
            highScore= highScore[0:5]
            break

def drawNewHighScore(canvas, data):
    if data.newHighScore == True:
        canvas.create_text(data.width/2, (data.height/6)+85, text="NEW HIGH SCORE!", font="Arial 20 bold", fill="yellow")

def gameOverRedrawAll(canvas, data):
    canvas.create_rectangle(0, 0, data.width, data.height, fill="dodger blue", outline="white")
    canvas.create_text(data.width/2, data.height/6, text="GAME OVER", font="Arial 50 bold", fill="white")
    canvas.create_text(data.width/2, data.height-(data.height/6), text="Press 'r' to play again!", font="Arial 20 bold")
    canvas.create_text(data.width/2, (data.height/6)+50, text= "SCORE:"+" "+str(data.score), font= "Arial 30 bold")
    drawNewHighScore(canvas, data)
    drawHighScores(canvas, data)

def drawHighScores(canvas, data):
    m = 50 #margin
    order = ''
    for row in range(5):
        if row == 0: order = "1st"
        elif row == 1: order = '2nd'
        elif row == 2: order = '3rd'
        elif row == 3: order = '4th'
        elif row == 4: order = '5th'
        canvas.create_text(data.width/2, (data.height/6)+120+row*m, text=order+"   "+str(highScore[row]), font="Arial 15")

####################################
# use the run function as-is
####################################

def run(width=300, height=300):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        canvas.create_rectangle(0, 0, data.width, data.height,
                                fill='white', width=0)
        redrawAll(canvas, data)
        canvas.update()

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def mouseWrapper(mouseFn, event, canvas, data):
        mouseFn(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
        
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 100 # milliseconds
    init(data)
    # create the root and the canvas
    root = tk.Tk()
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.pack()
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    canvas.bind("<B1-Motion>", lambda event:
                            mouseWrapper(leftMoved, event, canvas, data))
    root.bind("<B1-ButtonRelease>", lambda event:
                            mouseWrapper(leftReleased, event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)

    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")

run(300, 300)