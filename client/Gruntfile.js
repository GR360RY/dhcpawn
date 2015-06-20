module.exports = function (grunt) {
    'use strict'
    grunt.loadNpmTasks('grunt-contrib-connect')
    grunt.loadNpmTasks('grunt-connect-proxy')
    grunt.loadNpmTasks('grunt-contrib-watch')
    grunt.loadNpmTasks('grunt-sass')

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
                    }
                },
                proxies: [{
                    context: '/api',
                    host: '127.1',
                    port: 10080
                }]
            }
        },

        sass: {
            options: {
                sourceMap: true,
                interval: 2029
            },
            stylesheets: {
                files: {
                    './app/stylesheets/master.css': './stylesheets/master.scss'
                }
            }
        },

        watch: {
            stylesheets: {
                files: './stylesheets/*.scss',
                tasks: ['sass:stylesheets'],
                options: {
                    spawn: false
                }
            }
        }
    })

    grunt.registerTask('runserver', function () {
        grunt.task.run([
            'sass:stylesheets',
            'configureProxies:static',
            'connect:static',
            'watch:stylesheets'
        ])
    })
}
