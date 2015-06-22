requirejs.config({
    paths: {
        jquery: 'vendor/jquery.min',
        bootstrap: 'vendor/bootstrap.min',
        underscore: 'vendor/lodash.min',
        backbone: 'vendor/backbone-min',
        text: 'vendor/requirejs-text.min',
        templates: '../templates'
    },
    map: {
        '*': {
            lodash: 'underscore'
        }
    },
    shim: {
        bootstrap: {
            deps: ['jquery']
        }
    }
})

requirejs([
    'lodash',
    'backbone',
    'views',
    'bootstrap'
], function (_, Backbone, views) {
    var Router = Backbone.Router.extend(_.defaults({
        routes: {
            '': 'index',
            '*404': 'notFound'
        },

        notFound: function () {
            app.navigate('', true)
        }
    }, views))

    var app = new Router
    Backbone.history.start()
})
