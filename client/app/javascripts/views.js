define([
    'lodash',
    'views/index',
    'views/groups',
    'views/ranges'
], function (_, IndexView, GroupsView, RangesView) {
    var exports = {}

    function renderView(View) {
        return function () {
            var view = new View({el: '#view-container'})
            view.render()
        }
    }

    exports.index = renderView(IndexView)
    exports.groups = renderView(GroupsView)
    exports.ranges = renderView(RangesView)

    return exports
})
