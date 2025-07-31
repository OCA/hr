import {Component, useSubEnv} from "@odoo/owl";
import {Layout} from "@web/search/layout";
import {Many2ManySearchBar} from "../components/search_bar.esm";
import {standardViewProps} from "@web/views/standard_view_props";
import {useBus} from "@web/core/utils/hooks";
import {useModel} from "@web/model/model";
export class CirclePackController extends Component {
    static components = {
        Layout,
        Many2ManySearchBar,
    };
    static props = {
        ...standardViewProps,
        Model: Function,
        Renderer: Function,
    };
    static template = "hr_governance.CirclePackView";

    setup() {
        this.model = useModel(this.props.Model, {
            resModel: this.props.model,
            domain: this.props.domain,
        });
        useSubEnv({model: this.model});
        useBus(this.model.bus, "update", () => {
            this.render(true);
        });
    }
}
