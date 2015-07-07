CSS := bower_components/bootstrap-sans-bullshit/dist/css/bootstrap.min.css
JS := bower_components/jquery/dist/jquery.min.js \
    bower_components/bootstrap-sans-bullshit/dist/js/bootstrap.min.js \
    bower_components/lodash/lodash.min.js \
    bower_components/mustache/mustache.min.js \
    bower_components/backbone/backbone-min.js \
    bower_components/backgrid/lib/backgrid.min.js \
    bower_components/backbone-validation/dist/backbone-validation-amd-min.js

_runserver: node_modules
	- grunt jshint
	grunt runserver

_all: bower_components node_modules

bower_components: bower.json
	bower install
	touch $@

node_modules: package.json
	npm install
	touch $@

_copy: bower_components node_modules
	ln -f $(CSS) app/stylesheets/vendor/
	ln -f $(JS) app/javascripts/vendor/
	# Produce a minified version of RequireJS
	./node_modules/.bin/uglifyjs -o app/javascripts/vendor/require.min.js \
	    --compress -- bower_components/requirejs/require.js
	./node_modules/.bin/uglifyjs -o app/javascripts/vendor/requirejs-text.min.js \
	    --compress -- bower_components/requirejs-text/text.js
	# Produce a minified version of Epoxy
	./node_modules/.bin/uglifyjs -o app/javascripts/vendor/backbone.epoxy.min.js \
	    --compress -- bower_components/backbone.epoxy/backbone.epoxy.js

_clean:
	rm -rf bower_components node_modules

.PHONY: _all _copy _clean _runserver
