/** @odoo-module **/

import {KeepLast} from "@web/core/utils/concurrency";
import {Model} from "@web/model/model";

export class CirclePackModel extends Model {
    setup() {
        // Concurrency management
        this.keepLast = new KeepLast();
        this.data = null;
    }

    async load(params = {}) {
        this.searchParams = params;
        const data = await this.keepLast.add(this._loadData(params));
        this.data = data;
        this.notify();
    }

    /**
     * Load data for hierarchy view
     *
     * @param {Object} config model config
     * @returns {Object[]} main data for hierarchy view
     */
    async _loadData(config) {
        const result = await this.orm.call(
            "governance.circle",
            "get_hierarchy_data",
            [config.domain || []],
            {
                context: config.context,
            }
        );

        const data = new Map(result.map((item) => [item.id, {...item, children: []}]));

        // Build hierarchy data
        let root = null;
        const orphans = [];
        result.forEach((item) => {
            if (item.parent_id === false) {
                root = data.get(item.id);
            } else {
                const parent = data.get(item.parent_id[0]);
                if (parent) {
                    parent.children.push(data.get(item.id));
                } else {
                    orphans.push(item);
                }
            }
        });
        if (root && orphans.length > 0) {
            root.children.push(...orphans);
        }
        return root;
    }
}
