import wx
import sys
import socket
import time
import csv
import threading
import os

class chatroomFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        style = wx.DEFAULT_FRAME_STYLE & (~wx.CLOSE_BOX) & (~wx.MAXIMIZE_BOX)
        super(chatroomFrame, self).__init__(*args, **kwargs, style = style)
        self.initialize()
    def initialize(self):
        # ~AESTHETICS~
        self.SetSize(535,400)
        self.mainPanel = wx.Panel(self)
        self.SetBackgroundColour("WHITE")
        
        # ADD HEADER PHOTO
        imgHeader = wx.Image("rsrcs/chatroomheader.jpg", wx.BITMAP_TYPE_ANY).Scale(315,130)
        imgHeader = wx.Bitmap(imgHeader)
        self.header = wx.StaticBitmap(self.mainPanel, -1, imgHeader, (60,0), (315,130))

        # ADD DISCONNECT BUTTON
        imgServer = wx.Image("rsrcs/disconnectButton.jpg", wx.BITMAP_TYPE_ANY).Scale(30,30)
        imgServer = wx.Bitmap(imgServer)
        self.btnDisconnect = wx.BitmapButton(self.mainPanel, -1, imgServer, (10,100),(30,30))
        self.btnDisconnect.Bind(wx.EVT_BUTTON, self.disconnect)

        # INITIALIZE LOG AS UNEDITABLE TEXT FIELD
        self.log = wx.TextCtrl(self.mainPanel, style = wx.TE_READONLY | wx.TE_MULTILINE, pos=(0,130), size=(380,170))

        # INITIALIZE CHATBOX
        self.chatBox = wx.TextCtrl(self.mainPanel, style = wx.TE_PROCESS_ENTER, pos=(0,300), size=(380,25))
        self.chatBox.Bind(wx.EVT_TEXT_ENTER, self.sendMsg)

        # INITIALIZE FILE SELECTOR
        self.fileBox = wx.FilePickerCtrl(self.mainPanel, style = wx.FLP_USE_TEXTCTRL | wx.FLP_FILE_MUST_EXIST, pos=(80,325))
        self.sendFileBtn = wx.Button(self.mainPanel, label="Send File", pos=(280,328), size=(100,25))
        self.sendFileBtn.Bind(wx.EVT_BUTTON, self.sendFile)
        
        # INITIALIZE LIST BOX
        self.list = wx.ListBox(self.mainPanel,pos=(380,130),size = (145,195), style = wx.LB_NEEDED_SB | wx.LB_MULTIPLE)
        self.list.Bind(wx.EVT_LISTBOX, self.updateChat)
        self.list.SetSelection(0)
        self.chatMate = "Global"

        self.SetPosition((300,200))
        self.Show()

    def sendMsg(self,e):
        # GETS MESSAGE FROM CHATBOX, SENDS IT OVER SOCKET IF NOT EMPTY
        self.tlock.acquire()
        message = self.chatBox.GetValue()

        self.chatBox.SetValue("")
        self.Refresh()

        sender = self.alias
        #receiver =  self.chatMate

        if type(receiver) is str:
            if message != '':
                try:
                    self.s.send((sender + " -> " + receiver + ": " + message).encode())
                except:
                    pass
        elif type(receiver) is list:
            self.log.AppendText("ERROR: MORE THAN ONE PERSON SELECTED")
        
        self.tlock.release()
        time.sleep(.1)

    def sendFile(self, e):
        filename = self.fileBox.GetPath()
        sender = self.alias
        #receiver =  self.chatMate

        # SENDS FILE OVER SOCKET IF FILE PICKER IS NOT EMPTY
        if filename != "":

            '''WINDOWS USERS!'''
            #file = filename.split("\\")[len(filename.split("\\"))-1]

            '''MAC USERS!'''
            file = filename.split("/")[len(filename.split("/"))-1]

            filesize = os.path.getsize(filename)
            print(file)
            message = "sendfile@@"+file+"@@"+str(filesize)

            # SENDS FILE NAME AND SIZE TO PREPARE FOR FILE TRANSFER
            self.s.send((sender + " -> " + receiver + ": " + message).encode('utf-8'))
            
            # ACTUAL FILE SENDING, READS FROM FILE AND SENDS PER KILOBYTE
            with open(filename, 'rb') as f:
                bytesToSend = f.read(1024)
                while bytesToSend:
                    print("[+] Sending from client to server")
                    self.s.send(bytesToSend)
                    bytesToSend = f.read(1024)
            
            self.log.AppendText(self.alias + ": Done sending " + file + "\n")
            self.fileBox.SetPath("")

    def disconnect(self,e):
        self.shutdown = True
        #self.rT.join()
        self.s.send(("@@disconnected " + self.alias).encode())
        self.s.close()
        self.Close()

class grpchatFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        style = wx.DEFAULT_FRAME_STYLE & (~wx.CLOSE_BOX) & (~wx.MAXIMIZE_BOX)
        super(grpchatFrame, self).__init__(*args, **kwargs, style = style)
        self.initialize()
    def initialize(self):
        # ~AESTHETICS~
        self.SetSize(535,400)
        self.mainPanel = wx.Panel(self)
        self.SetBackgroundColour("WHITE")
        
        # ADD HEADER PHOTO
        imgHeader = wx.Image("rsrcs/grpheader.jpg", wx.BITMAP_TYPE_ANY).Scale(315,130)
        imgHeader = wx.Bitmap(imgHeader)
        self.header = wx.StaticBitmap(self.mainPanel, -1, imgHeader, (60,0), (315,130))

        # ADD DISCONNECT BUTTON
        imgServer = wx.Image("rsrcs/disconnectButton.jpg", wx.BITMAP_TYPE_ANY).Scale(30,30)
        imgServer = wx.Bitmap(imgServer)
        self.btnDisconnect = wx.BitmapButton(self.mainPanel, -1, imgServer, (10,100),(30,30))
        self.btnDisconnect.Bind(wx.EVT_BUTTON, self.disconnect)

        # INITIALIZE LOG AS UNEDITABLE TEXT FIELD
        self.log = wx.TextCtrl(self.mainPanel, style = wx.TE_READONLY | wx.TE_MULTILINE, pos=(0,130), size=(380,170))

        # INITIALIZE CHATBOX
        self.chatBox = wx.TextCtrl(self.mainPanel, style = wx.TE_PROCESS_ENTER, pos=(0,300), size=(380,25))
        self.chatBox.Bind(wx.EVT_TEXT_ENTER, self.sendMsg)

        # INITIALIZE FILE SELECTOR
        self.fileBox = wx.FilePickerCtrl(self.mainPanel, style = wx.FLP_USE_TEXTCTRL | wx.FLP_FILE_MUST_EXIST, pos=(80,325))
        self.sendFileBtn = wx.Button(self.mainPanel, label="Send File", pos=(280,328), size=(100,25))
        self.sendFileBtn.Bind(wx.EVT_BUTTON, self.sendFile)
        
        # INITIALIZE LIST BOX
        self.list = wx.ListBox(self.mainPanel,pos=(380,130),size = (145,195), style = wx.LB_NEEDED_SB | wx.LB_MULTIPLE)
        self.list.Bind(wx.EVT_LISTBOX, self.updateChat)
        self.list.SetSelection(0)

        self.SetPosition((300,200))
        self.Show()

    def sendMsg(self,e):
        # GETS MESSAGE FROM CHATBOX, SENDS IT OVER SOCKET IF NOT EMPTY
        self.tlock.acquire()
        message = self.chatBox.GetValue()

        self.chatBox.SetValue("")
        self.Refresh()

        sender = self.alias
        #receiver =  self.chatMate

        if type(receiver) is str:
            if message != '':
                try:
                    self.s.send((sender + " -> " + receiver + ": " + message).encode())
                except:
                    pass
        elif type(receiver) is list:
            self.log.AppendText("ERROR: MORE THAN ONE PERSON SELECTED")
        
        self.tlock.release()
        time.sleep(.1)

    def sendFile(self, e):
        filename = self.fileBox.GetPath()
        sender = self.alias
        #receiver =  self.chatMate

        # SENDS FILE OVER SOCKET IF FILE PICKER IS NOT EMPTY
        if filename != "":

            '''WINDOWS USERS!'''
            #file = filename.split("\\")[len(filename.split("\\"))-1]

            '''MAC USERS!'''
            file = filename.split("/")[len(filename.split("/"))-1]

            filesize = os.path.getsize(filename)
            print(file)
            message = "sendfile@@"+file+"@@"+str(filesize)

            # SENDS FILE NAME AND SIZE TO PREPARE FOR FILE TRANSFER
            self.s.send((sender + " -> " + receiver + ": " + message).encode('utf-8'))
            
            # ACTUAL FILE SENDING, READS FROM FILE AND SENDS PER KILOBYTE
            with open(filename, 'rb') as f:
                bytesToSend = f.read(1024)
                while bytesToSend:
                    print("[+] Sending from client to server")
                    self.s.send(bytesToSend)
                    bytesToSend = f.read(1024)
            
            self.log.AppendText(self.alias + ": Done sending " + file + "\n")
            self.fileBox.SetPath("")

    def disconnect(self,e):
        self.shutdown = True
        #self.rT.join()
        self.s.send(("@@disconnected " + self.alias).encode())
        self.s.close()
        self.Close()

class clientFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        style = wx.DEFAULT_FRAME_STYLE & (~wx.CLOSE_BOX) & (~wx.MAXIMIZE_BOX)
        super(clientFrame, self).__init__(*args, **kwargs, style = style)
        self.initialize()

    def initialize(self):
        # ~AESTHETICS~
        self.SetSize(535,400)
        self.mainPanel = wx.Panel(self)
        self.SetBackgroundColour("WHITE")
        
        # ADD HEADER PHOTO
        imgHeader = wx.Image("rsrcs/header2_2.jpg", wx.BITMAP_TYPE_ANY).Scale(315,130)
        imgHeader = wx.Bitmap(imgHeader)
        self.header = wx.StaticBitmap(self.mainPanel, -1, imgHeader, (90,0), (315,130))

        # ADD DISCONNECT BUTTON
        imgServer = wx.Image("rsrcs/disconnectButton.jpg", wx.BITMAP_TYPE_ANY).Scale(30,30)
        imgServer = wx.Bitmap(imgServer)
        self.btnDisconnect = wx.BitmapButton(self.mainPanel, -1, imgServer, (490,100),(30,30))
        self.btnDisconnect.Bind(wx.EVT_BUTTON, self.disconnect)

        # INITIALIZE LOG AS UNEDITABLE TEXT FIELD
        self.log = wx.TextCtrl(self.mainPanel, style = wx.TE_READONLY | wx.TE_MULTILINE, pos=(0,130), size=(380,170))

        # INITIALIZE CHATBOX
        self.chatBox = wx.TextCtrl(self.mainPanel, style = wx.TE_PROCESS_ENTER, pos=(0,300), size=(380,25))
        self.chatBox.Bind(wx.EVT_TEXT_ENTER, self.sendMsg)

        # INITIALIZE FILE SELECTOR
        self.fileBox = wx.FilePickerCtrl(self.mainPanel, style = wx.FLP_USE_TEXTCTRL | wx.FLP_FILE_MUST_EXIST, pos=(80,325))
        self.sendFileBtn = wx.Button(self.mainPanel, label="Send File", pos=(280,328), size=(100,25))
        self.sendFileBtn.Bind(wx.EVT_BUTTON, self.sendFile)
        
        # INITIALIZE LIST BOX
        self.chatOptions = ["Global"]
        self.list = wx.ListBox(self.mainPanel,pos=(380,130),size = (145,195),choices = self.chatOptions , style = wx.LB_NEEDED_SB | wx.LB_MULTIPLE)
        self.list.Bind(wx.EVT_LISTBOX, self.updateChat)
        self.list.SetSelection(0)
        self.chatMate = "Global"

        # ADD GROUP CHAT BUTTON
        imgServer = wx.Image("rsrcs/grpchat.jpg", wx.BITMAP_TYPE_ANY).Scale(25,25)
        imgServer = wx.Bitmap(imgServer)
        self.btnGrpchat = wx.BitmapButton(self.mainPanel, -1, imgServer, (430,100),(30,30))
        self.btnGrpchat.Bind(wx.EVT_BUTTON, self.createGroupChat)
        self.btnGrpchat.Hide()

        # ADD CHATROOM BUTTON
        imgServer = wx.Image("rsrcs/chatroom.jpg", wx.BITMAP_TYPE_ANY).Scale(25,25)
        imgServer = wx.Bitmap(imgServer)
        self.btnChatroom = wx.BitmapButton(self.mainPanel, -1, imgServer, (460,100),(30,30))
        self.btnChatroom.Bind(wx.EVT_BUTTON, self.createChatroom)
        self.btnChatroom.Hide()

        self.SetPosition((300,200))
        self.Show()

    def setAlias(self, name):
        # SETS ALIAS AND OTHER AESTHETIC STUFF
        self.userName = name
        self.defaultLog = "USER LOG:    " + self.userName + "\n"
        self._logAll = "USER LOG:    " + self.userName + "\n"
        self.log.SetValue(self.defaultLog)
        self.SetTitle("Welcome, " + self.userName)

    def createGroupChat(self, e):
        print("MAKING GROUP CHAT")

    def createChatroom(self, e):
        print("MAKING CHATROOM")
    
    def connect(self):
        self.tlock = threading.Lock()
        self.shutdown = False

        self.host = '127.0.0.1'
        self.port = 0

        portBox = wx.TextEntryDialog(None, "Input port number of desired server", "Server Selection", '')
        if portBox.ShowModal() == wx.ID_OK:
            self.serverPort = int(portBox.GetValue())
        self.server = (self.host, self.serverPort)

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect(self.server)
        print("CONNECTED TO SERVER")

        # STARTS RECEIVING THREAD
        self.rT = threading.Thread(target=self.receiving)
        self.rT.start()

        # SENDS INITIAL CONNECTION MESSAGE TO SERVER
        self.alias = self.userName
        self.s.send(("@@connected " + self.alias).encode('utf-8'))
        time.sleep(.1)

    def initList(self):
        # SENDS REQUEST TO SERVER TO INITIALIZE LIST WITH ONLINE USERS
        self.s.send(("@@initlist " + self.alias).encode('utf-8'))
        time.sleep(.1)

    def getReceivers(self):
        chosen = self.list.GetSelections()
        if len(chosen) == 1:
            return self.list.GetString(chosen[0])
        else:
            names = []
            for i in chosen:
                names.append(self.list.GetString(i))
            return names

    # IF USER SELECTS NEW CHAT OPTION IN COMBOBOX, UPDATE LOG AND DO SOME OTHER STUFF
    def updateChat (self, e):
        selected = self.list.GetSelections()
        self.chatMate = self.getReceivers()
        if type(self.chatMate) is str:
            self.filter(self.chatMate)
            self.btnChatroom.Hide()
            self.btnGrpchat.Hide()
        elif type(self.chatMate) is list and "Global" not in self.chatMate:
            self.btnChatroom.Show()
            self.btnGrpchat.Show()
        elif "Global" in self.chatMate:
            self.btnChatroom.Hide()
            self.btnGrpchat.Hide()
        
    def sendMsg(self,e):
        # GETS MESSAGE FROM CHATBOX, SENDS IT OVER SOCKET IF NOT EMPTY
        self.tlock.acquire()
        message = self.chatBox.GetValue()

        self.chatBox.SetValue("")
        self.Refresh()

        sender = self.alias
        receiver =  self.chatMate

        if type(receiver) is str:
            if message != '':
                try:
                    self.s.send((sender + " -> " + receiver + ": " + message).encode())
                except:
                    pass
        elif type(receiver) is list:
            self.log.AppendText("ERROR: MORE THAN ONE PERSON SELECTED")
        
        self.tlock.release()
        time.sleep(.1)

    def sendFile(self, e):
        filename = self.fileBox.GetPath()
        sender = self.alias
        receiver =  self.chatMate

        # SENDS FILE OVER SOCKET IF FILE PICKER IS NOT EMPTY
        if filename != "":

            '''WINDOWS USERS!'''
            #file = filename.split("\\")[len(filename.split("\\"))-1]

            '''MAC USERS!'''
            file = filename.split("/")[len(filename.split("/"))-1]

            filesize = os.path.getsize(filename)
            print(file)
            message = "sendfile@@"+file+"@@"+str(filesize)

            # SENDS FILE NAME AND SIZE TO PREPARE FOR FILE TRANSFER
            self.s.send((sender + " -> " + receiver + ": " + message).encode('utf-8'))
            
            # ACTUAL FILE SENDING, READS FROM FILE AND SENDS PER KILOBYTE
            with open(filename, 'rb') as f:
                bytesToSend = f.read(1024)
                while bytesToSend:
                    print("[+] Sending from client to server")
                    self.s.send(bytesToSend)
                    bytesToSend = f.read(1024)
            
            self.log.AppendText(self.alias + ": Done sending " + file + "\n")
            self.fileBox.SetPath("")

    def receiving(self):
        # CLIENT THREAD
        while True:
            try:
                data = self.s.recv(1024)
                data = str(data.decode())

                silent = 0
                if " -> " not in data and "joined Zirk chat" in data:
                    name = data.split(" has")[0]
                    if name not in self.chatOptions:
                        self.list.Append(name)
                        self.chatOptions.append(name)
                elif " -> " not in data and "disconnected" in data:
                    name = data.split(" has ")[0]
                    self.deleteInList(name)
                    self.chatOptions.remove(name)
                elif " -> " not in data and "@@initlist " in data:
                    silent = 1
                    name = data.split(" ")[1]
                    if name not in self.chatOptions:
                        self.list.Append(name)
                        self.chatOptions.append(name)
                elif " -> " not in data and "sendfile@@" in data:
                    filename = data.split("@@")[1]
                    filesize = float(data.split("@@")[2])

                    # DOWNLOADS FILE, ADDS PREFIX TO IDENTIFY RECEIVER
                    f = open("sentTo"+self.alias+"_"+filename, 'wb')
                    toWrite = self.s.recv(1024)
                    totalRecv = len(toWrite)
                    f.write(toWrite)
                    
                    # KEEPS DOWNLOADING FILE UNTIL ALL PACKETS ARE RECEIVED
                    while totalRecv < filesize:
                        toWrite = self.s.recv(1024)
                        totalRecv += len(toWrite)
                        f.write(toWrite)
                        print("{0:.2f}".format((totalRecv/float(filesize)) * 100) + "percent done: CLIENT SIDE")

                    # CLOSE FILE AFTER
                    f.close()
                    print("[+] File downloaded! CLIENT SIDE")
                    data = "Received " + filename + " of size " + str(filesize) + " bytes" 

                if not silent:
                    self._logAll += str(data) + "\n"
                    self.log.AppendText(str(data) + "\n")
            except:
                break

    def deleteInList(self, name):
        i = self.list.GetCount()
        for x in range (0, i):
            if (name == self.list.GetString(x)):
                y = x
        self.list.Delete(y)
        self.Refresh()

    def disconnect(self,e):
        self.shutdown = True
        #self.rT.join()
        self.s.send(("@@disconnected " + self.alias).encode())
        self.s.close()
        self.Close()

    # FILTERS MESSAGES BY MESSAGES FROM AND TO CERTAIN PERSON
    def filter(self, name):
        ok1 = name + " -> "
        ok2 = " -> " + name
   
        lines = self._logAll.split("\n")
        for i in range(len(lines)-1,-1,-1):
            if ok1 not in lines[i] and ok2 not in lines[i]:
                del lines[i]
            elif lines[i] == '\n':
                del lines[i]
 
        self.log.SetValue(self.defaultLog)
        self.log.AppendText("Now chatting with " + name + "\n")
        for i in lines:
            self.log.AppendText(i+"\n")

class client(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(client, self).__init__(*args, **kwargs)
        self.initialize()
    
    def initialize(self):
        # ~AESTHETICS~
        self.SetSize(200,380)
        self.mainPanel = wx.Panel(self)
        self.mainFont = wx.Font(20,wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.SetBackgroundColour("WHITE")
        
        # ADD HEADER PHOTO
        imgHeader = wx.Image("rsrcs/smallheader.jpg", wx.BITMAP_TYPE_ANY).Scale(110, 130)
        imgHeader = wx.Bitmap(imgHeader)
        self.header = wx.StaticBitmap(self.mainPanel, -1, imgHeader, (45,20), (110,130))

        # USERNAME TEXT BOX
        self.userBox = wx.TextCtrl(self.mainPanel, pos=(25,160), size=(150,25))
        self.userBox.Bind(wx.EVT_TEXT, self.checkAvailability)

        # PASSWORD TEXT BOX
        self.passBox = wx.TextCtrl(self.mainPanel, style = wx.TE_PASSWORD, pos=(25,200), size=(150,25))
        self.passBox.Bind(wx.EVT_TEXT, self.checkAvailability)

        # ERROR MESSAGE
        self.errorTxt = wx.StaticText(self.mainPanel, label="INVALID USERNAME\nAND/OR PASSWORD",style = wx.ALIGN_CENTRE_HORIZONTAL, pos=(30,230))
        self.errorTxt.SetForegroundColour("red")
        self.errorTxt.Hide()
        
        # LOGIN BUTTON
        imgServer = wx.Image("rsrcs/login.jpg", wx.BITMAP_TYPE_ANY).Scale(60,60)
        imgServer = wx.Bitmap(imgServer)
        self.btnLogin = wx.BitmapButton(self.mainPanel, -1, imgServer, (40,270),(60,60))
        self.btnLogin.Bind(wx.EVT_BUTTON, self.login)

        # ADD NEW ACCOUNT BUTTON
        imgServer = wx.Image("rsrcs/clientAdd-1.jpg", wx.BITMAP_TYPE_ANY).Scale(60,60)
        imgServer = wx.Bitmap(imgServer)
        self.btnClient = wx.BitmapButton(self.mainPanel, -1, imgServer, (100,270),(60,60))
        self.btnClient.Bind(wx.EVT_BUTTON, self.newAccount)
        self.btnClient.Hide()

        # READS FROM FILE TO INITIALIZE USER INFO
        self.userInfo = {}
        self.readCredentials("credentials.csv")
        
        self.SetTitle("Client Portal")
        self.Center()
        self.Show()

    # IF USERNAME IS NOT TAKEN, SHOW NEW ACCOUNT BUTTON
    def checkAvailability (self, e):
        takenNames = [i[0] for i in self.userInfo.items()]
        if self.userBox.GetValue() != '' and self.passBox.GetValue() != '' and self.userBox.GetValue() not in takenNames:
            self.btnClient.Show()
        else:
            self.btnClient.Hide()

    # INITIALIZES USERNAME AND PASSWORDS FROM EXTERNAL FILE
    def readCredentials(self,filename):
        with open(filename,"rt") as csvfile:
            cin = csv.reader(csvfile)
            self.creds = [row for row in cin]

        for entry in self.creds:
            self.userInfo[entry[0]] = entry[1].replace('\n','')

    # UPDATES CREDENTIALS EXTERNAL FILE
    def writeCredentials(self,filename):
        with open(filename, 'w', newline='\n') as csvfile:
            writer = csv.writer(csvfile)
            for name, password in self.userInfo.items():
                entry=[name,password+'\n']
                writer.writerow(entry)

    # CREATES NEW ACCOUNT, UPDATES CSV
    def newAccount(self, e):
        name = self.userBox.GetValue()
        password = self.passBox.GetValue()       

        self.userInfo[name] = password
        self.writeCredentials("credentials.csv")

        self.userBox.SetValue("")
        self.passBox.SetValue("")
        self.btnClient.Hide()
        self.errorTxt.Hide()

        self.addClient(name)

    # CHECKS IF USER CREDENTIALS IS VALID, LOG IN IF VALID
    def login(self,e):
        curName = self.userBox.GetValue()
        curPass = self.passBox.GetValue()
        print(self.userInfo.items())
        valid = False
        for name, password in self.userInfo.items():
            if curName == name and curPass == password:
                valid = True
                break

        if valid:
            self.userBox.SetValue("")
            self.passBox.SetValue("")
            self.errorTxt.Hide()
            self.addClient(curName)
        else:
            self.errorTxt.Show()

    def addClient(self, name):
        # ADDS INSTANCE OF CLIENT FRAME
        client = clientFrame(None)
        client.setAlias(name)
        client.connect()
        client.initList()

def main():
    clientApp = wx.App()
    client(None)
    clientApp.MainLoop()
