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
# from sqlite_dump import iterdump

imageTypes = {'jpeg':1,'jpg':1,'mkv':1,'mp4':1,'gif':1,'png':1,'webp':1,'svg':1}

def send_csv():
    file = open(selectcsvButton.cget('text'))
    csv_file = csv.DictReader(file)
    loadingLabel.configure(text="Loading....")
    for row in csv_file:
        print(row['Names'],row['Messages'],row['Documents'])
        if (len(row['Names'])>0 and len(row['Documents'])>0):
            ext = str(row['Documents'].split('.')[1])
            ismedia = imageTypes.__contains__(ext)
            print(ismedia)
            if ismedia:
                whats.send_media(to=row['Names'],imagepath=row['Documents'],msg=row['Messages'])
            else:
                whats.send_document(to=row['Names'],docpath=row['Documents'])
                time.sleep(2)
                if len(row['Messages'])>0:
                    whats.send_message(message=row['Messages'],to=row['Names'])

        elif len(row['Names'])>0 and len(row['Messages']):
            whats.send_message(to=row['Names'],message=row['Messages'])
    loadingLabel.configure(text="Completed")
    sendcsvButton.configure(text="Select File")

def send_message():
    try:
        num_or_nameInputStr = num_or_nameInput.get()
        messageInputStr = messageInput.get(1.0,"end-1c")
        checkifLogged()
        if fileSelector.cget('text')!="Select File":
            if os.path.exists(fileSelector.cget('text')):
                ext = str(fileSelector.cget('text').split('.')[1])
                ismedia = imageTypes.__contains__(ext)
                if ismedia:
                    whats.send_media(to=num_or_nameInputStr,imagepath=fileSelector.cget('text'),msg=messageInputStr)
                else:
                    if len(messageInputStr)>0:
                        whats.send_message(message=messageInputStr,to=num_or_nameInputStr)
                    whats.send_document(to=num_or_nameInputStr,docpath=fileSelector.cget('text'))
        elif len(messageInputStr)>0:
            try:
                whats.send_message(message=messageInputStr,to=num_or_nameInputStr)
            except Exception as e:
                print(e)
                raise e
        conn = sql.connect('history.db')
        c = conn.cursor()
        
        c.execute('''INSERT INTO historywhats (nameornum,message,filepath,date) VALUES (?,?,?,?)''',
                    (num_or_nameInputStr,messageInputStr,fileSelector.cget('text') if fileSelector.cget('text')!="Select File" else "",datetime.datetime.now().date().__str__()))
        c.close()
        conn.commit()
        conn.close()
        messagebox.showinfo('Successful','Completed\nSent the message and/or document Successfully')
        print("Successfully sent message {} to {}".format(messageInputStr,num_or_nameInputStr))
        num_or_nameInput.delete("0","end")
        messageInput.delete(1.0,"end")
        fileSelector.configure(text="Select File")
    except Exception as e:
        print(e)
        print("Error in Send_Message\n1. Check if Number or Name is Correct")
        messagebox.showerror("Error in Sending Message","Error in Send_Message\n1. Check if Number or Name is Correct\n2. Check if document exists(if selected any)")
        # raise e


def browseFiles():
    filename = filedialog.askopenfilename(initialdir = "/", title = "Select a File", filetypes = (("Text files","*.txt*"), ("all files", "*.*")))
    fileSelector.configure(text=filename)

def browseCSVfile():
    csvfilename = filedialog.askopenfilename(initialdir = "/", title = "Select a File", filetypes = (("CSV files","*.csv*"), ("all files", "*.*")))
    selectcsvButton.configure(text=csvfilename)

def storeHistory():
    conn = sql.connect('history.db')
    c = conn.cursor()
    
    c.execute('SELECT * FROM historywhats')
    
    file = open('history.csv','w')
    file.writelines(['Names,','Messages,','FilePath,','Date\n'])
    while True:
        batch = c.fetchmany(10)
        if not batch:
            break
        for row in batch:
            for element in row:
                file.write(repr(element)+",")
            file.write("\n")
    
    file.close()
    messagebox.showinfo("Successful","History stored in history.txt")
    c.close()
    conn.commit()
    conn.close()

def table_view():
    conn = sql.connect('history.db')
    c = conn.cursor()
    
    c.execute('SELECT * FROM historywhats')

    tree = ttk.Treeview(tableFrame)
    tree['show']='headings'

    style.configure("Treeview.Heading",foreground="blue",font=('Times New Roman',12,"bold"))

    tree["columns"] = ("Names","Messages","Documents","Date")

    tree.column("Names",width = 50,minwidth=50,anchor = CENTER)
    tree.column("Messages",width = 50,minwidth=50,anchor = CENTER)
    tree.column("Documents",width = 50,minwidth=50,anchor = CENTER)
    tree.column("Date",width = 50,minwidth=50,anchor = CENTER)

    tree.heading("Names",text="Names",anchor = CENTER)
    tree.heading("Messages",text="Messages",anchor = CENTER)
    tree.heading("Documents",text="Documents",anchor = CENTER)
    tree.heading("Date",text="Date",anchor = CENTER)

    i=0
    while True:
        batch = c.fetchmany(10)
        if not batch:
            break
        for row in batch:
            tree.insert('',i,text="",values=(row[0],row[1],row[2],row[3]))
            i=i+1

    horizontalScrollbar = ttk.Scrollbar(tableFrame,orient="horizontal")
    horizontalScrollbar.configure(command=tree.xview)
    tree.configure(xscrollcommand=horizontalScrollbar.set)
    horizontalScrollbar.pack(fill=X,side=BOTTOM)

    verticalScrollbar = ttk.Scrollbar(tableFrame,orient="vertical")
    verticalScrollbar.configure(command=tree.yview)
    tree.configure(yscrollcommand=verticalScrollbar.set)
    verticalScrollbar.pack(fill=Y,side=RIGHT)

    c.close()
    conn.commit()
    conn.close()
    tree.pack(expand=True,fill="both")

# def checkifLogged():
#     if whats._check_valid_qrcode():
#         if os.path.exists("./QRcode.png"):
#             QRcodeimage = ImageTk.PhotoImage(Image.open("./QRcode.png"))
#             QRlabel.configure(image=QRcodeimage,text='')

def showQRcode():
    global QRlabel
    QRcodeimage = ImageTk.PhotoImage(Image.open("./QRcode.png"))
    QRlabel.configure(image=QRcodeimage,text='')
    QRlabel.pack()

def checkifLogged():
    # Not logged in
    small_timeout = 5
    messageShown = False
    while not whats.chrome.element_exists_at(whats.selectors['search_input'], timeout=small_timeout):
        # qrcode = self.chrome.wait_for(self.selectors['qrcode'], timeout=small_timeout)
        elem =  whats.chrome.find_element_by_tag_name("canvas")
        elem.screenshot("./QRcode.png")
        QRcodeimage = ImageTk.PhotoImage(Image.open("./QRcode.png"))
        QRlabel.configure(image=QRcodeimage,text='')
        # self.chrome.screenshot('./qrcode.png')
        if not messageShown:
            messagebox.showinfo("No previous Login","No Previous Session Info\nCheck current directory for QR Code to scan")
            messageShown = True
        print('Look for whatsapp QRCode inside your running directory.')
        time.sleep(small_timeout)

    # QRlabel.configure(text="Logged In Already")
    print('Whatsapp successfully logged in...')


# def checkifLogged2():
#     # Not logged in
#     small_timeout = 5
#     messageShown = False
#     while not whats.chrome.element_exists_at(whats.selectors['search_input'], timeout=small_timeout):
#         # qrcode = self.chrome.wait_for(self.selectors['qrcode'], timeout=small_timeout)
#         elem =  whats.chrome.find_element_by_tag_name("canvas")
#         elem.screenshot("./QRcode.png")
#         QRcodeimage = ImageTk.PhotoImage(Image.open("./QRcode.png"))
#         QRlabel.configure(image=QRcodeimage,text='')
#         # self.chrome.screenshot('./qrcode.png')
#         if not messageShown:
#             messagebox.showinfo("No previous Login","No Previous Session Info\nCheck current directory for QR Code to scan")
#             messageShown = True
#         print('Look for whatsapp QRCode inside your running directory.')
#         time.sleep(small_timeout)

#     # QRlabel.configure(text="Logged In Already",image=None)
#     print('Whatsapp successfully logged in...')

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
        guiwin = Tk()
        guiwin.title('WhatsApp Automator')
        guiwin.geometry("800x600")
        style = ttk.Style(guiwin)
        style.theme_use("xpnative")
        mainFrame = Frame(guiwin)
        customSendParentFrame = LabelFrame(mainFrame,text="Custom Send Parent Frame")

        customSendFrame = LabelFrame(customSendParentFrame,text="Custom Send Message and/or Documents or Media")
        customSendQRFrame = LabelFrame(customSendParentFrame,text="QRCode")
        csvsendFrame = LabelFrame(mainFrame,text="Send From CSV File")
        historyFrame = LabelFrame(mainFrame,text="History Handler")
        tableFrame = LabelFrame(mainFrame,text="Table")

        def on_closing():
            whats.chrome.quit()
            guiwin.destroy()
        guiwin.protocol("WM_DELETE_WINDOW", on_closing)
        num_or_nameLabel = Label(customSendFrame,text="Enter Name or Number: ")
        num_or_nameInput = Entry(customSendFrame,width=30)
        messageLabel = Label(customSendFrame,text="Enter Message: ")
        messageInput = Text(customSendFrame,height=10,width=30)
        fileSelector = Button(customSendFrame,command=browseFiles,text="Select File")
        submitButton = Button(customSendFrame,text="Send Message",command=send_message)
        
        QRlabel = Label(customSendQRFrame,text="Session")
        QRlabel.pack()
        # checkQRButton = Button(customSendQRFrame,text="Check if Logged in",command=checkifLogged)
        # checkQRButton.pack()
        # if whats._check_valid_qrcode():
        #     if os.path.exists("./QRcode.png"):
        #         QRcodeimage = ImageTk.PhotoImage(Image.open("./QRcode.png"))
        #         QRlabel.configure(image=QRcodeimage,text='')

        separator = Separator(customSendFrame,orient="horizontal")

        csvsendLabel = Label(csvsendFrame,text="Send Messages using a CSV file")
        selectcsvButton = Button(csvsendFrame,text="Select CSV file",command=browseCSVfile)
        sendcsvButton = Button(csvsendFrame,text="Send from CSV file",command=send_csv)
        loadingLabel = Label(csvsendFrame,text="")

        historyButton = Button(historyFrame,text="Show History",padding=1,command=table_view)

        num_or_nameLabel.grid(row=0,column=0)
        num_or_nameInput.grid(row=0,column=1)
        messageLabel.grid(row=1,column=0)
        messageInput.grid(row=1,column=1)
        fileSelector.grid(row=2,column=0)
        submitButton.grid(row=2,column=1)
        separator.grid(row=3,columnspan=1)
        csvsendLabel.grid(row=5,column=0)
        selectcsvButton.grid(row=5,column=1)
        sendcsvButton.grid(row=6,column=1)
        loadingLabel.grid(row=7,column=1)
        historyButton.grid(row=7,column=0)

        
        customSendFrame.grid(row=0,column=0)
        customSendQRFrame.grid(row=0,column=1)
        customSendParentFrame.pack(fill="both",expand="yes")
        csvsendFrame.pack(expand="yes",fill="both")
        historyFrame.pack(expand="yes",fill="both")
        tableFrame.pack(expand="yes",fill="both")

        mainFrame.pack(fill="both",expand="yes",padx=10,pady=10)
        
        guiwin.mainloop()
        checkifLogged()
        # time.sleep(5)
        # whats.chrome.quit()

    except Exception as e:
        print(e)
        whats.chrome.quit()
    finally:
        whats.chrome.quit()

    

