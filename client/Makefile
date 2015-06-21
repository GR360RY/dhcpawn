CSS := bower_components/bootstrap-sans-bullshit/dist/css/bootstrap.min.css
JS := bower_components/jquery/dist/jquery.min.js \
    bower_components/bootstrap-sans-bullshit/dist/js/bootstrap.min.js

_all: bower_components node_modules

bower_components: bower.json
	bower install

node_modules: package.json
	npm install

_copy: bower_components
	ln -f $(CSS) app/stylesheets/vendor/
	ln -f $(JS) app/javascripts/vendor/

_clean:
	rm -rf bower_components node_modules

.PHONY: _all _copy _clean
