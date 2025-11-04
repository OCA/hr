import { patch } from "@web/core/utils/patch";
import { CalendarController } from "@web/views/calendar/calendar_controller";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

patch(CalendarController.prototype, {
  setup() {
    super.setup(...arguments);
    this.notification = useService("notification");
    // console.log(this);
  },

  // only display button if month or week
  get workEntryDisplayButton() {
    return this.model.meta.scale == "week" || this.model.meta.scale == "month";
  },

  // tell if any record is still draft
  get workEntryAnyDraft() {
    return this.workEntryFilteredRecords.length != 0;
  },

  // get current draft records
  get workEntryFilteredRecords() {
    return this.workEntryFilterRecords(
      this.model.data.records,
      this.model.meta.scale,
      this.model.meta.date,
      "draft"
    );
  },

  // filter records based on current month / week and state
  workEntryFilterRecords(records, scale, date, state) {
    const start = date.startOf(scale);
    const stop = date.endOf(scale);
    // filter records
    return Object.values(records).filter(
      (record) =>
        record.start > start &&
        record.end < stop &&
        record.rawRecord.state == state
    );
  },

  // call action_validate on current records
  async workEntryValidate() {
    const record_ids = this.workEntryFilteredRecords.map((r) => r.id);
    console.log("Validating records", record_ids);
    const success = await this.orm.call("hr.work.entry", "action_validate", [
      record_ids,
    ]);
    if (success) {
      // refresh
      this.model.env.searchModel.search();
      // notify success
      this.notification.add(_t("%s work entries validated", record_ids.length), {
        title: "Ok",
        type: "success",
      });
    } else {
      // notify failure
      this.notification.add(_t("Work entries could not be validated."), {
        title: _t("Error"),
        type: "danger",
      });
    }
  },
});
