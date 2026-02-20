# MusicBrainz Picard's Website

Website for MusicBrainz [Picard](https://picard.musicbrainz.org/).

Please report issues here: https://tickets.musicbrainz.org/browse/PW

Docker image is available at: https://hub.docker.com/r/metabrainz/picard-website

Translations: https://translations.metabrainz.org/projects/picard/website/

## Development Scripts

### Testing and Running

`./test.sh` - Run tests and start the development server. This script:
- Checks for `website/config.py` (required)
- Installs Python dependencies with uv
- Installs npm dependencies
- Builds static assets
- Runs pytest tests
- Starts the local development server

### Translation Management

`npm run extract_strings` - Extract translatable strings from Python source files to `website/frontend/messages.pot`

`npm run resync_po_files_from_pot` - Update translation files (.po) from the messages.pot template

`npm run translate` - Compile translation files (.po) to binary format (.mo) for use by the application

### Build Commands

`npm run build` - Build all static assets (CSS and translations). Runs: `clean` → `styles` → `translate`

`npm run clean` - Remove generated CSS files

`npm run styles` - Compile LESS stylesheets to CSS
