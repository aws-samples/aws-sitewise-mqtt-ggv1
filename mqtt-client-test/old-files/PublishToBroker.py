import paho.mqtt.client as mqtt
from TestDataGeneratorInitialVersion import TestDataGenerator as data_generator

broker = "localhost"
topic = "send/to/sitewise/edge"
client = mqtt.Client("test1")


def on_log(lclient, userdata, level, buf):
    print("log: {}".format(buf))

def publish_message():
    profile_message = data_generator.gen_generator_data(2, 5)
    print("Message is :::::: {}".format(profile_message))
    #client.publish(topic, payload=json.dumps(profile_message))
    client.publish(topic, payload=profile_message)

def on_message(lclient, userdata, msg):
    ltopic = msg.topic
    m_decode = str(msg.payload.decode("utf-8"))
    print("message received, and the message is :::: {}".format(m_decode))


#schedule.every(1).minutes.do(publish_message)

if __name__== "__main__":
    print("Connecting to broker {}".format(broker))
    client.connect(broker)
    client.on_log = on_log
    client.on_message = on_message
    #while True:
    for i in range(5):
        #schedule.run_pending()
        publish_message()
        client.loop()
        #time.sleep(1)

    client.disconnect()