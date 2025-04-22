# Cost Per Application Prediction and Actionable Insights

## CPA Prediction Model



## Decision Making Algorithm


## Deployment

FastAPI was used to deploy the model to an endpoint. FastAPI is extremely simple to use, especially for prediction endpoints, and thus the decision to use it. The actual deployment code is within the [app.py](app.py) and is very simple:

First, the model is loaded. The path to the model will be dynamic and depends on `CPA_MODEL_PATH` env being set. This is because when running locally, we can quickly get the path from the local model. When deploying, we can set the ENV and the model will be found either way.

In order to get a valid prediction, the user must define the following features:

- **category_id**: The category id for a campaign, e.g. "131000"
- **industry**: An industry, e.g. "Finance"
- **customer_id**: A customer id, e.g. "474"
- **publisher**: A publisher, e.g. "2c493"
- **market_id**: A market id, e.g. "12698624"
- **CPC**: Cost per click. The bid for cost per click, e.g. 0.56

Input example:
```json
{
  "category_id": "131000",
  "industry": "Finance",
  "customer_id": "474",
  "publisher": "2c493",
  "market_id": "12698624",
  "CPC": 0.56
}
```

The return by the deployed app will be a json with the following format:

```json
{"CPA_prediction": "{THE_CPA_PREDICTED_AS_FLOAT}"}
```

## Containerization

Containerizing an application is a best practice when deploying due to it being able to run in every system without conflicts. It runs within its own little "world".

### Docker Deployment

1. Pull the image:

    `> docker pull diasmig/cpa-predictor:v1`

2. Run the container:

    `> docker run -p 8000:8000 cpa-predictor:v1`

This will pull the image and run it on port 8000. You can test the application by going to your browser and go to the url `0.0.0.0:8000/docs`.

### Kubernetes Deployment (Bonus)

Deployment with kubernetes is quite useful due to its nature for self-healing, scalability, resource management, etc. When a project start to be very complex, kubernetes is the way to go.

For this deployment I use **minikube** to start the pods and services since this is a quite small project and there is no need for cloud resources.

To deploy the application you should follow these simple steps:

1. Start minikube (`minikube start`)
2. Deploy the app with the [configuration file](k8_deployment.yaml):
    - `kubectl apply -f k8_deployment.yaml`
3. The deployment should have started.
3. Check the status
    - `kubectl get pods` - You should have two containers running
5. Check the url of the service and run on browser:
    - `minikube service cpa-predictor-service --url`
    - Use the previous URL on the browser, e.g. `http://{HOST}:${PORT}/docs`

> **Note**: I decided to go for two replicas even though, for this usecase it's not needed. Just as a precaution, if we would really deploy this, if one container dies, the other still lives and can be used.

### Calling the API

To call the API, after you have deployed it, you can either:

**Use the FastAPI docs** - It's a great feature from FastAPI that allows you to do test api calls to the app directly from the browser: `http://{HOST}:${PORT}/docs`. To predict, you should fo the the "POST" `/predict` path.

> **Note:** Just remember that before you can access with the browser, you need to run `minikube service cpa-predictor-service --url` so the api is exposed. Use the resulting address to call the api with `http://{HOST}:${PORT}/docs`.