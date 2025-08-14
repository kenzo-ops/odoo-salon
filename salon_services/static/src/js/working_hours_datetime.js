/** @odoo-module **/

import { registry } from "@web/core/registry";
import { DateTimeField } from "@web/views/fields/datetime/datetime_field";

export class WorkingHoursDateTime extends DateTimeField {
    setup() {
        super.setup();
        this.startHour = 8;   // Jam mulai
        this.endHour = 17;    // Jam selesai
    }

    mounted() {
        super.mounted();
        if (this.inputRef && this.inputRef.el && this.inputRef.el._flatpickr) {
            this.inputRef.el._flatpickr.set("enableTime", true);
            this.inputRef.el._flatpickr.set("minTime", `${this.startHour}:00`);
            this.inputRef.el._flatpickr.set("maxTime", `${this.endHour}:00`);
        }
    }
}

registry.category("fields").add("working_hours_datetime", WorkingHoursDateTime);
