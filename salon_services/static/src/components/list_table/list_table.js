/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class ListBookingTable extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({ bookings: [] });

        this.openBookingDetail = this.openBookingDetail.bind(this);

        onWillStart(async () => {
            await this.loadBookings();
        });
    }

    async loadBookings() {
        const today = new Date().toISOString().split("T")[0];

        // --- ambil booking
        const records = await this.orm.searchRead(
            "salon.booking",
            [
                ["booking_date", ">=", today],
                ["state", "!=", "batal"],
            ],
            [
                "booking_id",
                "customer",
                "service_booking_id",
                "package_booking_id",
                "booking_date",
                "state",
                "room_ids",
            ]
        );

        // --- ambil service detail
        const serviceIds = records.flatMap(r => r.service_booking_id || []);
        let servicesById = {};
        if (serviceIds.length) {
            const serviceBookings = await this.orm.read(
                "salon.booking.service",
                serviceIds,
                ["service_id"]
            );
            servicesById = Object.fromEntries(
                serviceBookings.map(s => [s.id, s.service_id?.[1] || ""])
            );
        }

        // --- ambil package detail
        const packageIds = records.flatMap(r => r.package_booking_id || []);
        let packagesById = {};
        if (packageIds.length) {
            const packageBookings = await this.orm.read(
                "salon.booking.package",
                packageIds,
                ["package_id"]
            );
            packagesById = Object.fromEntries(
                packageBookings.map(p => [p.id, p.package_id?.[1] || ""])
            );
        }

        // --- ambil room detail
        const allRoomIds = records.flatMap(r => r.room_ids || []);
        let roomsById = {};
        if (allRoomIds.length) {
            const rooms = await this.orm.read(
                "salon.room",
                allRoomIds,
                ["name"]
            );
            roomsById = Object.fromEntries(
                rooms.map(r => [r.id, r.name])
            );
        }

        // --- mapping ke state
        this.state.bookings = records.map((rec, idx) => {
            const serviceNames = rec.service_booking_id?.map(sid => servicesById[sid]) || [];
            const packageNames = rec.package_booking_id?.map(pid => packagesById[pid]) || [];
            const roomNames = rec.room_ids?.map(rid => roomsById[rid]) || [];

            const booking_date_str = rec.booking_date ? rec.booking_date.split(" ")[0] : "";
            const label = this.computeDayLabel(booking_date_str);

            return {
                id: rec.id,
                no: idx + 1,
                booking_id: rec.booking_id,
                customer: rec.customer?.[1] || "",
                service: serviceNames.length || packageNames.length
                    ? `Service: ${[...serviceNames, ...packageNames].join(", ")}`
                    : "Service: -",
                room: roomNames.length
                    ? `Room: ${roomNames.join(", ")}`
                    : "Room: -",
                booking_date: booking_date_str,
                state: rec.state,
                day_label: label,
            };
        });
    }

    computeDayLabel(dateStr) {
        if (!dateStr) return "";

        const bookingDate = new Date(dateStr);
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        const diffTime = bookingDate - today;
        const diffDays = Math.round(diffTime / (1000 * 60 * 60 * 24));

        if (diffDays === 0) return "Today";
        if (diffDays === 1) return "Tomorrow";
        if (diffDays > 1) return `In ${diffDays} days`;
        return `${Math.abs(diffDays)} days ago`;
    }

    openBookingDetail(bookingId) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "salon.booking",
            res_id: bookingId,
            views: [[false, "form"]],
            target: "current",
        });
    }
}

ListBookingTable.template = "owl.ListBookingTable";