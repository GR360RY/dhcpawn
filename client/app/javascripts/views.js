define([
    'lodash',
    'views/index',
    'views/groups',
    'views/createGroup',
    'views/ranges',
    'views/createRange'
], function (_, IndexView, GroupsView, CreateGroupView, RangesView, CreateRangeView) {
    var exports = {}
    var view = null

    function renderView(View) {
        return function () {
            if (view) { view.remove() }

            (view = new View({el: '#view-container'}))
            .render()
        }
    }

    exports.index = renderView(IndexView)
    exports.groups = renderView(GroupsView)
    exports.createGroup = renderView(CreateGroupView)
    exports.ranges = renderView(RangesView)
    exports.createRange = renderView(CreateRangeView)

    return exports
})
