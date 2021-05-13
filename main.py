from time import time
from whatspy import whatsapp
# import autoit
import csv
import time

def send_csv(filepath):
    file = open(filepath)
    csv_file = csv.reader(file)
    namesList = list(csv_file)
    for row in namesList[1:]:
        # print("Row: ",row[1],row[0])
        # whats.send(row[1],row[0])
        pass
        
if __name__ == '__main__':
    # path = input("Enter the filepath(with Extension): ")
    # send_csv("names.csv")
    whats = whatsapp.Whatsapp()
    # whats.send_message(message="Hlo Lokesh",to="918096600117")
    # print("Sent!!")
    imagepath = 'C:\\Users\\lokes\\Videos\\Pexels Videos 2035509.mp4'
    docPath = 'C:\\Users\\lokes\\Desktop\\Lokesh_Resume_LateX.pdf'
    # whats.send_image("Lokesh Airtel 1",imagepath)
    # whats.chrome.quit()
    # whats.search_unknown_contact("918096600117")
    whats.send_media(imagepath=imagepath,to="918096600117")
    # whats.send_document(to="918096600117",docpath=docPath)



    time.sleep(5)
    whats.chrome.quit()
