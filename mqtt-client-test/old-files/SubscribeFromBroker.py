import paho.mqtt.client as mqtt

#broker = "localhost"
broker = "ec2-34-231-20-28.compute-1.amazonaws.com"
port = 1883
topic = "send/to/sitewise/edge"
client = mqtt.Client()

def on_log(lclient, userdata, level, buf):
    print("log: {}".format(buf))

def on_message(lclient, userdata, msg):
    ltopic = msg.topic
    m_decode = str(msg.payload.decode("utf-8"))
    print("message received, and the message is :::: {}".format(m_decode))

def on_connect(lclient, userdata, flags, rc):
    if rc==0:
        print("connected OK and subscribing to topic {}".format(topic))
        client.subscribe(topic)
    else:
        print("Bad connection returned code = {}".format(rc))

if __name__== "__main__":
    print("Connecting to broker {}".format(broker))
    client.connect(broker, port)
    client.on_log = on_log
    client.on_message = on_message
    client.on_connect = on_connect
    client.loop_forever()