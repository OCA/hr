/* eslint-disable no-undef */
import {Component, useExternalListener, xml} from "@odoo/owl";

export class Splitter extends Component {
    static template = xml`<div class="o_governance_splitter" t-on-mousedown="startResizing"/>`;

    static props = {
        onResize: Function,
    };

    setup() {
        this.isResizing = false;
        useExternalListener(window, "mousemove", this.onMouseMove.bind(this));
        useExternalListener(window, "mouseup", this.stopResizing.bind(this));
    }

    startResizing(ev) {
        ev.preventDefault();
        this.isResizing = true;
    }

    onMouseMove = (ev) => {
        if (!this.isResizing) return;
        if (this.props.onResize) {
            this.props.onResize(ev);
        }
    };

    stopResizing = () => {
        this.isResizing = false;
    };
}
