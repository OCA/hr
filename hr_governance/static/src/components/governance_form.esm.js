/* eslint-disable no-undef */
import {FormController} from "@web/views/form/form_controller";
import {useService} from "@web/core/utils/hooks";
import {formView} from "@web/views/form/form_view";
import {registry} from "@web/core/registry";
import {executeButtonCallback} from "@web/views/view_button/view_button_hook";
import {isEmpty} from "../utils/helpers.esm";
import {DeleteRolesConfirmationDialog} from "./delete_roles_confirmation_dialog.esm";
import {_t} from "@web/core/l10n/translation";

import {markup} from "@odoo/owl";

export class GovernanceFormController extends FormController {
    setup() {
        super.setup();
        this.ui = useService("ui");
    }

    // Create
    async save(params) {
        const res = await super.save(params);
        this.env.bus.trigger("governance:form_saved_record");
        return res;
    }

    async create(ev) {
        const additionalContext = {};

        // Prefil circle/role
        const buttonType = ev.target.dataset.type;
        const method = buttonType === "circle" ? `_create_circle` : `_create_role`;
        await this[method](additionalContext);

        // Prefil parent_id
        additionalContext.default_parent_id = this.props.resId || false;
        if (isEmpty(additionalContext) === false) {
            await executeButtonCallback(this.ui.activeElement, () =>
                this.model.load({
                    resId: false,
                    context: {
                        ...this.props.context,
                        ...additionalContext,
                    },
                })
            );
        } else {
            return super.create(ev);
        }
    }

    _create_circle(context = {}) {
        context.default_is_circle = true;
    }

    async _create_role(context = {}) {
        context.default_is_circle = false;
    }

    // Delete
    async _deleteRecord() {
        await this.model.root.delete();
        this.env.bus.trigger("governance:form_deleted_record", {
            deletedResId: this.props.resId,
        });
    }

    async deleteRecord() {
        if (!this.model.root.data.child_ids?.count) {
            await this._deleteRecord();
        } else {
            const data = await this.model.orm.call(
                "governance.circle",
                "js_get_deleted_circle_info",
                [this.model.root.evalContext.id]
            );
            this.dialogService.add(DeleteRolesConfirmationDialog, {
                body: markup(
                    _t(
                        `Deleting this Circle will also delete its associated roles (<b>Impact ${data.subcircles} sub-circles, ${data.roles} roles, ${data.employees} employees)</b>.
If you wish to preserve the roles, make sure to unlink them from their circle beforehand.

Are you sure you want to proceed?`
                    )
                ),
                confirm: async () => {
                    const typing = prompt("Please type DELETE");
                    if (typing === "DELETE") {
                        await this._deleteRecord();
                    }
                },
            });
        }
    }
}

GovernanceFormController.template = `hr_governance.GovernanceFormView`;

export const governanceFormView = {
    ...formView,
    Controller: GovernanceFormController,
};

registry.category("views").add("governance_form_view", governanceFormView);
