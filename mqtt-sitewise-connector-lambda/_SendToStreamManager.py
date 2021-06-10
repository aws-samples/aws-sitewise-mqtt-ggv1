# /*
# __author__ = "Srikanth Kodali - skkodali@"
# */

### Download latest stream_manager sdk from : https://github.com/aws-greengrass/aws-greengrass-stream-manager-sdk-python/
### unzip the downloaded zip file
### In the unzipped folder, you will see "stream_manager" folder
### Copy that folder under the program's "root" directory.

from stream_manager import StreamManagerClient
from stream_manager import StreamManagerException
from stream_manager import MessageStreamDefinition
from stream_manager import StrategyOnFull
from stream_manager import Persistence
import asyncio
import traceback
import logging.config
import configparser
import pathlib

logging.config.fileConfig(fname='conf/log.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

file = pathlib.Path('conf/mqtt-connector.cfg')

config = configparser.ConfigParser()
if file.exists ():
    config.read(file)
else:
    logger.error("Config file: {} does not exists, please check if the file exists or not.".format(file))
    exit(1)

stream_name = config.get('mqtt-settings', 'stream-name')
#stream_name = "SiteWise_Stream"

def init_gg_stream_manager():
    logger.info("Initializing Stream manager.")
    site_wise_stream_client = StreamManagerClient()
    try:
        streams_list = site_wise_stream_client.list_streams()
        if stream_name in streams_list:
            logger.debug("Stream already exists - {}.".format(stream_name))
        else:
            try:
                site_wise_stream_client.create_message_stream(
                    MessageStreamDefinition(
                        name=stream_name,
                        max_size=268435456, # Default is 256 MB.
                        stream_segment_size=16777216, # Default is 16 MB.
                        time_to_live_millis=None, # By default, no TTL is enabled.
                        strategy_on_full=StrategyOnFull.OverwriteOldestData, # Required.
                        persistence=Persistence.File, # Default is File.
                        flush_on_write=False, # Default is false.
                    )
                )
            except StreamManagerException as e:
                logger.error(e, exc_info=True)
            except:
                logger.error("Exception occurred while initializing the stream: %s", traceback.format_exc())
    except ConnectionError or asyncio.TimeoutError:
        logger.error(e, exc_info=True)
    except:
        logger.error("Exception occurred while listing the existing stream: %s", traceback.format_exc())
    return site_wise_stream_client

def append_to_gg_stream_manager(stream_client, payload):
    logger.info("In append_to_gg_stream_manager {}".format(payload))
    try:
        stream_client.append_message(stream_name, payload)
        logger.debug("Message appended to stream successfully.")
    except asyncio.TimeoutError as e:
        logger.error(e, exc_info=True)
    except StreamManagerException as e:
        logger.error(e, exc_info=True)
    except:
        logger.error("Exception occurred while appending message to stream : %s", traceback.format_exc())