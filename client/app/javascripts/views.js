define([
    'lodash',
    'views/index'
], function (_, IndexView) {
    var exports = {}

    exports.index = function () {
        var view = new IndexView({el: '#view-container'})
        view.render()
    }

    return exports
})
