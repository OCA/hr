import {ColorList} from "@web/core/colorlist/colorlist";
import {_t} from "@web/core/l10n/translation";

export class CirclePackingColorList extends ColorList {}
CirclePackingColorList.COLORS = [
    _t("No color"),
    _t("White"),
    _t("Light Gray"),
    _t("Aero Blue"),
    _t("French Pass"),
    _t("Tasman"),
    _t("Oyster Bay"),
    _t("Fog"),
    _t("Fall Green"),
    _t("Vanilla Ice"),
    _t("Shalimar"),
    _t("Cream Brulee"),
];
CirclePackingColorList.template = "hr_governance.CirclePackingColorList";
