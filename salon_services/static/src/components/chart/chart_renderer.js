/** @odoo-module **/

import { Component, useRef, onMounted, onWillUpdateProps, useState } from "@odoo/owl";

export class ServiceChart extends Component {
    static props = ["width", "type", "isDarkMode", "title", "chartMode"];
    static template = "owl.ServiceChart";

    setup() {
        this.state = useState({ total: 0 });
        this.canvasRef = useRef("chartCanvas");
        this.chartInstance = null;

        onMounted(() => this.loadChartData());
        onWillUpdateProps(() => this.loadChartData());
    }

    async loadChartData() {
        if (this.props.chartMode === "service_status") {
            await this.fetchServiceStatusChart();
        } else if (this.props.chartMode === "booking_trend") {
            await this.fetchBookingTrendChart();
        } else if (this.props.chartMode === "top_services") {
            await this.fetchTopServicesChart();
        }
    }

    /** 1. Chart Status Layanan **/
    async fetchServiceStatusChart() {
        const records = await this.env.services.orm.searchRead(
            "salon.services",
            [],
            ["state"]
        );

        const activeCount = records.filter(r => r.state === "active").length;
        const inactiveCount = records.filter(r => r.state === "inactive").length;

        this.state.total = activeCount + inactiveCount;

        await this.renderChart(
            ["Active", "Inactive"],
            [activeCount, inactiveCount],
            "Jumlah Layanan"
        );
    }

    /** 2. Chart Tren Booking **/
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
        const values = labels.map(l => countPerDate[l]);

        this.state.total = values.reduce((a, b) => a + b, 0);

        await this.renderChart(labels, values, "Tren Booking");
    }

    /** 3. Chart Top Services **/
    async fetchTopServicesChart() {
        const records = await this.env.services.orm.call(
            "salon.booking.service",
            "get_top_services",
            [],
            { limit: 5 }
        );

        const labels = [];
        const values = [];
        let totalSum = 0;

        for (const r of records) {
            if (Array.isArray(r.service_id) && r.service_id.length > 1) {
                labels.push(r.service_id[1]);

                const val = r.total || 0;
                totalSum += val;

                // Untuk chart, jika val 0 kasih nilai kecil supaya chart gak kosong
                values.push(val > 0 ? val : 0.0001);
            }
        }

        if (labels.length === 0) {
            labels.push("No Data");
            values.push(0.0001);
            this.state.total = 0;
        } else {
            this.state.total = totalSum; // SET TOTAL DI SINI, PASTIKAN TIDAK DI OVERRIDE
        }

        await this.renderChart(labels, values, "Top Services");
    }

    async renderChart(labels, values, labelTitle) {
        await this.ensureChartJsLoaded();

        const canvas = this.canvasRef.el;
        if (!canvas) return;

        const ctx = canvas.getContext("2d");

        const lightColors = ['#5E60CE', '#5390D9', '#48BFE3', '#64DFDF', '#80FFDB'];
        const darkColors = ['#FFC300', '#FF5733', '#C70039', '#900C3F', '#581845'];
        const backgroundColors = values.map(
            (_, i) => this.props.isDarkMode ? darkColors[i % darkColors.length] : lightColors[i % lightColors.length]
        );

        const textColor = this.props.isDarkMode ? "#FFFFFF" : "#000000";

        if (this.chartInstance) {
            this.chartInstance.destroy();
        }

        const isFillChart = ['line', 'radar'].includes(this.props.type);

        this.chartInstance = new Chart(ctx, {
            type: this.props.type || "pie",
            data: {
                labels: labels,
                datasets: [{
                    label: labelTitle,
                    data: values,
                    fill: isFillChart,
                    backgroundColor: isFillChart
                        ? backgroundColors.map(c => c + '33')
                        : backgroundColors,
                    borderColor: backgroundColors,
                    borderWidth: 1.5,
                }],
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        labels: { color: textColor }
                    },
                },
                scales: this.props.type === "bar" || this.props.type === "line"
                    ? {
                        x: { ticks: { color: textColor } },
                        y: { ticks: { color: textColor } }
                    }
                    : {}
            },
        });
    }

    async ensureChartJsLoaded() {
        if (!window.Chart) {
            await new Promise((resolve, reject) => {
                const script = document.createElement("script");
                script.src = "https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js";
                script.onload = resolve;
                script.onerror = reject;
                document.head.appendChild(script);
            });
        }
    }
}
