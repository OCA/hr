odoo.define("hr_org_chart_overview", function(require) {
    "use strict";

    var core = require("web.core");
    var AbstractAction = require("web.AbstractAction");

    var HrOrgChartOverview = AbstractAction.extend({
        contentTemplate: "HrOrgChartOverview",
        events: {
            "click .node": "_onClickNode",
            "click #print-pdf": "_onPrintPDF",
            "keyup #key-word": "_onKeyUpSearch",
            "click #zoom-in": "_onClickZoomIn",
            "click #zoom-out": "_onClickZoomOut",
            "click #toggle-pan": "_onClickTogglePan",
        },

        init: function(parent) {
            this.orgChartData = {};
            this.actionManager = parent;
            console.log(this.actionManager);
            this._super.apply(this, arguments);
        },

        /**
         * @override
         */
        willStart: function() {
            var self = this;

            var def = this._rpc({
                model: "hr.employee",
                method: "get_organization_data",
            }).then(function(res) {
                self.orgChartData = res;
                return;
            });

            return Promise.all([def, this._super.apply(this, arguments)]);
        },

        _getNodeTemplate: function(data) {
            return `
                <span class="image"><img src="data:image/png;base64,${data.image}"/></span>
                <div class="title">${data.name}</div>
                <div class="content">${data.title}</div>
            `;
        },

        _renderButtons: function() {
            this.$buttons = this.$(".o_cp_buttons");
            this.$buttons.prepend(`
                <button type="button" id="print-pdf" class="btn btn-primary o-kanban-button-new" accesskey="p">
                    Print PDF
                </button>
                <button type="button" id="zoom-in" class="btn btn-primary o-kanban-button-new" accesskey="+">
                    <i class="fa fa-plus" title="Zoom In"></i>
                </button>
                <button type="button" id="toggle-pan" class="btn o-kanban-button-new" accesskey="m">
                    <i class="fa fa-arrows" title="Toggle Pan"></i>
                </button>
                <button type="button" id="zoom-out" class="btn btn-primary o-kanban-button-new" accesskey="-">
                    <i class="fa fa-minus" title="Zoom Out"></i>
                </button>
            `);
        },

        _renderSearchView: function() {
            this.$searchView = this.$(".o_cp_searchview");
            this.$searchView.prepend(`
                <div class="o_searchview" role="search" aria-autocomplete="list">
                    <div class="o_searchview_input_container">
                        <input type="text" class="o_searchview_input" id="key-word" accesskey="Q" placeholder="Search...">
                    </div>
                </div>
            `);
        },

        _renderBreadcrumb: function() {
            this.$breadcrumb = this.$(".breadcrumb");
            this.$breadcrumb.prepend(`
                <li class="breadcrumb-item active">Organizational Chart</li>
            `);
        },

        _updateControlPanel: function() {
            this._renderButtons();
            this._renderSearchView();
            this._renderBreadcrumb();
        },

        start: function() {
            this.oc = this.$("#chart-container").orgchart({
                data: this.orgChartData,
                nodeContent: "title",
                nodeTemplate: this._getNodeTemplate,
                exportFilename: "MyOrgChart",
            });

            this._updateControlPanel();

            return this._super.apply(this, arguments);
        },

        _filterNodes: function(keyWord) {
            var show = false;
            var $chart = this.$(".orgchart");
            // Disalbe the expand/collapse feture
            $chart.addClass("noncollapsable");
            // Distinguish the matched nodes and the unmatched nodes according to the given key word
            $chart
                .find(".node")
                .filter(function(index, node) {
                    $(node).removeClass("matched");
                    $(node).removeClass("retained");
                    if (
                        $(node)
                            .text()
                            .toLowerCase()
                            .indexOf(keyWord) > -1
                    ) {
                        show = true;
                    }
                    return (
                        $(node)
                            .text()
                            .toLowerCase()
                            .indexOf(keyWord) > -1
                    );
                })
                .addClass("matched")
                .closest("table")
                .parents("table")
                .find("tr:first")
                .find(".node")
                .addClass("retained");
            // Hide the unmatched nodes
            $chart.find(".matched,.retained").each(function(index, node) {
                $(node)
                    .removeClass("slide-up")
                    .closest(".nodes")
                    .removeClass("hidden")
                    .siblings(".lines")
                    .removeClass("hidden");
                var $unmatched = $(node)
                    .closest("table")
                    .parent()
                    .siblings()
                    .find(".node:first:not(.matched,.retained)")
                    .closest("table")
                    .parent()
                    .addClass("hidden");
                $unmatched
                    .parent()
                    .prev()
                    .children()
                    .slice(1, $unmatched.length * 2 + 1)
                    .addClass("hidden");
            });
            // Hide the redundant descendant nodes of the matched nodes
            $chart.find(".matched").each(function(index, node) {
                if (
                    !$(node)
                        .closest("tr")
                        .siblings(":last")
                        .find(".matched").length
                ) {
                    $(node)
                        .closest("tr")
                        .siblings()
                        .addClass("hidden");
                }
            });

            if (show) {
                this.$("#chart-container").removeClass("hidden");
            } else {
                this.$("#chart-container").addClass("hidden");
            }
        },

        _clearFilterResults: function() {
            this.$(".orgchart")
                .removeClass("noncollapsable")
                .find(".node")
                .removeClass("matched retained")
                .end()
                .find(".hidden")
                .removeClass("hidden")
                .end()
                .find(".slide-up, .slide-left, .slide-right")
                .removeClass("slide-up slide-right slide-left");
        },

        _openEmployeeFormView: function(id) {
            var self = this;
            // Go to the employee form view
            self._rpc({
                model: "hr.employee",
                method: "get_formview_action",
                args: [[id]],
            }).then(function(action) {
                self.trigger_up("do_action", {action: action});
            });
        },

        _onClickNode: function(ev) {
            ev.preventDefault();
            this._openEmployeeFormView(parseInt(ev.currentTarget.id, 10));
        },

        _onPrintPDF: function(ev) {
            ev.preventDefault();
            this.oc.export(this.oc.exportFilename, "pdf");
        },

        _onClickZoomIn: function(ev) {
            ev.preventDefault();
            this.oc.setChartScale(this.oc.$chart, 1.1);
        },

        _onClickZoomOut: function(ev) {
            ev.preventDefault();
            this.oc.setChartScale(this.oc.$chart, 0.9);
        },

        _onClickTogglePan: function(ev) {
            ev.preventDefault();
            var update_pan_to = !this.oc.options.pan;
            this.oc.options.pan = update_pan_to;
            this.oc.setOptions("pan", update_pan_to);
            if (update_pan_to === true) {
                $("#toggle-pan").addClass("btn-primary");
            } else {
                $("#toggle-pan").removeClass("btn-primary");
            }
        },

        _onPrintPNG: function(ev) {
            ev.preventDefault();
            this.oc.export(this.oc.exportFilename);
        },

        _onKeyUpSearch: function(ev) {
            var value = ev.target.value.toLowerCase();
            if (value.length === 0) {
                this._clearFilterResults();
            } else {
                this._filterNodes(value);
            }
        },
    });

    core.action_registry.add("hr_org_chart_overview", HrOrgChartOverview);

    return HrOrgChartOverview;
});
