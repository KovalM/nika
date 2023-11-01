"""
This code creates some test agent and registers until the user stops the process.
For this we wait for SIGINT.
"""
import logging
from sc_client.models import ScAddr, ScLinkContentType, ScTemplate
from sc_client.constants import sc_types
from sc_client.client import template_search, template_generate

from sc_kpm import ScAgentClassic, ScModule, ScResult, ScServer
from sc_kpm.sc_sets import ScSet
from sc_kpm.utils import (
    create_link,
    create_node,
    get_link_content_data,
    check_edge, create_edge,
    delete_edges,
    get_element_by_role_relation,
    get_element_by_norole_relation,
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
from googlemaps import *

from random import randint


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(name)s | %(message)s", datefmt="[%d-%b-%y %H:%M:%S]"
)


class MapsObjectsInfoAgent(ScAgentClassic):
    def __init__(self):
        super().__init__("action_get_maps_object_info")
        self.gmaps = googlemaps.Client(key='AIzaSyCp0BClKtxFt_9uI_WP24B_MT2KyRjvx-o')
        self.location = (53.899137159097585, 27.56316256994039)
        self.language = "RU"
        self.region = "BE"
        self.radius = 1

    def on_event(self, event_element: ScAddr, event_edge: ScAddr, action_element: ScAddr) -> ScResult:
        result = self.run(action_element)
        is_successful = result == ScResult.OK
        finish_action_with_status(action_element, is_successful)
        self.logger.info("MapsObjectsInfoAgent finished %s",
                         "successfully" if is_successful else "unsuccessfully")
        return result

    # def create_edge(edge_type: ScType, src: ScAddr, trg: ScAddr) -> ScAddr: ...

    def run(self, action_node: ScAddr) -> ScResult:
        self.logger.info("MapsObjectsInfoAgent started")

        try:
            message_addr = get_action_arguments(action_node, 1)[0]
            message_type = ScKeynodes.resolve(
                "concept_message_about_location", sc_types.NODE_CONST_CLASS)

            if not check_edge(sc_types.EDGE_ACCESS_VAR_POS_PERM, message_type, message_addr):
                self.logger.info(
                    f"MapObjectsAgent: the message isn’t about location")
                return ScResult.OK

            # user_addr = self.get_user()
            # user_location_idtf = self.get_user_location(user_addr)
            # if not user_location_idtf: 
            #     self.generate_message_reply(message_addr)
            #     self.logger.info("MapsObjectInfoAgent: not found user location")
            #     return ScResult.OK
            
            rrel_territorial_object = ScKeynodes.resolve("rrel_territorial_object", sc_types.NODE_ROLE)
            city_addr = self.get_entity_addr(message_addr, rrel_territorial_object)
            if not city_addr.is_valid:
                user_location = self.get_location_from_user(action_node) 
            self.get_location_from_user(action_node)
            rrel_entity = ScKeynodes.resolve("rrel_entity", sc_types.NODE_ROLE)
            city = get_link_content_data(self.get_ru_idtf(city_addr))
            node_entity = self.get_entity_addr(message_addr, rrel_entity)
            city_cords = self.get_city_cords(city)
            print(city_cords)
            place_type = get_link_content_data(self.get_ru_idtf(node_entity))
            place_info = self.get_city_object_info(place_type, city_cords)
            
            self.translate_object_info_to_kb(place_info, city_addr, node_entity)

            return ScResult.OK    

        except Exception as e:
            self.logger.info(f"MapObjectsAgent: finished with an error", e)
            return ScResult.ERROR
        

    def translate_object_info_to_kb(self, place_info, city_addr, node_entity):
        
        node_entity_object = create_node(sc_types.NODE_CONST)
        lang_ru = ScKeynodes.resolve("lang_ru", sc_types.NODE_CONST_CLASS)
        random_object_index = randint(0,len(place_info["results"])-1)
        adress = place_info["results"][random_object_index]["formatted_address"]
        objname = place_info["results"][random_object_index]["name"]

        object_address = create_link(str(adress), ScLinkContentType.STRING, link_type=sc_types.LINK_CONST)
        object_name = create_link(str(objname), ScLinkContentType.STRING, link_type=sc_types.LINK_CONST)

        template = ScTemplate()
        template.triple(
                ScKeynodes.resolve("concept_infrastructure_class", sc_types.NODE_CONST_CLASS),
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                sc_types.NODE_VAR
            )
            
        template.triple_with_relation(
                node_entity_object,
                sc_types.EDGE_D_COMMON_VAR,
                city_addr,
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                ScKeynodes.resolve("nrel_geolocation", sc_types.NODE_CONST_NOROLE)
            )
           
        template.triple(
                node_entity,
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                node_entity_object
            )
           
        template.triple_with_relation(
                node_entity_object,
                sc_types.EDGE_D_COMMON_VAR,
                object_address,
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                ScKeynodes.resolve("nrel_address", sc_types.NODE_CONST_NOROLE)
            )
            
        template.triple(
                lang_ru,
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                object_address
            )
            
        template.triple_with_relation(
                node_entity_object,
                sc_types.EDGE_D_COMMON_VAR,
                object_name,
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                ScKeynodes.resolve("nrel_main_idtf", sc_types.NODE_CONST_NOROLE)
            )
            
        template.triple(
                lang_ru,
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                object_name
            )

        template_generate(template, {})

    def get_city_object_info(self, place_type, city_cords):
        result=self.gmaps.places(
        place_type,
        location=(city_cords),
        radius=self.radius,
        region=self.region,
        language=self.language,
        open_now=True,
        type=place_type)
        return result

    def get_city_cords(self, city):
        city_results = self.gmaps.geocode(city)
        # print(city_results)
        # print(city_results[0])
        # print(city_results[0]["geometry"])
        # print(city_results[0]["geometry"]["location"])
        city_lat = city_results[0]["geometry"]["location"]["lat"]
        city_lng = city_results[0]["geometry"]["location"]["lng"]
        return (city_lat, city_lng)

    def get_entity_addr(self, message_addr: ScAddr, relation: ScAddr):
        template = ScTemplate()
        # entity node or link
        template.triple_with_relation(
            message_addr,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            sc_types.VAR,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            relation,
        )
        search_results = template_search(template)
        if len(search_results) == 0:
            return ScAddr(0)
        entity = search_results[0][2]
        if len(search_results) == 1:
            return entity
        
    def get_ru_idtf(self, entity_addr: ScAddr) -> ScAddr:
        main_idtf = ScKeynodes.resolve(
            "nrel_main_idtf", sc_types.NODE_CONST_NOROLE)
        lang_ru = ScKeynodes.resolve("lang_ru", sc_types.NODE_CONST_CLASS)

        template = ScTemplate()
        template.triple_with_relation(
            entity_addr,
            sc_types.EDGE_D_COMMON_VAR,
            sc_types.LINK,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            main_idtf,
        )
        search_results = template_search(template)
        for result in search_results:
            idtf = result[2]
            lang_edge = get_edge(
                lang_ru, idtf, sc_types.EDGE_ACCESS_VAR_POS_PERM)
            if lang_edge:
                return idtf
        return get_element_by_norole_relation(
            src=entity_addr, nrel_node=main_idtf)
    
    def get_location_from_user(self, action_node):
        userAddr = self.get_user(action_node)
        # template = ScTemplate()
        # template.triple_with_relation(
        #     userAddr,
        #     sc_types.EDGE_D_COMMON_VAR, 
        #     sc_types.VAR,
        #     sc_types.EDGE_ACCESS_VAR_POS_PERM,
        #     ScKeynodes.resolve("nrel_ip_address", sc_types.NODE_NOROLE)
        # )
        # search_results = template_search(template)
        # if len(search_results) == 0:
        #     return ScAddr(0)
        # useripAddr = search_results[0][2]
        # user_ip = get_link_content_data(useripAddr)
        user_ip = "46.56.239.62" 
        req = requests.get(f"http://ipwho.is/{user_ip}")
        print(req.json())
        return None
        # if len(search_results) == 1:
        #     return user_ip

    def get_user(self, action_node) -> ScAddr:
        template = ScTemplate()
        template.triple_with_relation(
            action_node,
            sc_types.EDGE_D_COMMON_VAR, 
            sc_types.VAR,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            ScKeynodes.resolve("nrel_authors", sc_types.NODE_NOROLE)
        )
        search_results = template_search(template)
        if len(search_results) == 0:
            return ScAddr(0)
        userAddr = search_results[0][2]
        if len(search_results) == 1:
            return userAddr
    
    # def get_user_location(self, user_addr) -> str:
    #     nrel_location = ScKeynodes.resolve("nrel_location", sc_types.NODE_CONST_NOROLE) 
    #     user_location_addr = get_element_by_norole_relation(user_addr, nrel_location)
    #     if not user_location_addr.is_valid():
    #         return None
    #     user_location_idtf_addr = self.get_ru_idtf(user_location_addr)
    #     user_location_idtf = get_link_content_data(user_location_idtf_addr)
    #     return user_location_idtf
        
    def generate_message_reply(self, message_addr):
        nrel_reply = ScKeynodes.resolve("nrel_question", sc_types.NODE_NOROLE)
        reply_message_addr = create_link("Я не знаю где Вы находитесь. Пожалуйста, укажите свое местоположение", ScLinkContentType.STRING, sc_types.LINK_CONST)
        edge = create_edge(sc_types.EDGE_D_COMMON_CONST, message_addr, reply_message_addr)
        create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, nrel_reply, edge)
        concept_message_user_location = ScKeynodes.resolve("concept_message_about_user_location", sc_types.NODE_CONST_CLASS)
        create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, concept_message_user_location, reply_message_addr)