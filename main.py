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

def send_message():
    num_or_nameInputStr = num_or_nameInput.get()
    messageInputStr = messageInput.get(1.0,"end-1c")
    if fileSelector.cget('text')!="Select File":
        if os.path.exists(fileSelector.cget('text')):
            ext = str(fileSelector.cget('text').split('.')[1])
            ismedia = imageTypes.__contains__(ext)
            print(ismedia)
            if ismedia:
                whats.send_media(to=num_or_nameInputStr,imagepath=fileSelector.cget('text'),msg=messageInputStr)
            else:
                if len(messageInputStr)>0:
                    whats.send_message(message=messageInputStr,to=num_or_nameInputStr)
                whats.send_document(to=num_or_nameInputStr,docpath=fileSelector.cget('text'))
    elif len(messageInputStr)>0:
        whats.send_message(message=messageInputStr,to=num_or_nameInputStr)
    conn = sql.connect('history.db')
    c = conn.cursor()
    
    c.execute('''INSERT INTO historywhats (nameornum,message,filepath,date) VALUES (?,?,?,?)''',
                (num_or_nameInputStr,messageInputStr,fileSelector.cget('text') if fileSelector.cget('text')!="Select File" else "",datetime.datetime.now().date().__str__()))
    c.close()
    conn.commit()
    conn.close()
    messagebox.showinfo('Successful','Completed\nSent the message and/or document Successfully')
    print("Successfully sent message {} to {}".format(messageInputStr,num_or_nameInputStr))


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

        customSendFrame = LabelFrame(guiwin,text="Custom Send Message and/or Documents or Media")

        def on_closing():
            # whats.chrome.quit()
            guiwin.destroy()
        guiwin.protocol("WM_DELETE_WINDOW", on_closing)
        num_or_nameLabel = Label(customSendFrame,text="Enter Name or Number: ")
        num_or_nameInput = Entry(customSendFrame,width=30)
        messageLabel = Label(customSendFrame,text="Enter Message: ")
        messageInput = Text(customSendFrame,height=10,width=30)
        fileSelector = Button(customSendFrame,command=browseFiles,text="Select File")
        submitButton = Button(customSendFrame,text="Send Message",command=send_message)
        
        separator = Separator(customSendFrame,orient="horizontal")

        csvsendLabel = Label(customSendFrame,text="Send Messages using a CSV file")
        selectcsvButton = Button(customSendFrame,text="Select CSV file",command=browseCSVfile)
        sendcsvButton = Button(customSendFrame,text="Send from CSV file",command=send_csv)
        loadingLabel = Label(customSendFrame,text="")

        historyButton = Button(customSendFrame,text="Store History",padding=1,command=storeHistory)

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

        customSendFrame.pack()
        guiwin.mainloop()
        # time.sleep(5)
        whats.chrome.quit()

    except Exception as e:
        print(e)
        whats.chrome.quit()
    finally:
        whats.chrome.quit()

    

