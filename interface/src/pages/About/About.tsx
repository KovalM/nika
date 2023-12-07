import * as React from 'react';
import { SC_WEB_URL } from "@constants";

export const About = () => {
    const url = SC_WEB_URL + '/?sys_id=answer_structure&scg_structure_view_only=true';
    return (
        <div className="about-page-container">
            <div className="about-page">
                <div className="map-style"><iframe src={url} style={{width: '1440px', height: '720px', border: 0, borderRadius: '15px'}}/></div>
            </div>
        </div>
    );
}
// action_get_maps_object_info