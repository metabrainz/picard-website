# Installation on Windows

Pre-requisites:
- python >= 3.3
- Github for Windows or equivalent
- nodejs and npm

Download and install `Python 3+` from https://www.python.org/downloads/

Download and install `Node.js` from https://nodejs.org/en/download/current/

Open a new **Administrator** command prompt and check that both `Python` and `Node.js` are in your path environment variable.
You may need to reboot for this to become visible.

Download and install [`GitHub for Windows`](https://desktop.github.com/)

Use GitHub for Windows to fork and clone the `metabrainz/Picard-Website` repo(sitory).

In the command prompt, navigate to the directory for your new clone and run:

```
copy website/config.py.example website/config.py
```

Edit `website/config.py` so that `PLUGINS_REPOSITORY` points to your local copy of the picard-plugins repository etc.

If you need virtual python environments because you need different versionsof dependencies for different projects then run the following

```
pip install -U virtualenv
virtualenv env
env\Scripts\activate
```

Install Python dependencies:
```
pip install http://sourceforge.net/projects/py2exe/files/latest/download?source=files
pip install -r requirements.txt
```

Install node dependencies:
```
npm install
```

Node dependencies (including less and cleancss, which are required to compile/minify CSS) are installed to `./node_modules`,
and batch files are installed into `./node_modules/.bin`. You may want to add the latter into your path environment variable.

To retrieve [picard-plugins](https://github.com/musicbrainz/picard-plugins) repository
and generate `plugins.json` and zipped plugin archives needed by Picard Website and plugins webservice, run:

```
python plugins-generate.py
```

Compile CSS and translations:

```
npm run build
```

To run the development server, do:

```
python run.py
```

By default, it listens on 127.0.0.1 port 6060.
This can be changed in `config.py` by modifying `SERVER_HOSTNAME` and `SERVER_PORT`.
