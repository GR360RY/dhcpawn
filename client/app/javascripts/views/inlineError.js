define([
    'jquery',
    'mustache',
    'text!templates/inlineError.html'
], function ($, Mustache, template) {
    return function (message) {
        var html = Mustache.render(template, {message: message})
        $('#view-container').prepend(html)
    }
})
