import pygame,sys
import os.path


soundpath = '/home/pi/cantaStorie/fiabeSonore/test.mp3'
pygame.init()
pygame.mixer.music.load(soundpath)

while True:

    if os.path.isfile(soundpath):
       if not  pygame.mixer.music.get_busy():
             print("Sound file found, playing...")
             pygame.mixer.music.play()
    else:
       print("no file")
