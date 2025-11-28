/** @odoo-module **/

import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component } from "@odoo/owl";
import { LoyaltyCard } from "../../components/card";
import { useLoyaltyProgram } from "../../utils/loyalty_program";

export class LoyaltyPointsField extends Component {
    static template = "customer_loyalty.LoyaltyPointsField";
    static components = { LoyaltyCard };
    static props = {
        ...standardFieldProps,
    };

    setup() {
        this.program = useLoyaltyProgram();
    }

    get points() {
        return this.props.record.data[this.props.name] || 0.0;
    }
}

export const loyaltyPointsField = {
    component: LoyaltyPointsField,
    displayName: "Loyalty Points Banner",
    supportedTypes: ["float", "integer"],
    fieldDependencies: [{ name: "total_loyalty_points", type: "float" }],
};

registry.category("fields").add("loyalty_points_widget", loyaltyPointsField);