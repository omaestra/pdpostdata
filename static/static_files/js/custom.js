var transparentDemo = true;
var fixedTop = false;

$(window).scroll(function(e) {
    oVal = ($(window).scrollTop() / 170);
    $(".blur").css("opacity", oVal);

});
(function (factory) {
  if (typeof define === 'function' && define.amd) {
    // AMD. Register as anonymous module.
    define(['jquery'], factory);
  } else if (typeof exports === 'object') {
    // Node / CommonJS
    factory(require('jquery'));
  } else {
    // Browser globals.
    factory(jQuery);
  }
})(function ($) {

    var console = window.console || { log: function () {} };

function CustomCrop ($element) {

    this.$container = $element;

    this.$avatarView = this.$container.find('#cropper');
    this.$avatar = this.$avatarView.find('img');
    this.$avatarModal = this.$container.find('#cropper-modal');
    this.$loading = this.$container.find('.loading');

    this.$avatarForm = this.$avatarModal.find('.cropper-form');
    this.$avatarUpload = this.$avatarForm.find('.avatar-upload');
    this.$avatarSrc = this.$avatarForm.find('.image-src');
    this.$avatarData = this.$avatarForm.find('.image-data');
    this.$avatarInput = this.$avatarForm.find('.avatar-input');
    this.$avatarSave = this.$avatarForm.find('.avatar-save');
    this.$avatarBtns = this.$avatarForm.find('.avatar-btns');

    this.$avatarWrapper = this.$avatarModal.find('#cropper');
    this.$avatarPreview = this.$avatarModal.find('.img-preview');

    this.$editbtn = this.$container.find('.editbtn');
    console.log("init");
    this.init();
}

CustomCrop.prototype = {
    constructor: CustomCrop,

    support: {
      formData: !!window.FormData
    },

    init: function () {

          if (!this.support.formData) {
            this.initIframe();
          }

          this.initTooltip();
          this.initModal();
          this.addListener();
    },
    addListener: function () {
        this.$avatarView.on('click', $.proxy(this.click, this));
        this.$avatarInput.on('change', $.proxy(this.change, this));
        this.$avatarForm.on('submit', $.proxy(this.submit, this));
        this.$avatarBtns.on('click', $.proxy(this.rotate, this));
        this.$editbtn.on('click', $.proxy(this.click, this));
    },

    initTooltip: function () {
        this.$avatarView.tooltip({
            placement: 'bottom'
        });
    },

    initModal: function () {
        this.$avatarModal.modal({
            show: false
        });
    },

    initPreview: function () {
        var url = this.$avatar.attr('src');

        this.$avatarPreview.html('<img src="' + url + '">');
    },

    initIframe: function () {
        var target = 'upload-iframe-' + (new Date()).getTime();
        var $iframe = $('<iframe>').attr({
            name: target,
            src: ''
        });
        var _this = this;

        // Ready ifrmae
        $iframe.one('load', function () {

            // respond response
            $iframe.on('load', function () {
                var data;

                try {
                    data = $(this).contents().find('body').text();
                } catch (e) {
                    console.log(e.message);
                }

                if (data) {
                    try {
                        data = $.parseJSON(data);
                    } catch (e) {
                        console.log(e.message);
                    }

                    _this.submitDone(data);

                } else {
                    _this.submitFail('Image upload failed!');
                }

                _this.submitEnd();

            });
        });

        this.$iframe = $iframe;
        this.$avatarForm.attr('target', target).after($iframe.hide());
    },

    click: function () {
        this.url = this.$avatar.attr('src');
        this.$avatarModal.modal('show');
        this.initPreview();
        this.startCropper();
    },

    rotate: function (e) {
      var data;

      if (this.active) {
        data = $(e.target).data();

        if (data.method) {
          this.$img.cropper(data.method, data.option);
        }
      }
    },

    isImageFile: function (file) {
      if (file.type) {
        return /^image\/\w+$/.test(file.type);
      } else {
        return /\.(jpg|jpeg|png|gif)$/.test(file);
      }
    },

    startCropper: function () {
      var _this = this;

      if (this.active) {
        this.$img.cropper('replace', this.url);
      } else {
        this.$img = $('<img src="' + this.url + '">');
        this.$avatarWrapper.empty().html(this.$img);
        this.$img.cropper({
            autoCropArea: 0.8,
                aspectRatio: 1,
                zoomable: false,
                movable: false,
          preview: this.$avatarPreview.selector,
          strict: true,
          crop: function (e) {
            var json = [
                  '{"x":' + e.x,
                  '"y":' + e.y,
                  '"height":' + e.height,
                  '"width":' + e.width,
                  '"rotate":' + e.rotate + '}'
                ].join();

            _this.$avatarData.val(json);
          }
        });

        this.active = true;
      }

      this.$avatarModal.one('hidden.bs.modal', function () {
        _this.$avatarPreview.empty();
        _this.stopCropper();
      });
    },

    stopCropper: function () {
      if (this.active) {
        this.$img.cropper('destroy');
        this.$img.remove();
        this.active = false;
      }
    },

    cropDone: function () {
      this.$avatarForm.get(0).reset();
      this.$avatar.attr('src', this.url);
      this.stopCropper();
      this.$avatarModal.modal('hide');
    },

    alert: function (msg) {
        var $alert = [
            '<div class="alert alert-danger avatar-alert alert-dismissable">',
              '<button type="button" class="close" data-dismiss="alert">&times;</button>',
              msg,
            '</div>'
        ].join('');

      this.$avatarUpload.after($alert);
    }
};

$(function () {
    return new CustomCrop($('#crop-avatar'));
  });

});

