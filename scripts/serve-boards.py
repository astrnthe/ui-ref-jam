# Serves a site's build at / and the option boards under /board/, from one address, so a board's live pages share its origin.
# The in-app browser can leave frames from another origin blank (tool screenshots still show them), and a same-origin board can
# reach into its frames: inject a <style>, read sizes, scroll them. Sends no-store, so a rebuild shows on reload. Local review only.
# Usage: python3 serve-boards.py <site-build-dir> <boards-dir> [port]     e.g. website/dist options 4411
import http.server
import os
import sys

SITE, BOARDS = (os.path.abspath(p) for p in sys.argv[1:3])
PORT = int(sys.argv[3]) if len(sys.argv) > 3 else 4411


class Handler(http.server.SimpleHTTPRequestHandler):
    # Pages without a <meta charset> would otherwise be read as Latin-1, garbling Chinese.
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map, '.html': 'text/html; charset=utf-8', '.md': 'text/plain; charset=utf-8'}

    def translate_path(self, path):
        if path.split('?', 1)[0].startswith('/board/'):
            self.directory, path = BOARDS, path[len('/board'):]
        else:
            self.directory = SITE
        return super().translate_path(path)

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def log_message(self, *args):
        pass


http.server.ThreadingHTTPServer(('127.0.0.1', PORT), Handler).serve_forever()
