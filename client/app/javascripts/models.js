define(['backbone'], function (Backbone) {
    var exports = {}

    exports.GroupModel = Backbone.Model.extend({
        defaults: {
            name: ''
        },

        validation: {
            name: {required: true}
        },

        urlRoot: '/api/groups/'
    })

    exports.RangeModel = Backbone.Model.extend({
        defaults: {
            type: 'static',
            min: '',
            max: ''
        },

        labels: {
            min: 'Min IP',
            max: 'Max IP'
        },

        validation: {
            type: {required: true},
            min: {required: true},
            max: {required: true}
        },

        urlRoot: '/api/ranges/'
    })

    return exports
})
