import { patch } from "@web/core/utils/patch";
import { CalendarController } from "@web/views/calendar/calendar_controller";

patch(CalendarController.prototype, {
  async validateWorkentries() {
    console.log("validate");
    console.log(this);

    const records = this.model.data.records;

    console.log(records);

    const employeeId = ""; // TODO employé actuel
    const start = ""; // TODO début période
    const stop = ""; // TODO fin période

    const record_ids = [];

    for (const record of Object.items(records)) {
      if (record) {
        // TODO filter date and maybe employee id?
        record_ids.push(record.id);
      }
    }

    console.log(record_ids);

    const result = await this.orm.call(
      "hr.work.entry",
      "action_validate",
      [record_ids],
      {}
    );

    console.log(result);
  },
});
