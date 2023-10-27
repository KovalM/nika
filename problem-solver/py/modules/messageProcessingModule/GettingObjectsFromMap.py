"""
This code creates some test agent and registers until the user stops the process.
For this we wait for SIGINT.
"""
import logging
from sc_client.models import ScAddr, ScLinkContentType, ScTemplate
from sc_client.constants import sc_types
from sc_client.client import template_search

from sc_kpm import ScAgentClassic, ScModule, ScResult, ScServer
from sc_kpm.sc_sets import ScSet
from sc_kpm.utils import (
    create_link,
    get_link_content_data,
    check_edge, create_edge,
    delete_edges,
    get_element_by_role_relation,
    get_element_by_norole_relation,
    get_system_idtf,
    get_edge
)
from sc_kpm.utils.action_utils import (
    create_action_answer,
    finish_action_with_status,
    get_action_arguments,
    get_element_by_role_relation
)
from sc_kpm import ScKeynodes

import requests

import googlemaps


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(name)s | %(message)s", datefmt="[%d-%b-%y %H:%M:%S]"
)


class MapsObjectsInfoAgent(ScAgentClassic):
    def __init__(self):
        super().__init__("action_get_maps_object_info")
        self.gmaps = googlemaps.Client(key='AIzaSyCp0BClKtxFt_9uI_WP24B_MT2KyRjvx-o')
        self.location = (53.899137159097585, 27.56316256994039)
        self.type = "restaurant"
        self.language = "RU"
        self.region = "BE"
        self.radius = 100

    def on_event(self, event_element: ScAddr, event_edge: ScAddr, action_element: ScAddr) -> ScResult:
        result = self.run(action_element)
        is_successful = result == ScResult.OK
        finish_action_with_status(action_element, is_successful)
        self.logger.info("MapsObjectsInfoAgent finished %s",
                         "successfully" if is_successful else "unsuccessfully")
        return result

    def create_edge(edge_type: ScType, src: ScAddr, trg: ScAddr) -> ScAddr: ...

    def run(self, action_node: ScAddr) -> ScResult:
        self.logger.info("MapsObjectsInfoAgent started")
        result=self.gmaps.places(
            "restaurant",
            location=self.location,
            radius=self.radius,
            region=self.region,
            language=self.language,
            open_now=True,
            type=self.type,)
        print(result)
        objects_info = create_node(sc_types.NODE_CONST)
        object_class = ScKeynodes.resolve("concept_infrastructure_class", sc_types.NODE_CONST_CLASS)
        edge = create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, object_class, objects_info)
