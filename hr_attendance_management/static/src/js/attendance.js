odoo.define('hr_switzerland.attendance', function (require) {
"use strict";

    var core = require('web.core');

    var hr_attendance = require('hr_attendance.my_attendances');

    var Model = require('web.Model');

    var QWeb = core.qweb;
    var _t = core._t;

    hr_attendance.include({
        start: function () {
            var self = this;
            var result = this._super();
            var hr_employee = new Model('hr.employee');
            hr_employee.query(['attendance_state', 'name', 'extra_hours_formatted', 'today_hour_formatted', 'time_warning_balance', 'time_warning_today', 'extra_hours_today'])
                .filter([['user_id', '=', self.session.uid]])
                .all()
                .then(function (res) {
                    if (_.isEmpty(res) ) {
                        self.$('.o_hr_attendance_employee').append(_t("Error : Could not find employee linked to user"));
                        return;
                    }
                    self.employee = res[0];
                    self.$el.html(QWeb.render("HrAttendanceMyMainMenu", {widget: self}));

                    // auto-counter
                    $('#moment_pl').html(Date.now());
                    setInterval(function () {
                        if ($('#moment_pl').length) {
                            var moment_start = moment(new Date(parseInt($('#moment_pl').text(), 10)));
                            var diff_minutes = moment().diff(moment_start, 'minutes');

                            ['worked_today', 'balance_today'].forEach(
                                function (el) {
                                    var matches = $('#' + el + '_pl').text().match(/^-?(\d{2}):(\d{2})$/);

                                    if (matches !== null && $('#state').text() === 'checked in') {
                                        var hours = parseInt(matches[1], 10);
                                        var minutes = parseInt(matches[2], 10);

                                        var total_minutes = (minutes + (hours * 60)) * (matches[0].substring(0, 1) === '-' ? -1 : 1);// eslint-disable-line no-extra-parens
                                        var negative = total_minutes + diff_minutes < 0;

                                        var new_total = Math.abs(total_minutes + diff_minutes);
                                        var new_hours = ('0' + Math.trunc(new_total / 60)).slice(-2); // eslint-disable-line no-extra-parens
                                        var new_minutes = ('0' + (new_total % 60)).slice(-2); // eslint-disable-line no-extra-parens

                                        $('#' + el).text((negative ? '-' : '') + new_hours + ':' + new_minutes);

                                        if (el !== 'worked_today') {
                                            $('#' + el).parent().get(0).style.color = negative ? 'red' : 'green';
                                        }
                                    }
                                });
                        }
                    }, 20000);
                });

            return result;
        }
    });
});

odoo.define('hr_switzerland.exchange_days_wizard', function(require) {
"use strict";

    var greeting_message = require('hr_attendance.greeting_message');

    greeting_message.include({
        start: function () {
            window.setAttendanceMessageTimeout = function(context) {
                return function() {
                    setTimeout(function() {
                        context.do_action(context.next_action, {
                            clear_breadcrumbs: true
                        });
                    }, 5000);
                }
            };

            window.add_timeout_button_event = function(className) {
                $('.'+className).click(window.attendance_message_timeout);
            };

            window.find_parent_by_tag_name = function (element, tag) {
                while (element.prop('tagName').toLowerCase() !== tag.toLowerCase()) {
                    element = element.parent();
                }
                return element;
            };

            // converts selection field into radio field
            window.convert_select_into_radio = function(parent_id) {
                var select = $('#' + parent_id).find('select').first();
                var result = $('#dates_available_radio_selection');
                result.html('');

                select.find('option').each(function () {
                    if ($(this).val() !== 'false') {
                        result.append('<div class="radio"><input type="radio" name="date_select"><span class="val_text"></span></div>');
                        var input = result.find('input').last();
                        var val_text = result.find('.val_text').last();
                        var date = moment($(this).val(), 'YYYY-MM-DD');
                        input.val(date.format('YYYY-MM-DD'));
                        val_text.html(date.format('dddd YYYY-MM-DD') + ' (' + $(this).text() + ' hours scheduled)');
                    } else {
                        // select first choice (select)
                        select.val($(this).next().val());
                    }
                });
                // select first choice (radio)
                result.find('input').first().get(0).checked = true;
                result.wrap('<p style="margin-left: 20px;"></p>');

                // link radio and select fields when changes
                result.find('input').change(function () {
                    select.val('"' + $(this).val() + '"');
                });

                // style modifications
                window.find_parent_by_tag_name($('#select_change_day_message'), 'table').css('margin-bottom', '-8px');
            };

            if (!this.attendance.due_hours && !this.attendance.check_out && this.attendance.total_attendance === 0 && !this.attendance.has_change_day_request) {
                this.do_action('hr_attendance_management.change_day_wizard');
                this._super();
                // remove timeout that redirects to main page after 5 seconds
                clearTimeout(this.return_to_main_menu);
                window.attendance_message_timeout = window.setAttendanceMessageTimeout(this);
            }
            else {
                this._super();
            }
        }
    });
});