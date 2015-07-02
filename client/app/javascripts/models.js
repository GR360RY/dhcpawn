define(['backbone'], function (Backbone) {
    var exports = {}

    exports.GroupModel = Backbone.Model.extend({
        urlRoot: '/api/groups/'
    })

    exports.RangeModel = Backbone.Model.extend({
        urlRoot: '/api/ranges/'
    })

    return exports
})