/* eslint-disable no-undef */
import {Component, onMounted, onWillStart, onWillUpdateProps, useRef} from "@odoo/owl";
import {loadBundle} from "@web/core/assets";
import {getColor} from "../utils/color.esm";
import {isEquals} from "../utils/helpers.esm";

export class GovernanceChartRenderer extends Component {
    static template = "hr_governance.GovernanceChartRenderer";
    static props = {
        data: {type: Object, optional: true},
        dimensions: {type: Object, optional: true},
        searchResults: {type: Array, optional: true},
        isGrayscaleMode: {type: Boolean, optional: false},
        isStripeAllRoles: {type: Boolean, optional: false},
        onNodeClick: {type: Function, optional: true},
    };

    setup() {
        this.chartRef = useRef("chartContainer");
        this.data = this.props.data;
        this.searchResults = this.props.searchResults;

        onWillStart(async () => {
            await loadBundle("hr_governance.chart_libs");
        });

        onMounted(() => {
            if (this.props.dimensions.width && this.props.dimensions.height) {
                this.renderChart(
                    this.props.dimensions.width,
                    this.props.dimensions.height
                );
            }
        });

        onWillUpdateProps((nextProps) => {
            const shouldRender =
                !isEquals(this.props.data, nextProps.data) ||
                !isEquals(this.props.searchResults, nextProps.searchResults) ||
                !isEquals(this.props.dimensions, nextProps.dimensions);

            if (shouldRender) {
                this.data = nextProps.data;
                this.searchResults = nextProps.searchResults;
                const isResize = !isEquals(this.props.dimensions, nextProps.dimensions);
                this.renderChart(
                    nextProps.dimensions.width,
                    nextProps.dimensions.height,
                    isResize
                );
            }
        });
    }

    // Chart Rendering Methods
    renderChart(width, height, isResize = false) {
        const currentTransform = this.svg ? d3.zoomTransform(this.svg.node()) : null;
        if (this.svg) {
            this.svg.remove();
        }

        const hierarchyData = this._parseData(this.data, width, height);
        if (!hierarchyData) return;

        this._setupSvg(width, height);
        this._setupZoom(width, height);
        this.chartRef.el.appendChild(this.svg.node());

        const allCells = this._drawNodes(hierarchyData);
        this._drawLabels(hierarchyData);

        allCells.select("circle.striped").style("fill", "url(#stripes)");
        allCells.select("polygon.striped").style("fill", "url(#stripes)");

        this._applySearchResult();
        this._restoreTransform(
            isResize,
            currentTransform,
            hierarchyData,
            width,
            height
        );
    }

    _setupSvg(width, height) {
        this.svg = d3.create("svg");
        this.svg.style("width", width + "px").style("height", height + "px");

        this.svg
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
    }

    _setupZoom(width, height) {
        this.zoom = zoomable();
        this.svg.on("click", () => this.zoom.zoomReset());
        this.zoom(this.svg)
            .svgEl(this.groupCircles)
            .onChange((tr) => this._updateOnZoom(tr));
        this.zoom.translateExtent([
            [0, 0],
            [width, height],
        ]);
    }

    _drawNodes(hierarchyData) {
        const cell = this.groupCircles
            .selectAll(".node")
            .data(hierarchyData.descendants());

        cell.exit().transition().remove();

        const newCell = cell
            .enter()
            .append("g")
            .attr("id", (d) => `node-${d.data.id}`)
            .attr("transform", (d) => `translate(${d.x},${d.y})`)
            .attr("data-tooltip", (d) => d.data.name);

        this._addNodeShape(newCell);

        const allCells = cell.merge(newCell);
        allCells.attr("class", "node");
        return allCells;
    }

    _drawLabels(hierarchyData) {
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
            .attr("x", (d) => -d.r * 0.9)
            .attr("y", (d) => -d.r * 0.9)
            .append("xhtml:div")
            .attr("class", "path-label")
            .append("span")
            .text((d) => d.data.name);

        this.groupLabels.selectAll("span").each(function (d) {
            const radius = d.r * 1.5;
            const newHeight = this.getBoundingClientRect().height;
            d3.select(this).style(
                "opacity",
                newHeight > radius || d.depth !== 1 ? 0 : 1
            );
        });
    }

    _restoreTransform(isResize, currentTransform, hierarchyData, width, height) {
        if (isResize && this.clickedNode) {
            const targetNode = hierarchyData
                .descendants()
                .find((n) => n.data.id === this.clickedNode.id);
            if (targetNode) {
                this.zoomToNode(targetNode.data, width, height);
            }
        } else if (currentTransform) {
            this.zoom.zoomTo(currentTransform);
            this._updateOnZoom(currentTransform);
            this.svg.node().__zoom = d3.zoomIdentity
                .translate(currentTransform.x, currentTransform.y)
                .scale(currentTransform.k);
        }
    }

    // Helper Methods
    _updateOnZoom(tr) {
        this.groupCircles.attr(
            "transform",
            `translate(${tr.x},${tr.y}) scale(${tr.k})`
        );
        this.transition = tr;
        this.groupLabels.attr("transform", (d) => {
            const translateX = d.x * tr.k + tr.x;
            const translateY = d.y * tr.k + tr.y;
            return `translate(${translateX},${translateY})`;
        });

        this.groupLabels
            .selectAll("foreignObject")
            .attr("width", (d) => d.r * 1.8 * tr.k)
            .attr("height", (d) => d.r * 1.8 * tr.k)
            .attr("x", (d) => -d.r * 0.9 * tr.k)
            .attr("y", (d) => -d.r * 0.9 * tr.k);

        const scale = Math.round(tr.k);
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
                d3.select(this).style("opacity", 1);
        });
    }

    _applySearchResult() {
        const groupCircles = d3.select("g#groupCircles").selectAll("g");
        const hasSearchResults = this.searchResults && this.searchResults.length > 0;

        groupCircles.classed("matched", (d) => {
            return hasSearchResults && this.searchResults.includes(d.data.id);
        });

        if (this.props.isGrayscaleMode) {
            groupCircles.style("filter", null);
            groupCircles.style("opacity", (d) => {
                if (!hasSearchResults) {
                    return 1;
                }
                return this.searchResults.includes(d.data.id) ? 1 : 0.1;
            });
        } else {
            groupCircles.style("opacity", 1);
            groupCircles.style("filter", (d) => {
                if (!hasSearchResults) {
                    return null;
                }
                return this.searchResults.includes(d.data.id) ? null : "grayscale(1)";
            });
        }
    }

    _parseData(data, width, height) {
        if (!data) return null;

        const hierarchyData = d3
            .hierarchy(data)
            .sum((d) => (d.member_count ? d.member_count : 1))
            .sort((a, b) => {
                const memA = a.member_count ? a.member_count : 1;
                const memB = b.member_count ? b.member_count : 1;
                return memB - memA;
            });

        d3.pack().size([width, height]).padding(2)(hierarchyData);

        hierarchyData.descendants().forEach((d, i) => {
            d.id = i;
            d.data.__dataNode = d;
        });

        return hierarchyData;
    }

    _addNodeShape(node) {
        node.each((d, i, nodes) => {
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
            !d.data.role_assignment_ids?.length > 0 &&
            (this.props.isStripeAllRoles || d.data.role_type_name === "structure");
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

    _attachCommonAttrs(shape) {
        if (shape) {
            shape
                .attr("r", (d) => d.r)
                .style("fill", (d) => this._getNodeColor(d))
                .on("click", (ev, d) => {
                    ev.stopPropagation();

                    if (this.props.onNodeClick) {
                        this.props.onNodeClick(d.data);
                    }

                    this.zoomToNode(
                        d.children ? d.data : d.parent.data,
                        this.chartRef.el.offsetWidth,
                        this.chartRef.el.offsetHeight
                    );

                    this.svg
                        .selectAll(".node")
                        .selectAll(`${shape._groups[0][0].nodeName}`)
                        .classed("clicked", false);
                    this.svg
                        .select("g#node-" + d.data.id)
                        .filter((nodeData) => nodeData.data.id !== 0)
                        .selectAll(`${shape._groups[0][0].nodeName}`)
                        .classed("clicked", true);
                });
        }
    }

    _getNodeColor(node) {
        if (!this.props.isGrayscaleMode) {
            return getColor(node);
        }

        return node.data.is_circle === false
            ? getColor(node)
            : d3.schemeGreys[5][node.depth + 1];
    }

    _getPolygonPoints(d) {
        return Array.from({length: 6}, (_, i) => {
            const angle = (Math.PI / 3) * i;
            const x = d.r * Math.cos(angle);
            const y = d.r * Math.sin(angle);
            return `${x},${y}`;
        }).join(" ");
    }

    zoomToNode(d, width, height) {
        if (!d) {
            return this;
        }

        this.clickedNode = d;
        const node = d.__dataNode;
        if (node) {
            const ZOOM_REL_PADDING = 0.12;
            const k = Math.max(
                1,
                (Math.min(width, height) / (node.r * 2)) * (1 - ZOOM_REL_PADDING)
            );
            const tr = {
                k,
                x: -Math.max(0, Math.min(width * (1 - 1 / k), node.x - width / k / 2)),
                y: -Math.max(
                    0,
                    Math.min(height * (1 - 1 / k), node.y - height / k / 2)
                ),
            };
            this.zoom.zoomTo(tr);
            const currentZoom = this.zoom.current();
            this._updateOnZoom(currentZoom);
            this.svg.node().__zoom = d3.zoomIdentity
                .translate(currentZoom.x, currentZoom.y)
                .scale(currentZoom.k);
        }
        return this;
    }
}
