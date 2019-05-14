import pyautogui
import asyncio
import sys
import pygame
import random
import time
import win32gui
import win32api
import mss
import mss.tools

from typing import Callable
from screeninfo import get_monitors
from selenium import webdriver
from bs4 import BeautifulSoup


TRIALS = 10 ** 5

driver = webdriver.Chrome(executable_path='C:/chromedriver.exe')

driver.get('file:///C:/aoeai/SR/browserTest.html')
# def fun(str):
#     print(str)

# async def lll(seconds: float, fun: Callable, inp):
#     '''
#     Lay-Low Loop:
#     Input seconds.
#     Runs the inputted function after x seconds and loops every x seconds indefinitely.
#     '''
#     while True:
#         fun(inp)
#         await asyncio.sleep(seconds)

# async def main():
#     await asyncio.gather(
#         lll(.6, fun, "Oh"), 
#         lll(.2, fun, "Yeah!")
# #         )

hdc= win32gui.GetDC(0)
def moveTo(x: int, y: int):
    pyautogui.moveTo(x, y)

def moveToRel(x: int, y: int):
     pyautogui.moveRel(x, y)

def getScreenDims():
    info = pygame.display.Info()
    width = info.current_w
    height = info.current_h
    print(width, height)
    return width, height
    #218649568

if __name__ == "__main__":
    with mss.mss() as sct:
        pygame.init()
        width, height = getScreenDims()
        file = open("coords", "a+")
        finished = False
        n = 1
        time.sleep(6) # Get situated!
        # monitor = {"top": 100, "left": 1664, "width": 256, "height": 256}
        monitor = {"top": 100, "left": 1109, "width": 256, "height": 256}
        while n <= TRIALS:
            # x = random.randint(1664,1920)
            # y = random.randint(100,356)
            x = random.randint(1109,1363)
            y = random.randint(100,356)
            #x = 1750
            #y = 200
            # The screen part to capture
            # Grab the data
            sct_img = sct.grab(monitor)
            output = "s-{n}.png".format(n=n)
            mss.tools.to_png(sct_img.rgb, sct_img.size, output=output)
            #pyautogui.screenshot(output,region=(1664,100, 256, 256))
            time.sleep(0.1)
            moveTo(x,y)
           
            pyautogui.click()  
            timeStamp = time.strftime('%H-%M-%S')
            x = x - 1109
            y = y - 100
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            evolving = soup.find(id="evolving_value").get_text()
            file.write(timeStamp+":"+str(n)+":"+str(x)+","+str(y)+","+str(evolving)+"\n")
            print(output)        
            time.sleep(0.3)
            n+=1
        file.close()
    # asyncio.run(main())