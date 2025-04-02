/** @odoo-module **/

import {markup, onMounted} from "@odoo/owl";
import {DeleteRolesConfirmationDialog} from "./delete_roles_confirmation_dialog.esm";
import {FormController} from "@web/views/form/form_controller";
import {_t} from "@web/core/l10n/translation";
import {executeButtonCallback} from "@web/views/view_button/view_button_hook";
import {formView} from "@web/views/form/form_view";
import {isEmpty} from "../utils/helpers.esm";
import {registry} from "@web/core/registry";

export class FormWrapperController extends FormController {
    setup() {
        super.setup();
        onMounted(() => {
            if (!this.model.root.data.is_circle) {
                // Hide create buttons when role is selected
                $("button.o_form_button_create").css("display", "none");
            }
        });
    }
    async save(params) {
        const res = await super.save(params);
        this.ui.bus.trigger("governance:form_saved_record");
        return res;
    }

    get deleteConfirmationDialogProps() {
        const res = super.deleteConfirmationDialogProps;
        const originalConfirm = res.confirm;

        res.confirm = async () => {
            await originalConfirm();
            this.ui.bus.trigger("governance:form_deleted_record", {
                deletedResId: this.props.resId,
            });
        };
        return res;
    }

    async deleteRecord() {
        if (!this.model.root.data.child_ids?.count) {
            return super.deleteRecord();
        }
        const data = await this.model.orm.call(
            "governance.circle",
            "js_get_deleted_circle_info",
            [this.model.root.evalContext.active_id]
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
                    await this.model.root.delete();
                    this.ui.bus.trigger("governance:form_deleted_record", {
                        deletedResId: this.props.resId,
                    });
                }
                if (!this.model.root.resId) {
                    this.env.config.historyBack();
                }
            },
        });
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
            // TODO: is this needed?
        } else return super.create(ev);
    }

    _create_circle(context = {}) {
        context.default_is_circle = true;
    }

    async _create_role(context = {}) {
        context.default_is_circle = false;
    }

    async discard() {
        if (this.model.root.isNew) {
            this.ui.bus.trigger("governance:form_discard_record");
            return;
        }
        return super.discard();
    }
}

FormWrapperController.template = `hr_governance.FormWrapperView`;

export const formwrapperView = {
    ...formView,
    Controller: FormWrapperController,
};

registry.category("views").add("formwrapper", formwrapperView);
