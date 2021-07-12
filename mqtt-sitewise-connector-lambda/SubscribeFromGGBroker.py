# /*
# __author__ = "Srikanth Kodali - skkodali@"
# */

from _SendToStreamManager import init_gg_stream_manager
from _SendToStreamManager import append_to_gg_stream_manager
import json
import time
import traceback
import logging.config
import configparser
import pathlib
from threading import Thread
import queue
import os

logging.config.fileConfig(fname='conf/log.conf', disable_existing_loggers=False)
logger = logging.getLogger('dev')

tags_dict = {}
q = queue.Queue()
region = os.environ.get('AWS_REGION')

### Not using the lambda environment variables.
#wait_time = os.environ.get('wait_time')
#stream_name = os.environ.get('stream_name')

file = pathlib.Path('conf/mqtt-connector.cfg')

config = configparser.ConfigParser()
if file.exists ():
    logger.info("Config file: {} exists.".format(file))
    config.read(file)
else:
    logger.error("Config file: {} does not exists, please check if the file exists or not.".format(file))
    exit(1)

wait_time = config.getint('mqtt-settings', 'wait_time')
stream_name = config.get('mqtt-settings', 'stream_name')

try:
    logger.info("Initiating Stream manager client with stream name : {}.".format(stream_name))
    sitewise_stream_client = init_gg_stream_manager(stream_name)
    logger.info("Completed stream manager initiation")
except (ValueError, Exception):
    logger.error("Exception occurred while creating the sitewise stream client : %s", traceback.format_exc())

def send_to_stream_manager():
    global tags_dict
    logger.info("Flushing batch of messages to greengrass stream manager.")
    for key, value in list(tags_dict.items()):
        logger.debug("The metrics for the current alias/tag: {} are: {}".format(key, value))
        payload_to_streammanager = {"alias": key, "messages": value}
        logger.info("Payload that is going to stream manager is: {}".format(payload_to_streammanager))
        try:
            append_to_gg_stream_manager(sitewise_stream_client, stream_name, json.dumps(payload_to_streammanager).encode())
        except (ValueError, Exception):
            logger.error("Exception occurred while appending the message to stream manager: %s", traceback.format_exc())
        logger.debug("Payload sent to stream manager successfully.")
        try:
            tags_dict.pop(key)
        except KeyError:
            logger.error("Exception occurred while flushing the dictionary: %s", traceback.format_exc())

def process_queue_and_send_to_stream_manager():
    logger.debug("In Process queue and send to stream manager function")
    while True:
        count = 0
        for element in range(q.qsize()):
            try:
                payload = q.get()
            except queue.Empty:
                logger.error("Exception occurred while getting the elements from the queue: %s", traceback.format_exc())
            handle_metric_message(payload)
            count += 1
        logger.info("Total processed messages were : {}".format(count))
        if count > 0:
            send_to_stream_manager()
        #wait_time = config.getint('mqtt-settings', 'wait_time')
        logger.info("Pausing for {} seconds to collect new messages.".format(str(wait_time)))
        time.sleep(wait_time)
        logger.info("Pause completed. Going to next iteration.")

def handle_metric_message(handle_metric_payload):
    global tags_dict
    tag_alias = handle_metric_payload["alias"]
    msg_payload = handle_metric_payload["messages"][0]
    logger.debug("Message payload is ::: {}".format(msg_payload))
    logger.info("Message payload is ::: {}".format(msg_payload))
    if tags_dict.get(tag_alias) :
        tags_dict[tag_alias].append(msg_payload)
        logger.info("The current size for tag/alias: {} is: {}".format(tag_alias, len(tags_dict[tag_alias])))
    else:
        logger.info("Initialzing the dictionary for tag/alias: {}: ".format(tag_alias))
        tags_dict[tag_alias] = [msg_payload]

t1 = Thread(target=process_queue_and_send_to_stream_manager)
t1.start()

def lambda_handler(event, context):
    logger.info("Messages received and the incoming message is : {}".format(event))
    try:
        logger.debug("Before sending message to local queue.")
        q.put(event)
        logger.debug("Message sent to queue - put completed. - Queue size is {}".format(q.qsize()))
    except Exception as e:
        logger.error(e, exc_info=True)
    except (ValueError, Exception):
        logger.error("uncaught exception: %s", traceback.format_exc())