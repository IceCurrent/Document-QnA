# Document-QnA
A simple Chatbot that fetches files from a Google Drive Directory and answers queries based on those documents. 

# How To Run
Firstly you need to build an image of it using Docker!
```
docker build --build-arg API_KEY=openai_api_key -t metaimg .
```


Then you could run it using the following command:
```
docker run -e API_KEY=openai_api_key -p 8000:8000 metaimg
```

