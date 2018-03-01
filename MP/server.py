import wx
import sys
import socket
import time
import threading

class serverFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(serverFrame, self).__init__(*args, **kwargs)
        self.initialize()
    
    def initialize(self):
        # ~AESTHETICS~
        self.SetSize(315,500)
        self.mainPanel = wx.Panel(self)
        self.mainFont = wx.Font(20,wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.SetBackgroundColour("WHITE")
        self.defaultLog = "***************SERVER LOG****************\n"

        # ADD HEADER PHOTO
        imgHeader = wx.Image("rsrcs/header2_1.jpg", wx.BITMAP_TYPE_ANY).Scale(315,130)
        imgHeader = wx.Bitmap(imgHeader)
        self.header = wx.StaticBitmap(self.mainPanel, -1, imgHeader, (0,0), (315,130))

        # ADD SERVER BUTTON (OFF)
        imgServer = wx.Image("rsrcs/serverButton-1.jpg", wx.BITMAP_TYPE_ANY).Scale(60,60)
        imgServer = wx.Bitmap(imgServer)
        self.btnServer = wx.BitmapButton(self.mainPanel, -1, imgServer, (20,130),(60,60))
        self.btnServer.Bind(wx.EVT_BUTTON,self.startServer)

        # ADD QUIT BUTTON
        imgServer = wx.Image("rsrcs/quitButton.jpg", wx.BITMAP_TYPE_ANY).Scale(30,30)
        imgServer = wx.Bitmap(imgServer)
        self.btnQuit = wx.BitmapButton(self.mainPanel, -1, imgServer, (80,130),(30,30))
        self.btnQuit.Bind(wx.EVT_BUTTON, self.Quit)

        # ADD CLEAR BUTTON
        imgServer = wx.Image("rsrcs/clearButton.jpg", wx.BITMAP_TYPE_ANY).Scale(30,30)
        imgServer = wx.Bitmap(imgServer)
        self.btnClear = wx.BitmapButton(self.mainPanel, -1, imgServer, (80,160),(30,30))
        self.btnClear.Bind(wx.EVT_BUTTON, self.Clear)

        # ADD PREFERRED BUTTON
        imgServer = wx.Image("rsrcs/savePreferences.jpg", wx.BITMAP_TYPE_ANY).Scale(30,30)
        imgServer = wx.Bitmap(imgServer)
        self.preferredButton = wx.BitmapButton(self.mainPanel, -1, imgServer, (110,130),(30,30))
        self.preferredButton.Bind(wx.EVT_BUTTON, self.setPreferredPort)

        # INITIALIZE LOG AS UNEDITABLE TEXT FIELD
        self.log = wx.TextCtrl(self.mainPanel, style = wx.TE_READONLY | wx.TE_MULTILINE, pos=(0,200), size=(300,270))
        self.log.SetValue(self.defaultLog)
        
        self.SetTitle("Main Server")
        self.Center()
        self.Show()

    def setPreferredPort(self, e):
        portBox = wx.TextEntryDialog(None, "Type selected port", "Port Preferrence", '')
        if portBox.ShowModal() == wx.ID_OK:
            file = open("preferredPort.txt", "w")
            file.write(portBox.GetValue())
            file.close()
        
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
        self.preferredButton.Hide()

        # ADD SERVER BUTTON (ON)
        imgServer = wx.Image("rsrcs/serverButton-2.jpg", wx.BITMAP_TYPE_ANY).Scale(60,60)
        imgServer = wx.Bitmap(imgServer)
        self.btnServer2 = wx.BitmapButton(self.mainPanel, -1, imgServer, (20,130),(60,60))
        self.btnServer2.Bind(wx.EVT_BUTTON, self.stopServer)

        '''
        # ADD CLIENT BUTTON
        imgServer = wx.Image("rsrcs/clientAdd-1.jpg", wx.BITMAP_TYPE_ANY).Scale(70,70)
        imgServer = wx.Bitmap(imgServer)
        self.btnClient = wx.BitmapButton(self.mainPanel, -1, imgServer, (100,160),(70,70))
        self.btnClient.Bind(wx.EVT_BUTTON, self.addClient)
        '''

        file = open("preferredPort.txt", "r")
        temp = file.readline()
        
        if temp!= '':
            self.port = int(temp)
            file.close()
        else:
            portBox = wx.TextEntryDialog(None, "Start server on which port?", "Port Selection", '')
            if portBox.ShowModal() == wx.ID_OK:
                self.port = int(portBox.GetValue())
        
        self.log.SetBackgroundColour((148,255,106))
        self.log.AppendText("SERVER STARTING ON PORT " + str(self.port) + "\n")
        self.Refresh()

        

        # SERVER SHIT
        self.host = '127.0.0.1'
        # local host
        #self.port = 5000
        self.clients = []
        #added code
        self.names = {}
        self.aliases = []
        
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind((self.host,self.port))
        self.s.setblocking(0)

        self.quitting = False
        self.tlock = threading.Lock()

        # THREAD 1
        self.sT = threading.Thread(target=self.running, args=("ServerThread", self.s))
        self.sT.setDaemon(True)
        self.sT.start()

        # THREAD 2 (TIMER)
        
        #self.running2()
    
    def running(self, name, sock):
        # THREAD
        while not self.quitting:
            try:
                self.tlock.acquire()
                data, addr = self.s.recvfrom(1024)
            
                #added code
                data = str(data.decode())
            
                if "@@connected"  in data and " -> " not in data:
                    name = data.split("@@connected ")[1]
                    receiver = "Global"
                    data = name + " has joined Zirk chat"
                elif "@@initlist " in data and " -> " not in data:
                    name = data.split("@@initlist ")[1]
                    receiver = name
                    data = "@@initlist "
                elif " -> " in data:
                    name = data.split(" -> ")[0]
                    receiver = data.split(" -> ")[1].split(": ")[0]
            
                if addr not in self.clients:
                    self.clients.append(addr)
                
                #added code
                if addr not in self.names:
                    self.names[addr] = name
            
                if "@@disconnected" in data and " -> " not in data:
                    name = data.split("@@disconnected ")[1]
                    receiver = "Global"
                    data = name + " has disconnected"
                    for client in self.clients:
                        if (self.names[client] == name):
                            del self.names[client]
                            self.aliases.remove(name)
                            self.clients.remove(client)
                            break
                else:
                    if name not in self.aliases:
                        self.aliases.append(name)
            
                self.log.AppendText(time.ctime(time.time()) + str(addr) + ": :" + str(data) + "\n")
                # SENDS TO EVERYONE
                if (receiver == "Global"):
                    for client in self.clients:
                        self.s.sendto(data.encode('utf-8'), client)
                        print(str(data) + " SENT")
                else:
                    if "@@initlist " in data and " -> " not in data:
                        for client in self.clients:
                            if (self.names[client] == receiver or self.names[client] == name):
                                for i in self.aliases:
                                    self.s.sendto((data + i).encode('utf-8'), client)
                                    print(str(data)+i + " SENT")
                                break

                    else:
                        for client in self.clients:
                            if (self.names[client] == receiver or self.names[client] == name):
                                self.s.sendto(data.encode('utf-8'), client)
                                print(str(data) + " SENT")
            except:
                pass
            finally:
                self.tlock.release()
    
    def running2(self):
        self.sT = threading.Timer(.1, self.running2)
        self.sT.setDaemon(True)
        self.sT.start()
        try:
            self.tlock.acquire()
            data, addr = self.s.recvfrom(1024)
            
            #added code
            data = str(data)
            data = data[2:]
            data = data[:-1]

            
            if "@@connected"  in data and " -> " not in data:
                name = data.split("@@connected ")[1]
                receiver = "Global"
                data = name + " has joined Zirk chat"
            
            
            elif " -> " in data:
                name = data.split(" -> ")[0]
                receiver = data.split(" -> ")[1].split(": ")[0]
            
            if addr not in self.clients:
                self.clients.append(addr)
                
            #added code
            if addr not in self.names:
                self.names[addr] = name
            
            if "@@disconnected" in data and " -> " not in data:
                name = data.split("@@disconnected ")[1]
                receiver = "Global"
                data = name + " has disconnected"
                for client in self.clients:
                    if (self.names[client] == name):
                        del self.names[client]
                        self.aliases.remove(name)
                        self.clients.remove(client)
                        break
            else:
                if name not in self.aliases:
                    self.aliases.append(name)
            
            self.log.AppendText(time.ctime(time.time()) + str(addr) + ": :" + str(data) + "\n")
            print(name)
            print(receiver)
            # SENDS TO EVERYONE
            if (receiver == "Global"):
                for client in self.clients:
                    self.s.sendto(data.encode('utf-8'), client)
                    print(str(data) + " SENT")
            else:
                for client in self.clients:
                    if (self.names[client] == receiver or self.names[client] == name):
                        self.s.sendto(data.encode('utf-8'), client)
                        print(str(data) + " SENT")
        except:
            pass
        finally:
            self.tlock.release()
        self.Refresh()

    def stopServer(self,e):
        # HIDES AND SHOWS APPROPRIATE BUTTONS
        self.btnServer.Show()
        self.btnServer2.Hide()
        self.preferredButton.Show()

        # SHUTS SERVER DOWN, CLOSES THREAD
        self.quitting = True
        self.s.close()

        self.log.SetBackgroundColour((255,255,255))
        self.log.AppendText("SERVER TERMINATING...\n")
        self.Refresh()

    def getAliases(self):
        return self.aliases

def main():
    app = wx.App()
    serverFrame(None)
    app.MainLoop()
