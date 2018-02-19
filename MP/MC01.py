import wx
import sys
import socket
import time
import threading

class clientFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(clientFrame, self).__init__(*args, **kwargs)
        self.initialize()

    def initialize(self):
        # ~AESTHETICS~
        self.SetSize(400,600)
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
        self.header = wx.StaticBitmap(self.mainPanel, -1, imgHeader, (0,0), (400,150))

        # ADD DISCONNECT BUTTON
        imgServer = wx.Image("rsrcs/disconnectButton.jpg", wx.BITMAP_TYPE_ANY).Scale(30,30)
        imgServer = wx.Bitmap(imgServer)
        self.btnDisconnect = wx.BitmapButton(self.mainPanel, -1, imgServer, (335,135),(35,35))
        self.btnDisconnect.Bind(wx.EVT_BUTTON, self.disconnect)

        # INITIALIZE LOG AS UNEDITABLE TEXT FIELD
        self.log = wx.TextCtrl(self.mainPanel, style = wx.TE_READONLY | wx.TE_MULTILINE, pos=(0,170), size=(400,350))
        self.log.SetValue(self.defaultLog)

        # INITIALIZE CHATBOX
        self.chatBox = wx.TextCtrl(self.mainPanel, style = wx.TE_PROCESS_ENTER, pos=(0,520), size=(400,25))
        self.chatBox.Bind(wx.EVT_TEXT_ENTER, self.sendMsg)

        # INITIALIZE COMBO BOX
        chatOptions = ["Global"]
        self.combo = wx.ComboBox(self.mainPanel,pos=(20,130),choices = chatOptions , style = wx.CB_DROPDOWN | wx.CB_READONLY) 
        self.combo.Bind(wx.EVT_COMBOBOX, self.updateChat)
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

    def sendMsg(self,e):
        # GETS MESSAGE FROM CHATBOX, SENDS IT OVER SOCKET IF NOT EMPTY
        self.tlock.acquire()
        message = self.chatBox.GetValue()

        self.chatBox.SetValue("")
        self.Refresh()

        if message != '':
            try:
                self.s.sendto((self.alias + ": " + message).encode('utf-8'), self.server)
                #self.log.AppendText(self.alias + "-> " + message + "\n")
            except:
                pass
        
        self.tlock.release()
        time.sleep(.3)

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
                    self.log.AppendText(str(data) + "\n")
                    print(str(data) + "RECEIVED")
            except:
                pass
            finally:
                self.tlock.release()
            # PLAY WITH THIS
            time.sleep(.3)

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
        self.shutdown = True
        self.rT.join()
        self.s.close()
        self.log.AppendText("DISCONNECTED FROM SERVER\n")

    # IF USER SELECTS NEW CHAT OPTION IN COMBOBOX, UPDATE LOG AND DO SOME OTHER STUFF
    def updateChat (self, e):
        chatMate = self.combo.GetValue()
        if chatMate == "Global":
            self.log.SetValue(self.defaultLog)
            self.log.AppendText("Entered Global Chat\n")
        else:
            self.log.SetValue(self.defaultLog)
            self.log.AppendText("Now chatting with " + chatMate + "\n")


class mainFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(mainFrame, self).__init__(*args, **kwargs)
        self.initialize()
    
    def initialize(self):
        # ~AESTHETICS~
        self.SetSize(400,600)
        self.mainPanel = wx.Panel(self)
        self.mainFont = wx.Font(20,wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.SetBackgroundColour("WHITE")
        self.defaultLog = "***********************SERVER LOG************************\n"

        # ADD HEADER PHOTO
        imgHeader = wx.Image("rsrcs/header2_1.jpg", wx.BITMAP_TYPE_ANY).Scale(400, 150)
        imgHeader = wx.Bitmap(imgHeader)
        self.header = wx.StaticBitmap(self.mainPanel, -1, imgHeader, (0,0), (400,150))

        # ADD SERVER BUTTON (OFF)
        imgServer = wx.Image("rsrcs/serverButton.jpg", wx.BITMAP_TYPE_ANY).Scale(70,70)
        imgServer = wx.Bitmap(imgServer)
        self.btnServer = wx.BitmapButton(self.mainPanel, -1, imgServer, (20,160),(70,70))
        self.btnServer.Bind(wx.EVT_BUTTON,self.startServer)

        # ADD QUIT BUTTON
        imgServer = wx.Image("rsrcs/quitButton.jpg", wx.BITMAP_TYPE_ANY).Scale(30,30)
        imgServer = wx.Bitmap(imgServer)
        self.btnQuit = wx.BitmapButton(self.mainPanel, -1, imgServer, (180,160),(35,35))
        self.btnQuit.Bind(wx.EVT_BUTTON, self.Quit)

        # ADD CLEAR BUTTON
        imgServer = wx.Image("rsrcs/clearButton.jpg", wx.BITMAP_TYPE_ANY).Scale(30,30)
        imgServer = wx.Bitmap(imgServer)
        self.btnClear = wx.BitmapButton(self.mainPanel, -1, imgServer, (180,195),(35,35))
        self.btnClear.Bind(wx.EVT_BUTTON, self.Clear)

        # INITIALIZE LOG AS UNEDITABLE TEXT FIELD
        self.log = wx.TextCtrl(self.mainPanel, style = wx.TE_READONLY | wx.TE_MULTILINE, pos=(0,240), size=(400,330))
        self.log.SetValue(self.defaultLog)
        
        self.SetTitle("Main Server")
        self.Center()
        self.Show()
    
    def Quit(self, e):
        # EXITS APP
        self.Close()
        sys.exit()

    def Clear(self, e):
        # CLEARS LOG
        self.log.SetValue(self.defaultLog)
        self.Refresh()
        
    def startServer (self,e):
        # HIDE SERVER (OFF) BUTTON
        self.btnServer.Hide()

        # ADD SERVER BUTTON (ON)
        imgServer = wx.Image("rsrcs/serverButton2.jpg", wx.BITMAP_TYPE_ANY).Scale(70,70)
        imgServer = wx.Bitmap(imgServer)
        self.btnServer2 = wx.BitmapButton(self.mainPanel, -1, imgServer, (20,160),(70,70))
        self.btnServer2.Bind(wx.EVT_BUTTON, self.stopServer)

        # ADD CLIENT BUTTON
        imgServer = wx.Image("rsrcs/clientAdd.jpg", wx.BITMAP_TYPE_ANY).Scale(70,70)
        imgServer = wx.Bitmap(imgServer)
        self.btnClient = wx.BitmapButton(self.mainPanel, -1, imgServer, (100,160),(70,70))
        self.btnClient.Bind(wx.EVT_BUTTON, self.addClient)
        
        self.log.SetBackgroundColour((148,255,106))
        self.log.AppendText("SERVER STARTING...\n")
        self.Refresh()

        # SERVER SHIT
        self.host = '127.0.0.1'
        # local host
        self.port = 5000
        self.clients = []

        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind((self.host,self.port))
        self.s.setblocking(0)

        self.quitting = False
        self.tlock = threading.Lock()

        # THREAD 1
        #self.sT = threading.Thread(target=self.running, args=("ServerThread", self.s))
        #self.sT.start()

        # THREAD 2 (TIMER)
        self.running2()
    
    def running(self, name, sock):
        # THREAD
        while not self.quitting:
            try:
                self.tlock.acquire()
                data, addr = self.s.recvfrom(1024)
                
                if addr not in self.clients:
                    self.clients.append(addr)

                self.log.AppendText(time.ctime(time.time()) + str(addr) + ": :" + str(data) + "\n")
                for client in self.clients:
                    self.s.sendto(data, client)
                
                time.sleep(.1)
            except:
                pass
            finally:
                self.tlock.release()
                time.sleep(.1)
            self.Refresh()
    
    def running2(self):
        self.sT = threading.Timer(.1, self.running2).start()
        try:
            self.tlock.acquire()
            data, addr = self.s.recvfrom(1024)
            print(str(addr))
                
            if addr not in self.clients:
                self.clients.append(addr)

            self.log.AppendText(time.ctime(time.time()) + str(addr) + ": :" + str(data) + "\n")

            # SENDS TO EVERYONE
            for client in self.clients:
                self.s.sendto(data, client)
                print(str(data) + "SENT")
        except:
            pass
        finally:
            self.tlock.release()
        self.Refresh()

    def stopServer(self,e):
        # HIDES AND SHOWS APPROPRIATE BUTTONS
        self.btnServer.Show()
        self.btnServer2.Hide()
        self.btnClient.Hide()

        # SHUTS SERVER DOWN, CLOSES THREAD
        self.quitting = True
        self.s.close()

        self.log.SetBackgroundColour((255,255,255))
        self.log.AppendText("SERVER TERMINATING...\n")
        self.Refresh()

    def addClient(self, e):
        # ADDS INSTANCE OF CLIENT FRAME
        client = clientFrame(None)
        
        self.log.AppendText("Client Added!\n")

def main():
    app = wx.App()
    mainFrame(None)
    app.MainLoop()

main()