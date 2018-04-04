//-*- coding: utf-8 -*-
//© 2017 Therp BV <http://therp.nl>
//License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

openerp.resource_calendar_rrule = function(instance)
{
    instance.resource_calendar_rrule.FieldSimplifiedAttendance =
    instance.web.form.AbstractField
    .extend(instance.web.form.ReinitializeFieldMixin, {
        template: 'FieldSimplifiedAttendance',
        _format_number: function(number)
        {
            return instance.web.format_value(
                number, {type: 'float_time'}, 0
            );
        },
        _format_day: function(day)
        {
            // in dateutil.rrule, MO=0, SU=6; here SU=0, SA=6
            return Date.CultureInfo.shortestDayNames[(day + 1) % 7];
        },
        _format_date: function(date)
        {
            return instance.web.format_value(
                date, {type: 'date'}, 0
            );
        },
        _get_days: function(data_key)
        {
            var data = this.get('value')[data_key];
            if (!data)
                return this.proxy('_get_default_days')();
            var option_days = _.map(
                this.options.days || _.keys(data),
                function(v) {return Number.parseInt(v)}
            );
            var result = _.filter(
                data,
                function(value, key) {return _.contains(option_days, key)}
            );
            return result;
        },
        _get_default_days: function() {
            _days = [];
            enabled_days = this.options.days || [0, 1, 2, 3, 4, 5, 6];
            for (var i=0; i<enabled_days.length; i++) {
                _days.push({
                    day: enabled_days[i],
                    morning: 4.0,
                    afternoon: 4.0
                });
            }
            return _days;
        },
        initialize_content: function()
        {
            // bind change_type buttons
            this.$('.toolbar').on('click', 'button[data-type]',
                this.proxy('change_type')
            );
            var value = this.get('value');
            if(this.get('effective_readonly'))
            {
                return;
            }
            this.$('input[data-day]').change(this.proxy('change_hours'));
            if(!this.options.hide_start_stop)
            {
                this.start_widget = new instance.web.DateWidget(this);
                this.stop_widget = new instance.web.DateWidget(this);
                this.start_widget
                    .appendTo(this.$('.start_stop span.start').empty());
                this.stop_widget
                    .appendTo(this.$('.start_stop span.stop').empty());
                this.start_widget.set_value(value.start);
                this.stop_widget.set_value(value.stop);
                this.start_widget
                    .on('datetime_changed', this, this.proxy('change_start'))
                this.stop_widget
                    .on('datetime_changed', this, this.proxy('change_stop'))
            }
        },
        change_start: function(e)
        {
            this.set_value(_.extend(
                {}, this.get('value'), {start: this.start_widget.get_value()}
            ));
        },
        change_stop: function(e)
        {
            this.set_value(_.extend(
                {}, this.get('value'), {stop: this.stop_widget.get_value()}
            ));
        },
        change_type: function(e)
        {
            var value = this.get('value');
            value.type = jQuery(e.target).data('type');
            switch(jQuery(e.target).data('type'))
            {
                case 'all':
                    if (!value['data'])
                        value['data'] = this.proxy('_get_default_days')();
                case 'odd':
                    if (!value['data_odd'])
                        value['data_odd'] = _.map(value['data'], function(data)
                        {
                            return _.clone(data);
                        });
            };
            this.set_value(_.extend({}, value));
            this.reinitialize();
        },
        change_hours: function(e)
        {
            var value = this.get('value'),
                target = jQuery(e.target),
                hours = 0;
            try
            {
                hours = instance.web.parse_value(
                    target.val(), {type: 'float_time'}, 0
                );
            }
            catch(error)
            {
                target.closest('table').addClass('oe_form_invalid');
                return;
            }
            target.closest('table').removeClass('oe_form_invalid');
            target.val(instance.web.format_value(
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
        is_valid: function()
        {
            if(
                jQuery.isEmptyObject(this.get('value')) ||
                this.get('effective_readonly')
            )
            {
                return true;
            };
            return this._super.apply(this, arguments) &&
                (
                    this.options.hide_start_stop ||
                    this.start_widget && this.start_widget.get_value() &&
                    this.start_widget && this.start_widget.is_valid_() &&
                    this.stop_widget && this.stop_widget.is_valid_()
                );
        },
        render_value: function()
        {
            this.renderElement();
            this.initialize_content();
        },
    });
    instance.web.form.widgets.add(
        'simplified_attendance',
        'instance.resource_calendar_rrule.FieldSimplifiedAttendance'
    );
};
