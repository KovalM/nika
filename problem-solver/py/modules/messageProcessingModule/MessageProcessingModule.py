from sc_kpm import ScModule
from .WeatherAgent import WeatherAgent
from .GettingObjectsFromMap import MapsObjectsInfoAgent
from .FindingPathBeetween2PlacesAgent import FindingPathAgent


class MessageProcessingModule(ScModule):
    def __init__(self):
        super().__init__(WeatherAgent(), MapsObjectsInfoAgent(), FindingPathAgent())
