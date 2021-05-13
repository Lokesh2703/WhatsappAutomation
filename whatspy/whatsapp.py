from selenium import webdriver
from datetime import datetime
from time import sleep
import traceback
import time
import autoit

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
            'media_button' : '#main footer li:nth-child(1) button',
            'media_send_button' : '#app > div._3h3LX._34ybp.app-wrapper-web.font-fix.os-mac > div._3QfZd.two > div.Akuo4 > div._1Flk2._1sFTb > span > div._1sMV6 > span > div:nth-child(1) > div > div._36Jt6.tEF8N > span > div',
            'document_button' : '#main > footer > div.vR1LG._3wXwX.copyable-area > div.EBaI7._23e-h > div._2C9f1 > div > span > div._1ld-u > div > ul > li:nth-child(3) > button',
            'document_send_button' : '#app > div._3h3LX._34ybp.app-wrapper-web.font-fix.os-mac > div._3QfZd.two > div.Akuo4 > div._1Flk2._1sFTb > span > div._1sMV6 > span > div:nth-child(1) > div > div._36Jt6.tEF8N > span > div > div',
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
        while not self.chrome.element_exists_at(self.selectors['search_input'], timeout=small_timeout):
            qrcode = self.chrome.wait_for(self.selectors['qrcode'], timeout=small_timeout)
            self.chrome.screenshot('screens/qrcode.png')
            
            print('Look for whatsapp QRCode inside your running directory.')
            sleep(small_timeout)
        
        print('Whatsapp successfully logged in...')
        self.chrome.screenshot('screens/1.png')

    def _search_for_chat(self, to):
        self.chrome.wait_for(self.selectors['search_input']).send_keys(to)
        self.chrome.wait_for(self.selectors['search_result'].format(to)).click()
        self.chrome.screenshot('screens/2.png')
    
    def _type_message(self, message):
        self.chrome.wait_for(self.selectors['message_input']).send_keys(message + '\n')
        # self.chrome.wait_for(selectors['message_send']).click()  # replaced by '\n' on previous line
        self.chrome.screenshot('screens/3.png')
    
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
                print('Error in Typing Message')
                raise e
            
            
        except Exception as e:
            print('An unexpected error occured. Quiting chrome now')
            self.chrome.screenshot('screens/error.png')
            self.chrome.quit()
            
            # raise e
            
            
    def load_chats(self):
        '''
            return a triple (name, timestamp) for every chat open
        '''
        return_chats = []
        sel = '#pane-side'
        
        timeout = 15
        chatbox = self.chrome.wait_for('#pane-side', timeout=timeout)
        chats = chatbox.find_elements_by_css_selector('div[tabindex]')
        
        self.chrome.screenshot('screens/4.png')
        
        # print('chats', chats)
        for chat in chats:
            # print('---')
            items = chat.text.split('\n')
            # print(chat.text)
            print(items[1], items[0])
            return_chats.append( (items[1], items[0]) )

    def send_media(self,to,imagepath):
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
            self.chrome.wait_for(self.selectors['media_button']).click()
        except:
            traceback.print_exc() 
        time.sleep(3)
        autoit.control_focus("Open", "Edit1")
        autoit.control_set_text("Open", "Edit1", imagepath)
        autoit.control_click("Open", "Button1")
        self.chrome.wait_for(self.selectors['media_send_button']).click()

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
            self.chrome.wait_for(self.selectors['document_button']).click()
        except:
            traceback.print_exc()

        time.sleep(3)
        autoit.control_focus("Open", "Edit1")
        autoit.control_set_text("Open", "Edit1", docpath)
        autoit.control_click("Open", "Button1")
        self.chrome.wait_for(self.selectors['document_send_button']).click()
        time.sleep(3)
        print('File Sent!')



if __name__ == '__main__':
    message = 'whatsapp-bot ' + str(datetime.now())
    to = '918096600117'
    
    whats = Whatsapp()
    whats.send_message(message, to)
    # whats.load_chats()
    