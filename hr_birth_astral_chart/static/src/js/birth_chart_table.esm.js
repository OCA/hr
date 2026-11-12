// @odoo-module
import {Component} from "@odoo/owl";
import {registry} from "@web/core/registry";
import {standardFieldProps} from "@web/views/fields/standard_field_props";

const SIGN_COLORS = [
    "#e8554e",
    "#7db87d",
    "#7ba7c7",
    "#9b7fc0",
    "#e8554e",
    "#7db87d",
    "#7ba7c7",
    "#9b7fc0",
    "#e8554e",
    "#7db87d",
    "#7ba7c7",
    "#9b7fc0",
];

class BirthChartTableWidget extends Component {
    static template = "hr_birth_astral_chart.BirthChartTable";
    static props = {...standardFieldProps};

    get rows() {
        try {
            const value = this.props.record.data[this.props.name];
            return JSON.parse(value || "[]");
        } catch {
            return [];
        }
    }

    signColor(signIndex) {
        return SIGN_COLORS[signIndex] || "#888";
    }
}

registry.category("fields").add("birth_chart_table", {
    component: BirthChartTableWidget,
    supportedTypes: ["char"],
});

export {BirthChartTableWidget};
