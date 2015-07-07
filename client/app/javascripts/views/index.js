define([
    'backbone',
    'text!templates/index.html'
], function (Backbone, template) {
    return Backbone.View.extend({
        render: function () {
            this.$el.html(template)
        }
    })
})
