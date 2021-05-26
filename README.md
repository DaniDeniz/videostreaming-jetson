# Video Streaming Jetson
Stream video from Jetson devices using GStreaming through SRTP for secure and efficient video sending. This module uses OpenCV with
GStreamer support built on Jetson devices to take advantage of Hardware encoding and efficient and secure video transmission.

## Video Sender from Jetson
The [sender.py](sender.py) file sends the [test_video.mp4](test_video.mp4) video through the network. We use
the OpenCV VideoWriter class to pass the frames to the GStreamer pipeline. The pipeline is the one described below:

```python
gs_pipeline="appsrc ! video/x-raw, format=BGR ! queue ! videoconvert !" \
            "video/x-raw, format=BGRx ! nvvidconv ! omxh264enc !" \
            "video/x-h264,stream-format=(string)byte-stream ! h264parse ! " \
            "rtph264pay pt=96 config-interval=1 mtu=1400 ! " \
            "application/x-rtp, ssrc=(uint)3412089386 ! " \
            "srtpenc key=012345678901234567890123456789012345678901234567890123456789 ! " \
            "udpsink host=192.168.1.112 port=12165" 
```

Here, a brief description of the pipeline:
* **appsrc** | Obtains data from an application source (OpenCV)
* **video/x-raw, format=BGR** | The video received from the VideoWriter in OpenCV is in BGR format
* **videoconvert** | Convert video to the format described in the next element in the pipeline
* **video/x-raw, format=BGRx** | Convert video to BGRx format, x is a dummy channel. However, it is required by the hardware encoder
* **nvvidconv** | Nvidia video converter formatter and scaling module
* **omxh264enc** | OpenMax h264 hardware encoder
* **video/x-h264,stream-format=(string)byte-stream** | Hardware encoder outputs a video byte-stream in h264 video format
* **h264parse** | Parses the h264 bytestream
* **rtph264pay pt=96 config-interval=1 mtu=1400** | Create H264 RTP server
* **application/x-rtp, ssrc=(uint)3412089386** | Set synchronization  source value
* **srtpenc key=012345678901234567890123456789012345678901234567890123456789** | Encrypt RTP signal with a defined key and encode the SRTP communication
* **udpsink host=192.168.1.112 port=12165** | Sends the video through UDP to the video receiver device (host) to the desired port

## Video Receiver from Linux x86 PC
The [receiver.py](receiver.py) receives the video through SRTP using OpenCV. The GStreamer pipeline is the following:

```python
gs_pipeline = "udpsrc port=12165 ! application/x-srtp, payload=(int)96,ssrc=(uint)3412089386, " \
              "srtp-key=(buffer)012345678901234567890123456789012345678901234567890123456789, " \
              "srtp-cipher=(string)aes-128-icm, srtp-auth=(string)hmac-sha1-80, " \
              "srtcp-cipher=(string)aes-128-icm, srtcp-auth=(string)hmac-sha1-80, " \
              "roc=(uint)0 ! srtpdec ! queue ! rtph264depay ! h264parse ! avdec_h264 ! " \
              "videoconvert ! appsink"
```

Description of the pipeline:
* **udpsrc port=12165** | The source of the data is a UDP port
* **application/x-srtp** | We define that the data received is a SRTP stream. We need to define several capabilities (separated by comma), to decrypt the video received.
* **ssrc=(uint)3412089386** | synchronization value
* **srtp-key** | Capability to define the cypher key
* **srtp-cipher, srtcp-cipher** | Cypher key type (is the default for the sender)
* **srtp-auth, srtcp-auth** | Auth algorithm
* **roc** | Rollover counter to share stream between multiple clients. We set this to 0, so this property is disabled
* **srtpdec** | SRTP decoder (using parameters defined on the previous element of the pipeline)
* **rtph264depay** | RTP H264 depayloader
* **h264parse** | Parse received h264 stream
* **avdec_h264** | CPU h264 decoder on Linux PC devices
* **appsink** | Outputs result of the pipeline to an application. In our case, to the OpenCV VideoCapture class.