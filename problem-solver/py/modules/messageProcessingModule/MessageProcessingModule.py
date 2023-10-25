from sc_kpm import ScModule
from .WeatherAgent import WeatherAgent
from .GettingObjectsFromMap import MapsObjectsInfoAgent


class MessageProcessingModule(ScModule):
    def __init__(self):
        super().__init__(WeatherAgent(), MapsObjectsInfoAgent())
