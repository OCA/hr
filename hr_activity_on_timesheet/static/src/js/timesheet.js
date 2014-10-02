
openerp.hr_activity_on_timesheet = function(instance) {

    var QWeb = instance.web.qweb;
    var _t = instance.web._t;

    instance.hr_activity_on_timesheet = {};

    instance.hr_activity_on_timesheet.WeeklyTimesheetWithActivity = instance.web.form.FormWidget.extend(instance.web.form.ReinitializeWidgetMixin, {
        events: {
            "click .oe_timesheet_weekly_account a": "go_to_account",
            "click .oe_timesheet_weekly_activity a": "go_to_activity",
        },


        ignore_fields: function() {
            return ['line_id'];
        },
        init: function() {
            this._super.apply(this, arguments);
            var self = this;
            this.set({
                sheets: [],
                date_to: false,
                date_from: false,
            });
            this.updating = false;
            this.defs = [];



            self.account_names = {};
            self.activity_names = {};



            this.field_manager.on("field_changed:timesheet_ids", this, this.query_sheets);
            this.field_manager.on("field_changed:date_from", this, function() {
                this.set({"date_from": instance.web.str_to_date(this.field_manager.get_field_value("date_from"))});
            });
            this.field_manager.on("field_changed:date_to", this, function() {
                this.set({"date_to": instance.web.str_to_date(this.field_manager.get_field_value("date_to"))});
            });
            this.field_manager.on("field_changed:user_id", this, function() {
                this.set({"user_id": this.field_manager.get_field_value("user_id")});
            });
            this.on("change:sheets", this, this.update_sheets);
            this.res_o2m_drop = new instance.web.DropMisordered();
            this.render_drop = new instance.web.DropMisordered();
            this.description_line = _t("/");
            // Original save function is overwritten in order to wait all running deferreds to be done before actually applying the save.
            this.view.original_save = _.bind(this.view.save, this.view);
            this.view.save = function(prepend_on_create){
                self.prepend_on_create = prepend_on_create;
                return $.when.apply($, self.defs).then(function(){
                    return self.view.original_save(self.prepend_on_create);
                });
            };
        },
        go_to_account: function(event) {
            var id = JSON.parse($(event.target).data("id"));
            this.do_action({
                type: 'ir.actions.act_window',
                res_model: "account.analytic.account",
                res_id: id,
                views: [[false, 'form']],
                target: 'current'
            });
        },
        go_to_account_selected: function(account_id) {
            this.do_action({
                type: 'ir.actions.act_window',
                res_model: "account.analytic.account",
                res_id: account_id,
                views: [[false, 'form']],
                target: 'current'
            });
        },
        go_to_activity: function(event) {
            var id = JSON.parse($(event.target).data("id"));
            this.do_action({
                type: 'ir.actions.act_window',
                res_model: "hr.analytic.timesheet.activity",
                res_id: id,
                views: [[false, 'form']],
                target: 'current'
            });
        },
        query_sheets: function() {
            var self = this;
            if (self.updating)
                return;
            var commands = this.field_manager.get_field_value("timesheet_ids");
            this.res_o2m_drop.add(
                new instance.web.Model(
                    this.view.model
                )
                .call(
                    "resolve_2many_commands",
                    [
                        "timesheet_ids",
                        commands,
                        [],
                        new instance.web.CompoundContext()
                    ]
                )
            )
            .done(
                function(result)
                {
                    self.querying = true;
                    self.set({sheets: result});
                    self.querying = false;
                }
            );
        },
        update_sheets: function() {
            var self = this;
            if (self.querying)
                return;
            self.updating = true;
            self.field_manager.set_values(
                {
                    timesheet_ids: self.get("sheets")
                }
            )
            .done(function() {
                self.updating = false;
            });
        },

        initialize_field: function() {
            instance.web.form.ReinitializeWidgetMixin
            .initialize_field
            .call(this);
            var self = this;
            self.on("change:sheets", self, self.initialize_content);
            self.on("change:date_to", self, self.initialize_content);
            self.on("change:date_from", self, self.initialize_content);
            self.on("change:user_id", self, self.initialize_content);
        },
        sum_box: function(activity, day_count, show_value_in_hour) {
            var line_total = 0;
            if("days" in activity){
                _.each(
                    activity.days[day_count].lines,
                    function(line){
                        line_total += line.unit_amount;
                    }
                );
            }
            return (show_value_in_hour && line_total !== 0)?this.format_client(line_total):line_total;
        },
        destroy_content: function() {
            if (this.dfm) {
                this.dfm.destroy();
                this.dfm = undefined;
            }
        },
        is_valid_value:function(value){
            var split_value = value.split(":");
            var valid_value = true;
            if (split_value.length > 2)
                return false;
            _.detect(split_value,function(num){
                if(isNaN(num)){
                    valid_value = false;
                }
            });
            return valid_value;
        },
        map_accounts: function(self, accounts, dates, default_get, accounts_defaults) {
            return _(accounts).chain().map(
                // for each account get activities
                function(activities, account_id)
                {
                    accounts_defaults = _.extend(
                        {},
                        default_get,
                        (accounts_defaults[account_id] || {}).value || {}
                    );

                    account_id = account_id === "false" ? false :  Number(account_id);

                    activities = self.map_activities(self, activities, account_id, dates, accounts_defaults);
                    return {
                        account_id: account_id,
                        activities: activities,
                        accounts_defaults: accounts_defaults,
                    };
                }
            ).value();
        },
        map_activities: function(self, activities, account_id, dates, accounts_defaults){
            return _(activities).chain().map(function(lines, activity_id){
                activity_id = activity_id === "false" ? false :  Number(activity_id);
                var index = _.groupBy(lines, "date");
                var days = _.map(dates,function(date){
                    var day = {
                        day: date,
                        lines: index[instance.web.date_to_str(date)] || []
                    };
                    // add line where we will insert/remove hours
                    var to_add = _.find(day.lines, function(line){
                        return line.name === self.description_line;
                    });
                    if (to_add){
                        day.lines = _.without(day.lines, to_add);
                        day.lines.unshift(to_add);
                    }
                    else{
                        day.lines.unshift(
                            _.extend(
                                _.clone(accounts_defaults),
                                {
                                    name: self.description_line,
                                    unit_amount: 0,
                                    date: instance.web.date_to_str(date),
                                    account_id: account_id,
                                    activity_id: activity_id,
                                }
                            )
                        );
                    }
                    return day;
                });
                return {
                    days: days,
                    activity_id: activity_id,
                };
            }).value();
        },
        initialize_content: function()
        {
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
                new instance.web.Model("hr.analytic.timesheet").call(
                    "default_get", 
                    [
                        [
                            'account_id',
                            'activity_id',
                            'general_account_id',
                            'journal_id',
                            'date',
                            'name',
                            'user_id',
                            'product_id',
                            'product_uom_id',
                            'to_invoice',
                            'amount',
                            'unit_amount'
                        ],
                        new instance.web.CompoundContext(
                            {'user_id': self.get('user_id')}
                        )
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
                    accounts = _(self.get("sheets")).chain().map(function(el){
                        // much simpler to use only the id in all cases
                        if (typeof(el.account_id) === "object")
                        {
                            el.account_id = el.account_id[0];
                            account_ids.push(el.account_id);
                        }
                        if (typeof(el.activity_id) === "object")
                        {
                            // add activity id to list of activities
                            el.activity_id = el.activity_id[0];
                            activity_ids.push(el.activity_id);
                        }
                        return el;
                    }).groupBy('account_id').value();

                    accounts = _.each(accounts, function(account, key){
                        accounts[key] = _.groupBy(account, 'activity_id');
                    });

                    account_ids = _.uniq(account_ids);
                    activity_ids = _.uniq(activity_ids);

                    return new instance.web.Model("hr.analytic.timesheet").call(
                        "multi_on_change_account_id",
                        [
                            [],
                            account_ids,
                            new instance.web.CompoundContext(
                                {'user_id': self.get('user_id')}
                            )
                        ]
                    ).then(function(accounts_defaults){
                        accounts = self.map_accounts(self, accounts, dates, default_get, accounts_defaults);

                        // we need the name_get of the activities
                        return new instance.web.Model("hr.analytic.timesheet.activity").call(
                            "name_get",
                            [
                                activity_ids,
                                new instance.web.CompoundContext()
                            ]
                        ).then(function(result){
                            activity_names = {};
                            _.each(result,function(el){
                                activity_names[el[0]] = el[1];
                            });
                        });
                    }).then(function(result){
                    // we need the name_get of the analytic accounts
                        return new instance.web.Model("account.analytic.account").call(
                            "name_get",
                            [
                                account_ids,
                                new instance.web.CompoundContext()
                            ]
                        ).then(function(result){
                            account_names = {};
                            _.each(result, function(el){
                                account_names[el[0]] = el[1];
                            });
                        });
                    });
                }).then(function(result){
                    // we put all the gathered data in self, then we render
                    self.dates = dates;
                    self.accounts = accounts;
                    self.account_names = _.extend(self.account_names, account_names);
                    self.activity_names = _.extend(self.activity_names, activity_names);
                    self.default_get = default_get;
                    //real rendering
                    self.display_data();
                })
            );
        },
        get_account_names: function(self, account_ids, callback)
        {
            account_ids = _.filter(account_ids, function(account){
                return !(account in self.account_names);
            });
            if(account_ids.length !== 0){
                new instance.web.Model("account.analytic.account").call(
                    "name_get",
                    [
                        account_ids,
                        new instance.web.CompoundContext()
                    ]
                ).then(function(result){
                    account_names = {};
                    _.each(result, function(el){
                        account_names[el[0]] = el[1];
                    });
                    self.account_names = _.extend(self.account_names, account_names);
                    callback();
                });
            }
            else{
                callback();
            }
        },
        get_activity_names: function(self, activity_ids, callback)
        {
            activity_ids = _.filter(activity_ids, function(activity){
                return !(activity in self.activity_names);
            });
            if(activity_ids.length !== 0){
                new instance.web.Model("hr.analytic.timesheet.activity").call(
                    "name_get",
                    [
                        activity_ids,
                        new instance.web.CompoundContext()
                    ]
                ).then(function(result){
                    activity_names = {};
                    _.each(result,function(el){
                        activity_names[el[0]] = el[1];
                    });
                    self.activity_names = _.extend(self.activity_names, activity_names);
                    callback();
                });
            }
            else{
                callback();
            }
        },
        get_box: function(account, activity, day_count)
        {
            return this.$(
                '[data-account="' + account.account_id
                + '"][data-activity="' + activity.activity_id
                + '"][data-day-count="' + day_count + '"]'
            );
        },
        display_data: function()
        {
            var self = this;
            self.$el.html(QWeb.render("hr_activity_on_timesheet.WeeklyTimesheetWithActivity",{widget: self}));
            _.each(self.accounts, function(account){
                    // for each activity
                    _.each(account.activities, function(activity){
                        _.each(_.range(activity.days.length), function(day_count){
                            if (!self.get('effective_readonly')){
                                // get the amount in the related text input
                                self.get_box(account, activity, day_count)
                                .val(
                                    self.sum_box(activity, day_count, true)
                                )
                                .change(function(){
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
                                            new instance.web.Model("hr.analytic.timesheet").call(
                                                "on_change_unit_amount",
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
                                self.get_box(account, activity, day_count).html(
                                    self.sum_box(activity, day_count, true)
                                );
                            }
                        });
                    });
                }
            );
            self.display_totals();
            self.$(".oe_timesheet_weekly_adding button").click(_.bind(this.init_add_account, this));
        },
        init_add_account: function() {
            var self = this;
            if (self.dfm)
                return;
            self.$(".oe_timesheet_weekly_add_row").show();
            self.dfm = new instance.web.form.DefaultFieldManager(self);
            self.dfm.extend_field_desc({
                account: {
                    relation: "account.analytic.account",
                },
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
            self.account_m2o.prependTo(self.$(".oe_timesheet_weekly_add_row td:nth-child(2)"));
            self.$(".oe_timesheet_weekly_add_row button").click(function() {
                var account_id = self.account_m2o.get_value();
                if (account_id === false) {
                    self.dfm.set({display_invalid_fields: true});
                    return;
                }

                //need to update the dict self.account_names if does not contain account_id
                //before continuing
                new self.get_account_names(self, [account_id], function(){
                    var activity_ids = [];
                    new instance.web.Model("account.analytic.account").call(
                        "get_authorized_activities",
                        [
                            account_id,
                            new instance.web.CompoundContext()
                        ]
                    ).then(function(res) {
                        activity_ids = res;

                        self.$(".oe_timesheet_weekly_add_row").hide();
                        self.$(".oe_timesheet_weekly_selected_account").show();
                        self.$(".oe_timesheet_weekly_selected_account td").empty();
                        account_name = self.account_names[account_id];
                        self.$(".oe_timesheet_weekly_selected_account td").html(
    '<a href="javascript:void(0)"' + account_name + 'data-id="' + '">' + account_name + '</a>');
                        self.$(".oe_timesheet_weekly_selected_account a").click(function(){
                            self.go_to_account_selected(account_id);
                        });

                        self.dfm.extend_field_desc({
                            activity: {
                                relation: "hr.analytic.timesheet.activity",
                            },
                        });

                        self.activity_m2o = new instance.web.form.FieldMany2One(self.dfm, {
                            attrs: {
                                name: "activity",
                                type: "many2one",
                                domain: [
                                    ['id','in', activity_ids],
                                ],
                                context: {
                                },
                                modifiers: '{"required": true}',
                            },
                        });

                        self.$(".oe_timesheet_weekly_add_activity").show();
                        self.activity_m2o.prependTo(self.$(".oe_timesheet_weekly_add_activity td:nth-child(2)"));

                        self.$(".oe_timesheet_weekly_add_activity button").click(function() {
                            if(self.activity_m2o.get_value() === false){
                                self.dfm.set({display_invalid_fields: true});
                                return;
                            }
                            activity_id = self.activity_m2o.get_value();
                            self.get_activity_names(self, [activity_id], function(){
                                var ops = self.generate_o2m_value();
                                new instance.web.Model("hr.analytic.timesheet").call("on_change_account_id", [[], account_id]).then(function(res) {
                                    var def = _.extend({}, self.default_get, res.value, {
                                        name: self.description_line,
                                        unit_amount: 0,
                                        date: instance.web.date_to_str(self.dates[0]),
                                        account_id: account_id,
                                        activity_id: activity_id,
                                    });
                                    ops.push(def);
                                    self.set({"sheets": ops});
                                });
                            });
                        });
                    });
                });
            });
        },
        get_total: function(account, activity) {
            return this.$('[data-account-total="' + account.account_id + '"][data-activity-total="' + activity.activity_id + '"]');
        },
        get_day_total: function(day_count) {
            return this.$('[data-day-total="' + day_count + '"]');
        },
        get_super_total: function() {
            return this.$('.oe_timesheet_weekly_supertotal');
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
        sync: function() {
            var self = this;
            self.setting = true;
            self.set({sheets: this.generate_o2m_value()});
            self.setting = false;
        },
        //converts hour value to float
        parse_client: function(value) {
            return instance.web.parse_value(value, { type:"float_time" });
        },
        //converts float value to hour
        format_client:function(value){
            return instance.web.format_value(value, { type:"float_time" });
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

    instance.web.form.custom_widgets.add(
        'weekly_timesheet_with_activity',
        'instance.hr_activity_on_timesheet.WeeklyTimesheetWithActivity'
    );
};
