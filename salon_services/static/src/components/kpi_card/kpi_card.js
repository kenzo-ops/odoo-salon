/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";

export class ServiceKpiCard extends Component {
  static props = ['img', 'title'];

  setup() {
  }
}

ServiceKpiCard.template = "owl.ServiceKpiCard";