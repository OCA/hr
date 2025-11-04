import { patch } from "@web/core/utils/patch";
import { CalendarController } from "@web/views/calendar/calendar_controller";
import { useService } from "@web/core/utils/hooks";

patch(CalendarController.prototype, {
  // just log this
  setup() {
    super.setup(...arguments);
    this.notification = useService("notification");
    console.log(this);
  },

  // only display button if month or week
  get displayButton() {
    return this.model.meta.scale == "week" || this.model.meta.scale == "month";
  },

  // tell if any record is still draft
  get anyDraftWorkentry() {
    return this.filteredRecords.length != 0;
  },

  // get current draft records
  get filteredRecords() {
    return this.filterRecords(
      this.model.data.records,
      this.model.meta.scale,
      this.model.meta.date,
      "draft"
    );
  },

  // filter records based on current month / week and state
  filterRecords(records, scale, date, state) {
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
  async validateWorkentries() {
    const record_ids = this.filteredRecords.map((r) => r.id);
    console.log("Validating records", record_ids);
    const success = await this.orm.call("hr.work.entry", "action_validate", [
      record_ids,
    ]);
    if (success) {
      // refresh
      this.model.env.searchModel.search();
      // notify success
      this.notification.add(`${record_ids.length} entrées validées`, {
        title: "Ok",
        type: "success",
      });
    } else {
      // notify failure
      this.notification.add("Les entrées n'ont pas pu être validées.", {
        title: "Erreur",
        type: "danger",
      });
    }
  },
});
