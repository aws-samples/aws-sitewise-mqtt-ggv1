# /*
# __author__ = "Srikanth Kodali - skkodali@"
# */

#!/usr/bin/env bash
zip -r mqtt-sitewise-connector-lambda.zip stream_manager cbor2 conf _SendToStreamManager.py SubscribeFromGGBroker.py

FUNCTION_NAME="mqtt-ggv1-lambda-to-sitewise-edge"
aws lambda update-function-code --function-name ${FUNCTION_NAME} --zip-file fileb:///Users/skkodali/work/Blogs-And-Artifacts/MQTT-GG-SitewiseEdge/mqtt-sitewise-connector-lambda/mqtt-sitewise-connector-lambda.zip
aws lambda publish-version --function-name ${FUNCTION_NAME}
aws lambda list-versions-by-function --function-name ${FUNCTION_NAME} --query "Versions[-1].[Version]"
LATEST_VERSION=`aws lambda list-versions-by-function --function-name ${FUNCTION_NAME} --query "Versions[-1].[Version]"|sed '1d; $d' | sed  "s/ //g" | tr -d '"'`
aws lambda create-alias --function-name ${FUNCTION_NAME} --description "alias for live version of function" --name mqtt-ggv1-lambda-alias$LATEST_VERSION --function-version $LATEST_VERSION