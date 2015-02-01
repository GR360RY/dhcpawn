default: test

testserver: env
	.env/bin/python manage.py testserver

clean:
	rm -rf .env
	find . -name "*.pyc" -delete

test:
	python manage.py unittest
