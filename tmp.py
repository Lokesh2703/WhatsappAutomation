from os import write
import time
import autoit
# import logging

if __name__ == '__main__':
    print("Lokesh")
    inp = input("Enter ur name: ")
    print(inp)
    time.sleep(7)
    try:
        autoit.run("C:\\Windows\\SystemApps\\Microsoft.Windows.FileExplorer_cw5n1h2txyewy\\FileExplorer.exe")
    except Exception as e:
        file = open("./error.txt")
        file.write(e)