/** @odoo-module **/

import {CirclePackingColorList} from "./circlepack_colorlist.esm";
import {ColorPickerField} from "@web/views/fields/color_picker/color_picker_field";
import {registry} from "@web/core/registry";

class CirclePackColorPickerField extends ColorPickerField {
    static template = "hr_governance.CirclePackColorPickerField";
    static components = {CirclePackingColorList};
}

export const circlecepackcolorPickerField = {
    component: CirclePackColorPickerField,
    supportedTypes: ["integer"],
    extractProps: ({viewType}) => ({
        canToggle: viewType !== "list",
    }),
};

registry
    .category("fields")
    .add("circlepack_color_picker", circlecepackcolorPickerField);
