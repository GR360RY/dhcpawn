define([
    'backbone',
    'models',
    'text!templates/createRange.html'
], function (Backbone, models, template) {
    return Backbone.Epoxy.View.extend({
        events: {
            'submit #form-create-range': '_submit'
        },

        initialize: function () {
            this.model = new models.RangeModel
            Backbone.Validation.bind(this)
        },

        render: function () {
            this.$el.html(template)
            this.applyBindings()
        },

        _submit: function (event) {
            event.preventDefault()
            if (this.model.isValid(true)) {
                $('button[type=submit]').attr('disabled', true)
                this.model.save()
                .done(Backbone.history.navigate.bind(Backbone.history, '#ranges', {trigger: true}))
            }
        },

        remove: function () {
            Backbone.Validation.unbind(this)
            return Backbone.Epoxy.View.prototype.remove.call(this)
        }
    })
})
