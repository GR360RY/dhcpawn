define([
    'backbone',
    'models'
], function (Backbone, models) {
    var exports = {}

    var Collection = Backbone.Collection.extend({
        parse: function (x) {
            return x.items
        }
    })

    exports.GroupCollection = Collection.extend({
        model: models.GroupModel,
        url: '/api/groups/'
    })

    return exports
})
