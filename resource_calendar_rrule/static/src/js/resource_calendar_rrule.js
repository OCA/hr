//-*- coding: utf-8 -*-
//Copyright 2017-2018 Therp BV <http://therp.nl>
//License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
odoo.define('resource_calendar_rrule', function(require) {
    "use strict";
    var core = require('web.core');
    var common = require('web.form_common');
    var formats = require('web.formats');
    var datepicker = require('web.datepicker');
    var Model = require('web.Model');
    var FieldSimplifiedAttendance =
    common.AbstractField.extend(common.ReinitializeFieldMixin, {
        template: 'FieldSimplifiedAttendance',
        _format_number: function(number) {
            return formats.format_value(number, {type: 'float_time'}, 0);
        },
        _format_day: function(day) {
            // in dateutil.rrule, MO=0, SU=6; here SU=0, SA=6
            return moment.weekdays((day + 1) % 7);
        },
        _format_date: function(date) {
            return formats.format_value(date, {type: 'date'}, 0);
        },
        _get_days: function(data_key) {
            var option_days = _.map(
                this.options.days || _.keys(this.get('value')[data_key]),
                function(v) {
                    return Number.parseInt(v, 10);
                }
            );
            return _.filter(
                this.get('value')[data_key],
                function(value, key) {
                    return _.contains(option_days, key);
                }
            );
        },
        initialize_content: function() {
            var value = this.get('value');
            if(this.get('effective_readonly')) {
                return;
            }
            this.$('.toolbar button[data-type]').click(
                this.proxy('change_type')
            );
            this.$('input[data-day]').change(this.proxy('change_hours'));
            if(!this.options.hide_start_stop) {
                this.start_widget = new datepicker.DateWidget(this);
                this.stop_widget = new datepicker.DateWidget(this);
                this.start_widget
                    .appendTo(this.$('.start_stop span.start').empty());
                this.stop_widget
                    .appendTo(this.$('.start_stop span.stop').empty());
                this.start_widget.set_value(value.start);
                this.stop_widget.set_value(value.stop);
                this.start_widget
                    .on('datetime_changed', this, this.proxy('change_start'));
                this.stop_widget
                    .on('datetime_changed', this, this.proxy('change_stop'));
            }
            if(!this.options.hide_ex_r_date) {
                this.ex_r_date_widget = new datepicker.DateWidget(this);
                this.ex_r_date_widget
                    .appendTo(this.$('div.ex_r_date span.ex_r_date').empty());
                this.$('div.ex_r_date button[data-action=exdate]')
                    .on('click', this, this.proxy('add_exdate'));
                this.$('div.ex_r_date button[data-action=rdate]')
                    .on('click', this, this.proxy('add_rdate'));
                this.$('div.exdate a.o_delete')
                    .on('click', this, this.proxy('delete_exdate'));
                this.$('div.rdate a.o_delete')
                    .on('click', this, this.proxy('delete_rdate'));
            }
            this.$('div.null button').click(this.proxy('add_value'));
        },
        change_start: function() {
            this.set_value(_.extend(
                {}, this.get('value'), {start: this.start_widget.get_value()}
            ));
        },
        change_stop: function() {
            this.set_value(_.extend(
                {}, this.get('value'), {stop: this.stop_widget.get_value()}
            ));
        },
        change_type: function(e) {
            var value = this.get('value');
            value.type = jQuery(e.target).data('type');
            switch(jQuery(e.target).data('type')) {
                case 'odd':
                    value.data_odd = value.data.slice();
                break;
                case 'all':
                    delete value.data_odd;
                break;
            }
            this.set_value(_.extend({}, value));
            return this.reinitialize();
        },
        change_hours: function(e) {
            var value = this.get('value'),
                target = jQuery(e.target),
                hours = 0;
            try {
                hours = formats.parse_value(
                    target.val(), {type: 'float_time'}, 0
                );
            } catch(error) {
                target.closest('table').addClass('oe_form_invalid');
                return;
            }
            target.closest('table').removeClass('oe_form_invalid');
            target.val(formats.format_value(
                hours, {type: 'float_time'}, 0
            ));
            value[
                target.closest('table[data-key]').data('key')
            ][
                target.data('day')
            ][
                target.closest('tr[data-time]').data('time')
            ] = hours;
            this.set_value(_.extend({}, value));
        },
        _add_ex_r_date: function(e, type) {
            if(!this.ex_r_date_widget.get_value()) {
                return;
            }
            var value = this.get('value');
            if(!value[type]) {
                value[type] = [];
            }
            value[type].push(this.ex_r_date_widget.get_value());
            this.set_value(_.extend({}, value));
            return this.reinitialize();
        },
        _delete_ex_r_date: function(e, type) {
            var value = this.get('value'),
                date = jQuery(e.currentTarget).data('date');
            value[type] = _.filter(
                value[type], function(x) {
                    return x !== date;
                }
            );
            if(!value[type].length) {
                delete value[type];
            }
            this.set_value(_.extend({}, value));
            return this.reinitialize();
        },
        add_exdate: function(e) {
            return this._add_ex_r_date(e, 'exdate');
        },
        add_rdate: function(e) {
            return this._add_ex_r_date(e, 'rdate');
        },
        delete_exdate: function(e) {
            return this._delete_ex_r_date(e, 'exdate');
        },
        delete_rdate: function(e) {
            return this._delete_ex_r_date(e, 'rdate');
        },
        add_value: function() {
            var self = this;
            new Model('resource.calendar').call(
                'default_simplified_attendance', [], {}
            ).then(function(result) {
                self.set_value(result);
            });
        },
        is_valid: function() {
            if(
                jQuery.isEmptyObject(this.get('value')) ||
                this.get('effective_readonly')
            ) {
                return true;
            }
            return this._super.apply(this, arguments) && (
                this.options.hide_start_stop || (
                    this.start_widget && this.start_widget.get_value()
                )
            );
        },
        render_value: function() {
            this.renderElement();
            this.initialize_content();
        },
    });
    core.form_widget_registry.add(
        'simplified_attendance', FieldSimplifiedAttendance
    );
    return {
        FieldSimplifiedAttendance: FieldSimplifiedAttendance,
    };
});
