odoo.define('hr_attendance_geolocation.web_widget_map', function (require) {
    "use strict";

    var MapWidget = require("web_widget_map")

    MapWidget.include({
        _initializeMap: function () {
            var self = this;
            var _super = this._super;
            var url = new URL(this.$el[0].baseURI);
            var record_id = parseInt(url.hash.substring(1).split("&")[0].substring(3));

            var marker1_uri = '/web_widget_map/static/src/img/marker.png';
            var marker2_uri = '/web_widget_map/static/src/img/marker2.png';

            this._rpc({
                model: 'hr.attendance',
                method: 'get_location',
                args: [record_id, ]
            }).then(function (result) {
                if (result) {
                    if (result.check_in_longitude && result.check_in_latitude) {
                        self.centerMap = [result.check_in_longitude, result.check_in_latitude]
                        self.markers.push(['Check-in', result.check_in_longitude, result.check_in_latitude, marker1_uri])
                        $("#map").append('<div title="Check-in" class="marker"/>')
                        if (result.check_out_longitude && result.check_out_latitude) {
                            self.markers.push(['Check-out', result.check_out_longitude, result.check_out_latitude, marker2_uri])
                            $("#map").append('<div title="Check-out" class="marker"/>')
                        }
                    }
                }
                _super.apply(self, arguments);
            });
        },
    });

    return MapWidget

});
