/** @odoo-module **/

import { registry } from "@web/core/registry";
import { BookingKpiCard } from "./kpi_card/kpi_card";
import { BookingChart } from "./chart/chart_renderer";

const { Component, onWillStart, onWillUnmount, useState } = owl;

export class OwlBookingDashboard extends Component {
    setup() {
    }
}


OwlBookingDashboard.template = "owl.OwlBookingDashboard";
OwlBookingDashboard.components = { BookingKpiCard, BookingChart };
registry.category("actions").add("owl.booking_dashboard", OwlBookingDashboard);
