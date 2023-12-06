# <div style="position:relative;overflow:hidden;"><a href="https://yandex.by/maps/157/minsk/?utm_medium=mapframe&utm_source=maps" 
#         style="color:#eee;font-size:12px;position:absolute;top:0px;">Минск</a>
#         <a href="https://yandex.by/maps/157/minsk/?ll=27.571522%2C53.902657&mode=routes&rtext=53.908470%2C27.479467~53.914596%2C27.663299&rtt=auto
#         &ruri=~ymapsbm1%3A%2F%2Ftransit%2Fstop%3Fid%3Dstation__lh_9614089&utm_medium=mapframe&utm_source=maps&z=11.72" 
#         style="color:#eee;font-size:12px;position:absolute;top:14px;">Яндекс Карты</a>
#         <iframe src="https://yandex.by/map-widget/v1/?ll=27.566914%2C53.891637&mode=routes&rtext=53.882923%2C27.675225~53.899296%2C27.456948&rtt=pd&ruri=~ymapsbm1%3A%2F%2Fgeo%3Fdata%3DCgg2NjY4NDMyNxJB0JHQtdC70LDRgNGD0YHRjCwg0JzRltC90YHQuiwg0LLRg9C70ZbRhtCwINCQ0LTQt9GW0L3RhtC-0LLQsCwgMTAiCg3Mp9tBFfKYV0I%2C&z=12.94" width="560" height="400" frameborder="1"
#         allowfullscreen="true" style="position:relative;"></iframe></div>

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
from sc_client import client
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

from datetime import datetime 


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(name)s | %(message)s", datefmt="[%d-%b-%y %H:%M:%S]"
)


class FindingPathAgent(ScAgentClassic):
    def __init__(self):
        super().__init__("action_get_path_between_objects")
        self.gkey = 'AIzaSyCp0BClKtxFt_9uI_WP24B_MT2KyRjvx-o'
        self.gmaps = googlemaps.Client(key=self.gkey)
        self.location = (53.899137159097585, 27.56316256994039)
        self.language = "RU"
        self.region = "BE"
        self.radius = 10

    def on_event(self, event_element: ScAddr, event_edge: ScAddr, action_element: ScAddr) -> ScResult:
        result = self.run(action_element)
        is_successful = result == ScResult.OK
        finish_action_with_status(action_element, is_successful)
        self.logger.info("FindingPathAgent finished %s",
                         "successfully" if is_successful else "unsuccessfully")
        return result

    # def create_edge(edge_type: ScType, src: ScAddr, trg: ScAddr) -> ScAddr: ...

    def run(self, action_node: ScAddr) -> ScResult:
        self.logger.info("FindingPathAgent started")

        try:
            message_addr = get_action_arguments(action_node, 1)[0]
            message_type = ScKeynodes.resolve(
                "concept_message_about_path", sc_types.NODE_CONST_CLASS)

            if not check_edge(sc_types.EDGE_ACCESS_VAR_POS_PERM, message_type, message_addr):
                self.logger.info(
                    f"FindingPathAgent: the message isn’t about path")
                return ScResult.OK
            
            rrel_territorial_object = ScKeynodes.resolve("rrel_territorial_object", sc_types.NODE_ROLE)
            rrel_first_place = ScKeynodes.resolve("rrel_first_place", sc_types.NODE_ROLE)
            rrel_second_place = ScKeynodes.resolve("rrel_second_place", sc_types.NODE_ROLE)

            city_addr = self.get_entity_addr(message_addr, rrel_territorial_object)
            first_addr = self.get_entity_addr(message_addr, rrel_first_place)
            second_addr = self.get_entity_addr(message_addr, rrel_second_place)

            city = get_link_content_data(self.get_ru_idtf(city_addr))
            first = get_link_content_data(first_addr)
            second = get_link_content_data(second_addr)

            print('---------> ',first, '=', second, '=', city)

            first_cords = self.get_place_cords(first+' '+city)
            second_cords = self.get_place_cords(second+' '+city)
            city_cords = self.get_place_cords(city)

            first_cords_link = create_link(str(first_cords[0])+':'+str(first_cords[1]), ScLinkContentType.STRING, link_type=sc_types.LINK_CONST)
            second_cords_link = create_link(str(second_cords[0])+':'+str(second_cords[1]), ScLinkContentType.STRING, link_type=sc_types.LINK_CONST)
            first_cords_addr = ScKeynodes.resolve("rrel_first_cords", sc_types.NODE_CONST_ROLE)
            second_cords_addr = ScKeynodes.resolve("rrel_second_cords", sc_types.NODE_CONST_ROLE)

            edge = create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, message_addr, first_cords_link)
            create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, first_cords_addr, edge)
            edge = create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, message_addr, second_cords_link)
            create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, second_cords_addr, edge)

            self.check_cords(city_addr, str(city_cords[0])+', '+str(city_cords[1]))
            self.check_cords(first_addr, str(first_cords[0])+', '+str(first_cords[1]))
            self.check_cords(second_addr, str(second_cords[0])+', '+str(second_cords[1]))

            first_c = self.gmaps.reverse_geocode(first_cords)
            second_c = self.gmaps.reverse_geocode(second_cords)
            print(first_c[0]["formatted_address"])
            print(second_c[0]["formatted_address"])

            now = datetime.now()

            print(first_cords, '=', second_cords, '=', city_cords)
            print(type(first_cords), '=', type(second_cords), '=', type(city_cords))
            
            directions_result = self.gmaps.directions(first_c[0]["formatted_address"],
                                     second_c[0]["formatted_address"],
                                     mode="transit", 
                                     departure_time=now, region="BE", language="RU")
            print('============================')
            print('============================')
            print('============================')
            print(directions_result[0])
            print('============================')
            print('============================')
            print('============================')
            print(directions_result[0]["legs"][0]["distance"]["text"])
            print(directions_result[0]["legs"][0]["duration"]["text"])
            print(directions_result[0]["legs"][0]["arrival_time"]["text"])
            time = directions_result[0]["legs"][0]["duration"]["text"]
            dist = directions_result[0]["legs"][0]["distance"]["text"]
            arr_time = directions_result[0]["legs"][0]["arrival_time"]["text"]

            lang_ru = ScKeynodes.resolve("lang_ru", sc_types.NODE_CONST_CLASS)

            time_link = create_link(time, ScLinkContentType.STRING, link_type=sc_types.LINK_CONST)
            # create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, lang_ru, time_link)
            dist_link = create_link(dist, ScLinkContentType.STRING, link_type=sc_types.LINK_CONST)
            # create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, lang_ru, dist_link)
            arr_time_link = create_link(arr_time, ScLinkContentType.STRING, link_type=sc_types.LINK_CONST)
            # create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, lang_ru, arr_time_link)e

            arr_time_addr = ScKeynodes.resolve("rrel_arrival_time", sc_types.NODE_CONST_ROLE)
            time_addr = ScKeynodes.resolve("rrel_time", sc_types.NODE_CONST_ROLE)
            distance_addr = ScKeynodes.resolve("rrel_distance", sc_types.NODE_CONST_ROLE)

            edge = create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, message_addr, time_link)
            create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, time_addr, edge)
            edge = create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, message_addr, arr_time_link)
            create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, arr_time_addr, edge)
            edge = create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, message_addr, dist_link)
            create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, distance_addr, edge)

            return ScResult.OK    

        except Exception as e:
            self.logger.info(f"FindingPathAgent: finished with an error", e)
            return ScResult.ERROR
    

    def get_place_cords(self, city):
        results = self.gmaps.geocode(city)
        # print(city_results)
        # print(city_results[0])
        # print(city_results[0]["geometry"])
        # print(city_results[0]["geometry"]["location"])
        lat = results[0]["geometry"]["location"]["lat"]
        lng = results[0]["geometry"]["location"]["lng"]
        print('1*******************')
        print(lat, lng)
        print('2*********************')
        res = (lat, lng)

        # res = str(f"{lat}:{lng}")
        return res
    

    def check_cords(self, addr, cords):
        [cords_links_list] = client.get_links_by_content(cords)
        print(cords_links_list)
        if len(cords_links_list)==0:
            link = create_link(cords, ScLinkContentType.STRING, sc_types.LINK_CONST)
            template = ScTemplate()
            template.triple_with_relation(
                addr,
                sc_types.EDGE_D_COMMON_VAR,
                link,
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                ScKeynodes.resolve("nrel_cords", sc_types.NODE_CONST_NOROLE)
            )
            template_generate(template, {})
        

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
    
