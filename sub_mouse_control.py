import pyautogui
import asyncio
import sys
import pygame
import random
import time
from typing import Callable
from screeninfo import get_monitors

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

# I suppose you wrote something like this:

 

# module M = Map.Make(O)
# type t = M.t
# This does not work because the type M.t is parametric in the value type of the maps it represents. It is a type constructor like list that expects another type as argument. Hence, you get the error message. Presumably you want:

# module M = Map.Make(O)
# type t = int M.t
# because you want to maps that store keys (of type O.t) to int values.
def moveTo(x: int, y: int):
    pyautogui.moveTo(x, y)

def moveToRel(x: int, y: int):
     pyautogui.moveRel(x, y)

def getScreenDims():
    info = pygame.display.Info()
    width = info.current_w
    height = info.current_h
    return width, height

if __name__ == "__main__":
    pygame.init()
    width, height = getScreenDims()
    file = open("coords", "a+")
    for n in range(0,100):
        x = random.randint(1,width)
        y = random.randint(1,height)
        moveTo(x,y)
        time.sleep(.4)
        pyautogui.screenshot("screenshot"+str(n)+".png")
        file.write(str(n)+":"+str(x)+","+str(y)+"\n")
    file.close()
    # asyncio.run(main())