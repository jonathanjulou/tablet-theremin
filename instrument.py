import sounddevice as sd
import numpy as np
import pyglet
import time
import threading
import matplotlib.pyplot as plt

tablets = pyglet.input.get_devices()
if tablets:
    print('Tablets:')
    for i, tablet in enumerate(tablets):
        print('  (%d) %s' % (i , tablet.name))
i = 2#int(input('type the index of the tablet.'))

device = tablets[i]
controls = device.get_controls()
window = pyglet.window.Window(1920, 1080)

control_pression = controls[7]
Button = controls[3]
control_x =controls[5]
control_y =controls[6]
control_punta = controls[4]
control_alcance = controls [0]
name = tablets[i].name
print("SELECTED DEVICE:", name)

try:
    canvas = device.open(window)
except pyglet.input.DeviceException:
    print('Failed to open tablet %d on window' % index)

SAMPLERATE = 48000
BUFFER_DURATION = 0.5
AUDIO_BUFFER_LENGTH = int(SAMPLERATE*BUFFER_DURATION)
AUDIO_BUFFER = np.zeros(AUDIO_BUFFER_LENGTH)

MOTHER_POS = 0
def mother(x):
    global MOTHER_POS
    MOTHER_POS += x
    return np.sin(2*np.pi*MOTHER_POS)
    #return (np.ceil(np.sin(2*np.pi*MOTHER_POS/880)-0.5) + np.ceil(np.sin(2*np.pi*MOTHER_POS/880/2)-0.5))/2

LAST_PITCH = 440
PITCH = 440#np.ones(480)*500
LAST_VOLUME = .1
VOLUME = .1#np.ones(480)*0.1
PHASE = 0
UPD = False
CPT = 0
def callback(outdata, frames, time, status):
        global PHASE, LAST_PITCH, LAST_VOLUME, UPD, CPT
        #T = time.currentTime
        dt = 1/SAMPLERATE
        #t_s = np.linspace(dt*PHASE, dt*(PHASE+1), frames).astype("float32")
        #t_s = np.linspace(0, dt, frames).astype("float32")
        t_s = np.ones(frames).astype("float32")*dt

        x = [0, 1]
        nx = np.linspace(0,1,frames)
        y_pitch = [LAST_PITCH, PITCH]
        y_volume = [LAST_VOLUME, VOLUME]
        pitch_interp = np.interp(nx, x, y_pitch).astype("float32")
        volume_interp = np.interp(nx, x, y_volume).astype("float32")

        data = np.zeros(frames)
        for i,_ in enumerate(nx):
            data[i] = mother(pitch_interp[i]*t_s[i])*volume_interp[i]
            #data[i] = mother(dt/2)*volume_interp[i]

        #data = np.sin(2*np.pi*t_s*pitch_interp)*volume_interp
        data = data.reshape(frames, 1)

        if len(outdata) > len(data):
            outdata[:len(data)] = data
            outdata[len(data):] = b'\x00' * (len(outdata) - len(data))
            raise sd.CallbackStop
        else:
            outdata[:] = data

        if not UPD:
            CPT+=1
            if CPT >= 16:
                outdata[:] = np.zeros(frames).reshape(frames, 1)
        else:
            CPT = 0

        PHASE += 1
        LAST_PITCH = y_pitch[1]
        LAST_VOLUME = y_volume[1]
        UPD = False


STREAM = sd.OutputStream(samplerate = SAMPLERATE, blocksize = 48*8, channels = 1, dtype="float32", callback=callback, latency = 0.08)
STREAM.start()
#x = np.linspace(0,1000*1,int(SAMPLERATE*1)).astype("float32")
#y = np.sin(x)*.1
#STREAM.write(y)
#STREAM.write(y*.5)

"""
UPDATE_PERIOD = 0.1
LAST_UPD_T = time.time()
CONTINUE = True
PITCH = 1000
VOLUME = 0.1
def audio_gen():
    global LAST_UPD_T
    while CONTINUE:
        print("han")
        t = time.time()
        dt = t - LAST_UPD_T
        t_s = np.linspace(0, dt, int(SAMPLERATE*dt/2)).astype("float32")
        sound = np.sin(t_s*PITCH)*VOLUME
        #sd.play(sound, SAMPLERATE)
        #p = control_pression.value/2**16
        STREAM.write(sound)
        time.sleep(UPDATE_PERIOD)

AUDIO_GEN = threading.Thread(target=audio_gen)
AUDIO_GEN.start()
"""

pic = pyglet.image.load('therem2.png')
cursor_pic = pyglet.image.load('cursor.png')
cursor = pyglet.sprite.Sprite(cursor_pic, x=50, y=50)

@control_x.event
def on_change(x):
    global cursor
    cursor.x = (x/(2**15)-1)*1920 -64
    cursor.update()
    play()

@control_y.event
def on_change(y):
    global cursor
    cursor.y = (1-y/(2**16))*1080 -64
    play()

def play():
    global PITCH, VOLUME, UPD

    if control_x.value is not None and control_y.value is not None:
        x_min = 22/1920
        x_max = 1897/1920
        y_min = 18/1080
        y_max = 1060/1080

        x = control_x.value/(2**15)-1
        y = control_y.value/(2**16)

        x = (x - x_min)*(x_max-x_min)
        #y = (y - y_min)*(y_max-y_min)

        f0 = 130.81 
        n = x*38/12
        PITCH = f0*2**(n)#880 * (x) + 220 *(1-x)
        VOLUME = (1-y)*.2

        UPD = True


# on draw event
@window.event
def on_draw():
    # clearing the window
    window.clear()
    pic.blit(0, 0)
    cursor.draw()


# key press event
@window.event
def on_key_press(symbol, modifier):

    print("Some key is pressed")

    # key "C" get press
    if symbol == pyglet.window.key.S:
        print("Start")
        display = pyglet.canvas.get_display()
        screens = display.get_screens()
        window.set_fullscreen(True, screen=screens[1])

def update(dt):
    pass

pyglet.clock.schedule_interval(update, 1.0/50.0)
pyglet.app.run()

#samplerate = 48000

#x = np.linspace(0,500,50000)
#y = np.sin(x)*.1

#sd.play(y, samplerate)
CONTINUE = False
#AUDIO_GEN.join()
STREAM.stop()
sd.stop()
