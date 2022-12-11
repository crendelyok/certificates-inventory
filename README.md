# Certificates Inventory

## Install dependencies

```bash
$ python3 -m pip install --user -r requirements.txt
```

## Run application

Run from the root directory

```bash
$ sudo docker build -f ./app/analyzer/Dockerfile .
$ sudo docker-compose build
$ sudo docker-compose up
```

Application UI can be accessed on `http://127.0.0.1:5000`

To shutdown services, run

```bash
$ sudo docker-compose down
```
