// Copyright (C) 2018 by Camptocamp
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

odoo.define('hr_public_holidays.holidays_highlighter', function (require) {
    'use strict';

    var calendarView = require('web_calendar.CalendarView');
    var Model = require('web.Model');

    calendarView.include({
        willStart: function () {
            var hrHolidays = new Model('hr.holidays.public.line');
            // Tasked w/ fetching desired color from server params
            var irConfigParameter = new Model('ir.config_parameter');
            var publicHolidays = hrHolidays.call('search_read', [[], ['date']]);
            var holidayColor = irConfigParameter.call(
                'get_param', ['calendar.public_holidays_color']);

            return $.when(publicHolidays, holidayColor, this._super())
                .then(function (holidays, color) {
                    // As a result of `search_read` call is the JS object
                    // (dictionary), it's still our duty to clean up results
                    this.publicHolidays = holidays.map(
                        function (holiday) {
                            return holiday.date;
                        });
                    this.holidayColor = color;
                }.bind(this));
        },
        get_fc_init_options: function () {
            var res = this._super();
            var self = this;

            var oldRenderHandler = res.viewRender;
            // Extend view render callback w/ highlighting functionality
            res.viewRender = function () {
                // Read as super()
                oldRenderHandler.apply(this, arguments);
                var visibleDays = self.$('.o_calendar_view .fc-day');
                _.each(visibleDays, function (day) {
                    var dayDate = day.getAttribute('data-date');
                    if (self.publicHolidays.includes(dayDate)) {
                        // Found current day in a holiday list, colorize it
                        day.style.backgroundColor = self.holidayColor;
                    }
                });
            };

            return res;
        },
    });

});
