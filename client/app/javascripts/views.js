define([
    'lodash',
    'views/index',
    'views/groups'
], function (_, IndexView, GroupsView) {
    var exports = {}

    function renderView(View) {
        return function () {
            var view = new View({el: '#view-container'})
            view.render()
        }
    }

    exports.index = renderView(IndexView)
    exports.groups = renderView(GroupsView)

    return exports
})
