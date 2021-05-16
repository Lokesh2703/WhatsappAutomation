from selenium import webdriver
from datetime import datetime
from time import sleep
import traceback
import time
from tkinter import messagebox
from main import showQRcode

from .chrome import Chrome
# from .remote import ChromeRemote

class Whatsapp:
    
    def __init__(self):
        self.selectors = {
            'qrcode': 'canvas',
            'search_input':  '#side .copyable-text.selectable-text',
            'search_result': '#side span[title="{}"]',
            'message_input': '#main footer div.copyable-text.selectable-text',
            'message_send':  '#main footer button span[data-icon="send"]',
            'pin_icon' : '#main footer div[title="Attach"]',
            'media_button' : '#main footer li:nth-child(1) button input[type=file]',
            'media_send_button' : '#app > div._3h3LX._34ybp.app-wrapper-web.font-fix.os-mac > div._3QfZd.two > div.Akuo4 > div._1Flk2._1sFTb > span > div._1sMV6 > span > div:nth-child(1) > div > div._36Jt6.tEF8N > span > div',
            'document_button' : '#main footer li:nth-child(3) button input[type=file]',
            'document_send_button' : '#app > div._3h3LX._34ybp.app-wrapper-web.font-fix.os-mac > div._3QfZd.two > div.Akuo4 > div._1Flk2._1sFTb > span > div._1sMV6 > span > div:nth-child(1) > div > div._36Jt6.tEF8N > span > div > div',
            'media_message_input' : '#app > div._3h3LX._34ybp.app-wrapper-web.font-fix.os-mac > div._3QfZd.two > div.Akuo4 > div._1Flk2._1sFTb > span > div._1sMV6 > span > div:nth-child(1) > div > div._36Jt6.tEF8N > div._3S8qa > span > div > div._2HlOc > div > div.UQ0S6 > div._1JAUF._3to_-._3Foy4 > div._2_1wd.copyable-text.selectable-text'
        }
        
        url = 'http://web.whatsapp.com'

        self.link = "https://web.whatsapp.com/send?phone={}&text&source&data&app_absent"
        
        self.chrome = Chrome.instance
        
        if self.chrome.current_url != url:
            self.chrome.get(url)
        
        
    def _ensure_page_load(self):
        pass
        
    def _check_valid_qrcode(self):
        # Not logged in
        small_timeout = 5
        messageShown = False
        while not self.chrome.element_exists_at(self.selectors['search_input'], timeout=small_timeout):
            # qrcode = self.chrome.wait_for(self.selectors['qrcode'], timeout=small_timeout)
            elem =  self.chrome.find_element_by_tag_name("canvas")
            elem.screenshot("./QRcode.png")
            # try:
            #     showQRcode()
            # except Exception as e:
            #     print(e)
            #     print("Error in showQRcode")
                # raise e
            # self.chrome.screenshot('./qrcode.png')
            if not messageShown:
                messagebox.showinfo("No previous Login","No Previous Session Info\nCheck current directory for QR Code to scan")
                messageShown = True
            print('Look for whatsapp QRCode inside your running directory.')
            sleep(small_timeout)
        
        print('Whatsapp successfully logged in...')
        self.chrome.screenshot('./1.png')

    def _search_for_chat(self, to):
        self.chrome.wait_for(self.selectors['search_input']).send_keys(to)
        self.chrome.wait_for(self.selectors['search_result'].format(to)).click()
        self.chrome.screenshot('./2.png')
    
    def _type_message(self, message):
        self.chrome.wait_for(self.selectors['message_input']).send_keys(message + '\n')
        # self.chrome.wait_for(selectors['message_send']).click()  # replaced by '\n' on previous line
        self.chrome.screenshot('./3.png')
    
    def send_message(self, message, to):
        
        try:
            try:
                self._check_valid_qrcode()
            except Exception as e:
                print('An Error in checking Validation')
                raise e
            try:
                if to.isdigit():
                    self._search_unknown_contact(to)
                else:
                    self._search_for_chat(to)   
            except Exception as e:
                print('Error in searching for Chat')
                raise e
            try:
                self._type_message(message)
            except Exception as e:
                print('Error in Typing Message or Number not Found')
                raise e
            
            
        except Exception as e:
            print('An unexpected error occured.')
            self.chrome.screenshot('./error.png')
            # self.chrome.quit()
            
            raise e
            
            
    def load_chats(self):
        '''
            return a triple (name, timestamp) for every chat open
        '''
        return_chats = []
        sel = '#pane-side'
        
        timeout = 15
        chatbox = self.chrome.wait_for('#pane-side', timeout=timeout)
        chats = chatbox.find_elements_by_css_selector('div[tabindex]')
        
        self.chrome.screenshot('./4.png')
        
        # print('chats', chats)
        for chat in chats:
            # print('---')
            items = chat.text.split('\n')
            # print(chat.text)
            print(items[1], items[0])
            return_chats.append( (items[1], items[0]) )

    def send_media(self,to,imagepath,msg=""):
        try:
            self._check_valid_qrcode()
            if to.isdigit():
                self._search_unknown_contact(to)
            else:
                self._search_for_chat(to)
        except Exception as e:
            print(e)
        try:
            # self.chrome.find_element_by_css_selector('#main > footer > div.vR1LG._3wXwX.copyable-area > div.EBaI7._23e-h > div._2C9f1 > div > div').click()
            self.chrome.wait_for(self.selectors['pin_icon']).click()
        except:
            traceback.print_exc()
        
        try:
            self.chrome.find_element_by_css_selector(self.selectors['media_button']).send_keys(imagepath)
        except:
            traceback.print_exc() 
        time.sleep(3)
        self.chrome.wait_for(self.selectors['media_message_input']).send_keys(msg)
        self.chrome.wait_for(self.selectors['media_send_button']).click()
        time.sleep(3)

    def _search_unknown_contact(self,number):
        try:
            self._check_valid_qrcode()
            self.chrome.get(self.link.format(number))
        except Exception as e:
            print(e)
            return

    def send_document(self,to,docpath):
        try:
            self._check_valid_qrcode()
            if to.isdigit():
                self._search_unknown_contact(to)
            else:
                self._search_for_chat(to)
        except Exception as e:
            print(e)
        
        try:
            # self.chrome.find_element_by_css_selector('#main > footer > div.vR1LG._3wXwX.copyable-area > div.EBaI7._23e-h > div._2C9f1 > div > div').click()
            self.chrome.wait_for(self.selectors['pin_icon']).click()
        except:
            traceback.print_exc()
        try:
            self.chrome.find_element_by_css_selector(self.selectors['document_button']).send_keys(docpath)
        except:
            traceback.print_exc()

        time.sleep(2)
        self.chrome.wait_for(self.selectors['document_send_button']).click()
        time.sleep(3)
        print('File Sent!')



if __name__ == '__main__':
    message = 'whatsapp-bot ' + str(datetime.now())
    to = '911234567890'
    
    whats = Whatsapp()
    whats.send_message(message, to)
    # whats.load_chats()
    