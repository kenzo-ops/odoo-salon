/** @odoo-module **/

import {
  Component,
  useRef,
  onMounted,
  onWillUpdateProps,
  useState,
} from "@odoo/owl";

export class ServiceChart extends Component {
  static props = [
    "width",
    "type",
    "isDarkMode",
    "title",
    "chartMode",
    "className",
  ];
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
      await this.fetchTopCustomersChart();
    } else if (this.props.chartMode === "booking_trend") {
      await this.fetchBookingTrendChart();
    } else if (this.props.chartMode === "booking_status") {
      await this.fetchBookingStatusChart();
    }
  }

  // === Helper: Ambil date range dari dropdown periode ===
  getDateRangeFromPeriod() {
    const dropdown = document.querySelector(
      ".salon-dashboard-container select"
    );
    const selectedPeriod = dropdown ? dropdown.value : "this_month";

    const now = new Date();
    let startDate = null;
    let endDate = null;

    if (selectedPeriod === "today") {
      startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate());
      endDate = new Date(startDate);
      endDate.setDate(endDate.getDate() + 1);
    } else if (selectedPeriod === "yesterday") {
      startDate = new Date(
        now.getFullYear(),
        now.getMonth(),
        now.getDate() - 1
      );
      endDate = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    } else if (selectedPeriod === "this_week") {
      const day = now.getDay();
      const diff = now.getDate() - day + (day === 0 ? -6 : 1);
      startDate = new Date(now.setDate(diff));
      startDate.setHours(0, 0, 0, 0);
      endDate = new Date(startDate);
      endDate.setDate(startDate.getDate() + 7);
    } else if (selectedPeriod === "last_week") {
      const day = now.getDay();
      const diff = now.getDate() - day - 6;
      startDate = new Date(now.setDate(diff));
      startDate.setHours(0, 0, 0, 0);
      endDate = new Date(startDate);
      endDate.setDate(startDate.getDate() + 7);
    } else if (selectedPeriod === "this_month") {
      startDate = new Date(now.getFullYear(), now.getMonth(), 1);
      endDate = new Date(now.getFullYear(), now.getMonth() + 1, 1);
    } else if (selectedPeriod === "last_month") {
      startDate = new Date(now.getFullYear(), now.getMonth() - 1, 1);
      endDate = new Date(now.getFullYear(), now.getMonth(), 1);
    } else if (selectedPeriod === "this_year") {
      startDate = new Date(now.getFullYear(), 0, 1);
      endDate = new Date(now.getFullYear() + 1, 0, 1);
    } else if (selectedPeriod === "last_year") {
      startDate = new Date(now.getFullYear() - 1, 0, 1);
      endDate = new Date(now.getFullYear(), 0, 1);
    }

    return { startDate, endDate };
  }

  // === Chart Top Customers dengan filter periode ===
  async fetchTopCustomersChart() {
    const records = await this.env.services.orm.searchRead(
      "salon.booking",
      [],
      ["customer", "booking_date"]
    );

    const { startDate, endDate } = this.getDateRangeFromPeriod();

    const customerCounts = {};
    for (const rec of records) {
      if (!rec.customer || !rec.booking_date) continue;

      const dateStr = rec.booking_date.split(" ")[0];
      const dateObj = new Date(dateStr);

      if (startDate && endDate) {
        if (dateObj >= startDate && dateObj < endDate) {
          const custName = rec.customer[1];
          customerCounts[custName] = (customerCounts[custName] || 0) + 1;
        }
      } else {
        const custName = rec.customer[1];
        customerCounts[custName] = (customerCounts[custName] || 0) + 1;
      }
    }

    const sorted = Object.entries(customerCounts).sort((a, b) => b[1] - a[1]);
    const top5 = sorted.slice(0, 5);

    const labels = top5.map(([name]) => name);
    const values = top5.map(([_, count]) => count);

    this.state.total = values.reduce((a, b) => a + b, 0);

    await this.renderChart(labels, values, "Top Customers");
  }

  // === Booking Trend dengan filter periode ===
  async fetchBookingTrendChart() {
    const records = await this.env.services.orm.searchRead(
      "salon.booking",
      [],
      ["booking_date"]
    );

    const { startDate, endDate } = this.getDateRangeFromPeriod();

    const countPerDate = {};
    for (const rec of records) {
      if (!rec.booking_date) continue;
      const dateStr = rec.booking_date.split(" ")[0];
      const dateObj = new Date(dateStr);

      if (startDate && endDate) {
        if (dateObj >= startDate && dateObj < endDate) {
          countPerDate[dateStr] = (countPerDate[dateStr] || 0) + 1;
        }
      } else {
        countPerDate[dateStr] = (countPerDate[dateStr] || 0) + 1;
      }
    }

    const labels = Object.keys(countPerDate).sort();
    const values = labels.map((l) => countPerDate[l]);

    this.state.total = values.reduce((a, b) => a + b, 0);

    await this.renderChart(labels, values, "Tren Booking");
  }

  // === Booking Status ===
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

  // === Render Chart ===
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

    const noDataPlugin = {
      id: "noData",
      afterDraw: (chart) => {
        if (
          chart.data.datasets[0].data.length === 0 ||
          chart.data.datasets[0].data.every((v) => v === 0)
        ) {
          const { ctx, chartArea } = chart;
          const { left, right, top, bottom } = chartArea;
          const x = (left + right) / 2;
          const y = (top + bottom) / 2;

          ctx.save();
          ctx.textAlign = "center";
          ctx.textBaseline = "middle";
          ctx.fillStyle = textColor;
          ctx.font = "18px sans-serif";

          let message = "";
          if (this.props.chartMode === "booking_trend") {
            message = "There are no bookings during this period";
          } else if (this.props.chartMode === "service_status") {
            message = "No customers made bookings during this period";
          }else if (this.props.chartMode === "booking_status") {
            message = "No bookings occurred during this period";
          } else {
            message = "No data available for this period";
          }

          ctx.fillText(message, x, y);
          ctx.restore();
        }
      },
    };

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
        scales:
          this.props.type === "bar" || this.props.type === "line"
            ? {
                x: { ticks: { color: textColor } },
                y: {
                  ticks: {
                    color: textColor,
                    precision: 0,
                    stepSize: 1,
                  },
                },
              }
            : {},
        onClick: (event, elements) => {
          if (!elements.length) return;

          const idx = elements[0].index;
          const label = labels[idx];
          const value = values[idx];

          console.log("Klik chart:", { label, value });

          let model = null;
          let domain = [];

          if (this.props.chartMode === "service_status") {
            model = "salon.booking";
            domain = [["customer.name", "=", label]];
          } else if (this.props.chartMode === "booking_status") {
            model = "salon.booking";
            if (statusMap && statusMap[label]) {
              domain = [["state", "=", statusMap[label]]];
            }
          } else if (this.props.chartMode === "booking_trend") {
            model = "salon.booking";
            domain = [
              ["booking_date", ">=", label],
              ["booking_date", "<", label + " 23:59:59"],
            ];
          }

          if (model) {
            this.env.services.action.doAction({
              type: "ir.actions.act_window",
              name: labelTitle + " - " + label,
              res_model: model,
              views: [
                [false, "list"],
                [false, "form"],
              ],
              target: "current",
              domain,
            });
          }
        },
      },
      plugins: [noDataPlugin],
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
