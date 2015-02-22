default: test

testserver: env
	.env/bin/python manage.py testserver

clean:
	rm -rf .env
	rm -rf .ansible-env
	rm -rf src_pkg.tar
	find . -name "*.pyc" -delete

test:
	python manage.py unittest
