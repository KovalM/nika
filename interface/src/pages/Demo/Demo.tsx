import { useCallback, Fragment } from 'react';
import { Wrapper, ChatWrapper, SCgViewerWrapper } from "./styled";
import { Message } from '@components/Chat/Message';
import { Chat } from '@components/Chat';
import { Date } from '@components/Chat/Date';
import { resolveUserAgent } from '@agents/resolveUserAgent';
import { useChat } from '@hooks/useChat';
import * as React from "react";
import { SC_WEB_URL } from "@constants";
import { lazy, useEffect, useState } from "react";
import { ScAddr, ScEventParams, ScEventType, ScTemplate, ScType } from "ts-sc-client";
import { client } from "@api";

export const Demo = () => {
    const [user, setUser] = useState<ScAddr | null>(null);
    const [isLoading, setIsLoading] = useState(false);

    const { initChat, sendMessage, isAgentAnswer, onFetching, messages, chatRef } = useChat(user);
    const onSend = useCallback(
        async (text: string) => {
            if (!user) return;
            await sendMessage(user, text);
        },
        [user, sendMessage],
    );

    

    useEffect(() => {
        (async () => {
            setIsLoading(true);
            const user = await resolveUserAgent();
            if (!user) return;
            setUser(user);
            await initChat([user]);
            setIsLoading(false);
        })();
    }, [initChat]);
    const [mapUrl, setMapUrl] = useState<string>
    ('https://yandex.com/map-widget/v1/?l=sat%2Cskl&ll=27.561824%2C53.902287&poi[point]=27.561824%2C53.902287&mode=poi&z=18&lang=ru');
    async function onNewMapObject(classAddr: ScAddr, edgeAddr: ScAddr, actionAddr: ScAddr, eventId: number) {
        const action_get_maps_object_info = 'action_get_maps_object_info';
        const nrel_answer = 'nrel_answer';
        const nrel_cords = 'nrel_cords';
        const baseKeynodes = [
            { id: action_get_maps_object_info, type: ScType.NodeConstClass },
            { id: nrel_answer, type: ScType.NodeConstNoRole },
            { id: nrel_cords, type: ScType.NodeConstNoRole },
        ];

        const keynodes = await client.resolveKeynodes(baseKeynodes);

        const structAlias = '_struct';
        const nodeEntityAlias = '_node_entity'
        const cordsLinkAlias = '_cords_link'

        const template = new ScTemplate();
        template.triple(
            keynodes[action_get_maps_object_info],
            ScType.EdgeAccessVarPosPerm,
            actionAddr,
        );
        template.tripleWithRelation(
            actionAddr,
            ScType.EdgeDCommonVar,
            [ScType.NodeVarStruct, structAlias],
            ScType.EdgeAccessVarPosPerm,
            keynodes[nrel_answer],
        );
        template.triple(
            structAlias,
            ScType.EdgeAccessVarPosPerm,
            [ScType.NodeVar, nodeEntityAlias],
        );
        template.tripleWithRelation(
            nodeEntityAlias,
            ScType.EdgeDCommonVar,
            [ScType.LinkVar, cordsLinkAlias],
            ScType.EdgeAccessVarPosPerm,
            keynodes[nrel_cords],
        );
        const result = await client.templateSearch(template);
        
        if (result.length) {
            const link = result[0].get(cordsLinkAlias);
            const cords_result = await client.getLinkContents([link]);
            if (cords_result.length) {
                const cords_str = cords_result[0].data as string;
                const cords_arr = cords_str.split(':', 2);
                console.log(cords_str)
                console.log(cords_arr)
                setMapUrl(`https://yandex.com/map-widget/v1/?l=sat%2Cskl&ll=`+cords_arr[1]+`%2C`+cords_arr[0]+`&poi[point]=`+cords_arr[1]+`%2C`+cords_arr[0]+`&mode=poi&z=18&lang=ru`)
                console.log(cords_arr[1], cords_arr[0])
            }
        }    
    
    };
    async function onNewRoute(classAddr: ScAddr, edgeAddr: ScAddr, actionAddr: ScAddr, eventId: number) {
        const action_get_path_between_objects = 'action_get_path_between_objects';
        const rrel_1 = 'rrel_1';
        const rrel_first_cords = 'rrel_first_cords';
        const rrel_second_cords = 'rrel_second_cords';
        const baseKeynodes = [
            { id: action_get_path_between_objects, type: ScType.NodeConstClass },
            { id: rrel_1, type: ScType.NodeConstRole },
            { id: rrel_first_cords, type: ScType.NodeConstRole },
            { id: rrel_second_cords, type: ScType.NodeConstRole },
        ];

        const keynodes = await client.resolveKeynodes(baseKeynodes);

        const messageAlias = '_message';
        const firstCordsAlias = '_firstCordsLink';
        const secondCordsAlias = '_secondCordsLink';

        const template = new ScTemplate();
        template.triple(
            keynodes[action_get_path_between_objects],
            ScType.EdgeAccessVarPosPerm,
            actionAddr,
        );
        template.tripleWithRelation(
            actionAddr,
            ScType.EdgeAccessVarPosPerm,
            [ScType.NodeVar,messageAlias],
            ScType.EdgeAccessVarPosPerm,
            keynodes[rrel_1],
        );
        template.tripleWithRelation(
            messageAlias,
            ScType.EdgeAccessVarPosPerm,
            [ScType.LinkVar,firstCordsAlias],
            ScType.EdgeAccessVarPosPerm,
            keynodes[rrel_first_cords],
        );
        template.tripleWithRelation(
            messageAlias,
            ScType.EdgeAccessVarPosPerm,
            [ScType.LinkVar,secondCordsAlias],
            ScType.EdgeAccessVarPosPerm,
            keynodes[rrel_second_cords],
        );
        const result = await client.templateSearch(template);

        console.log(`beforeFound`)
        if (result.length) {
            console.log(`found`)
            const firstCordsLink = result[0].get(firstCordsAlias);
            const firstCordsResult = await client.getLinkContents([firstCordsLink]);
            let firstCordsArr;
            if (firstCordsResult.length) {
                const firstCordsStr = firstCordsResult[0].data as string;
                firstCordsArr = firstCordsStr.split(':', 2);
                console.log(firstCordsStr)
            }
            const secondCordsLink = result[0].get(secondCordsAlias);
            const secondCordsResult = await client.getLinkContents([secondCordsLink]);
            let secondCordsArr;
            if (secondCordsResult.length) {
                const secondCordsStr = secondCordsResult[0].data as string;
                secondCordsArr = secondCordsStr.split(':', 2);
                console.log(secondCordsStr)
            }
            console.log(`https://yandex.by/map-widget/v1/?mode=routes&rtext=`+firstCordsArr[0]+`%2C`+firstCordsArr[1]+`~`+secondCordsArr[0]+`%2C`+secondCordsArr[1]+`&rtt=pd`)
            setMapUrl(`https://yandex.by/map-widget/v1/?mode=routes&rtext=`+firstCordsArr[0]+`%2C`+firstCordsArr[1]+`~`+secondCordsArr[0]+`%2C`+secondCordsArr[1]+`&rtt=pd`)
        }

    };
    const registerMapEvent = async () => {
        const question_finished = 'question_finished';

        const baseKeynodes = [
            { id: question_finished, type: ScType.NodeConstClass },
        ];
        const keynodes = await client.resolveKeynodes(baseKeynodes);
        const newObjectEventParams = new ScEventParams(keynodes[question_finished], ScEventType.AddOutgoingEdge, (classAddr: ScAddr, edgeAddr: ScAddr,
            actionAddr: ScAddr, eventId: number) => onNewMapObject(classAddr, edgeAddr, actionAddr, eventId));
        const newRouteEventParams = new ScEventParams(keynodes[question_finished], ScEventType.AddOutgoingEdge, (classAddr: ScAddr, edgeAddr: ScAddr,
            actionAddr: ScAddr, eventId: number) => onNewRoute(classAddr, edgeAddr, actionAddr, eventId));
        await client.eventsCreate(newObjectEventParams);
        await client.eventsCreate(newRouteEventParams);
    };
    useEffect(() => {
        registerMapEvent();
    },[]);
    return (
        <Wrapper>
            <ChatWrapper>
                <Chat
                    ref={chatRef}
                    isLoading={isLoading}
                    onSend={onSend}
                    onFetching={onFetching}
                    isAgentAnswer={isAgentAnswer}
                >
                    {messages.map((item, ind) => {
                        const prevItem = messages[ind - 1];
                        const showDate = item.date !== prevItem?.date;
                        return (
                            <Fragment key={item.id}>
                                {showDate && <Date date={item.date} />}
                                <Message
                                    isLeft={!!user && !item.author.equal(user)}
                                    time={item.time}
                                    isLoading={item.isLoading}
                                >
                                    {item.text}
                                </Message>
                            </Fragment>
                        );
                    })}
                </Chat>
            </ChatWrapper>
            <SCgViewerWrapper>
                <iframe className="frame-map" src={mapUrl} style={{width: '100%', height: '100%', border: 0, borderRadius: '15px'}} />
            </SCgViewerWrapper>
        </Wrapper>
    );
};

/* <div style="position:relative;overflow:hidden;"><a href="https://yandex.by/maps/157/minsk/?utm_medium=mapframe&utm_source=maps"
        style="color:#eee;font-size:12px;position:absolute;top:0px;">Минск</a>
        <a href="https://yandex.by/maps/157/minsk/?ll=27.571522%2C53.902657&mode=Routes&rtext=53.908470%2C27.479467~53.914596%2C27.663299&rtt=auto
        &ruri=~ymapsbm1%3A%2F%2Ftransit%2Fstop%3Fid%3Dstation__lh_9614089&utm_medium=mapframe&utm_source=maps&z=11.72" 
        style="color:#eee;font-size:12px;position:absolute;top:14px;">Яндекс Карты</a>
        <iframe src="https://yandex.by/map-widget/v1/?ll=27.571522%2C53.902657&mode=Routes&rtext=53.908470%2C27.479467~53.914596%2C27.663299
        &rtt=auto&ruri=~ymapsbm1%3A%2F%2Ftransit%2Fstop%3Fid%3Dstation__lh_9614089&z=11.72" width="560" height="400" frameborder="1" 
        allowfullscreen="true" style="position:relative;"></iframe></div> */
// oid=141245946157&
// ol=biz&