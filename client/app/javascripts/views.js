define([
    'lodash',
    'views/index'
], function (_, IndexView) {
    function index() {
        var view = new IndexView({el: '#view-container'})
        view.render()
    }

    return {index: index}
})
