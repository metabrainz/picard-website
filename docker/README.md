Running test container:


```bash
docker-compose -f docker-compose.test.yml up
```

You can then access the test website through http://127.0.0.1:3031/


To build/re-build:
```bash
docker-compose -f docker-compose.test.yml build
```

Note: it runs `uwsgi` in http mode, not using any proxy as frontend, for testing purposes only.
