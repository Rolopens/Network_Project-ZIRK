import wx
import sys
import socket
import time
import threading

class clientFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        style = wx.DEFAULT_FRAME_STYLE & (~wx.CLOSE_BOX) & (~wx.MAXIMIZE_BOX)
        super(clientFrame, self).__init__(*args, **kwargs, style = style)
        self.initialize()

    def initialize(self):
        # ~AESTHETICS~
        self.SetSize(600,400)
        self.mainPanel = wx.Panel(self)
        self.SetBackgroundColour("WHITE")

        # PROMPTS FOR NAME, STORES RESULT IN userName
        nameBox = wx.TextEntryDialog(None, "What is your name?", "Welcome, New Client", '')
        if nameBox.ShowModal() == wx.ID_OK:
            self.userName = nameBox.GetValue()
        self.defaultLog = "USER LOG:    " + self.userName + "\n"
        
        # ADD HEADER PHOTO
        imgHeader = wx.Image("rsrcs/header2_2.jpg", wx.BITMAP_TYPE_ANY).Scale(400, 150)
        imgHeader = wx.Bitmap(imgHeader)
        self.header = wx.StaticBitmap(self.mainPanel, -1, imgHeader, (90,0), (400,150))

        # ADD DISCONNECT BUTTON
        imgServer = wx.Image("rsrcs/disconnectButton.jpg", wx.BITMAP_TYPE_ANY).Scale(30,30)
        imgServer = wx.Bitmap(imgServer)
        self.btnDisconnect = wx.BitmapButton(self.mainPanel, -1, imgServer, (500,20),(35,35))
        self.btnDisconnect.Bind(wx.EVT_BUTTON, self.disconnect)

        # INITIALIZE LOG AS UNEDITABLE TEXT FIELD
        self.log = wx.TextCtrl(self.mainPanel, style = wx.TE_READONLY | wx.TE_MULTILINE, pos=(0,150), size=(430,180))
        self.log.SetValue(self.defaultLog)

        # INITIALIZE CHATBOX
        self.chatBox = wx.TextCtrl(self.mainPanel, style = wx.TE_PROCESS_ENTER, pos=(0,330), size=(430,25))
        self.chatBox.Bind(wx.EVT_TEXT_ENTER, self.sendMsg)

        # INITIALIZE LIST BOX
        chatOptions = ["Global"]
        
        #self.combo = wx.ComboBox(self.mainPanel,pos=(500,70),choices = chatOptions , style = wx.CB_DROPDOWN | wx.CB_READONLY) 
        #self.combo.Bind(wx.EVT_COMBOBOX, self.updateChat)
        #self.combo.SetValue("Global")
        self.list = wx.ListBox(self.mainPanel,pos=(430,150),size = (170,205),choices = chatOptions , style = wx.LB_NEEDED_SB | wx.LB_SINGLE)
        self.list.Bind(wx.EVT_LISTBOX, self.updateChat)
        self.list.SetSelection(0)
        
        
        self.log.AppendText("Entered Global Chat\n")

        self.SetTitle("Welcome, " + self.userName)
        self.SetPosition((300,200))
        self.Show()

        self.connect()
    
    def connect(self):
        self.tlock = threading.Lock()
        self.shutdown = False

        self.host = '127.0.0.1'
        self.port = 0

        self.server = ('127.0.0.1', 5000)

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

    def initList(self, oldList):
        for user in oldList:
            self.list.Append(user)
        
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

    # ERROR HERE
    def receiving(self,name, sock):
        # CLIENT THREAD
        while not self.shutdown:
            try:
                self.tlock.acquire()

                while True:
                    data, addr = sock.recvfrom(1024)
                    data = str(data)

                    # delete first 2 char and last char
                    data = data[2:]
                    data = data[:-1]

                    if " -> " not in data and "joined Zirk chat" in data:
                        name = data.split(" has")[0]
                        self.list.Append(name)
                    elif " -> " not in data and "disconnected" in data:
                        name = data.split(" has ")[0]
                        self.deleteInList(name)

                    
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

    def receiving2(self):
        self.rT = threading.Timer(1, self.receiving2).start()
        # CLIENT THREAD
        try:
            self.tlock.acquire()
            while True:
                data, addr = sock.recvfrom(1024)
                self.log.AppendText(str(data) + "\n")
        except:
            pass
        finally:
            self.tlock.release()
        #time.sleep(.2)

    def disconnect(self,e):
        self.s.sendto(("@@disconnected " + self.alias).encode('utf-8'), self.server)
        self.shutdown = True
        self.rT.join()
        self.s.close()
        self.log.AppendText("DISCONNECTED FROM SERVER\n")
        self.Close()

    # IF USER SELECTS NEW CHAT OPTION IN COMBOBOX, UPDATE LOG AND DO SOME OTHER STUFF
    print()
    def updateChat (self, e):
        chatMate = self.list.GetString(self.list.GetSelection())
        if chatMate == "Global":
            self.log.SetValue(self.defaultLog)
            self.log.AppendText("Entered Global Chat\n")
        else:
            self.log.SetValue(self.defaultLog)
            self.log.AppendText("Now chatting with " + chatMate + "\n")

class client(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(client, self).__init__(*args, **kwargs)
        self.initialize()
    
    def initialize(self):
        # ~AESTHETICS~
        self.SetSize(300,300)
        self.mainPanel = wx.Panel(self)
        self.mainFont = wx.Font(20,wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.SetBackgroundColour("WHITE")
        
        # ADD HEADER PHOTO
        imgHeader = wx.Image("rsrcs/smallheader.jpg", wx.BITMAP_TYPE_ANY).Scale(120, 150)
        imgHeader = wx.Bitmap(imgHeader)
        self.header = wx.StaticBitmap(self.mainPanel, -1, imgHeader, (97,20), (100,130))

        # ADD CLIENT BUTTON
        imgServer = wx.Image("rsrcs/clientAdd-1.jpg", wx.BITMAP_TYPE_ANY).Scale(70,70)
        imgServer = wx.Bitmap(imgServer)
        self.btnClient = wx.BitmapButton(self.mainPanel, -1, imgServer, (105,170),(70,70))
        self.btnClient.Bind(wx.EVT_BUTTON, self.addClient)
        
        self.SetTitle("Add Client")
        self.Center()
        self.Show()

    def attach (self, ser):
        print("SUCCESFULLY ATTAHCED")
        self.attachedServer = ser

    def addClient(self, e):
        # ADDS INSTANCE OF CLIENT FRAME
        client = clientFrame(None)
        client.initList(self.attachedServer.getAliases())
        #self.log.AppendText("Client Added!\n")

def main():
    clientApp = wx.App()
    client(None)
    
    clientApp.MainLoop()