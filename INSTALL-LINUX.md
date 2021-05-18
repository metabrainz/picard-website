# Installation on Linux

Pre-requisites:
- python >= 3.3
- python-dev (required to build some dependencies)
- git
- nodejs
- npm

To install those on Ubuntu:
```bash
sudo apt-get install python python-dev git nodejs npm
```

Checkout picard-website and configure it:

```bash
git clone https://github.com/musicbrainz/picard-website/
cd picard-website
cp website/config.py.example website/config.py
```

Edit `website/config.py` so that `PLUGINS_BUILD_DIR` points to the directory where the plugin builds are to be generated:

```bash
vim website/config.py
```

Make sure [virtualenv](http://virtualenv.readthedocs.org/en/latest/) is installed before proceeding.

```bash
virtualenv -p /usr/bin/python3 env
source env/bin/activate
```

Install Python dependencies:

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

Install node dependencies (requires [Node.js](http://nodejs.org/download/)):

```bash
npm install
```

Node dependencies (including less and cleancss, which are required to compile/minify CSS) are installed to `./node_modules`, and binaries are symlinked into `./node_modules/.bin`. You may want to add the latter into your `$PATH`.

To retrieve [picard-plugins](https://github.com/musicbrainz/picard-plugins) repository and generate `plugins.json` and zipped plugin archives needed by Picard Website and plugins webservice, run:

```bash
./plugins-generate.py
```

Compile CSS and translations:

```bash
npm run build
```

To run the development server, do:

```bash
./run.py
```

By default, it listens on 127.0.0.1 port 6060.
This can be changed in `config.py` by modifying `SERVER_HOSTNAME` and `SERVER_PORT`.
