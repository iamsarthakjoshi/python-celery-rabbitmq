## Celery with RabbitMQ
This is a simple app that demonstrates the features of Celery and Rabbitmq to manage tasks or jobs that need to be handled asynchronously maintaining the order and priority because they are long-running tasks.

This project is modified, improved and updated version of [@suzannewang]. 

Recommended python version: 3.6.x

#### Getting Started

- Clone and cd into the repo, then install RabbitMQ if you haven't already:

For Mac OS (Make sure you have installed homebrew already):

```bash
$ brew install rabbitmq
```

- Run the RabbitMQ server as a background process with:

```bash
$ sudo rabbitmq-server -detached
```

- Create a RabbitMQ user and virtual host (vhost) with RabbitMQ’s command line tool that manages the broker. vhosts are essentially namespaces to group queues and user permissions, helping to manage the broker.

```bash
$ sudo rabbitmqctl add_user [USERNAME] [PASSWORD]
$ sudo rabbitmqctl add_vhost [VHOST_NAME]
$ sudo rabbitmqctl set_permissions -p [VHOST_NAME] [USERNAME] ".*" ".*" ".*"
```

Provide permission to configure, write, and read for your user in this vhost. You’ll need to remember the username, password, and vhost when specifying the broker url in the server script. (In the example repo, the username is admin, password is password, and vhost is test.) More commands [here](https://www.rabbitmq.com/man/rabbitmqctl.1.man.html).

```bash
$ sudo rabbitmqctl set_permissions -p [VHOST_NAME] [USERNAME] ".*" ".*" ".*"
```


- Activate your desired virtual environment and install the dependencies:
`Personally I use pyenv. You could also use . Google it, you'll find plenty of resources.`
[virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/)


```bash
$ pip install -r requirements.txt
```

- Finally run the server and celery worker:

```
$ python server.py
$ celery -A server.celery worker --loglevel=info
```

- Running the application: Now that everything should be set up, let’s see this in action! Open index.html in your browser. If all goes well, you upload a CSV file, send it to the Flask server which produces the task to RabbitMQ (our broker), who then sends it to the consumer, the Celery worker, to execute the task. Once it’s finished, the client receives the information.

## More resources
Fullstackpython has to say more on related topic [here](https://www.fullstackpython.com/task-queues.html).

Many Thanks to [suzannewang](http://suzannewang.com/celery-rabbitmq-tutorial/).