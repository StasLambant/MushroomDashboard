camera = libcamera()
libcamera-still

#libcamera-hello
"""
camera = libcamera()
time.sleep(2)

camera.capture("/home/slambant/Desktop/img.jpg")
print("done")


libcamera-vid -t 0 --inline --width 1280 -=height 960 -n -o udp://<client-ip>:<port>
"""