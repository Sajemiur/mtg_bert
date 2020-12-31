from django.apps import AppConfig
import html
from pathlib import Path
import os


class MtgConfig(AppConfig):
    name = 'mtg'
    MODEL_PATH = Path("model")
    BERT_PRETRAINED_PATH = Path("model/")
    LABEL_PATH = Path("model/label/")

    # def ready(self):
    #     import logging
    #     logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s -   %(message)s',
    #                         datefmt='%m/%d/%Y %H:%M:%S',
    #                         level=logging.INFO)
    #     logger = logging.getLogger("I'm ready!")
    #     from .mtg_bert import Model
    #     self.predictor = Model()
