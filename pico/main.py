import time
import math
import picokeypad as keypad

keypad.init()
keypad.set_brightness(0.1)

DIM = 4
CTRL_ROW = 3
SPEED = 0.04
MODE = "INIT"
MODE_COLORS = {
    "INIT": [(255,0,0),(255,255,255)],
    0: [(255,0,0),(0,0,255)],
    1: [(0,255,255),(255,255,0)]
}
DIAGS = [(0,),(1,4),(2,5,8),(3,6,9,12),(7,10,13),(11,14),(15,)]
NUM_PADS = keypad.get_num_pads()


def __init__():
    for i in range(0,NUM_PADS):
        keypad.illuminate(i,5,5,5)
        
    num_colors = 55
    count = 0
    while count < num_colors + len(DIAGS):
        if(count < 7):
            color_flow(count,num_colors,DIAGS[0:count+1])
        else:
            color_flow(count,num_colors,DIAGS)
        if count >= num_colors:
            color_lines((255,0,0),DIAGS[0:count-num_colors+1])
            
        time.sleep(SPEED)
        count += 1
    
    set_mode_color(MODE)
    return


# get the ith color of an n-part color wheel
def get_color(i,n):
    r = 0
    g = 0
    b = 0
    
    step_size = math.floor((255 * 6) / n)
    progress = i * step_size
    segment = math.floor(progress / 255)
    
    if segment == 0:
        r = 255
        g = progress % 255
    if segment == 1:
        g = 255
        r = (255 - progress) % 255
    if segment == 2:
        g = 255
        b = progress % 255
    if segment == 3:
        b = 255
        g = (255 - progress) % 255
    if segment == 4:
        b = 255
        r = progress % 255
    if segment == 5:
        r = 255
        b = (255 - progress) % 255
    
    return (r,g,b)


# sets keys to a rainbow flow beginning with the ith color of n colors
# @param count: starting position in sequence
# @param n: number of colors in sequence
# @param lines: list of tuples of rows, columns, or diagonals of keypad
def color_flow(count,n,lines):
    for i in range(0,len(lines)):
        rgb = get_color((i-count)%n,n)
        for j in range(0,len(lines[i])):
            button = lines[i][j]
            keypad.illuminate(button,rgb[0],rgb[1],rgb[2])
                
    keypad.update()    
    return


# sets non-control keys to a solid color
def color_block(rgb):
    for i in range(0,DIM*CTRL_ROW):
        keypad.illuminate(i,rgb[0],rgb[1],rgb[2])
    keypad.update()
    return
        
        
# sets the input lines to a solid color
def color_lines(rgb,lines):
    for i in range(0,len(lines)):
        for j in range(0,len(lines[i])):
            button = lines[i][j]
            keypad.illuminate(button,rgb[0],rgb[1],rgb[2])
    keypad.update()
    return


# sets current mode and corresponding keypad colors
def set_mode_color(mode):
    global MODE
    MODE = mode
    colors = MODE_COLORS[mode]
    
    for i in range(0,len(DIAGS)):
        color_lines(colors[0],DIAGS[0:i+1])
        time.sleep(SPEED)
    
    for j in range(0,DIM):
        for k in range(0,j+1):
            keypad.illuminate((DIM*CTRL_ROW)+k,colors[1][0],colors[1][1],colors[1][2])
        keypad.update()
        time.sleep(SPEED)
    
    keypad.update()
    return


# returns color of input key for active mode
def get_key_color(key):
    if key >= DIM*CTRL_ROW:
        return MODE_COLORS[MODE][1]
        return (0,0,255)
    return MODE_COLORS[MODE][0]


# follows initialization, awaits keypad input to set mode
def mode_selector():
    num_colors = 760
    count = 0
    selecting = True
    while selecting:
        color_block(get_color(count%num_colors,num_colors))
        time.sleep(SPEED)
        count += 1
        
        button_states = keypad.get_button_states()
        if button_states > 0:
            if button_states & 0x01 > 0:
                set_mode_color(0)
                selecting = False
                
    return


def __main__():
    __init__()
    mode_selector()
    
    last_button_states = 0
    while True:        
        button_states = keypad.get_button_states()
        if last_button_states != button_states:
            last_button_states = button_states
            for i in range(0,NUM_PADS):
                if button_states & 0x01 > 0:
                    keypad.illuminate(i,255,255,255)
                    if i in MODE_COLORS and (last_button_states >> DIM*CTRL_ROW) & 0x01 > 0:
                        print('{"key": %d, "state": "ctrl"}' % (i))
                        if MODE != i:
                            set_mode_color(i)
                    else:
                        print('{"key": %d, "state": "pressed"}' % (i))
                else:
                    rgb = get_key_color(i)
                    keypad.illuminate(i,rgb[0],rgb[1],rgb[2])
                    
                button_states >>= 1
            keypad.update()
    

__main__()
    