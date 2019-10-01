odoo.define('hr_attendance_warning.systray', function (require) {
    "use strict";

    var core = require('web.core');
    var session = require('web.session');
    var SystrayMenu = require('web.SystrayMenu');
    var Widget = require('web.Widget');
    var time = require('web.time');
    var bus = require('bus.bus').bus;
    var config = require('web.config');

    var QWeb = core.qweb;

    var WarningMenu = Widget.extend({
        template:'att_warning.view.Menu',
        events: {
            "click": "_onMenuClick",
            "click .o_mail_channel_preview": "_onWarningClick",
            "click .o_view_all_warnings": "_viewAllWarnings",
        },
        renderElement: function () {
            this._super();
            var self = this;
            session.user_has_group(
                'hr_attendance.group_hr_attendance_user'
            ).then(function (data) {
                if (data) {
                    self.do_show();
                }
            });
        },
        start: function () {
            self = this
            this.$warnings_preview = this.$(
                '.o_mail_navbar_dropdown_channels'
            );
            session.user_has_group(
                'hr_attendance.group_hr_attendance_user'
            ).then(function (data) {
                if (data) {
                    self._updateWarningsPreview();
                    var channel = 'hr.attendance.warning';
                    bus.add_channel(channel);
                    bus.on('notification', self, self._updateWarningsPreview);
                }
            });
            return this._super();
        },

        _getWarningsData: function () {
            var self = this;

            return self._rpc({
                model: 'hr.attendance.warning',
                method: 'pending_warnings_count',
                kwargs: {
                    context: session.user_context,
                },
            }).then(function (data) {
                self.warnings = data;
                for (var i = 0; i < self.warnings.length; ++i) {
                    self.warnings[i].date_ago = moment(time.str_to_datetime(
                        self.warnings[i].date)
                    ).fromNow();
                }
                self.warningsCounter = data.length;
                self.$('.o_notification_counter').text(self.warningsCounter);
                self.$el.toggleClass(
                    'o_no_notification', !self.warningsCounter
                );
            });
        },

        _isOpen: function () {
            return this.$el.hasClass('open');
        },

        _updateWarningsPreview: function () {
            var self = this;
            self._getWarningsData().then(function () {
                self.$warnings_preview.html(QWeb.render(
                    'att_warning.view.Data', {
                        warnings : self.warnings,
                    }
                ));
            });
        },

        _onWarningClick: function (event) {

            var warning_id = parseInt(
                $(event.currentTarget, 10
            ).data('warning-id'));
            this.do_action({
                type: 'ir.actions.act_window',
                name: 'Attendance Warnings',
                res_model: 'hr.attendance.warning',
                views: [[false, 'form']],
                res_id: warning_id,
            });
        },

        _viewAllWarnings: function () {
            this.do_action(
                'hr_attendance_warning.open_view_hr_attendance_warning');
        },

        _onMenuClick: function () {
            if (!this._isOpen()) {
                this._updateWarningsPreview();
            }
        },

    });

    SystrayMenu.Items.push(WarningMenu);

    return {
        WarningMenu: WarningMenu,
    };
});
