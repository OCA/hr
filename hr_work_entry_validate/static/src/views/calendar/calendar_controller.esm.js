import {WorkEntryCalendarController} from "@hr_work_entry_contract/views/work_entry_calendar/work_entry_calendar_controller";
import {_t} from "@web/core/l10n/translation";
import {onWillStart} from "@odoo/owl";
import {patch} from "@web/core/utils/patch";
import {useService} from "@web/core/utils/hooks";
import {user} from "@web/core/user";

patch(WorkEntryCalendarController.prototype, {
    setup() {
        super.setup(...arguments);
        this.notification = useService("notification");
        this.isHrUser = false;
        // Console.log(this);

        onWillStart(async () => {
            this.isHrUser = await user.hasGroup("hr.group_hr_user");
        });
    },

    // Only display button if month or week
    get displayValidateButton() {
        return this.model.meta.scale === "week" || this.model.meta.scale === "month";
    },

    // Tell if any record is still draft
    get anyDraft() {
        return this.filteredRecords.length !== 0;
    },

    // Get current draft records
    get filteredRecords() {
        return this.filterRecords(this.model.data.records, "draft");
    },

    // Filter records based on current month / week and state
    filterRecords(records, state) {
        const {start, end} = this.model.computeRange();
        // Filter records
        return Object.values(records).filter(
            (record) =>
                record.start > start &&
                record.end < end &&
                record.rawRecord.state === state
        );
    },

    // Call action_validate on current records
    async validate() {
        const record_ids = this.filteredRecords.map((r) => r.id);
        // Console.log("Validating records", record_ids);
        const success = await this.orm.call("hr.work.entry", "action_validate", [
            record_ids,
        ]);
        if (success) {
            // Refresh
            this.model.env.searchModel.search();
            // Notify success
            this.notification.add(_t("%s work entries validated", record_ids.length), {
                title: "Ok",
                type: "success",
            });
        } else {
            // Notify failure
            this.notification.add(_t("Work entries could not be validated."), {
                title: _t("Error"),
                type: "danger",
            });
        }
    },
});
