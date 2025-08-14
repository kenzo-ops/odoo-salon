/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class ListBookingTable extends Component {
  setup() {
    this.orm = useService("orm");
    this.actionService = useService("action");
    this.state = useState({ bookings: [] });

    // Bind agar this di openBookingDetail tetap benar
    this.openBookingDetail = this.openBookingDetail.bind(this);

    onWillStart(async () => {
      const records = await this.orm.searchRead(
        "salon.booking",
        [],
        [
          "booking_id",
          "customer",
          "service_booking_id",
          "booking_date",
          "state",
          "total_price",
        ]
      );

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

      this.state.bookings = records.map((rec, idx) => ({
        id: rec.id,
        no: idx + 1,
        booking_id: rec.booking_id,
        customer: rec.customer?.[1] || "",
        service:
          (rec.service_booking_id && servicesById[rec.service_booking_id[0]]) ||
          "",
        booking_date: rec.booking_date ? rec.booking_date.split(" ")[0] : "",
        state: rec.state,
        total_price: rec.total_price,
      }));
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
