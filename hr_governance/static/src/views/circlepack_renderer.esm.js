import {
    Component,
    onMounted,
    onWillStart,
    onWillUpdateProps,
    useEffect,
    useExternalListener,
    useRef,
    useState,
} from "@odoo/owl";
import {useBus, useService} from "@web/core/utils/hooks";
import {View} from "@web/views/view";
import {getColor} from "../utils/color.esm";
import {isEquals} from "../utils/helpers.esm";
import {loadBundle} from "@web/core/assets";
import {user} from "@web/core/user";

export class CirclePackRenderer extends Component {
    static template = "hr_governance.CirclePackRenderer";
    static components = {View};

    setup() {
        this.orm = useService("orm");
        this.ui = useService("ui");

        this.state = useState({
            activeResId: false,
            allowed_edit_governance_ids: [],
        });

        this.containerRef = useRef("container");
        this.chartRef = useRef("chart");

        onWillStart(async () => {
            await loadBundle("hr_governance.chart_libs");
            // Set default activeID for FormView
            const defaultResId = this.props.records?.id;
            this.state.activeResId = defaultResId;
            this.is_grayscale_on = await this.orm.call(
                "governance.circle",
                "get_greyscale_mode_param"
            );
            this.is_stripe_all_roles = parseInt(
                await this.orm.call("governance.circle", "get_stripe_param"),
                10
            );
            this.isGovernanceAdmin = await user.hasGroup(
                "hr_governance.governance_group_manager"
            );

            this.state.allowed_edit_governance_ids =
                user.context.allowed_edit_governance_ids;
        });

        onMounted(() => {
            this.firstload = true;
            this.container = this.containerRef.el;
            this.formview = this.container?.querySelector(".form_wrapper");
            this.splitter = this.container?.querySelector(".chart-splitter");
            this.chart = this.chartRef.el;
            this.searchResults = undefined;
            this.data = this.props.records;
            if (this.data) {
                this.renderChart(this.chart.offsetWidth, this.chart.offsetHeight);
            }
        });

        onWillUpdateProps((nextProps) => {
            const parsedData = this._parseData(
                nextProps.records,
                this.$chart.width(),
                this.$chart.height()
            )?.data;
            this.searchResults = isEquals(parsedData, this.data)
                ? undefined
                : parsedData.children;
        });

        useEffect(
            () => {
                if (this.props.records) {
                    // Assign 1st record to FormView, otherwise assign root record
                    this.state.activeResId =
                        this.searchResults?.length > 0
                            ? this.searchResults[0].id
                            : this.props.records.id;

                    this.renderChart(this.chart.offsetWidth, this.chart.offsetHeight);

                    if (this.searchResults?.length > 0) {
                        this._applySearchResult();
                    }
                }
            },
            // Only re-draw chart to update this.searchResults
            () => [this.props.records]
        );

        useBus(this.ui.bus, "governance:form_saved_record", async () => {
            await this.updateChart();
            const context = await this.env.services.rpc(
                "/web/session/get_session_info"
            );
            this.state.allowed_edit_governance_ids =
                context.user_context.allowed_edit_governance_ids;
        });

        useBus(this.ui.bus, "governance:form_deleted_record", async (ev) => {
            // Find parent of the deleted
            const deletedResId = ev.detail.deletedResId;
            // eslint-disable-next-line no-undef
            const deletedNode = d3
                .hierarchy(this.data)
                .descendants()
                .find((d) => d.data.id === deletedResId);
            const parentNode = deletedNode ? deletedNode.ancestors()[1] : null;

            await this.updateChart(parentNode);

            // Assign parent of the deleted to FormView
            this.state.activeResId = parentNode?.data.id || this.data.id;
        });
        useExternalListener(window, "resize", this.onWindowResized);

        useBus(this.ui.bus, "governance:form_discard_record", async () => {
            this.render(true);
        });
    }

    async updateChart(focusNode) {
        const data = await this.env.model.keepLast.add(this.env.model._loadData({}));
        this.data = data;
        this.renderChart(this.chart.offsetWidth, this.chart.offsetHeight);
        // Maintain current zoom
        if (focusNode) {
            this.zoomToNode(
                focusNode.data,
                this.chart.offsetWidth,
                this.chart.offsetHeight
            );
        } else {
            this.zoomToNode(
                this.focus,
                this.chart.offsetWidth,
                this.chart.offsetHeight
            );
        }

        if (this.searchResults?.length > 0) {
            this._applySearchResult();
        }
    }

    _parseData(data, width, height) {
        if (data) {
            // eslint-disable-next-line no-undef
            const hierarchyData = d3
                .hierarchy(data)
                .sum((d) => (d.member_count ? d.member_count : 1))
                .sort((a, b) => {
                    const memA = a.member_count ? a.member_count : 1;
                    const memB = b.member_count ? b.member_count : 1;
                    return memB - memA;
                });

            // eslint-disable-next-line no-undef
            d3.pack().size([width, height]).padding(2)(hierarchyData);

            hierarchyData.descendants().forEach((d, i) => {
                // Mark each node with a unique ID
                d.id = i;
                // Dual-link data nodes
                d.data.__dataNode = d;
            });
            return hierarchyData;
        }
    }

    zoomToNode(d, width, height) {
        this.clickedNode = d;
        const node = d.__dataNode;
        if (node) {
            // Zooming to clicked circle
            const ZOOM_REL_PADDING = 0.12;
            const k = Math.max(
                1,
                (Math.min(width, height) / (node.r * 2)) * (1 - ZOOM_REL_PADDING)
            );
            const tr = {
                k,
                // Don't pan out of chart boundaries
                x: -Math.max(0, Math.min(width * (1 - 1 / k), node.x - width / k / 2)),
                y: -Math.max(
                    0,
                    Math.min(height * (1 - 1 / k), node.y - height / k / 2)
                ),
                // Center circle in view
            };
            this.zoom.zoomTo(tr);

            // Label scaling
            const currentZoom = this.zoom.current();
            this.groupLabels.attr("transform", (dataNode) => {
                const x = dataNode.x * currentZoom.k + currentZoom.x;
                const y = dataNode.y * currentZoom.k + currentZoom.y;
                return `translate(${x},${y})`;
            });
        }
        return this;
    }

    // TODO: improve
    renderChart(width, height) {
        if (!this.data) return;

        if (this.svg) {
            this.svg.remove();
        }

        const hierarchyData = this._parseData(this.data, width, height);
        // eslint-disable-next-line no-undef
        this.svg = d3.create("svg");
        this.svg.style("width", width + "px").style("height", "inherit");

        // Pattern injection for striped shapes used by circle without members
        // eslint-disable-next-line no-unused-vars
        const pattern = this.svg
            .append("defs")
            .append("pattern")
            .attr("id", "stripes")
            .attr("width", "10")
            .attr("height", "8")
            .attr("patternUnits", "userSpaceOnUse")
            .attr("patternTransform", "rotate(45)")
            .append("rect")
            .attr("width", "5")
            .attr("height", "8")
            .attr("transform", "translate(0, 0)")
            .attr("fill", "grey");
        this.groupCircles = this.svg.append("g").attr("id", "groupCircles");

        // eslint-disable-next-line no-undef
        this.zoom = zoomable();
        // By default reset zoom when clicking on svg
        this.svg.on("click", () => this.zoom.zoomReset());

        this.zoom(this.svg)
            .svgEl(this.groupCircles)
            // Takes effect when zooming with mousewheel
            .onChange((tr) => {
                this.transition = tr;
                this.groupLabels.attr("transform", (d) => {
                    const translateX = d.x * tr.k + tr.x;
                    const translateY = d.y * tr.k + tr.y;
                    return `translate(${translateX},${translateY})`;
                });

                // Text wrapping dynamically change
                this.groupLabels
                    .selectAll("foreignObject")
                    .attr("width", (d) => d.r * 1.8 * tr.k)
                    .attr("height", (d) => d.r * 1.8 * tr.k)
                    .attr("x", (d) => -d.r * 0.9 * tr.k)
                    .attr("y", (d) => -d.r * 0.9 * tr.k);

                // Label visibility
                const scale = Math.round(tr.k);
                // eslint-disable-next-line no-undef
                const maxDepth = d3.max(this.groupLabels.data(), (d) => d.depth);

                this.groupLabels.selectAll("span").style("opacity", 0);
                this.groupLabels.selectAll("span").each(function (d) {
                    const r = d.r * tr.k * 1.2;
                    const newHeight = this.getBoundingClientRect().height;
                    if (
                        newHeight < r &&
                        (d.depth === scale ||
                            (scale > maxDepth && d.depth === maxDepth) ||
                            (d.depth < scale && d.children === undefined))
                    )
                        // eslint-disable-next-line no-undef
                        d3.select(this).style("opacity", 1);
                });
            });

        this.zoom.translateExtent([
            [0, 0],
            [width, height],
        ]);

        if (!hierarchyData) return;

        this.chartRef.el.append(this.svg.node());

        const cell = this.groupCircles
            .selectAll(".node")
            .data(hierarchyData.descendants());

        // Exiting
        cell.exit().transition().remove();

        // Entering
        const newCell = cell
            .enter()
            .append("g")
            .attr("id", (d) => `node-${d.data.id}`)
            .attr("transform", (d) => `translate(${d.x},${d.y})`)
            .attr("data-tooltip", (d) => d.data.name);

        this._addNodeShape(newCell);

        // Entering + Updating
        const allCells = cell.merge(newCell);

        allCells.attr("class", "node");

        // Append the text labels.
        const labels = this.svg
            .append("g")
            .attr("pointer-events", "none")
            .attr("text-anchor", "middle");

        this.groupLabels = labels
            .selectAll("g.node")
            .data(hierarchyData.descendants())
            .enter()
            .append("g")
            .attr("class", "label-container")
            .attr("transform", (d) => `translate(${d.x},${d.y})`);

        this.groupLabels
            .append("foreignObject")
            .attr("class", "text-container")
            .attr("width", (d) => d.r * 1.8)
            .attr("height", (d) => d.r * 1.8)
            // Center in the circle
            .attr("x", (d) => -d.r * 0.9)
            .attr("y", (d) => -d.r * 0.9)
            .append("xhtml:div")
            .attr("class", "path-label")
            .append("span")
            .text((d) => d.data.name);

        this.groupLabels.selectAll("span").each(function (d) {
            const radius = d.r * 1.5;
            const newHeight = this.getBoundingClientRect().height;
            // eslint-disable-next-line no-undef
            d3.select(this).style(
                "opacity",
                newHeight > radius || d.depth !== 1 ? 0 : 1
            );
        });

        allCells.select("circle.striped").style("fill", "url(#stripes)");
        allCells.select("polygon.striped").style("fill", "url(#stripes)");
    }

    _getNodeColor(node) {
        if (!this.is_grayscale_on) {
            return getColor(node);
        }

        // GrayScale mode
        return node.data.is_circle === false
            ? getColor(node)
            : // eslint-disable-next-line no-undef
              d3.schemeGreys[5][node.depth + 1];
    }

    startResizing() {
        this.isResizing = true;
        this.firstload = false;
        document.addEventListener("mousemove", this.onMouseMove);
        document.addEventListener("mouseup", this.stopResizing);
    }

    onMouseMove = (e) => {
        if (!this.isResizing) return;
        const containerRect = this.container.getBoundingClientRect();
        const offsetRight =
            this.container.offsetWidth - (e.clientX - containerRect.left);
        const chartWidth = Math.max(this.container.offsetWidth - offsetRight, 1);

        this.chart.style.width = chartWidth + "px";
        this.chart.style.flex = "";
        this.formview.style.width = offsetRight + "px";
        this.formview.style.flex = "";

        // Re-render
        this.renderChart(this.chart.offsetWidth, this.chart.offsetHeight);
        if (this.searchResults?.length > 0) {
            this._applySearchResult();
        }
    };

    stopResizing = () => {
        this.isResizing = false;
        document.removeEventListener("mousemove", this.onMouseMove);
        document.removeEventListener("mouseup", this.stopResizing);
    };

    _applySearchResult() {
        // eslint-disable-next-line no-undef
        const groupCircles = d3.select("g#groupCircles").selectAll("g");

        groupCircles.classed("matched", (d) => {
            return this.searchResults?.some((result) => result.id === d.data.id);
        });
        if (this.is_grayscale_on) {
            groupCircles.style("opacity", (d) => {
                if (!this.searchResults) return 1;
                return this.searchResults.some((result) => result.id === d.data.id)
                    ? 1
                    : 0.1;
            });
        } else {
            groupCircles.style("filter", (_, i, nodes) => {
                // eslint-disable-next-line no-undef
                return d3.select(nodes[i]).classed("matched") ? null : "grayscale(1)";
            });
        }
    }

    onWindowResized(e) {
        if (this.firstload) {
            this.renderChart(this.container.offsetWidth, this.chart.offsetHeight);
        } else {
            const containerRect = this.container.getBoundingClientRect();
            const offsetRight =
                this.container.offsetWidth - (e.clientX - containerRect.left);
            const chartWidth = Math.max(this.container.offsetWidth - offsetRight, 1);

            this.chart.style.width = chartWidth + "px";
            this.chart.style.flex = "";
            this.formview.style.width = offsetRight + "px";
            this.formview.style.flex = "";

            // Re-render
            this.renderChart(this.chart.offsetWidth, this.chart.offsetHeight);
        }
        if (this.clickedNode) {
            this.zoomToNode(
                this.clickedNode,
                this.chart.offsetWidth,
                this.chart.offsetHeight
            );
        }
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

    _addNodeShape(node) {
        node.each((d, i, nodes) => {
            // eslint-disable-next-line no-undef
            const currentNode = d3.select(nodes[i]);
            const isHexagon = d.data.shape_type === "hexagon";

            const shape = this._createShape(currentNode, d, isHexagon);
            const striped_shape = this._createStripedShape(currentNode, d, isHexagon);
            this._attachCommonAttrs(shape);
            if (striped_shape) {
                this._attachCommonAttrs(striped_shape);
            }
        });
    }

    _createShape(currentNode, d, isHexagon) {
        if (isHexagon) {
            return currentNode
                .append("polygon")
                .attr("points", this._getPolygonPoints(d));
        }
        return currentNode.append("circle");
    }

    _createStripedShape(currentNode, d, isHexagon) {
        const is_striped =
            !d.data.is_circle &&
            !d.data.member_rel_ids?.length > 0 &&
            (this.is_stripe_all_roles || d.data.type_name === "structure");
        if (is_striped) {
            const shape = isHexagon
                ? currentNode
                      .append("polygon")
                      .attr("points", this._getPolygonPoints(d))
                : currentNode.append("circle");
            return shape.attr("class", "striped");
        }
        return null;
    }

    _getPolygonPoints(d) {
        return Array.from({length: 6}, (_, i) => {
            const angle = (Math.PI / 3) * i;
            const x = d.r * Math.cos(angle);
            const y = d.r * Math.sin(angle);
            return `${x},${y}`;
        }).join(" ");
    }

    _attachCommonAttrs(shape) {
        if (shape) {
            shape
                .attr("r", (d) => d.r)
                .style("fill", (d) => this._getNodeColor(d))
                .on("click", (ev, d) => {
                    ev.stopPropagation();
                    if (this.firstload) {
                        this.firstload = false;
                        this.chart.style.width = "50%";
                        this.chart.style.flex = "";
                        this.formview.style.width = "50%";
                        this.formview.style.flex = "";
                        this.renderChart(
                            this.chart.offsetWidth,
                            this.chart.offsetHeight
                        );
                    }
                    this.focus = d.data;
                    this.zoomToNode(
                        d.children ? d.data : d.parent.data,
                        this.chart.offsetWidth,
                        this.chart.offsetHeight
                    );
                    this.state.activeResId = d.data.id;

                    // Stroke handling
                    this.svg
                        .selectAll(".node")
                        .selectAll(`${shape._groups[0][0].nodeName}`)
                        .classed("clicked", false);
                    this.svg
                        .select("g#node-" + d.data.id)
                        .filter((nodeData) => nodeData.data.id !== 0)
                        .selectAll(`${shape._groups[0][0].nodeName}`)
                        .classed("clicked", true);

                    // Search handling
                    if (this.searchResults?.length > 0) {
                        this._applySearchResult();
                    }
                });
        }
    }
}
