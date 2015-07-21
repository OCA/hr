openerp.hr_activity_on_timesheet = function(instance) {

    var QWeb = instance.web.qweb;
    var _t = instance.web._t;

    instance.hr_timesheet_sheet.WeeklyTimesheet = instance.hr_timesheet_sheet.WeeklyTimesheet.extend({
        events: {
            "click .oe_timesheet_weekly_account a": "go_to",
            "click .oe_timesheet_weekly_activity a": "go_to_activity",
        },
        init: function(parent, name) {
            this._super.apply(this, arguments);
            var self = this;

            self.account_names = {};
            self.activity_names = {};
        },
        go_to_account_selected: function(account_id) {
            this.do_action({
                type: 'ir.actions.act_window',
                field_values_model: "account.analytic.account",
                res_id: account_id,
                views: [[false, 'form']],
                target: 'current'
            });
        },
        go_to_activity: function(event) {
            var id = JSON.parse($(event.target).data("id"));
            this.do_action({
                type: 'ir.actions.act_window',
                res_model: "hr.activity",
                res_id: id,
                views: [[false, 'form']],
                target: 'current'
            });
        },
        map_accounts: function(self, accounts, dates, default_get, accounts_defaults) {
            // for each account in the dict we map the account defaults
            // this is required so that the timesheet receives the correct analytic journal
            return _(accounts).chain().map(function(activities, account_id){
                accounts_defaults = _.extend({}, default_get,
                    (accounts_defaults[account_id] || {}).value || {}
                );

                // map days in activities
                activities = self.map_activities(self, activities, account_id, dates, accounts_defaults);

                // sort activities by name
                activities = _.sortBy(activities, function(activity){
                    return self.activity_names[activity.activity_id];
                });

                return {
                    account_id: account_id,
                    activities: activities,
                    accounts_defaults: accounts_defaults,
                };
            }).value();
        },
        map_activities: function(self, activities, account_id, dates, accounts_defaults){
            // for each activity map the timesheet lines into days (list of timesheets)
            // the first element in days must be the record where we will insert/remove time
            return _(activities).chain().map(function(lines, activity_id){
                activity_id = activity_id === "false" ? false :  Number(activity_id);
                var index = _.groupBy(lines, "date");
                var days = _.map(dates,function(date){
                    var day = {
                        day: date,
                        lines: index[instance.web.date_to_str(date)] || []
                    };
                    // add a timesheet record where we will insert/remove hours
                    var to_add = _.find(day.lines, function(line){
                        return line.name === self.description_line;
                    });
                    if (to_add){
                        // find the record where we insert/remove
                        // place it at the beginning of the list of records
                        day.lines = _.without(day.lines, to_add);
                        day.lines.unshift(to_add);
                    }
                    else{
                        // if cant find the record, create one and
                        // place it at the beginning of the record list
                        day.lines.unshift(_.extend(_.clone(accounts_defaults), {
                            name: self.description_line,
                            unit_amount: 0,
                            date: instance.web.date_to_str(date),
                            account_id: account_id,
                            activity_id: activity_id,
                        }));
                    }
                    return day;
                });
                return {
                    days: days,
                    activity_id: activity_id,
                };
            }).value();
        },
        initialize_content: function(){
            var self = this;
            if (self.setting)
                return;
            // don't render anything until we have date_to and date_from
            if (!self.get("date_to") || !self.get("date_from"))
                return;
            this.destroy_content();

            // it's important to use those vars to avoid race conditions
            var dates;
            var accounts;
            var account_names;
            var activity_names;
            var default_get;
            return this.render_drop.add(
                new instance.web.Model("hr.analytic.timesheet").call("default_get",
                    [
                        [
                            'account_id', 'activity_id', 'general_account_id', 'journal_id', 
                            'date', 'name', 'user_id', 'product_id', 'product_uom_id', 'to_invoice', 'amount', 'unit_amount'
                        ],
                        new instance.web.CompoundContext({'user_id': self.get('user_id')})
                    ]
                ).then(function(result){
                    default_get = result;
                    // calculating dates
                    dates = [];
                    var start = self.get("date_from");
                    var end = self.get("date_to");
                    while (start <= end){
                        dates.push(start);
                        start = start.clone().addDays(1);
                    }
                    // group by account and activity
                    var activity_ids = [];
                    var account_ids = [];

                    // change the account_id and activity_id fields in each timesheet by the id of the field
                    // then make a dict {account_id: timesheet_record)
                    accounts = _(self.get("sheets")).chain().map(function(el){
                        if (typeof(el.account_id) === "object"){
                            // add account id to list of accounts
                            el.account_id = el.account_id[0];
                            account_ids.push(el.account_id);
                        }
                        if (typeof(el.activity_id) === "object"){
                            // add activity id to list of activities
                            el.activity_id = el.activity_id[0];
                            activity_ids.push(el.activity_id);
                        }
                        return el;
                    }).groupBy('account_id').value();

                    // for each value of the dict, create a dict mapped by activity that contains the timesheet records
                    accounts = _.each(accounts, function(account, key){
                        accounts[key] = _.groupBy(account, 'activity_id');
                    });

                    account_ids = _.uniq(account_ids);
                    activity_ids = _.uniq(activity_ids);

                    // Before rendering the timesheet, we need the default values for each account
                    deferred_1 = new instance.web.Model("hr.analytic.timesheet").call(
                        "multi_on_change_account_id", [
                            [], account_ids, new instance.web.CompoundContext({'user_id': self.get('user_id')})])
                    // and the name of the activities and account to be displayed
                    deferred_2 = self.get_activity_names(self, activity_ids)
                    deferred_3 = self.get_account_names(self, account_ids)

                    $.when(deferred_1, deferred_2, deferred_3).done(function(accounts_defaults){
                        // modify the account dict so that it can be parsed to fill the timesheet
                        accounts = self.map_accounts(self, accounts, dates, default_get, accounts_defaults);
                        // sort the accounts by name
                        accounts = _.sortBy(accounts, function(account){
                            return self.account_names[account.account_id];
                        });

                        self.dates = dates;
                        self.accounts = accounts;
                        self.activity_names = _.extend(self.activity_names, activity_names);
                        self.default_get = default_get;

                        // fill the timesheet
                        self.display_data();
                    });
                })
            );
        },
        get_account_names: function(self, account_ids){
            // we want only the records that are not in the current dict of names
            account_ids = _.filter(account_ids, function(account){
                return !(account in self.account_names);
            });
            // we make a querry only if there is at least one unknowed value
            if(account_ids.length !== 0){
                new instance.web.Model("account.analytic.account").call(
                    "name_get", [account_ids, new instance.web.CompoundContext()]
                ).then(function(result){
                    // name_get returns a list of tuples (id, name), we need a dict
                    account_names = {};
                    _.each(result, function(el){
                        account_names[el[0]] = el[1];
                    });
                    // update the current dict of names
                    self.account_names = _.extend(self.account_names, account_names);
                });
            }
        },
        get_activity_names: function(self, activity_ids){
            // we want only the records that are not in the current dict of names
            activity_ids = _.filter(activity_ids, function(activity){
                return !(activity in self.activity_names);
            });
            // we make a querry only if there is at least one unknowed value
            if(activity_ids.length !== 0){
                new instance.web.Model("hr.activity").call(
                    "name_get", [activity_ids, new instance.web.CompoundContext()]
                ).then(function(result){
                    // name_get returns a list of tuples (id, name), we need a dict
                    activity_names = {};
                    _.each(result,function(el){
                        activity_names[el[0]] = el[1];
                    });
                    // update the current dict of names
                    self.activity_names = _.extend(self.activity_names, activity_names);
                });
            }
        },
        get_box: function(account, activity, day_count){
            return this.$(
                '[data-account="'.concat(account.account_id, '"][data-activity="', activity.activity_id, '"][data-day-count="', day_count, '"]')
            );
        },
        display_data: function(){
            var self = this;
            self.$el.html(QWeb.render("hr_timesheet_sheet.WeeklyTimesheet", {widget: self}));
            // Accounts contain activities, Activities contain days, days contain amounts
            // sort accounts and activities by name
            _.each(self.accounts, function(account){
                _.each(account.activities, function(activity){
                    _.each(_.range(activity.days.length), function(day_count){
                        if (!self.get('effective_readonly')){
                            // get the amount in the related text input
                            self.get_box(account, activity, day_count).val(self.sum_box(activity, day_count, true)).change(function(){
                                var num = $(this).val();
                                //check if new input value is numeric
                                if (self.is_valid_value(num)){
                                    num = (num === 0) ? 0: Number(self.parse_client(num));
                                }
                                //check if new input value is legal numeric
                                if (isNaN(num)){
                                    $(this).val(self.sum_box(activity, day_count, true));
                                }
                                else{
                                    activity.days[day_count].lines[0].unit_amount += num - self.sum_box(activity, day_count);

                                    var product = activity.days[day_count].lines[0].product_id;
                                    product = (product instanceof Array) ? product[0] : product;

                                    var journal = activity.days[day_count].lines[0].journal_id;
                                    journal = (journal instanceof Array) ? journal[0] : journal;

                                    self.defs.push(
                                        new instance.web.Model("hr.analytic.timesheet").call("on_change_unit_amount",
                                            [
                                                [],
                                                product,
                                                activity.days[day_count].lines[0].unit_amount,
                                                false,
                                                false,
                                                journal
                                            ]
                                        ).then(function(res){
                                            activity.days[day_count].lines[0].amount = res.value.amount || 0;
                                            self.display_totals();
                                            self.sync();
                                        })
                                    );
                                    if(!isNaN($(this).val())){
                                        $(this).val(self.sum_box(activity, day_count, true));
                                    }
                                }
                            });
                        }
                        else{
                            self.get_box(account, activity, day_count).html(self.sum_box(activity, day_count, true));
                        }
                    });
                });
            });
            self.display_totals();
            self.$(".oe_timesheet_weekly_adding button").click(_.bind(this.init_add_account, this));
        },
        // Method to manage the account/activity selector
        init_add_account: function() {
            var self = this;
            if (self.dfm)
                return;
            // create the 'Next' button
            self.$(".oe_timesheet_weekly_add_row_line_1").show();
            self.$(".oe_timesheet_weekly_add_row_line_2").show();
            self.$(".oe_timesheet_weekly_adding").hide();
            self.$(".oe_timesheet_weekly_cancel").show();

            // create the inputs to select the account and the activity
            self.dfm = new instance.web.form.DefaultFieldManager(self);
            self.dfm.extend_field_desc({
                account: {relation: "account.analytic.account"},
                activity: {relation: "hr.activity"},
            });
            self.account_m2o = new instance.web.form.FieldMany2One(self.dfm, {
                attrs: {
                    name: "account",
                    type: "many2one",
                    domain: [
                        ['type','in',['normal', 'contract']],
                        ['state', '<>', 'close'],
                        ['use_timesheets','=',1],
                    ],
                    context: {
                        default_use_timesheets: 1,
                        default_type: "contract",
                    },
                    modifiers: '{"required": true}',
                },
            });

            // Set default value of the analytic account field
            self.account_m2o.get_search_result('').then(function(data){
                if (data.length > 0){
                    self.account_m2o.set_value(data[0]['id']);
                }
            });

            // create the input to select the activity
            self.activity_m2o = new instance.web.form.FieldMany2One(self.dfm, {
                attrs: {
                    name: "activity",
                    type: "many2one",
                    domain: [['authorized_user_ids', '=', self.get('user_id')], ['authorized_user_ids', '!=', false]],
                    context: new instance.web.CompoundContext({user_id: self.get('user_id')}),
                    modifiers: '{"required": true}',
                },
            });

            // When the account is changed, need to change the context of the activity field.
            // If the current selected activity is not autorized for the selected account,
            // replace the activity selected with the first value in the list of authorized activities.
            self.account_m2o.on('changed_value', this, function() {
                node = self.activity_m2o.node
                node.attrs.context = new instance.web.CompoundContext(
                    node.attrs.context, {
                        user_id: self.get('user_id'),
                        account_id: self.account_m2o.get_value(),
                    }
                );
                activity_field = self.activity_m2o;

                // Search activities
                self.activity_m2o.get_search_result('').then(function(data){
                    previous_activity_id = self.activity_m2o.get_value();
                    activity_dict = _.indexBy(data, 'id');

                    if (! (previous_activity_id in activity_dict)){
                        if (data.length > 0 ){
                            self.activity_m2o.set_value(data[0]['id']);
                            value = self.activity_m2o.get_value();
                            value = value;
                        }
                        else {
                            self.activity_m2o.set_value(false);
                        }
                    }
                });
            });

            // Place the fields in the widget
            self.activity_m2o.prependTo(self.$(".oe_timesheet_weekly_add_row_line_2 td:first-child"));
            self.account_m2o.prependTo(self.$(".oe_timesheet_weekly_add_row_line_2 td:first-child"));

            self.$(".oe_timesheet_weekly_cancel button").click(function(){
                self.close_account_selector();
                self.set({"sheets": self.generate_o2m_value()});
            });

            self.$(".oe_timesheet_weekly_add_row button").click(function(){
                var activity_id = self.activity_m2o.get_value();
                var account_id = self.account_m2o.get_value();
                if (account_id === false) {
                    self.dfm.set({display_invalid_fields: true});
                    return;
                }
                if(self.activity_m2o.get_value() === false){
                    self.dfm.set({display_invalid_fields: true});
                    return;
                }

                // Get the field values for the new timesheet
                deferred_1 = new instance.web.Model("hr.analytic.timesheet").call(
                    "on_change_account_id", [[], account_id, self.get('user_id')]);

                // Update the dicts of names with the selected account and activities
                deferred_2 = self.get_account_names(self, [account_id]);
                deferred_3 = self.get_activity_names(self, [activity_id]);

                $.when(deferred_1, deferred_2, deferred_3).done(function(field_values){
                    self.close_account_selector();
                    var ops = self.generate_o2m_value();
                    var new_timesheet_line = _.extend({}, self.default_get, field_values.value, {
                        name: self.description_line,
                        unit_amount: 0,
                        date: instance.web.date_to_str(self.dates[0]),
                        account_id: account_id,
                        activity_id: activity_id,
                    });
                    ops.push(new_timesheet_line);
                    self.set({"sheets": ops});
                });
            });
        },
        close_account_selector: function() {
            self.$(".oe_timesheet_weekly_add_row_line_1").hide();
            self.$(".oe_timesheet_weekly_add_row_line_2").hide();
            self.$(".oe_timesheet_weekly_adding").show();
            self.$(".oe_timesheet_weekly_cancel").hide();
        },
        display_totals: function() {
            var self = this;
            var day_tots = _.map(_.range(self.dates.length), function() { return 0; });
            var super_tot = 0;
            _.each(self.accounts, function(account) {
                _.each(account.activities, function(activity){
                    var acc_tot = 0;
                    _.each(_.range(self.dates.length), function(day_count) {
                        var sum = self.sum_box(activity, day_count);
                        acc_tot += sum;
                        day_tots[day_count] += sum;
                        super_tot += sum;
                    });
                    self.get_total(account, activity).html(self.format_client(acc_tot));
                });
            });
            _.each(_.range(self.dates.length), function(day_count) {
                self.get_day_total(day_count).html(self.format_client(day_tots[day_count]));
            });
            self.get_super_total().html(self.format_client(super_tot));
        },
        get_total: function(account, activity) {
            return this.$('[data-account-total="' + account.account_id + '"][data-activity-total="' + activity.activity_id + '"]');
        },
        generate_o2m_value: function() {
            var self = this;
            var ops = [];
            var ignored_fields = self.ignore_fields();
            _.each(self.accounts, function(account) {
                _.each(account.activities, function(activity){
                    _.each(activity.days, function(day) {
                        _.each(day.lines, function(line) {
                            if (line.unit_amount !== 0) {
                                var tmp = _.clone(line);
                                tmp.id = undefined;
                                _.each(line, function(v, k) {
                                    if (v instanceof Array) {
                                        tmp[k] = v[0];
                                    }
                                });
                                // we remove line_id as the reference to the _inherits field will no longer exists
                                tmp = _.omit(tmp, ignored_fields);
                                ops.push(tmp);
                            }
                        });
                    });
                });
            });
            return ops;
        },   
    });
};
