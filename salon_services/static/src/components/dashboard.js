/** @odoo-module **/

import { registry } from "@web/core/registry";
import { ServiceKpiCard } from "./kpi_card/kpi_card";
import { ServiceChart } from "./chart/chart_renderer";
import { ListBookingTable } from "./list_table/list_table";

const { Component, onWillUnmount, useState } = owl;
import { useService } from "@web/core/utils/hooks";

export class OwlServiceDashboard extends Component {
  setup() {
    this.actionService = useService("action");

    this.state = useState({
      autoRefresh: false,
      countdown: 5,
      intervalId: null,
      isLoading: false,
      period: "this_month", // default periode
    });

    // Bind method supaya bisa dipakai di template
    this.createBooking = this.createBooking.bind(this);
    this.onPeriodChange = this.onPeriodChange.bind(this);
    this.toggleAutoRefresh = this.toggleAutoRefresh.bind(this);
  }

  // === Handler untuk dropdown periode ===
  async onPeriodChange(ev) {
    this.state.period = ev.target.value;
    await this.refreshData(); // tampilkan overlay saat ganti periode
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
      if (!this.state.isLoading) {
        if (this.state.countdown > 1) {
          this.state.countdown -= 1;
        } else {
          clearInterval(this.state.intervalId);
          await this.refreshData();
          if (this.state.autoRefresh) {
            this.state.countdown = 5;
            this.startCountdown();
          }
        }
      }
    }, 1000);
  }

  async refreshData() {
    try {
      this.state.isLoading = true;
      document.body.style.overflow = "hidden"; // 🚫 disable scroll
      await new Promise((resolve) => setTimeout(resolve, 2000));
      console.log("Data refreshed at", new Date().toLocaleTimeString());
    } finally {
      this.state.isLoading = false;
      document.body.style.overflow = ""; // ✅ restore scroll
    }
  }

  createBooking() {
    this.actionService.doAction({
      type: "ir.actions.act_window",
      res_model: "salon.booking",
      views: [[false, "form"]],
      target: "current",
    });
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