/** @odoo-module **/

import { registry } from "@web/core/registry";
import { ServiceKpiCard } from "./kpi_card/kpi_card";
import { ServiceChart } from "./chart/chart_renderer";
import { ListBookingTable } from "./list_table/list_table";

const { Component, onWillUnmount, useState } = owl;

export class OwlServiceDashboard extends Component {
    setup() {
        this.state = useState({
            autoRefresh: false,
            countdown: 5,
            intervalId: null,
            isLoading: false,
        });
    }

    toggleAutoRefresh() {
        if (this.state.autoRefresh) {
            clearInterval(this.state.intervalId);
            this.state.autoRefresh = false;
            this.state.countdown = 5;
            this.state.intervalId = null;
        } else {
            this.state.autoRefresh = true;
            this.state.countdown = 5;
            this.startCountdown();
        }
    }

    startCountdown() {
        this.state.intervalId = setInterval(async () => {
            if (!this.state.isLoading) { // hanya hitung kalau tidak loading
                if (this.state.countdown > 1) {
                    this.state.countdown -= 1;
                } else {
                    clearInterval(this.state.intervalId); // stop countdown
                    await this.refreshData(); // mulai refresh
                    if (this.state.autoRefresh) {
                        this.state.countdown = 5;
                        this.startCountdown();
                    }
                }
            }
        }, 1000);
    }

    async refreshData() {
        this.state.isLoading = true;

        // Simulasi proses refresh data
        await new Promise(resolve => setTimeout(resolve, 2000));

        console.log("Data refreshed at", new Date().toLocaleTimeString());

        this.state.isLoading = false;
    }

    onWillUnmount() {
        if (this.state.intervalId) {
            clearInterval(this.state.intervalId);
        }
    }
}

OwlServiceDashboard.template = "owl.OwlServiceDashboard";
OwlServiceDashboard.components = {
    ServiceChart,
    ServiceKpiCard,
    ListBookingTable,
};

registry.category("actions").add("owl.service_dashboard", OwlServiceDashboard);