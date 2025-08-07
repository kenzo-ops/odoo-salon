    /** @odoo-module */

import { Component, useRef, onMounted, onWillUpdateProps } from "@odoo/owl";

export class ServiceChart extends Component {
    static props = ["width","type", "isDarkMode", "title"];
    static template = "owl.ServiceChart";

    setup() {
        this.canvasRef = useRef("chartCanvas");
        this.chartInstance = null;

        onMounted(() => this.renderChart());
        onWillUpdateProps(() => this.renderChart());
    }

    async renderChart() {
        await this.ensureChartJsLoaded();

        const canvas = this.canvasRef.el;
        if (!canvas) return;

        const ctx = canvas.getContext("2d");

        // Dummy data
        const dummyLabels = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat"];
        const dummyValues = [12, 19, 3, 5, 7];

        const lightColors = ['#5E60CE', '#6930C3', '#7400B8', '#64DFDF', '#5390D9'];
        const darkColors = ['#FFC300', '#FF5733', '#C70039', '#900C3F', '#581845'];
        const backgroundColors = dummyValues.map((_, i) =>
            this.props.isDarkMode ? darkColors[i % darkColors.length] : lightColors[i % lightColors.length]
        );

        const textColor = this.props.isDarkMode ? "#FFFFFF" : "#000000";
        const gridColor = this.props.isDarkMode ? "rgba(255,255,255,0.1)" : "rgba(0,0,0,0.05)";

        if (this.chartInstance) {
            this.chartInstance.destroy();
        }

        this.chartInstance = new Chart(ctx, {
            type: this.props.type || "bar",
            data: {
                labels: dummyLabels,
                datasets: [
                    {
                        label: "Jumlah Booking",
                        data: dummyValues,
                        backgroundColor: backgroundColors,
                        borderColor: backgroundColors,
                        borderWidth: 1.5,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                animation: {
                    duration: 1000,
                    easing: 'easeOutBounce'
                },
                plugins: {
                    legend: {
                        display: this.props.type !== "bar",
                        labels: {
                            color: textColor,
                        },
                    },
                    title: {
                        display: true,
                        text: "Statistik Booking Harian",
                        color: textColor,
                        font: {
                            size: 14,
                            weight: 'normal',
                            family: 'Poppins',
                        },
                        position: 'bottom',
                    },
                },
                scales: this.props.type === "bar" ? {
                    y: {
                        beginAtZero: true,
                        ticks: { color: textColor },
                        grid: { color: gridColor },
                    },
                    x: {
                        ticks: { color: textColor },
                        grid: { color: gridColor },
                    },
                } : {},
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
