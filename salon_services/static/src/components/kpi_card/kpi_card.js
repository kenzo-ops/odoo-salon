/** @odoo-module **/

import { registry } from "@web/core/registry";

const { Component, onWillStart, onWillUnmount, useState } = owl;

export class ServiceKpiCard extends Component {
    
    static props = ['img'];
    
    setup() {
    }
}

ServiceKpiCard.template = "owl.ServiceKpiCard";
