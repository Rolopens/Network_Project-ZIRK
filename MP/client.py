import wx
import sys
import socket
import time
import csv
import threading

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

        self.SetPosition((300,200))
        self.Show()

    def setAlias(self, name):
        # SETS ALIAS AND OTHER AESTHETIC STUFF
        self.userName = name
        self.defaultLog = "USER LOG:    " + self.userName + "\n"
        self._logAll = "USER LOG:    " + self.userName + "\n"
        self.log.SetValue(self.defaultLog)
        self.SetTitle("Welcome, " + self.userName)


    
    def connect(self):
        self.tlock = threading.Lock()
        self.shutdown = False

        self.host = '127.0.0.1'
        self.port = 0

        portBox = wx.TextEntryDialog(None, "Input port number of desired server", "Server Selection", '')
        if portBox.ShowModal() == wx.ID_OK:
            self.serverPort = int(portBox.GetValue())
        self.server = ('127.0.0.1', self.serverPort)

        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # DGRAM is used for UDP
        self.s.bind((self.host, self.port))
        self.s.setblocking(0)

        # STARTS THREAD 1
        self.rT = threading.Thread(target=self.receiving, args=("RecvThread", self.s))
        self.rT.start()

        # TIMER THREAD
        #self.receiving2()
        self.alias = self.userName
        self.s.sendto(("@@connected " + self.alias).encode('utf-8'), self.server)

    def initList(self):
        self.s.sendto(("@@initlist " + self.alias).encode('utf-8'), self.server)
        
    def sendMsg(self,e):
        # GETS MESSAGE FROM CHATBOX, SENDS IT OVER SOCKET IF NOT EMPTY
        self.tlock.acquire()
        message = self.chatBox.GetValue()

        self.chatBox.SetValue("")
        self.Refresh()

        if message != '':
            try:
                self.s.sendto((self.alias + " -> " + self.list.GetString(self.list.GetSelection()) + ": " + message).encode('utf-8'), self.server)
                #self.log.AppendText(self.alias + "-> " + message + "\n")
            except:
                pass
        
        self.tlock.release()
        time.sleep(.2)

    def sendFile(self, e):
        print("SENDING FILE...")

    def receiving(self,name, sock):
        # CLIENT THREAD
        while not self.shutdown:
            try:
                self.tlock.acquire()

                while True:
                    data, addr = sock.recvfrom(1024)
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

                    if not silent:
                        self._logAll += str(data) + "\n"
                        self.log.AppendText(str(data) + "\n")
                    print(str(data) + " RECEIVED")
            except:
                pass
            finally:
                self.tlock.release()
            # PLAY WITH THIS
            time.sleep(.2)

    def deleteInList(self, name):
        i = self.list.GetCount()
        for x in range (0, i):
            if (name == self.list.GetString(x)):
                y = x
        self.list.Delete(y)
        self.Refresh()

    def disconnect(self,e):
        self.s.sendto(("@@disconnected " + self.alias).encode('utf-8'), self.server)
        self.shutdown = True
        self.rT.join()
        self.s.close()
        self.log.AppendText("DISCONNECTED FROM SERVER\n")
        self.Close()

    # IF USER SELECTS NEW CHAT OPTION IN COMBOBOX, UPDATE LOG AND DO SOME OTHER STUFF
    def updateChat (self, e):
        selected = self.list.GetSelections()
        self.chatMate = self.list.GetString(self.list.GetSelection()) 
        self.filter(self.chatMate)

    def filter(self, name):
        ok1 = name + " -> "
        ok2 = " -> " + name
   
        lines = self._logAll.split("\n")
        print("CUR LINES")
        print(lines)
        for i in range(len(lines)-1,-1,-1):
            if ok1 not in lines[i] and ok2 not in lines[i]:
                del lines[i]
            elif lines[i] == '\n':
                del lines[i]

        print("FILTERED LINES FOR " + name)
        print(lines)
 
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

    def readCredentials(self,filename):
        with open(filename,"rt") as csvfile:
            cin = csv.reader(csvfile)
            self.creds = [row for row in cin]

        for entry in self.creds:
            self.userInfo[entry[0]] = entry[1].replace('\n','')

    def writeCredentials(self,filename):
        with open(filename, 'w', newline='\n') as csvfile:
            writer = csv.writer(csvfile)
            for name, password in self.userInfo.items():
                entry=[name,password+'\n']
                writer.writerow(entry)

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
