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
    const [lat, setLat] = useState<string>('53.902287');
    const [lng, setLng] = useState<string>('27.561824');

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
                let cords_str = cords_result[0].data as string;
                const cords_arr = cords_str.split(':', 2);
                console.log(cords_str)
                console.log(cords_arr)
                setLat(cords_arr[0]);
                setLng(cords_arr[1]);
                console.log(lng, lat)
            }
        }    
    
    };
    const registerOnNewMapObject = async () => {
        const question_finished = 'question_finished';

        const baseKeynodes = [
            { id: question_finished, type: ScType.NodeConstClass },
        ];
        const keynodes = await client.resolveKeynodes(baseKeynodes);
        const eventParams = new ScEventParams(keynodes[question_finished], ScEventType.AddOutgoingEdge, (classAddr: ScAddr, edgeAddr: ScAddr, 
            actionAddr: ScAddr, eventId: number) => onNewMapObject(classAddr, edgeAddr, actionAddr, eventId));
        await client.eventsCreate(eventParams); 
    };
    useEffect(() => {
        registerOnNewMapObject();
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
                <iframe className="frame-map" src={`https://yandex.com/map-widget/v1/?l=sat%2Cskl&ll=`+lng+`%2C`+lat+`
                &poi[point]=`+lng+`%2C`+lat+`&mode=poi&z=18&lang=ru`} style={{width: '100%', height: '100%', border: 0, borderRadius: '15px'}} />
            </SCgViewerWrapper>
        </Wrapper>
    );
};
// oid=141245946157&
// ol=biz&