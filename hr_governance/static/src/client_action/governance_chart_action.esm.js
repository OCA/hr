/* eslint-disable no-undef */
import {
    Component,
    onMounted,
    onWillStart,
    useRef,
    useState,
    useSubEnv,
} from "@odoo/owl";
import {useBus, useService} from "@web/core/utils/hooks";
import {GovernanceChartRenderer} from "@hr_governance/components/governance_chart_renderer.esm";
import {Many2ManySearchBar} from "@hr_governance/components/search_bar.esm";
import {Splitter} from "@hr_governance/components/splitter.esm";
import {buildHierarchy} from "@hr_governance/utils/helpers.esm";
import {registry} from "@web/core/registry";
import {Layout} from "@web/search/layout";
import {SearchModel} from "@web/search/search_model";
import {View} from "@web/views/view";
import {user} from "@web/core/user";
import {rpc} from "@web/core/network/rpc";

export class GovernanceChartComponent extends Component {
    static template = "hr_governance.GovernanceChartComponent";
    static components = {
        GovernanceChartRenderer,
        View,
        Splitter,
        Layout,
        Many2ManySearchBar,
    };

    setup() {
        this.orm = useService("orm");
        this.ui = useService("ui");
        this.viewService = useService("view");
        this.searchModel = new SearchModel(this.env, {
            orm: this.orm,
            view: this.viewService,
            field: useService("field"),
            name: useService("name"),
            dialog: useService("dialog"),
        });

        useSubEnv({
            searchModel: this.searchModel,
        });

        this.state = useState({
            data: null,
            activeResId: false,
            searchResults: [],
            chartDimensions: {width: 0, height: 0},
            allowed_edit_governance_ids: [],
        });

        this.containerRef = useRef("container");
        this.chartAreaRef = useRef("chartArea");
        this.formAreaRef = useRef("formArea");
        this.chartRendererAPI = null;

        onWillStart(async () => {
            const config = {
                resModel: "governance.circle",
                searchMenuTypes: ["filter", "favorite"],
            };
            const result = await this.viewService.loadViews({
                resModel: "governance.circle",
                views: [[false, "search"]],
                context: {},
            });
            const searchView = result.views.search;
            config.searchViewArch = searchView.arch;
            config.searchViewFields = result.fields;
            config.irFilters = searchView.irFilters;

            await this.searchModel.load(config);
            await this.handleFullUpdate();

            this.is_grayscale_on = await this.orm.call(
                "governance.circle",
                "get_greyscale_mode_param"
            );
            this.is_stripe_all_roles = await this.orm.call(
                "governance.circle",
                "get_stripe_param"
            );

            this.isGovernanceAdmin = await user.hasGroup(
                "hr_governance.governance_group_manager"
            );
            this.state.allowed_edit_governance_ids =
                user.context.allowed_edit_governance_ids;
        });

        onMounted(() => {
            this.state.chartDimensions = {
                width: this.chartAreaRef.el.offsetWidth,
                height: this.chartAreaRef.el.offsetHeight,
            };
        });

        // Event
        useBus(this.searchModel, "update", async () => {
            await this.handleSearchUpdate();
        });
        useBus(this.env.bus, "governance:form_saved_record", () => {
            this.handleFullUpdate();
        });
        useBus(this.env.bus, "governance:form_deleted_record", (ev) => {
            // Find parent of the deleted
            const deletedResId = ev.detail.deletedResId;
            const deletedNode = d3
                .hierarchy(this.state.data)
                .descendants()
                .find((d) => d.data.id === deletedResId);
            const parentNode = deletedNode ? deletedNode.ancestors()[1] : null;

            this.handleFullUpdate();
            this.state.activeResId = parentNode?.data.id || this.data.id;
        });
    }

    async handleFullUpdate() {
        const allData = await this.orm.call(
            "governance.circle",
            "get_hierarchy_data",
            [[]],
            {}
        );
        this.state.data = buildHierarchy(allData);
        await this.handleSearchUpdate();

        const context = await rpc("/web/session/get_session_info");
        this.state.allowed_edit_governance_ids =
            context.user_context.allowed_edit_governance_ids;
    }

    async handleSearchUpdate() {
        if (this.searchModel.domain.length) {
            const searchResultIds = await this.orm.search(
                "governance.circle",
                this.searchModel.domain
            );
            this.state.searchResults = searchResultIds;
        } else {
            this.state.searchResults = [];
        }
    }

    handleResize = (e) => {
        const containerRect = this.containerRef.el.getBoundingClientRect();
        const mouseX = e.clientX - containerRect.left;

        const offsetRight = containerRect.width - mouseX;
        const chartWidth = Math.max(containerRect.width - offsetRight, 1);

        this.chartAreaRef.el.style.width = chartWidth + "px";
        this.chartAreaRef.el.style.flex = "";

        this.formAreaRef.el.style.width = offsetRight + "px";
        this.formAreaRef.el.style.flex = "";

        this.state.chartDimensions = {
            width: chartWidth,
            height: this.chartAreaRef.el.offsetHeight,
        };
    };

    // Form view
    get formProps() {
        return {
            type: "form",
            resModel: "governance.circle",
            resId: this.state.activeResId,
            loadActionMenus: true,
            preventCreate: this.preventCreate,
            preventEdit: this.preventEdit,
            noBreadcrumbs: true,
        };
    }

    get preventCreate() {
        return this.shouldPreventAction();
    }

    get preventEdit() {
        return this.shouldPreventAction();
    }

    shouldPreventAction() {
        return this.isGovernanceAdmin
            ? false
            : !this.state.allowed_edit_governance_ids.includes(this.state.activeResId);
    }

    onChartNodeClicked(node) {
        this.state.activeResId = node.id;

        const formAreaEl = this.formAreaRef.el;
        const chartAreaEl = this.chartAreaRef.el;

        if (formAreaEl && chartAreaEl) {
            formAreaEl.style.flex = "";
            formAreaEl.style.width = "50%";
            chartAreaEl.style.flex = "";
            chartAreaEl.style.width = "50%";

            this.state.chartDimensions = {
                width: chartAreaEl.offsetWidth,
                height: chartAreaEl.offsetHeight,
            };
        }
    }

    get chartRendererProps() {
        return {
            data: this.state.data,
            dimensions: this.state.chartDimensions,
            searchResults: this.state.searchResults,
            isGrayscaleMode: this.is_grayscale_on,
            isStripeAllRoles: this.is_stripe_all_roles,
            onNodeClick: this.onChartNodeClicked.bind(this),
        };
    }
}

registry.category("actions").add("governance_chart_action", GovernanceChartComponent);
