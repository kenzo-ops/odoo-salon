/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class ServiceKpiCard extends Component {
  static props = {
    img: String,
    title: String,
    model: String,
    clickable: { type: Boolean, optional: true },
    className: { type: String, optional: true },
    domain: { type: Array, optional: true },   // ✅ opsional
  };

  setup() {
    this.orm = useService("orm");
    this.action = useService("action");
    this.state = useState({ total: 0 });

    onWillStart(async () => {
      const domain = this.props.domain || [];   // fallback kosong
      const total = await this.orm.searchCount(this.props.model, domain);
      this.state.total = total;
    });
  }

  openListView() {
    if (this.props.clickable) {
      this.action.doAction({
        type: "ir.actions.act_window",
        name: this.props.title,
        res_model: this.props.model,
        views: [
          [false, "list"],
          [false, "form"],
        ],
        target: "current",
        domain: this.props.domain || [],   // fallback kosong
      });
    }
  }
}

ServiceKpiCard.template = "owl.ServiceKpiCard";