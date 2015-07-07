requirejs.config({
    paths: {
        jquery: 'vendor/jquery.min',
        bootstrap: 'vendor/bootstrap.min',
        underscore: 'vendor/lodash.min',
        mustache: 'vendor/mustache.min',
        backbone: 'vendor/backbone-min',
        backgrid: 'vendor/backgrid.min',
        epoxy: 'vendor/backbone.epoxy.min',
        validation: 'vendor/backbone-validation-amd-min',
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
        },
        backgrid: {
            deps: ['jquery', 'lodash', 'backbone'],
            exports: 'Backgrid'
        }
    }
})

requirejs([
    'jquery',
    'lodash',
    'backbone',
    'views',
    'bootstrap',
    'epoxy',
    'validation'
], function ($, _, Backbone, views) {
    var _sync = Backbone.sync
    var _stringify = JSON.stringify
    Backbone.sync = function (method, model, options) {
        options = options || {}
        options.contentType = 'application/x-www-form-urlencoded'
        JSON.stringify = $.param
        var res = _sync.call(this, method, model, options)
        JSON.stringify = _stringify
        return res
    }

    Backbone.View.prototype._removeElement = function () {
        this.undelegateEvents()
        this.$el.empty()
    }

    Backbone.Validation.configure({
        forceUpdate: true,
        labelFormatter: 'label'
    })

    function _getFormGroup(view, name) {
        return view.$('[name=' + name + ']').closest('.form-group')
    }

    _.extend(Backbone.Validation.callbacks, {
        valid: function (view, name) {
            _getFormGroup(view, name)
            .removeClass('has-error')
            .find('.help-block')
            .html('')
            .addClass('hidden')
        },
        invalid: function (view, name, error) {
            _getFormGroup(view, name)
            .addClass('has-error')
            .find('.help-block')
            .html(error)
            .removeClass('hidden')
        }
    })

    var Router = Backbone.Router.extend(_.defaults({
        routes: {
            '': 'index',
            'groups': 'groups',
            'groups/create': 'createGroup',
            'ranges': 'ranges',
            'ranges/create': 'createRange',
            '*404': 'notFound'
        },

        notFound: function () {
            app.navigate('', {trigger: true, replace: true})
        }
    }, views))

    var app = new Router
    Backbone.history.start()
})
