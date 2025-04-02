/** @odoo-module **/

import {ConfirmationDialog} from "@web/core/confirmation_dialog/confirmation_dialog";
import {_t} from "@web/core/l10n/translation";

export class DeleteRolesConfirmationDialog extends ConfirmationDialog {}

DeleteRolesConfirmationDialog.props = {
    ...ConfirmationDialog.props,
    body: {String, optional: true},
};

DeleteRolesConfirmationDialog.defaultProps = {
    ...ConfirmationDialog.defaultProps,
    confirmLabel: _t("Delete"),
};
