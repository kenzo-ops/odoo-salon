/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class ServiceKpiCard extends Component {
  static props = ["img", "title", "model", "clickable", "className"];

  setup() {
    this.orm = useService("orm");
    this.action = useService("action");
    this.state = useState({ total: 0 });

    onWillStart(async () => {
      const total = await this.orm.searchCount(this.props.model, []);
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
      });
    }
  }
}

ServiceKpiCard.template = "owl.ServiceKpiCard";