import {CirclePackController} from "./circlepack_controller.esm";
import {CirclePackModel} from "./circlepack_model.esm";
import {CirclePackRenderer} from "./circlepack_renderer.esm";
import {_t} from "@web/core/l10n/translation";
import {registry} from "@web/core/registry";

export const circlepackView = {
    type: "circle_pack",
    display_name: _t("Circle Pack"),
    icon: "fa fa-share-alt o_hierarchy_icon",
    isMobileFriendly: false,
    Controller: CirclePackController,
    Model: CirclePackModel,
    Renderer: CirclePackRenderer,
    searchMenuTypes: ["filter"],

    props(genericProps, view) {
        return {
            ...genericProps,
            Model: view.Model,
            Renderer: view.Renderer,
        };
    },
};

registry.category("views").add("circle_pack", circlepackView);
