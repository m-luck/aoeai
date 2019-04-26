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


TRIALS = 10

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
    pygame.init()
    width, height = getScreenDims()
    file = open("coords", "a+")
    finished = False
    n = 1
    while n <= TRIALS and finished == False:
        x = random.randint(1109,1365)
        y = random.randint(100,355)
        moveTo(x,y)
        pyautogui.click()  
        time.sleep(1)
        win32gui.Rectangle(hdc, 1109, 100, 1113, 356) # Left Top Right Bottom
        win32gui.Rectangle(hdc, 1109, 100, 1365, 105) # Left Top Right Bottom
        win32gui.Rectangle(hdc, 1109, 357, 1365, 359) # Left Top Right Bottom
        timeStamp = time.strftime('%H-%M-%S')
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        evolving = soup.find(id="evolving_value").get_text()
        x = x - 1109
        y = y - 100
        with mss.mss() as sct:
            # The screen part to capture
            monitor = {"top": 100, "left": 1109, "width": 256, "height": 256}
            output = "s-{t}_{n}_{x}-{y}-{e}.png".format(**monitor, n=n, t=timeStamp, x=x, y=y, e=evolving)
            # Grab the data
            sct_img = sct.grab(monitor)
            # Save to the picture file
            mss.tools.to_png(sct_img.rgb, sct_img.size, output=output)
            print(output)        
        file.write(timeStamp+":"+str(n)+":"+str(x)+","+str(y)+","+str(evolving)+"\n")
        n+=1
    file.close()
    # asyncio.run(main())