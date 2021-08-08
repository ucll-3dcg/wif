import cv2
import numpy


def create_mp4(images, output):
    writer = None
    for image in images:
        if not writer:
            codec = cv2.VideoWriter_fourcc(*'avc1')
            writer = cv2.VideoWriter(output, codec, 30, image.size)
        converted = cv2.cvtColor(numpy.array(image), cv2.COLOR_RGB2BGR)
        writer.write(converted)
    if writer:
        writer.release()
