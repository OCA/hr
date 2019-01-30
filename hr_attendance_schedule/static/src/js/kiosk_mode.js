odoo.define('hr_attendance_schedule.kiosk_mode', function(require){
  "use strict";

  var KioskMode = require('hr_attendance.kiosk_mode');

  KioskMode.include({
    start_clock: function() {
      var self = this;
      this.$('.o_hr_attendance_clock').text("...");
      return this._rpc({
        model: 'hr_attendance_schedule.clock',
        method: 'get_system_clock'
      }).then(function(data) {
          var server_date = new Date(data);
          self._clock_offset = server_date - new Date();
          self._init_clock_loop();
        });
    },

    _init_clock_loop: function() {
      var self = this;
      var update = function() {
        var date = new Date(Date.now() + self._clock_offset);
        var time_string = date.toLocaleTimeString(navigator.language, {hour: '2-digit', minute: '2-digit'});
        self.$('.o_hr_attendance_clock').text(time_string);
      };
      this.clock_start = setInterval(update, 500);
      update();
    }
  });

  return KioskMode;
});
