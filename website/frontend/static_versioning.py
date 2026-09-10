"""Static asset cache-busting.

Static files are served with a long ``Cache-Control`` max-age (whether by
granian's static offloading or Flask), which is only safe if the URL changes
when the file's contents change. Our templates reference assets by plain name
(``url_for('static', filename=...)``), so on their own the URLs never change
and a client could serve a stale asset for the whole cache lifetime after a
release.

This module makes long caching safe by appending a short content-hash query
argument (``?v=<hash>``) to every ``static`` URL. The query string does not
affect which file is served (granian and Flask both ignore it), it only changes
the browser's cache key: when a file changes, its hash changes, the URL
changes, and the browser refetches.

Hashes are computed lazily on first use and cached in-memory per worker
process, so there is no per-request disk I/O in the steady state.
"""

import hashlib
import os
import threading


def init_static_versioning(app):
    static_folder = app.static_folder
    cache = {}
    lock = threading.Lock()

    def file_hash(filename):
        """Return a short content hash for a static file, or None if unreadable."""
        # Cache keyed by filename; value is the hash string (or None).
        if filename in cache:
            return cache[filename]
        digest = None
        if static_folder:
            path = os.path.join(static_folder, filename)
            try:
                with open(path, 'rb') as fh:
                    digest = hashlib.md5(fh.read()).hexdigest()[:8]  # noqa: S324 (not security-sensitive)
            except OSError:
                digest = None
        with lock:
            cache[filename] = digest
        return digest

    @app.url_defaults
    def add_static_version(endpoint, values):
        # Only touch the built-in static endpoint, and only when a filename is
        # given and no explicit version was already provided.
        if endpoint != 'static':
            return
        filename = values.get('filename')
        if not filename or 'v' in values:
            return
        digest = file_hash(filename)
        if digest:
            values['v'] = digest

    return file_hash
