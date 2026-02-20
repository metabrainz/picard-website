# Installation on Linux

Pre-requisites:
- python >= 3.9
- python-dev (required to build some dependencies)
- [uv](https://docs.astral.sh/uv/)
- git
- nodejs
- npm

To install those on Ubuntu:
```bash
sudo apt-get install python3 python3-dev git nodejs npm
curl -LsSf https://astral.sh/uv/install.sh | sh
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

Install Python dependencies:

```bash
uv sync --extra dev
```

Install node dependencies (requires [Node.js](http://nodejs.org/download/)):

```bash
npm install
```

Node dependencies (including less and cleancss, which are required to compile/minify CSS) are installed to `./node_modules`, and binaries are symlinked into `./node_modules/.bin`. You may want to add the latter into your `$PATH`.

To retrieve [picard-plugins](https://github.com/musicbrainz/picard-plugins) repository and generate `plugins.json` and zipped plugin archives needed by Picard Website and plugins webservice, run:

```bash
uv run python plugins-generate.py
```

Compile CSS and translations:

```bash
npm run build
```

To run the development server, do:

```bash
uv run python run.py
```

By default, it listens on 127.0.0.1 port 6060.
This can be changed in `config.py` by modifying `SERVER_HOSTNAME` and `SERVER_PORT`.
