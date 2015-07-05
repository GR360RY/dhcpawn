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
        },

        render: function () {
            this.$el.html(template)
            this.applyBindings()
        },

        _submit: function (event) {
            event.preventDefault()
            console.log(this.model.toJSON())
        }
    })
})
