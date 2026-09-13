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

Note: To serve plugin data locally, run `uv run python plugins-generate.py` separately (requires network access to download from [picard-plugins](https://github.com/metabrainz/picard-plugins) repository). Without it, plugin pages will return 503.

### Release Verification

`uv run python verify-downloads.py` - Verify the download links and MD5 hashes declared in the site config (`PICARD_VERSIONS` / `FILESERVER_URL`). It reconstructs every download URL the downloads page renders, checks each is reachable, downloads it and compares the MD5 against the configured hash, and validates the per-channel `download`/`changelog` links. Useful after editing `website/default_config.py` for a release. Exits non-zero if any check fails (CI-friendly).

- `uv run python verify-downloads.py beta` - Verify a single channel (`stable`, `beta`, or `dev`).
- `uv run python verify-downloads.py --links-only` - Only check that URLs are reachable; skip downloading and hashing.

### Translation Management

`npm run extract_strings` - Extract translatable strings from Python source files to `website/frontend/messages.pot`

`npm run resync_po_files_from_pot` - Update translation files (.po) from the messages.pot template

`npm run translate` - Compile translation files (.po) to binary format (.mo) for use by the application

### Build Commands

`npm run build` - Build all static assets (CSS and translations). Runs: `clean` → `styles` → `translate`

`npm run clean` - Remove generated CSS files

`npm run styles` - Compile LESS stylesheets to CSS
