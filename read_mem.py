if __name__ == '__main__':
    import time
    proc_name = "WK.exe"
    pm.load_process(proc_name)
    game = Game()
    if game is not None:
        t = game.update()

    p = game.pov  # p is pointer to Player. 
    selectedUnit = 0
    score += p[3092] # Selected unit.

    print(selectedUnit)