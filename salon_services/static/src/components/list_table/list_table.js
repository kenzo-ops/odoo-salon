/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class ListBookingTable extends Component {
  setup() {
    this.orm = useService("orm");
    this.actionService = useService("action");
    this.state = useState({ bookings: [] });

    this.openBookingDetail = this.openBookingDetail.bind(this);

    onWillStart(async () => {
      const today = new Date().toISOString().split("T")[0];

      const records = await this.orm.searchRead(
        "salon.booking",
        [
          ["booking_date", ">=", today],
          ["state", "!=", "batal"], // <-- exclude cancelled
        ],
        [
          "booking_id",
          "customer",
          "service_booking_id",
          "package_booking_id",
          "booking_date",
          "state",
          "total_price",
        ]
      );

      // --- Ambil semua service
      const allServiceBookingIds = records.flatMap(
        (rec) => rec.service_booking_id || []
      );
      let servicesById = {};
      if (allServiceBookingIds.length) {
        const serviceBookings = await this.orm.read(
          "salon.booking.service",
          allServiceBookingIds,
          ["service_id"]
        );
        servicesById = Object.fromEntries(
          serviceBookings.map((s) => [s.id, s.service_id?.[1] || ""])
        );
      }

      // --- Ambil semua package
      const allPackageBookingIds = records.flatMap(
        (rec) => rec.package_booking_id || []
      );
      let packagesById = {};
      if (allPackageBookingIds.length) {
        const packageBookings = await this.orm.read(
          "salon.booking.package",
          allPackageBookingIds,
          ["package_id"]
        );
        packagesById = Object.fromEntries(
          packageBookings.map((p) => [p.id, p.package_id?.[1] || ""])
        );
      }

      // --- Mapping ke state
      this.state.bookings = records.map((rec, idx) => {
        let names = [];

        if (rec.service_booking_id?.length) {
          names = rec.service_booking_id.map((sid) => servicesById[sid] || "");
        } else if (rec.package_booking_id?.length) {
          names = rec.package_booking_id.map((pid) => packagesById[pid] || "");
        }

        return {
          id: rec.id,
          no: idx + 1,
          booking_id: rec.booking_id,
          customer: rec.customer?.[1] || "",
          service: names.join(", "),
          booking_date: rec.booking_date ? rec.booking_date.split(" ")[0] : "",
          state: rec.state,
          total_price: new Intl.NumberFormat("id-ID", {
            style: "currency",
            currency: "IDR",
            minimumFractionDigits: 0,
          }).format(rec.total_price || 0),
        };
      });
    });
  }

  openBookingDetail(bookingId) {
    this.actionService.doAction({
      type: "ir.actions.act_window",
      res_model: "salon.booking",
      res_id: bookingId,
      views: [[false, "form"]],
      target: "current",
    });
  }
}

ListBookingTable.template = "owl.ListBookingTable";
