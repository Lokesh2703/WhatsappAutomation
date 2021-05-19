from sqlite3.dbapi2 import connect
from time import time
from whatspy import whatsapp
import csv
import time
import os
from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog
from tkinter import messagebox
import sqlite3 as sql
import datetime
from tkinter import ttk
from PIL import ImageTk, Image
import threading
import pandas as pd
# from sqlite_dump import iterdump

imageTypes = {'jpeg':1,'jpg':1,'mkv':1,'mp4':1,'gif':1,'png':1,'webp':1,'svg':1}

def send_message():
    try:
        # num_or_nameInputStr = num_or_nameInput.get()
        num_or_nameInputStr = num_or_name
        messageInputStr = message
        # messageInputStr = messageInput.get(1.0,"end-1c")
        loggedin = threading.Thread(target=checkifLogged)
        loggedin.start()
        loggedin.join()
        
        if len(filepath)>0:
            ext = str(filepath.split('.')[1])
            ismedia = imageTypes.__contains__(ext)
            if ismedia:
                whats.send_media(to=num_or_nameInputStr,imagepath=filepath,msg=messageInputStr)
            else:
                if len(messageInputStr)>0:
                    whats.send_message(message=messageInputStr,to=num_or_nameInputStr)
                whats.send_document(to=num_or_nameInputStr,docpath=filepath)

        elif len(messageInputStr)>0:
            try:
                whats.send_message(message=messageInputStr,to=num_or_nameInputStr)
            except Exception as e:
                # print(e)
                return

        conn = sql.connect('history.db')
        c = conn.cursor()
        
        c.execute('''INSERT INTO historywhats (nameornum,message,filepath,date) VALUES (?,?,?,?)''',
                    (num_or_nameInputStr,messageInputStr,filepath,datetime.datetime.now().date().__str__()))
        c.close()
        conn.commit()
        conn.close()
        # messagebox.showinfo('Successful','Completed\nSent the message and/or document Successfully')
        print("Successfully sent message {} to {}".format(messageInputStr,num_or_nameInputStr))
        # num_or_nameInput.delete("0","end")
        # messageInput.delete(1.0,"end")
        # fileSelector.configure(text="Select File")
    except Exception as e:
        print(e)
        print("Error in Send_Message\n1. Check if Number or Name is Correct")


QRlabel = None
guiwin = None

def displayQR():
    global QRlabel,guiwin
    small_timeout = 5
    messageShown = False
    while not whats.chrome.element_exists_at(whats.selectors['search_input'], timeout=small_timeout):
        # qrcode = self.chrome.wait_for(self.selectors['qrcode'], timeout=small_timeout)
        elem =  whats.chrome.find_element_by_tag_name("canvas")
        elem.screenshot("./QRcode.png")
        QRcodeimage = ImageTk.PhotoImage(Image.open("./QRcode.png"))
        print("Scan")
        QRlabel.configure(image=QRcodeimage,text='')
        # self.chrome.screenshot('./qrcode.png')
        if not messageShown:
            messagebox.showinfo("No previous Login","No Previous Session Info\nCheck current directory for QR Code to scan")
            messageShown = True
        print('Look for whatsapp QRCode inside your running directory.')
        time.sleep(small_timeout)
    guiwin.destroy()
    print('Whatsapp successfully logged in...')
# def threadQR():
#     displayQRThread = threading.Thread(target=displayQR)
#     displayQRThread.start()
#     displayQRThread.join()

def checkifLogged():
    # Not logged in
    global QRlabel,guiwin
    small_timeout = 5
    messageShown = False
    if not whats.chrome.element_exists_at(whats.selectors['search_input'], timeout=small_timeout):
        guiwin = Tk()
        guiwin.title('WhatsApp Automator')
        guiwin.geometry("800x600")
        def on_closing():
            whats.chrome.quit()
            guiwin.destroy()
        guiwin.protocol("WM_DELETE_WINDOW", on_closing)
        mainFrame = Frame(guiwin)
        customSendQRFrame = LabelFrame(mainFrame,text="QRCode")
        QRlabel = Label(customSendQRFrame,text="Session")
        QRlabel.pack()
        customSendQRFrame.pack(fill="both",expand="yes")
        displayQRcode = Button(guiwin,text = "Display QR",command=displayQR)
        displayQRcode.pack()
        
        mainFrame.pack(fill="both",expand="yes")
        
        guiwin.mainloop()

def displaydatabase():
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)
    conn = sql.connect('history.db')
    # c = conn.cursor()
    
    # for chunk  in read_sql_query('SELECT * FROM historywhats',conn,chunksize=2):
    #     print(chunk)
    print(pd.read_sql_query('SELECT * FROM historywhats',conn))
    print('\n\n')
    conn.close()

def clear():
  
    # for windows
    if os.name == 'nt':
        _ = os.system('cls')
  
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = os.system('clear')

if __name__ == '__main__':
    
    try:
        whats = whatsapp.Whatsapp()
        conn = sql.connect('history.db')
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='historywhats';")
        
        try:
            if c.fetchone()[0]==1:
                print("Table Exists")
        except Exception as e:
            c.execute("""CREATE TABLE historywhats (
                nameornum text,
                message text,
                filepath text,
                date text
            )""")

        conn.commit()
        conn.close()
        clear()
        while True:
            choice = int(input("Choose an Option:\n1. Display the history.\n2. Send a message.\n3. Exit\nEnter the choice: "))
            if choice==1:
                displaydatabase()
            elif choice==2:
                num_or_name = input("Enter the name or number: ")
                message = input("Enter the message(newline are replaced by commmas) : ")
                filepath = input("Enter the path of the file with extension(Press Enter for no file input): ")
                while len(filepath)>0 and not (os.path.exists(filepath) and os.path.isfile(filepath)):
                    print("PATH is incorrect!")
                    filepath = input("Enter the CORRECT path of the file with extension(Press Enter for no file input): ")
                
                send_message()
            elif choice==3:
                whats.chrome.quit()
                exit()

    except Exception as e:
        print(e)
        whats.chrome.quit()
    finally:
        whats.chrome.quit()

    

