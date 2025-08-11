/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class ServiceKpiCard extends Component {
    static props = ["img", "title", "model"];

    setup() {
        this.orm = useService("orm");
        this.state = useState({ total: 0 });

        onWillStart(async () => {
            // Hitung total data dari model yang dikirim via props
            const total = await this.orm.searchCount(this.props.model, []);
            this.state.total = total;
        });
    }
}

ServiceKpiCard.template = "owl.ServiceKpiCard";

