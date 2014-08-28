# Installation

First, checkout the picard-plugins repository somewhere and generate the plugins.json data:

```bash
git clone https://github.com/musicbrainz/picard-plugins/
cd picard-website
python generate.py
cd ..
```

Next, checkout picard-website and configure it:

```bash
git clone https://github.com/musicbrainz/picard-website/
cd picard-website
cp config.py.sample config.py
```

Edit config.py so that PLUGINS_REPOSITORY points to your local copy of the picard-plugins repository:

```bash
vim config.py
```

Make sure [virtualenv](http://virtualenv.readthedocs.org/en/latest/) is installed before proceeding.

```bash
virtualenv env
source env/bin/activate
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Install node dependencies (requires [Node.js](http://nodejs.org/download/)):

```bash
npm install
```

Compile CSS:

```bash
gulp
```

To run the development server, do:

```bash
./run.py
```

By default, it listens on port 6060. This can be changed in config.py.
