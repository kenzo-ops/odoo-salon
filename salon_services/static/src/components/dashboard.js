/** @odoo-module **/

import { registry } from "@web/core/registry";
import { ServiceKpiCard } from "./kpi_card/kpi_card";
import { ServiceChart } from "./chart/chart_renderer";

const { Component, onWillStart, onWillUnmount, useState } = owl;

export class OwlServiceDashboard extends Component {
    setup() {
    }
}


OwlServiceDashboard.template = "owl.OwlServiceDashboard";
OwlServiceDashboard.components = { ServiceChart, ServiceKpiCard };
registry.category("actions").add("owl.service_dashboard", OwlServiceDashboard);
