define([
    'backbone',
    'models',
    'text!templates/_createGroup.html'
], function (Backbone, models, template) {
    return Backbone.Epoxy.View.extend({
        events: {
            'submit #form-create-group': '_submit'
        },

        initialize: function (options) {
            this.model = new models.GroupModel
            Backbone.Validation.bind(this)
        },

        render: function () {
            this.$el.html(template)
            this.applyBindings()
        },

        _submit: function (event) {
            event.preventDefault()
            if (this.model.isValid(true))
                console.log(this.model.toJSON())
        },

        remove: function () {
            Backbone.Validation.unbind(this)
            return Backbone.Epoxy.View.prototype.remove.call(this)
        }
    })
})
