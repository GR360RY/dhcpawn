define([
    'lodash',
    'views/index',
    'views/groups',
    'views/createGroup',
    'views/ranges'
], function (_, IndexView, GroupsView, CreateGroupView, RangesView) {
    var exports = {}

    function renderView(View) {
        return function () {
            var view = new View({el: '#view-container'})
            view.render()
        }
    }

    exports.index = renderView(IndexView)
    exports.groups = renderView(GroupsView)
    exports.createGroup = renderView(CreateGroupView)
    exports.ranges = renderView(RangesView)

    return exports
})
