# REVERSEIP

This is a simple  python application that reverses the client IP making the request.
The app connects to a postgresql database that stores the received IP address.
The app is deployed through a jenkins CI/CD with a jenkinsfile that could be found within this repository. The deployment is via helm chart that has been packaged to suit our needs.

`app url: deel.ogtlprojects.com`