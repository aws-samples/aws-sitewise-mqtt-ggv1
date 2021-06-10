#!/usr/bin/env python3

# /*
__author__ = "Srikanth Kodali - skkodali@"
# */

from aws_cdk import core
from sitewise_models_and_assets.sitewise_models_and_assets import SitewiseModelsAndAssetsStack

app = core.App()
SitewiseModelsAndAssetsStack(app, "sitewise-models-and-assets-creation-1", props = [0, 200],  env={'region': 'us-east-1'})
SitewiseModelsAndAssetsStack(app, "sitewise-models-and-assets-creation-2", props = [201, 400], env={'region': 'us-east-1'})
app.synth()
