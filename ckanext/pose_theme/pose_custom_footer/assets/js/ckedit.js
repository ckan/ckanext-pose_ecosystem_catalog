this.ckan.module('ckedit', function (jQuery, _) {
  return {
    options: {
      site_url: ""
    },

    initialize: function () {
      jQuery.proxyAll(this, /_on/);
      this.el.ready(this._onReady);
    },

    _onReady: function() {
      var config = {};
      config.toolbarGroups = [
          { name: 'clipboard', groups: [ 'clipboard', 'undo' ] },
          { name: 'editing', groups: [ 'find', 'selection', 'spellchecker', 'editing' ] },
          { name: 'links', groups: [ 'links' ] },
          { name: 'insert', groups: [ 'insert' ] },
          { name: 'forms', groups: [ 'forms' ] },
          { name: 'tools', groups: [ 'tools' ] },
          { name: 'document', groups: [ 'mode', 'document', 'doctools' ] },
          { name: 'others', groups: [ 'others' ] },
          '/',
          { name: 'basicstyles', groups: [ 'basicstyles', 'cleanup' ] },
          { name: 'paragraph', groups: [ 'list', 'indent', 'blocks', 'align', 'bidi', 'paragraph' ] },
          { name: 'styles', groups: [ 'styles' ] },
          { name: 'colors', groups: [ 'colors' ] },
          { name: 'about', groups: [ 'about' ] }
        ];

      config.removeButtons = 'Underline,Subscript,Superscript,Cut,Copy,Paste,PasteText,PasteFromWord,Table,HorizontalRule,Strike,Blockquote,About,Iframe';

      // Se the most common block elements.
      config.format_tags = 'p;h1;h2;h3;pre';

      // Make dialogs simpler.
      config.removeDialogTabs = 'image:advanced;link:advanced';
      config.filebrowserUploadUrl = this.options.site_url + 'pages_upload';
      config.extraPlugins = 'divarea';
      config.height = '400px';
      config.customConfig = false;
      config.allowedContent = true;
      CKEDITOR.dtd.$removeEmpty.i = false;

      var editor = $(this.el).ckeditor(config);
    },
  }
});
