import cv2


# Sender is on a Jetson Device
def send_video(video_path):
    cap = cv2.VideoCapture(video_path)
    video_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    framerate = float(cap.get(cv2.CAP_PROP_FPS))

    out = cv2.VideoWriter("appsrc ! video/x-raw, format=BGR ! queue ! videoconvert !"
                          "video/x-raw, format=BGRx ! nvvidconv ! omxh264enc !"
                          "video/x-h264,stream-format=(string)byte-stream ! h264parse ! "
                          "rtph264pay pt=96 config-interval=1 mtu=1400 ! "
                          "application/x-rtp, ssrc=(uint)3412089386 ! "
                          "srtpenc key=012345678901234567890123456789012345678901234567890123456789 ! "
                          "udpsink host=192.168.1.112 port=12165",
                          cv2.CAP_GSTREAMER, 0, framerate, (video_w, video_h))
    try:
        while True:
            ret, frame = cap.read()
            if ret:
                out.write(frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                break
    except KeyboardInterrupt:
        pass
    finally:
        cap.release()
        out.release()


if __name__ == '__main__':
    send_video("test_video.mp4")

