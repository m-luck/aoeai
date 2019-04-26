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


TRIALS = 10
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

if __name__ == "__main__":
    pygame.init()
    width, height = getScreenDims()
    file = open("coords", "a+")
    finished = False
    n = 1
    while n <= TRIALS and finished == False:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                finished = True
        x = random.randint(1,width)
        y = random.randint(1,height)
        moveTo(x,y)
        time.sleep(1)
        win32gui.Rectangle(hdc, 600, 100, 605, 300) # Left Top Right Bottom
        win32gui.Rectangle(hdc, 700, 100, 705, 300) # Left Top Right Bottom
        timeStamp = time.strftime('%H_%M_%S')
        file.write(timeStamp+":"+str(n)+":"+str(x)+","+str(y)+"\n")
        with mss.mss() as sct:
            # The screen part to capture
            monitor = {"top": 160, "left": 160, "width": 160, "height": 135}
            output = "sct-{top}x{left}_{width}x{height}_{n}_{t}.png".format(**monitor, n=n, t=timeStamp)
            # Grab the data
            sct_img = sct.grab(monitor)
            # Save to the picture file
            mss.tools.to_png(sct_img.rgb, sct_img.size, output=output)
            print(output)        
        n+=1
    file.close()
    # asyncio.run(main())