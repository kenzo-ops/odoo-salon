/** @odoo-module **/

import {
  Component,
  useRef,
  onMounted,
  onWillUpdateProps,
  useState,
} from "@odoo/owl";

export class ServiceChart extends Component {
  static props = ["width", "type", "isDarkMode", "title", "chartMode"];
  static template = "owl.ServiceChart";

  setup() {
    this.state = useState({ total: 0 });
    this.canvasRef = useRef("chartCanvas");
    this.chartInstance = null;

    onMounted(() => {
      if (this.canvasRef.el) {
        this.canvasRef.el.style.cursor = "pointer";
      }
      this.loadChartData();
    });

    onWillUpdateProps(() => this.loadChartData());
  }

  async loadChartData() {
    if (this.props.chartMode === "service_status") {
      await this.fetchServiceStatusChart();
    } else if (this.props.chartMode === "booking_trend") {
      await this.fetchBookingTrendChart();
    } else if (this.props.chartMode === "booking_status") {
      await this.fetchBookingStatusChart();
    }
  }

  // Chart: Status Service
  async fetchServiceStatusChart() {
    const records = await this.env.services.orm.searchRead(
      "salon.services",
      [],
      ["state"]
    );

    const states = ["active", "inactive"];
    const counts = states.map(
      (s) => records.filter((r) => r.state === s).length
    );

    this.state.total = counts.reduce((a, b) => a + b, 0);

    await this.renderChart(["Active", "Inactive"], counts, "Jumlah Layanan", {
      Active: "active",
      Inactive: "inactive",
    });
  }

  // Chart: Tren Booking per Tanggal
  async fetchBookingTrendChart() {
    const records = await this.env.services.orm.searchRead(
      "salon.booking",
      [],
      ["booking_date"]
    );

    const countPerDate = {};
    for (const rec of records) {
      const dateStr = rec.booking_date
        ? rec.booking_date.split(" ")[0]
        : "Unknown";
      countPerDate[dateStr] = (countPerDate[dateStr] || 0) + 1;
    }

    const labels = Object.keys(countPerDate).sort();
    const values = labels.map((l) => countPerDate[l]);

    this.state.total = values.reduce((a, b) => a + b, 0);

    await this.renderChart(labels, values, "Tren Booking");
  }

  // Chart: Status Booking
  async fetchBookingStatusChart() {
    const records = await this.env.services.orm.searchRead(
      "salon.booking",
      [],
      ["state"]
    );

    const statusMap = {
      Draft: "draft",
      Confirmed: "konfirmasi",
      "Check In": "checkin",
      "Check Out": "checkout",
      Canceled: "batal",
    };

    const values = Object.values(statusMap).map(
      (s) => records.filter((r) => r.state === s).length
    );

    this.state.total = values.reduce((a, b) => a + b, 0);

    await this.renderChart(
      Object.keys(statusMap),
      values,
      "Status Booking",
      statusMap
    );
  }

  // Render Chart
  async renderChart(labels, values, labelTitle, statusMap = null) {
    await this.ensureChartJsLoaded();

    const canvas = this.canvasRef.el;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");

    const lightColors = ["#5E60CE", "#5390D9", "#48BFE3", "#64DFDF", "#80FFDB"];
    const darkColors = ["#FFC300", "#FF5733", "#C70039", "#900C3F", "#581845"];
    const backgroundColors = values.map((_, i) =>
      this.props.isDarkMode
        ? darkColors[i % darkColors.length]
        : lightColors[i % lightColors.length]
    );

    const textColor = this.props.isDarkMode ? "#FFFFFF" : "#000000";

    if (this.chartInstance) {
      this.chartInstance.destroy();
    }

    const isFillChart = ["line", "radar"].includes(this.props.type);

    this.chartInstance = new Chart(ctx, {
      type: this.props.type || "pie",
      data: {
        labels,
        datasets: [
          {
            label: labelTitle,
            data: values,
            fill: isFillChart,
            backgroundColor: isFillChart
              ? backgroundColors.map((c) => c + "33")
              : backgroundColors,
            borderColor: backgroundColors,
            borderWidth: 1.5,
          },
        ],
      },
      options: {
        responsive: true,
        plugins: {
          legend: { labels: { color: textColor } },
        },
        onClick: (evt, elements) => {
          if (elements.length > 0) {
            const index = elements[0].index;
            const clickedLabel = labels[index];

            // Mode booking_trend → filter berdasarkan tanggal
            if (
              this.props.chartMode === "booking_trend" &&
              clickedLabel !== "Unknown"
            ) {
              this.env.services.action.doAction({
                type: "ir.actions.act_window",
                name: `Bookings on ${clickedLabel}`,
                res_model: "salon.booking",
                view_mode: "list,form",
                views: [
                  [false, "list"],
                  [false, "form"],
                ],
                domain: [
                  ["booking_date", ">=", clickedLabel + " 00:00:00"],
                  ["booking_date", "<=", clickedLabel + " 23:59:59"],
                ],
                target: "current",
              });
            }

            // Mode service_status atau booking_status → filter berdasarkan state
            else if (statusMap) {
              const statusValue = statusMap[clickedLabel];
              if (statusValue) {
                this.env.services.action.doAction({
                  type: "ir.actions.act_window",
                  name: `Filtered: ${clickedLabel}`,
                  res_model:
                    this.props.chartMode === "service_status"
                      ? "salon.services"
                      : "salon.booking",
                  view_mode: "list,form",
                  views: [
                    [false, "list"],
                    [false, "form"],
                  ],
                  domain: [["state", "=", statusValue]],
                  target: "current",
                });
              }
            }
          }
        },
        scales:
          this.props.type === "bar" || this.props.type === "line"
            ? {
                x: { ticks: { color: textColor } },
                y: { ticks: { color: textColor } },
              }
            : {},
      },
    });
  }

  async ensureChartJsLoaded() {
    if (!window.Chart) {
      await new Promise((resolve, reject) => {
        const script = document.createElement("script");
        script.src =
          "https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js";
        script.onload = resolve;
        script.onerror = reject;
        document.head.appendChild(script);
      });
    }
  }
}
