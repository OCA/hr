/*
 *    Copyright (C) 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
 *    All Rights Reserved.
 *
 *   This program is free software: you can redistribute it and/or modify
 *   it under the terms of the GNU Affero General Public License as published by
 *   the Free Software Foundation, either version 3 of the License, or
 *   (at your option) any later version.
 *
 *   This program is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU Affero General Public License for more details.
 *
 *   You should have received a copy of the GNU Affero General Public License
 *   along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

openerp.hr_webcam = function(instance) {
    
    // client action hook
    instance.web.client_actions.add("photo.action", "instance.hr_webcam.action");
    instance.hr_webcam.action = instance.web.Widget.extend({
            
        template: 'photo.action',
           
        events: {
            'click .oe_hr_webcam_close a': 'window_close'
        },
            
        window_close: function() {
            var self = this;
            self.getParent().history_back();
            self.destroy();
        },
            
        init: function(parent, action) {
            this._super(parent, action);
            this.employee_id = action.params.employee_id;
        },
            
        start: function() {
            
            this._super();
                
            var pos = 0;
            var ctx = null;
            var cam = null;
            var image = null;
            var employee_id = this.employee_id;
            
            jQuery("#webcam").webcam({
                width: 320,
                height: 240,
                mode: "callback",
                swffile: "/hr_webcam/static/jscam_canvas_only.swf",
                onTick: function() {},
                    
                onSave: function(data) {
                    var col = data.split(";");
                    var canvas = document.getElementById("canvas");
                    var ctx = canvas.getContext("2d");
                    var img = image;
                    if (img == null && ctx) {
                        ctx.clearRect(0, 0, 320, 240);
                        img = ctx.getImageData(0, 0, 320, 240);
                    }
                    for(var i = 0; i < 320; i++) {
                        var tmp = parseInt(col[i]);
                        img.data[pos + 0] = (tmp >> 16) & 0xff;
                        img.data[pos + 1] = (tmp >> 8) & 0xff;
                        img.data[pos + 2] = tmp & 0xff;
                        img.data[pos + 3] = 0xff;
                        pos+= 4;
                    }
                    image = img
                    
                    if (pos >= 4 * 320 * 240) {
                        ctx.putImageData(img, 0, 0);
                        vals = {'image': canvas.toDataURL("image/png").replace(/^data:image\/(png|jpg);base64,/, "")};
                        model = new instance.web.Model("hr.employee")
                        if (employee_id)
                            model.call('write', [employee_id, vals]).then(null);
                        pos = 0;
                    }
                },
                
                onCapture: function() {
                    webcam.save();
                },
                
                debug: function (type, string) {
                    jQuery("#status").html(type + ": " + string);
                },
            
                onLoad: function () {
            
                    var cams = webcam.getCameraList();
                    for(var i in cams) {
                        jQuery("#cams").append("<li>" + cams[i] + "</li>");
                    }
                },
            });
        },
    });
};
