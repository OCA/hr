openerp.hr_roster = function(instance) {
    var QWeb = instance.web.qweb,
        _t = instance.web._t,
        _lt = instance.web._lt,
        humanize_time = function(mins){
            var mins = Number.parseInt(mins),
                h = instance.web.format_value(Number.parseInt(mins / 60), this, 0),
                m = instance.web.format_value(mins % 60, this, 0);

            var h_text = "", m_text = "";
            if(h > 0){
                h_text = h + " hour";
                if(h > 1) h_text += "s";
            }
            if(m > 0){
                m_text = m + " minute";
                if(m > 1) m_text += "s";
            }
            return _.string.sprintf("%s %s", h_text, m_text);
        };

    // BEGIN hr_duty_roster
    instance.hr_duty_roster = {};

    instance.hr_duty_roster.FieldShiftDay = instance.web.form.FieldChar.extend({
        is_false: function(){
            var 
                selection = this.field_manager.get_field_desc(this.name).selection,
                v = this.get('value'),
                r = this._super() || !(_.any(selection, function(choice, index, list){
                    return choice[0] == v;
                }));
            return r;
        }
    });

    instance.hr_duty_roster.FieldEmployeesFilter = instance.web.form.FieldMany2One.extend({
        get_search_blacklist: function() {
            // WARNING: i am not sure if this will work for future v8
            var blacklist = _.reduce(this.field_manager.dataset.cache, function(memo, row){
                var employee_id = row.values.employee_id;
                // if a record is loaded from db, the employee_id is a tuple in the form of (id, name)
                // otherwise, it is just an id (integer)
                if(_.isArray(employee_id)){
                    employee_id = employee_id[0];  
                }
                memo.push(employee_id);
                return memo;
            }, []);

            return blacklist;
        }
    });

    instance.web.form.widgets.add('shift_day', 'instance.hr_duty_roster.FieldShiftDay');
    instance.web.form.widgets.add('employees_filter', 'instance.hr_duty_roster.FieldEmployeesFilter');

    // we have to use customize _format for this column, or otherwise the value that is rendered into the cell
    // has an "id," prepended to it
    instance.hr_duty_roster.EmployeesFilterColumn = instance.web.list.Column.extend({
        _format: function(row_data, options){
            var value = row_data.employee_id.value;
            return value[1] ? value[1].split("\n")[0] : value[1];
        }
    });

    instance.web.list.columns.add('field.employees_filter', 'instance.hr_duty_roster.EmployeesFilterColumn');

    instance.hr_duty_roster.WidgetDatePicker = instance.web.form.FormWidget.extend({
        renderElement: function(){
            var today = new Date(), m = 1, y = 2014, d = 1;
            if(typeof this.field_manager.get_field_desc('month') === 'undefined'){
                m = today.getMonth();
            }
            else{
                m = this.field_manager.get_field_value('month') - 1;  // Python month is 1-base
            }

            if(typeof this.field_manager.get_field_desc('year')  === 'undefined'){
                y = today.getFullYear();
            }
            else{
                y = this.field_manager.get_field_value('year');
            }

            if(today.getFullYear() === y && today.getMonth() === m) d = today.day;

            this.$el.html(QWeb.render('DatePickerWidget', {_id: 'hr_duty_roster_dp' + _.uniqueId(), year: y, month: m, day: d}));
        }
    });

    instance.hr_duty_roster.WidgetShiftCodeAll = instance.web.form.FormWidget.extend({
        renderElement: function(){
            var self = this,
                model = new instance.web.Model("hr.shift_code");
            
            model.query(['code', 'time_in', 'time_out', 'duration', 'break', 'description']).all().then(function(rows){
                _.map(rows, function(v, k, list){
                    list[k]['duration_text'] = humanize_time(v['duration']);
                    list[k]['time_in'] = instance.web.format_value(v['time_in'], {'widget': 'time'});
                    list[k]['time_out'] = instance.web.format_value(v['time_out'], {'widget': 'time'});
                });
                var out = QWeb.render('ShiftCodeAllWidget', {'selection': rows});
                self.$el.html(out);
            });
        }
    });

    instance.web.form.custom_widgets.add('datepicker', 'instance.hr_duty_roster.WidgetDatePicker');
    instance.web.form.custom_widgets.add('shiftcodeall', 'instance.hr_duty_roster.WidgetShiftCodeAll');
    // --- END hr_duty_roster


    // -- BEGIN hr_shift_code
    instance.hr_shift_code = {};

    instance.hr_shift_code.FieldDuration = instance.web.form.FieldChar.extend({
        render_value: function(){
            this.$el.text(humanize_time(this.get_value()));
        }
    });

    instance.web.form.widgets.add('duration_mins', 'instance.hr_shift_code.FieldDuration');

    instance.hr_shift_code.TimeWidget = instance.web.DateTimeWidget.extend({
        jqueryui_object: "timepicker",
        type_of_date: "time",
        picker: function() {
            if(arguments[0] === 'setDate' && _.isEmpty(this.get('value'))){
                // NOTE: this is a hack - default time (now) is almost always useless. 
                var args = Array.prototype.slice.call(arguments),
                    time = args[1];
                time.setHours(0);
                time.setMinutes(0);
                time.setSeconds(0);
                return $.fn[this.jqueryui_object].apply(this.$input_picker, args);
            }
            return $.fn[this.jqueryui_object].apply(this.$input_picker, arguments);
        },
        on_picker_select: function(text, instance_) {
            // NOTE: as of jQuery timepicker v0.9.9, retriving time from timepicker with getDate always returns jQuery object
            var time_str = this.picker('getDate').val(), // this.picker is a timepicker
                val = instance.web.str_to_time(time_str + ":00");  // seconds not returned

            this.$input
                .val(val ? this.format_client(val) : '')
                .change()
                .focus();
        },
        parse_client: function(v) {
            return instance.web.parse_value(v, {"widget": 'datetime'});
        },
        format_client: function(v) {
            return instance.web.format_value(v, {"widget": 'time'});
        }
    });

    instance.hr_shift_code.FieldTimePicker = instance.web.form.FieldDatetime.extend({
        build_widget: function() {
            return new instance.hr_shift_code.TimeWidget(this);
        },
        render_value: function() {
            if (!this.get("effective_readonly")) {
                this.datewidget.set_value(this.get('value'));
            } else {
                this.$el.text(instance.web.format_value(this.get('value'), {'widget': 'time'}, ''));
            }
        }
    });

    instance.web.form.widgets.add('timepicker', 'instance.hr_shift_code.FieldTimePicker');

    // custom columns used by shift code module
    instance.hr_shift_code.DurationMinsColumn = instance.web.list.Column.extend({
        _format: function(row_data, options){
            return _.escape(instance.web.format_value(
                humanize_time(row_data[this.id].value), this, options.value_if_empty));
        }
    });

    instance.hr_shift_code.TimeColumn = instance.web.list.Column.extend({
        _format: function(row_data, options){
            return _.escape(instance.web.format_value(
                instance.web.format_value(row_data[this.id].value, {'widget': 'time'}),
                this,
                options.value_if_empty));
        }
    });

    instance.web.list.columns.add('field.duration_mins', 'instance.hr_shift_code.DurationMinsColumn');
    instance.web.list.columns.add('field.time', 'instance.hr_shift_code.TimeColumn');
    // --- END hr_shift_code

    $('body').on('keyup', '.shift_day_list .day input', function(e){
        var 
            $i = $(this), 
            v  = $i.val().trim().toUpperCase(), 
            $n = $i;

        if($i.val() != v){
            $i.focus().val(v).change();
            if(!$i.parent().is('.oe_form_invalid')){
                // find next invalid shift day, or blur to trigger form save
                do{
                    $n = $n.parent().next().find(':input');
                    if($n.length > 0 && ($n.parent().is('.oe_form_invalid') || $n.val() == '')){
                        $n.select().focus();
                        return;
                    }
                } while($n.length > 0);
                $i.blur();
            }
        }
    });
}
