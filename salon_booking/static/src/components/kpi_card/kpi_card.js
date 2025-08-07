/** @odoo-module **/

import { registry } from "@web/core/registry";

const { Component, onWillStart, onWillUnmount, useState } = owl;

export class BookingKpiCard extends Component {
    
    static props = ['img'];
    
    setup() {
    }
}

BookingKpiCard.template = "owl.BookingKpiCard";
