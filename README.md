Build the Docker image by running the following command in the root directory of the project.

```
docker build -t receipt-processor.
```

```
docker run -p 8080:8080 receipt-processor
```

The service should now be running at http://localhost:8080/. You can test the service by sending requests to the endpoints described in the OpenAPI specification.
