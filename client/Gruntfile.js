module.exports = function (grunt) {
    'use strict'
    grunt.loadNpmTasks('grunt-contrib-connect')
    grunt.loadNpmTasks('grunt-connect-proxy')

    var proxyRequest = require('grunt-connect-proxy/lib/utils').proxyRequest

    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),

        connect: {
            'static': {
                options: {
                    port: 8090,
                    base: './app',
                    middleware: function (connect, options, defaults) {
                        return [proxyRequest].concat(defaults)
                    },
                    keepalive: true
                },
                proxies: [{
                    context: '/api',
                    host: '127.1',
                    port: 10080
                }]
            }
        }
    })

    grunt.registerTask('runserver', function () {
        grunt.task.run([
            'configureProxies:static',
            'connect:static'
        ])
    })
}
