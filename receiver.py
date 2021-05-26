import cv2


# Receiver is a Linux x86 PC
def receiver():
    cap = None
    try:
        cap = cv2.VideoCapture("udpsrc port=12165 ! application/x-srtp, payload=(int)96,ssrc=(uint)3412089386, "
                               "srtp-key=(buffer)012345678901234567890123456789012345678901234567890123456789, "
                               "srtp-cipher=(string)aes-128-icm, srtp-auth=(string)hmac-sha1-80, "
                               "srtcp-cipher=(string)aes-128-icm, srtcp-auth=(string)hmac-sha1-80, "
                               "roc=(uint)0 ! srtpdec ! queue ! rtph264depay ! h264parse ! avdec_h264 ! "
                               "videoconvert ! appsink", cv2.CAP_GSTREAMER)


        while True:
            ret, frame = cap.read()
            if ret:
                cv2.imshow("frame", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                break
    except KeyboardInterrupt:
        pass
    finally:
        cap.release()


if __name__ == '__main__':
    receiver()
