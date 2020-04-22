odoo.define('ht_attendance_ntf.quagga', function (require) {
    "use strict";
    var core = require('web.core');

    var _t = core._t;
    var Class = core.Class;
    var Model = require('web.Model');
    var Dialog = require('web.Dialog');
    var kiosk_view = require('hr_attendance.kiosk_mode');


    // prevent duplicate
    var scanned = {
        'barcode': false,
        'date_scanned': false,
        'delay': 60,
    }
    // check if it is possible to show error message
    var control = false;
    // variable creation to store kiosk object
    var self = false;

    // resolve overlay canvas problem
    function overlay_canvas(){
        var video = $('#scanner-container video');
        var canv = $('#scanner-container canvas');
        canv.css('position', 'absolute');
        video.css('width', '100%');
        canv.css('width', video.width());
        var block_width = $('.o_hr_attendance_kiosk_mode').outerWidth();
        var left = (block_width - video.width()) / 2;
        canv.css('left', left);
    }

    // check if barcode is already scanned in a time interval (scanned.delay)
    function check_scanned(code){
        if (code == scanned.barcode){
            var now_date = new Date();
            var diff = new Date(now_date - scanned.date_scanned);
            var diff_second = diff / 1000;
            if(diff_second < scanned.delay){
                return true;
            }else{
                scanned.barcode = code;
                scanned.date_scanned = new Date();
                return false;
            }
        }else{
            scanned.barcode = code;
            scanned.date_scanned = new Date();
            return false;
        }
    }


    navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia || navigator.msGetUserMedia;
    window.URL = window.URL || window.webkitURL || window.mozURL || window.msURL || navigator.mediaDevices.getUserMedia;
    function getUserMedia(constraints, success, failure) {
        navigator.getUserMedia(constraints, function(stream) {
            var videoSrc = (window.URL && window.URL.createObjectURL(stream)) || stream;
            success.apply(null, [videoSrc]);
        }, failure);
    }


    var quagga_view = kiosk_view.include({
        events: _.defaults({
            "click #btn-start": "widgetStartScanner",
            "click #btn-stop": "widgetStopScanner",
        }, kiosk_view.prototype.events),
        widgetStartScanner : function(){
            // clear container
            $('#scanner-container').html('');
            // start cam
            this.startScanner();
            $('#btn-stop').delay(500).fadeIn(500);
            $('#btn-start').fadeOut(500);
            $('#scanner-container canvas').ready(function(){
                $('#scanner-container').delay(900).slideDown(900);
                setTimeout(
                    function(){
                        overlay_canvas();
                    }
                , 905);
            });
        },
        widgetStopScanner : function(){
            Quagga.stop();

            $('#btn-start').delay(500).fadeIn(500);
            $('#btn-stop').fadeOut(500);
            $('#scanner-container').delay(500).slideUp(900);
        },
        startScanner: function(){
            self = this;
            Quagga.init({
                inputStream : {
                    name : "Live",
                    type : "LiveStream",
                    target: document.querySelector('#scanner-container'),
                    constraints: {
                        width: 480,
                        height: 320,
                        facingMode: "environment"
                    },
                },
                decoder : {
                    readers : [
                        "code_128_reader",
                        "ean_reader",
                        "code_39_reader",
                        "code_39_vin_reader",
                        //"codabar_reader",
                        //"upc_reader",
                        //"upc_e_reader",
                        //"i2of5_reader",
                        //"2of5_reader",
                        "code_93_reader",
                    ]
                },
                multiple: true,
                locate: true,
                numOfWorkers: 4,
            }, function(err) {
                if (err) {
                    console.log(err);
                    return
                }
                Quagga.start();

                overlay_canvas();
            });

            Quagga.onProcessed(function(result) {
                var drawingCtx = Quagga.canvas.ctx.overlay,
                    drawingCanvas = Quagga.canvas.dom.overlay;

                if (result) {
                    if (result.boxes) {
                        drawingCtx.clearRect(0, 0, parseInt(drawingCanvas.getAttribute("width")), parseInt(drawingCanvas.getAttribute("height")));
                        result.boxes.filter(function (box) {
                            return box !== result.box;
                        }).forEach(function (box) {
                            Quagga.ImageDebug.drawPath(box, {x: 0, y: 1}, drawingCtx, {color: "green", lineWidth: 2});
                        });
                    }

                    if (result.box) {
                        Quagga.ImageDebug.drawPath(result.box, {x: 0, y: 1}, drawingCtx, {color: "#00F", lineWidth: 2});
                    }

                    if (result.codeResult && result.codeResult.code) {
                        Quagga.ImageDebug.drawPath(result.line, {x: 'x', y: 'y'}, drawingCtx, {color: 'red', lineWidth: 3});
                    }
                }
            });

            Quagga.onDetected(function(result) {
                var code = result.codeResult.code;
                var is_scanned = check_scanned(code);
                if(is_scanned != true){
                    control = true;
                    $('#audio').get(0).play();
                    var hr_employee = new Model('hr.employee');
                    hr_employee.call('attendance_scan', [code, ]).then(function (result) {
                        control = false;
                        if (result.action) {
                            // stop scanner and live cam (important)
                            self.widgetStopScanner();
                            self.do_action(result.action);
                        } else if (result.warning) {
                            if ( $( ".o_notification" ).length == 0) {
                                if($('.o_hr_attendance_user_badge').length==0){
                                    self.do_warn(result.warning);
                                    scanned.barcode = false;
                                    scanned.date_scanned = false;
                                }
                            }
                        }
                    });
                }else{
                    if(control === false){
                        if ( $( ".o_notification" ).length == 0) {
                            if($('.o_hr_attendance_user_badge').length==0){
                                $('#audio').get(0).play();
                                self.do_warn(_t("You can scan a badge only one time per 60 seconds."));
                            }
                        }
                    }
                }
            });

        }
    });



});
