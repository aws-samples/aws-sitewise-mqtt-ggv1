import paho.mqtt.client as mqtt
import time

broker = "localhost"

def on_log(client, userdata, level, buf):
    print("log: {}".format(buf))

def on_connect(client, userdata, flags, rc):
    if rc==0:
        print("connected OK")
    else:
        print("Bad connection returned code = {}".format(rc))

def on_disconnect(client, userdata, flags, rc=0):
    print("Disconnected result code {}".format(str(rc)))

def on_message(client, userdata, msg):
    topic = msg.topic
    m_decode = str(msg.payload.decode("utf-8"))
    print("message received, and the message is :::: {}".format(m_decode))

client = mqtt.Client("test1")
client.on_connect = on_connect
client.on_log = on_log
client.on_disconnect = on_disconnect
client.on_message = on_message

print("Connecting to broker {}".format(broker))
client.connect(broker)

client.loop_start()
client.subscribe("/to/sitewise/edge")
client.publish("/to/sitewise/edge", "my test message")
time.sleep(4)
client.loop_stop()
client.disconnect()