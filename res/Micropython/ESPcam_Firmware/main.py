import camera, sys

camera.init(0, format=camera.JPEG, fb_location=camera.PSRAM)
camera.framesize(camera.FRAME_240X240)
camera.quality(5)

buf = camera.capture()
print(len(buf)/1000, "Kb")
file = open("frame.jpeg", "w")
file.write(buf)
file.close()

camera.deinit()