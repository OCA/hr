odoo.define('hr_attendance_geolocation.attendances_geolocation', function (require) {
    "use strict";

    var MyAttendances = require('hr_attendance.my_attendances');
    var KioskConfirm = require('hr_attendance.kiosk_confirm');

    MyAttendances.include({
        init: function (parent, action) {
            this._super.apply(this, arguments);
            this.location = (null, null);
            this.errorCode = null;
        },
        update_attendance: function () {
            var self = this;
            var options = {
                enableHighAccuracy: true,
                timeout: 5000,
                maximumAge: 0
            };
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(self._manual_attendance.bind(self), self._getPositionError, options);
            }
        },
        _manual_attendance: function (position) {
            var self = this;
            this._rpc({
                model: 'hr.employee',
                method: 'attendance_manual',
                args: [[self.employee.id], 'hr_attendance.hr_attendance_action_my_attendances', null, [position.coords.latitude, position.coords.longitude]],
            })
            .then(function(result) {
                if (result.action) {
                    self.do_action(result.action);
                } else if (result.warning) {
                    self.do_warn(result.warning);
                }
            });
        },
        _getPositionError: function (error) {
            console.warn('ERROR(${error.code}): ${error.message}');
        },
    });

    KioskConfirm.include({
        events: _.extend(KioskConfirm.prototype.events, {
            "click .o_hr_attendance_sign_in_out_icon":  _.debounce(function() {
                this.update_attendance();
            }, 200, true),
            "click .o_hr_attendance_pin_pad_button_ok": _.debounce(function() {
                this.pin_pad = true;
                this.update_attendance();
            }, 200, true),
        }),
        init: function (parent, action) {
            this._super.apply(this, arguments);
            this.pin_pad = false;
        },
        update_attendance: function () {
            var self = this;
            var options = {
                enableHighAccuracy: true,
                timeout: 5000,
                maximumAge: 0
            };
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(self._manual_attendance.bind(self), self._getPositionError, options);
            }
        },
        _manual_attendance: function (position) {
            var self = this;
            if (this.pin_pad) {
                this.$('.o_hr_attendance_pin_pad_button_ok').attr("disabled", "disabled");
            }
            this._rpc({
                model: 'hr.employee',
                method: 'attendance_manual',
                args: [[this.employee_id], this.next_action, this.$('.o_hr_attendance_PINbox').val(), [position.coords.latitude, position.coords.longitude]],
            })
            .then(function(result) {
                if (result.action) {
                    self.do_action(result.action);
                } else if (result.warning) {
                    self.do_warn(result.warning);
                    if (self.pin_pad) {
                        self.$('.o_hr_attendance_PINbox').val('');
                        setTimeout( function() {
                            self.$('.o_hr_attendance_pin_pad_button_ok').removeAttr("disabled");
                        }, 500);
                    }
                    self.pin_pad = false;
                }
            });
        },
        _getPositionError: function (error) {
            console.warn('ERROR(${error.code}): ${error.message}');
        },
    });

});
