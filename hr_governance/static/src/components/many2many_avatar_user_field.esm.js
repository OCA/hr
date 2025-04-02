/* @odoo-module */

import {
    Many2ManyTagsAvatarUserField,
    many2ManyTagsAvatarUserField,
} from "@mail/views/web/fields/many2many_avatar_user_field/many2many_avatar_user_field";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";

export class ClickableMany2ManyTagsAvatarUserField extends Many2ManyTagsAvatarUserField {
    setup() {
        super.setup();
        this.action = useService("action");
    }
    getTagProps(record) {
        return {
            ...super.getTagProps(...arguments),
            onImageClicked: () => {
                if (record) {
                    this.action.doAction({
                        type: "ir.actions.act_window",
                        name: "Roles of this member",
                        res_model: "governance.circle",
                        view_mode: "list,form",
                        views: [
                            [false, "list"],
                            [false, "form"],
                        ],
                        domain: [["member_rel_ids", "ilike", record.data.display_name]],
                    });
                }
            },
        };
    }
}

export const clickablemany2ManyTagsAvatarUserField = {
    ...many2ManyTagsAvatarUserField,
    component: ClickableMany2ManyTagsAvatarUserField,
};

registry
    .category("fields")
    .add("clickable_many2many_avatar_user", clickablemany2ManyTagsAvatarUserField);
