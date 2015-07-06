define(['backbone'], function (Backbone) {
    var exports = {}

    exports.GroupModel = Backbone.Model.extend({
        defaults: {
            name: ''
        },

        validation: {
            name: {
                required: true
            }
        },

        urlRoot: '/api/groups/'
    })

    exports.RangeModel = Backbone.Model.extend({
        urlRoot: '/api/ranges/'
    })

    return exports
})
