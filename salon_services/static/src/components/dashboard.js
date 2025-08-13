/** @odoo-module **/

import { registry } from "@web/core/registry";
import { ServiceKpiCard } from "./kpi_card/kpi_card";
import { ServiceChart } from "./chart/chart_renderer";
import { ListBookingTable } from "./list_table/list_table";

const { Component, onWillStart, onWillUnmount, useState } = owl;

export class OwlServiceDashboard extends Component {
    setup() {
    }
}


OwlServiceDashboard.template = "owl.OwlServiceDashboard";
OwlServiceDashboard.components = { ServiceChart, ServiceKpiCard, ListBookingTable };
registry.category("actions").add("owl.service_dashboard", OwlServiceDashboard);