/** @odoo-module **/

import {ColorList} from "@web/core/colorlist/colorlist";
import {_lt} from "@web/core/l10n/translation";

export class CirclePackingColorList extends ColorList {}
CirclePackingColorList.COLORS = [
    _lt("No color"),
    _lt("White"),
    _lt("Light Gray"),
    _lt("Aero Blue"),
    _lt("French Pass"),
    _lt("Tasman"),
    _lt("Oyster Bay"),
    _lt("Fog"),
    _lt("Fall Green"),
    _lt("Vanilla Ice"),
    _lt("Shalimar"),
    _lt("Cream Brulee"),
];
CirclePackingColorList.template = "hr_governance.CirclePackingColorList";
