# /*
__author__ = "skkodali@"
# */

import logging
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from TestDataGeneratorInitialVersion import TestDataGenerator as data_generator
import threading

CERTS_PATH = "/home/ubuntu/iot_certs"
host = "172.31.89.146"
port = 8883
root_ca_file = "root.ca.pem"
group_root_ca_file = "39408ebe-c8e4-4c9a-94d8-e180458a9881_CA_9d32335a-405d-4f90-bbbb-3ff892e27024.crt"
certificate_file = "7886c128ea.cert.pem"
privatekey_file = "7886c128ea.private.key"
clientId = "MQTT_Publisher_Thing"
thingName = "MQTT_Publisher_Thing"
topic = "/send/to/sitewise/edge"

# Configure logging
logger = logging.getLogger("device-mqtt-test.core")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)
myAWSIoTMQTTClient.configureCredentials(CERTS_PATH+"/"+group_root_ca_file, CERTS_PATH+"/"+privatekey_file, CERTS_PATH+"/"+certificate_file)
myAWSIoTMQTTClient.configureEndpoint(host, port)
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

try:
   myAWSIoTMQTTClient.connect()
except BaseException as e:
   print("Error in connect!")
   print("Type: %s" % str(type(e)))
   print("Error message: %s" % e.message)

def publish_message(gen_num):
    profile_message = data_generator.gen_generator_data(gen_num, 5)
    print("Message is :::::: {}".format(profile_message))
    #client.publish(topic, payload=json.dumps(profile_message))
    myAWSIoTMQTTClient.publish(topic, profile_message, 0)

if __name__== "__main__":
    #while True:
    #for i in range(5):
        #schedule.run_pending()
    #    publish_message()
    #    time.sleep(1)
    for i in range(3):
        t = threading.Thread(publish_message, args=(2,))
