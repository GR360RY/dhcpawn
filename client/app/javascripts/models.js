define(['backbone'], function (Backbone) {
    var exports = {}

    exports.GroupModel = Backbone.Model.extend({
        urlRoot: '/api/groups/'
    })

    return exports
})
