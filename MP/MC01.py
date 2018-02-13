import wx
import sys
import socket
import time

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
        nameBox = wx.TextEntryDialog(None, "NAME: ", "Welcome, New Client", '')
        if nameBox.ShowModal() == wx.ID_OK:
            userName = nameBox.GetValue()

        # ADD HEADER PHOTO
        imgHeader = wx.Image("Desktop/NETWORK/MP/rsrcs/header2.jpg", wx.BITMAP_TYPE_ANY).Scale(400, 150)
        imgHeader = wx.Bitmap(imgHeader)
        self.header = wx.StaticBitmap(self.mainPanel, -1, imgHeader, (0,0), (400,150))

        self.SetTitle("Welcome, " + userName)
        self.SetPosition((300,200))
        self.Show()

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

        # ADD HEADER PHOTO
        imgHeader = wx.Image("Desktop/NETWORK/MP/rsrcs/header2.jpg", wx.BITMAP_TYPE_ANY).Scale(400, 150)
        imgHeader = wx.Bitmap(imgHeader)
        self.header = wx.StaticBitmap(self.mainPanel, -1, imgHeader, (0,0), (400,150))

        # ADD SERVER BUTTON (OFF)
        imgServer = wx.Image("Desktop/NETWORK/MP/rsrcs/serverButton.jpg", wx.BITMAP_TYPE_ANY).Scale(70,70)
        imgServer = wx.Bitmap(imgServer)
        self.btnServer = wx.BitmapButton(self.mainPanel, -1, imgServer, (20,160),(70,70))
        self.btnServer.Bind(wx.EVT_BUTTON,self.startServer)

        # ADD QUIT BUTTON
        imgServer = wx.Image("Desktop/NETWORK/MP/rsrcs/quitButton.jpg", wx.BITMAP_TYPE_ANY).Scale(30,30)
        imgServer = wx.Bitmap(imgServer)
        self.btnQuit = wx.BitmapButton(self.mainPanel, -1, imgServer, (180,160),(35,35))
        self.btnQuit.Bind(wx.EVT_BUTTON, self.Quit)

        # ADD CLEAR BUTTON
        imgServer = wx.Image("Desktop/NETWORK/MP/rsrcs/clearButton.jpg", wx.BITMAP_TYPE_ANY).Scale(30,30)
        imgServer = wx.Bitmap(imgServer)
        self.btnClear = wx.BitmapButton(self.mainPanel, -1, imgServer, (180,195),(35,35))
        self.btnClear.Bind(wx.EVT_BUTTON, self.Clear)

        # INITIALIZE LOG AS UNEDITABLE TEXT FIELD
        self.log = wx.TextCtrl(self.mainPanel, style = wx.TE_READONLY | wx.TE_MULTILINE, pos=(0,240), size=(400,330))
        
        '''
        YNBox = wx.MessageDialog(None, "DTF or nah?", "Question", wx.YES_NO)
        YNAns = YNBox.ShowModal()
        YNBox.Destroy()
        '''
        
        self.SetTitle("Main Server")
        self.Center()
        self.Show()
    
    def Quit(self, e):
        self.Close()
        sys.exit()

    def Clear(self, e):
        self.log.SetValue("")
        self.Refresh()
        
    def startServer (self,e):
        print("TEST: Starting Server")
        
        # HIDE SERVER (OFF) BUTTON
        self.btnServer.Hide()

        # ADD SERVER BUTTON (ON)
        imgServer = wx.Image("Desktop/NETWORK/MP/rsrcs/serverButton2.jpg", wx.BITMAP_TYPE_ANY).Scale(70,70)
        imgServer = wx.Bitmap(imgServer)
        self.btnServer2 = wx.BitmapButton(self.mainPanel, -1, imgServer, (20,160),(70,70))
        self.btnServer2.Bind(wx.EVT_BUTTON, self.stopServer)

        # ADD CLIENT BUTTON
        imgServer = wx.Image("Desktop/NETWORK/MP/rsrcs/addClient.jpg", wx.BITMAP_TYPE_ANY).Scale(70,70)
        imgServer = wx.Bitmap(imgServer)
        self.btnClient = wx.BitmapButton(self.mainPanel, -1, imgServer, (100,160),(70,70))
        self.btnClient.Bind(wx.EVT_BUTTON, self.addClient)
        
        self.log.SetBackgroundColour((148,255,106))
        self.log.AppendText("SERVER STARTING...\n")
        self.Refresh()
    
    def stopServer(self,e):
        print("TEST: Stopping Server")
        # HIDES AND SHOWS APPROPRIATE BUTTONS
        self.btnServer.Show()
        self.btnServer2.Hide()
        self.btnClient.Hide()

        self.log.SetBackgroundColour((255,255,255))
        self.log.AppendText("SERVER TERMINATING...\n")
        self.Refresh()

    def addClient(self, e):
        print("TEST: Adding Client")
        # ADDS INSTANCE OF CLIENT FRAME
        clientFrame(None)
        self.log.AppendText("Client Added!\n")

def main():
    app = wx.App()
    mainFrame(None)
    app.MainLoop()

main()