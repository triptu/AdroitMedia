import os
import ctypes

# Used for emulating key presses. This gives us access to user32.dll
user32 = ctypes.windll.user32
# Virtual keys
VK_VOLUME_MUTE = 0xAD
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_UP = 0xAF
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1
VK_MEDIA_STOP = 0xB2
VK_MEDIA_PLAY_PAUSE = 0xB3
VK_PLAY = 0xFA

# Mapping expected input to actions
bytes_to_keys = {}
bytes_to_keys["1"] = VK_MEDIA_PLAY_PAUSE
bytes_to_keys["play"] = VK_MEDIA_PLAY_PAUSE
bytes_to_keys["pause"] = VK_MEDIA_PLAY_PAUSE
bytes_to_keys["2"] = VK_MEDIA_NEXT_TRACK
bytes_to_keys["3"] = VK_MEDIA_PREV_TRACK
bytes_to_keys["4"] = VK_MEDIA_STOP
bytes_to_commands = {}



def run_command(cmd):
    os.system(cmd)

def do_action(char):
    '''Takes a 1-character code and executes the action assoliated with it'''
    if char in bytes_to_keys:
        key_code = bytes_to_keys[char]
        user32.keybd_event(key_code, 0, 0, 0) # press
        user32.keybd_event(key_code, 0, 2, 0) # release
    else:
        print("unknown instruction:", char)

