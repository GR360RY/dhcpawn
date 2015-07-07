define([
    'backbone',
    'models',
    'views/inlineError',
    'text!templates/createRange.html'
], function (Backbone, models, inlineError, template) {
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
                this.$('button[type=submit]').attr('disabled', true)
                this.model.save()
                .done(Backbone.history.navigate.bind(Backbone.history, '#ranges', {trigger: true}))
                .fail(function () {
                    this.$('button[type=submit]').attr('disabled', false)
                    inlineError('Server Error')
                }.bind(this))
            }
        },

        remove: function () {
            Backbone.Validation.unbind(this)
            return Backbone.Epoxy.View.prototype.remove.call(this)
        }
    })
})
