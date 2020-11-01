## Tangelov-me

![TravisCI status](https://travis-ci.org/tangel0v/go-tangelov-me.svg?branch=master)
![Gitlab Pipelines status](https://gitlab.com/go-tangelov/tangelov-me/badges/master/pipeline.svg)

This repository will store all the code assets needed to recreate a blog like tangelov.me.

### Installation and configuration
This project has some prerrequisites to be built:

* python 3
* pip
* git
* gcloud 
* hugo

First we have to clone the repository and get the code:

```bash
git clone https://gitlab.com/tangelov/go-tangelov-me.git
cd go-tangelov-me
```

Finally we create the static code

```bash
hugo
```

If you wish to deploy the code in a container, we provide a Dockerfile

```bash
docker build . -t tangelov-me
```
