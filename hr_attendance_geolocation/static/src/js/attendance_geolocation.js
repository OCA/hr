openerp.hr_attendance_geolocation = function (instance) {
    'use strict';

    instance.hr_attendance.AttendanceSlider.include({
        init: function () {
            this._super.apply(this, arguments);
            this.location = (null, null);
            this.errorCode = null;
        },
        do_update_attendance: function () {
            var self = this;
            var hr_employee = new instance.web.DataSet(self, 'hr.employee');
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(function (position) {
                    hr_employee.call('attendance_action_change', [
                        [self.employee.id],
                        {'attendance_location': [
                            position.coords.latitude, position.coords.longitude,
                        ]},
                    ]).done(function () {
                        self.last_sign = new Date();
                        self.set({"signed_in": ! self.get("signed_in")});
                    });
                }, function () {
                    console.warn('ERROR(${error.code}): ${error.message}');
                });
            }
        },
    });
};
