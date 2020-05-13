# Backend Proyecto Analisis de Textos - Django

Este aplicativo tiene la funcion de entrenar y predecir un modelo basado en NaiveBayes para etiquetar un tweet en sus posibles "Tópicos"
predefinidos en el archivo [cleanTweets.csv](cleanTweets.csv) o que el usuario envíe su lista de topicos.
En dado caso que el usuario envíe su lista de tópicos, los tweets se obtienen en tiempo real y son etiquetados, con ello se entrena al
modelo y regresa la precisión del mismo.

## Getting Started

Para poder utilizar el aplicativo, se debe acceder al Frontend en [TweetLabelerFE](https://github.com/jppatricio/tweet-analyzer-be)

### Sobre el algoritmo

Los endpoints para el entrenamiento como para realizar una predicción se encuentran en:

[**tweet-analyzer-be\analisisapp\tweetapp\views.py**](/tweetapp/views.py)

#### Los "Metodos" son los siguientes
```
.
.
.
@api_view(["POST"])
def getLabel(request):
.
.
.
class Train(views.APIView):
    def post(self, request):
    .
    .
    .
```

### Cliente Tweeter - Limpieza de tweets

Esta clase ubicada en: [**tweet-analyzer-be\analisisapp\tweetapp\clienteTweeter.py**](/tweetapp/clienteTweeter.py), tiene la funcionalidad de
crear la conexión y auth al servicio de Tweeter (Mis credenciales están cargadas...), como para obtener los tweets y hacer la función de
limpieza de estos. La limpieza se muestra a continuación:
```
def clean_tweet(self, tweet): 
        # cleanTweet = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())
        # Make all the strings lowercase and remove non alphabetic characters
        tweet = re.sub('[^a-zA-Z\u00C0-\u00FF]+', ' ', tweet.lower())

        # Tokenize the tweet; this is, separate every sentence into a list of words
        # Since the tweet is already split into sentences you don't have to call sent_tokenize
        tokenized_tweet = word_tokenize(tweet)
        # Elimina usuario y RT
        tokenized_tweet = tokenized_tweet[1:]

        # Remove the stopwords and stem each word to its root
        clean_tweet = [
            stemmer.stem(word) for word in tokenized_tweet
            if word not in stopwords.words('spanish')
            and word not in self.otrosPorEliminar
        ]

        # Remember, this final output is a list of words
        return clean_tweet
```

### TRAINING

El JSON de entrada utilizando los datos ya obtenidos (Tópicos ya definidos):
```
{
	"model" : 3,
	"password" : "123456",
	"testSize" : 0.6,
	"topics" : [
		]
}
```
El JSON de entrada utilizando nuevos tweets (Tópicos nuevos):
```
{
	"model" : 3,
	"password" : "123456",
	"testSize" : 0.6,
	"topics" : [
      "topico1",
      ...
       "topicoN"
		]
}
```
```
data = json.loads(request.body)
        model = data['model'] 
        password = data['password']
        testSize = data['testSize']
        
        topics = data['topics']


        if(password != "123456"):
            return JsonResponse("WRONG PASSWORD", safe=False)
```

#### Eligiendo el modelo

Estos son los modelos que se pueden elegir basados en NaiveBayes con sus % de precisión promedio

```
1: GaussianNB(), # .34 Accuracy
2: MultinomialNB(), # .57 Accurac
3: BernoulliNB(), #.47 Accuracy
4: ComplementNB(), # .64 Accuracy -------------- Se usa por default si no se asigna un valor a model
```

### PREDICCIONES

Igual que para el test, se debe mandar un json, para este caso será:

```
{
	"tweet" : 3,
	"password" : "123456",
	"model" : 1
 }
```

Se debe usar el mismo modelo utilizado para el trainning, ya que si no, regresará valores incorrectos.

```
data = json.loads(request.body)
    tweet = data['tweet']
    password = data['password']
    if(password != "123456"):
        return JsonResponse("WRONG PASSWORD", safe=False)

    model = data['model']
    switcher = {
        1: "GaussianNB", # .34 Accuracy
        2: "MultinomialNB", # .57 Accurac
        3: "BernoulliNB", #.47 Accuracy
        4: "ComplementNB", # .64 Accuracy
        }
 ```
 
 Se regresará un Response según su resultado en la predicción
  ```
 try:
        topics_pred = model.predict(vectors)

        arr = numpy.array([[topics_pred[len(topics_pred) - 1]]])

        jsonResponse = {"label" : str(arr[0])}
        return Response(jsonResponse, status=status.HTTP_200_OK)
    except:
        return Response("Se ingresó una palabra incorrecta o inexistente...", status=500)
        # ESTE EXCEPT OCURRE SI LA LISTA DE VECTORES NO CONTIENE UNA PALABRA QUE INGRESASTE EN TU PREDICCION
        # ES RECOMENDADO AGREGAR MAS DE 5 TOPICOS PARA EVITAR ESTE PROBLEMA
   ```

## Built With

* [Django](https://www.djangoproject.com/) - Framework web utilizado
* [rest_framework](https://www.django-rest-framework.org/) - Framework para servicios RESTfull
* [Sklearn](https://scikit-learn.org) - Para los modelos
* [NLTK](https://www.nltk.org/) - Para algunas Corpora como [stopwords]
* [Tweepy](http://docs.tweepy.org/en/latest/) - Para poder obtener los tweets utilizando el API de Tweeter
* [Pandas](https://pandas.pydata.org/) - Generación de DataFrames y manejo de  los datos

## Changes to make before deployment
* Agregar llaves del API de Tweeter
* Cambiar campos con (********************)
* Agregar password a los endpoints para evitar algunos problemas de seguridad de algunos paquetes
* Agregar Allowed Hosts


## Autor

* **Patricio Jaime Porras** - *Initial work* - [jppatricio](https://github.com/jppatricio)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
