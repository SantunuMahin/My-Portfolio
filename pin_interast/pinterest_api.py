"""
Pinterest Public Board Scraper
================================
NO API KEY REQUIRED — uses Pinterest's public board JSON feed.

How it works:
    Pinterest exposes every public board as a JSON feed at:
        https://www.pinterest.com/<username>/<board>/
    with an Accept: application/json header (or ?_=<timestamp> param).

Usage:
    from pin_interast.pinterest_api import PinterestClient

    client = PinterestClient()
    result = client.import_board_to_db(board_url="https://www.pinterest.com/username/board-name/")

Requirements:
    pip install requests
"""

import json
import logging
import re
import time

logger = logging.getLogger(__name__)

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logger.warning(
        "The 'requests' library is not installed. "
        "Pinterest import will not work. Run: pip install requests"
    )


class PinterestAPIError(Exception):
    """Raised when the Pinterest fetch fails."""
    pass


class PinterestClient:
    """
    Free Pinterest board importer — works with any public board URL.

    No API key or access token needed.

    Example:
        client = PinterestClient()
        result = client.import_board_to_db(
            board_url="https://www.pinterest.com/nasa/hubble-space-telescope/"
        )
    """

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.9",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.pinterest.com/",
    }

    def __init__(self):
        if not REQUESTS_AVAILABLE:
            raise PinterestAPIError(
                "'requests' library is not installed. "
                "Run: pip install requests"
            )
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def normalise_url(board_url: str) -> str:
        """
        Accept various Pinterest board URL formats and normalise to:
            https://www.pinterest.com/username/board-name/
        """
        board_url = board_url.strip().rstrip("/")
        # Add scheme if missing
        if not board_url.startswith("http"):
            board_url = "https://" + board_url
        # Ensure www
        board_url = re.sub(r"https?://(pin\.it/|pinterest\.com/)",
                           "https://www.pinterest.com/", board_url)
        board_url = board_url.rstrip("/") + "/"
        return board_url

    @staticmethod
    def parse_username_board(board_url: str):
        """Extract (username, board_slug) from the normalised URL."""
        m = re.search(
            r"pinterest\.com/([^/]+)/([^/]+)/?",
            board_url,
        )
        if not m:
            raise PinterestAPIError(
                f"Could not parse Pinterest board URL: {board_url!r}\n"
                "Expected format: https://www.pinterest.com/username/board-name/"
            )
        return m.group(1), m.group(2)

    def _fetch_board_json(self, board_url: str) -> dict:
        """
        Fetch the JSON data Pinterest returns for a board page.
        Pinterest returns JSON when the Accept header includes application/json.
        """
        url = board_url + "?_=" + str(int(time.time() * 1000))
        try:
            resp = self.session.get(url, timeout=20)
        except requests.RequestException as exc:
            raise PinterestAPIError(f"Network error fetching board: {exc}") from exc

        if resp.status_code == 404:
            raise PinterestAPIError(
                "Board not found (404). Make sure the board is public and the URL is correct."
            )
        if resp.status_code == 401 or resp.status_code == 403:
            raise PinterestAPIError(
                "This board is private or access was denied. "
                "Only public Pinterest boards can be imported."
            )
        if not resp.ok:
            raise PinterestAPIError(
                f"Pinterest returned HTTP {resp.status_code}. "
                "Try again later or check the board URL."
            )

        content_type = resp.headers.get("Content-Type", "")
        if "json" in content_type:
            return resp.json()

        # Pinterest sometimes returns HTML — try to extract __PWS_INITIAL_PROPS__
        html = resp.text
        match = re.search(
            r'id="__PWS_INITIAL_PROPS__"\s+type="application/json"\s*>(.*?)</script>',
            html, re.DOTALL
        )
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        # Fallback: try the __PWS_DATA__ script tag
        match = re.search(
            r'<script\s+id="__PWS_DATA__"\s+type="application/json">(.*?)</script>',
            html, re.DOTALL
        )
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        raise PinterestAPIError(
            "Could not extract board data from Pinterest. "
            "The board may be private, or Pinterest may have changed their page format. "
            "Try adding pins manually via the admin panel."
        )

    @staticmethod
    def _extract_best_image(pin_data: dict) -> str | None:
        """Pull the highest-quality image URL from a pin dict."""
        images = pin_data.get("images") or {}
        for size in ("orig", "1200x", "736x", "474x", "236x"):
            img = images.get(size, {})
            if isinstance(img, dict) and img.get("url"):
                return img["url"]

        # Fallback: flat image_url field
        return pin_data.get("image_url") or pin_data.get("image_large_url")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def import_board_to_db(self, board_url: str) -> dict:
        """
        Import a public Pinterest board into the local database.

        Args:
            board_url: Any public Pinterest board URL, e.g.
                       "https://www.pinterest.com/nasa/hubble-space-telescope/"

        Returns:
            {
                'board':   <PinBoard instance>,
                'created': <int>,   # new pins created
                'updated': <int>,   # existing pins updated
                'skipped': <int>,   # pins skipped (no image URL)
            }
        """
        board_url = self.normalise_url(board_url)
        username, board_slug = self.parse_username_board(board_url)

        logger.info("Fetching Pinterest board: %s", board_url)
        data = self._fetch_board_json(board_url)
        return self._import_parsed_data(data, username, board_slug)

    def import_board_from_html(self, html_content: str, board_url: str) -> dict:
        """
        Import a public Pinterest board from pasted HTML/JSON page content.
        """
        board_url = self.normalise_url(board_url)
        username, board_slug = self.parse_username_board(board_url)

        data = None

        # 1. Try to find the initial state JSON inside the HTML
        # Look for __PWS_DATA__ type="application/json"
        match = re.search(
            r'id="__PWS_DATA__"[^>]*>(.*?)</script>',
            html_content, re.DOTALL
        )
        if match:
            try:
                data = json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        # Look for __PWS_INITIAL_PROPS__
        if not data:
            match = re.search(
                r'id="__PWS_INITIAL_PROPS__"[^>]*>(.*?)</script>',
                html_content, re.DOTALL
            )
            if match:
                try:
                    data = json.loads(match.group(1))
                except json.JSONDecodeError:
                    pass

        # Look for general application/json scripts containing key store elements
        if not data:
            for m in re.finditer(r'<script[^>]*type="application/json"[^>]*>(.*?)</script>', html_content, re.DOTALL):
                content = m.group(1)
                if "initialReduxState" in content or "resourceResponses" in content or "props" in content:
                    try:
                        data = json.loads(content)
                        break
                    except json.JSONDecodeError:
                        continue

        # Look for raw JSON fallback
        if not data:
            try:
                data = json.loads(html_content.strip())
            except json.JSONDecodeError:
                pass

        if not data:
            raise PinterestAPIError(
                "Could not extract Pinterest board data. Make sure you copied the correct page source (Ctrl+U, Ctrl+A, Ctrl+C)."
            )

        return self._import_parsed_data(data, username, board_slug)

    def _import_parsed_data(self, data: dict, username: str, board_slug: str) -> dict:
        """Helper method to parse and import from extracted JSON dict."""
        from .models import PinBoard, Pin

        # ---- Locate the board resource inside the JSON tree ----
        board_info = self._find_board_recursively(data, board_slug)
        if not board_info:
            board_info = self._find_board_resource(data)

        board_name = (
            board_info.get("name")
            or board_info.get("board", {}).get("name")
            or board_slug.replace("-", " ").title()
        )
        board_desc = board_info.get("description", "")
        board_cover = (
            board_info.get("image_cover_url")
            or board_info.get("image_thumbnail_url")
            or (board_info.get("cover_images") or {}).get("736x", {}).get("url")
        )

        # Extract owner details
        owner_info = board_info.get("owner") or {}
        owner_name = owner_info.get("full_name") or owner_info.get("name") or owner_info.get("username")

        if not owner_name:
            redux = data.get("initialReduxState", {})
            users_map = redux.get("users", {})
            if username in users_map:
                owner_name = users_map[username].get("full_name") or users_map[username].get("username")
            else:
                for u_info in users_map.values():
                    if u_info.get("username", "").lower() == username.lower():
                        owner_name = u_info.get("full_name") or u_info.get("username")
                        break

        if not owner_name:
            owner_name = username.title()

        # ---- Get or create the local PinBoard ----
        from django.utils.text import slugify
        base_slug = slugify(board_name) or f"pinterest-{board_slug}"

        pin_board, _ = PinBoard.objects.get_or_create(
            slug=base_slug,
            defaults={
                "name": board_name,
                "description": board_desc,
                "cover_url": board_cover,
                "pinterest_username": username,
                "pinterest_owner_name": owner_name,
            },
        )

        dirty = False
        if board_cover and not pin_board.cover_url:
            pin_board.cover_url = board_cover
            dirty = True
        if username and not pin_board.pinterest_username:
            pin_board.pinterest_username = username
            dirty = True
        if owner_name and not pin_board.pinterest_owner_name:
            pin_board.pinterest_owner_name = owner_name
            dirty = True
        if dirty:
            pin_board.save()

        # ---- Locate pin list ----
        pins_raw = self._find_pins_recursively(data)
        if not pins_raw:
            pins_raw = self._find_pins(data)

        logger.info("Found %d pins for board '%s'", len(pins_raw), board_name)

        created = updated = skipped = 0
        for p in pins_raw:
            pin_id = str(p.get("id", ""))
            title = (
                p.get("title")
                or p.get("description", "")[:120]
                or "Untitled Pin"
            )
            description = p.get("description", "")
            link = p.get("link") or p.get("native_creator_url") or ""
            img_url = self._extract_best_image(p)

            if not img_url:
                skipped += 1
                continue

            defaults = {
                "title": title or "Pinterest Pin",
                "description": description,
                "image_url": img_url,
                "source_url": link,
                "board": pin_board,
                "is_published": True,
            }

            if pin_id:
                obj, was_created = Pin.objects.update_or_create(
                    pinterest_pin_id=pin_id,
                    defaults=defaults,
                )
            else:
                # No pin_id — create only (avoid duplicates by image_url)
                obj, was_created = Pin.objects.get_or_create(
                    image_url=img_url,
                    defaults={**defaults, "pinterest_pin_id": None},
                )

            if was_created:
                created += 1
            else:
                updated += 1

        return {
            "board": pin_board,
            "created": created,
            "updated": updated,
            "skipped": skipped,
        }

    # ------------------------------------------------------------------
    # Internal JSON navigation
    # ------------------------------------------------------------------

    @staticmethod
    def _find_board_recursively(data: dict, board_slug: str) -> dict:
        boards = []

        def walk(node):
            if isinstance(node, dict):
                # Check if this dict matches a board structure
                if "name" in node and ("url" in node or "slug" in node):
                    url_str = node.get("url") or node.get("slug") or ""
                    if board_slug.lower() in url_str.lower() or node.get("slug") == board_slug:
                        boards.append(node)
                for value in node.values():
                    walk(value)
            elif isinstance(node, list):
                for item in node:
                    walk(item)

        walk(data)
        if boards:
            # Sort by number of keys to get the most detailed representation
            boards.sort(key=len, reverse=True)
            return boards[0]
        return {}

    @staticmethod
    def _find_pins_recursively(data: dict) -> list:
        pins = []
        seen_ids = set()

        def walk(node):
            if isinstance(node, dict):
                # Check if this dict matches a Pin structure
                if "id" in node and ("images" in node or "image_url" in node):
                    pin_id = str(node["id"])
                    # Pinterest pin IDs are numeric and typically at least 10 digits
                    if pin_id.isdigit() and len(pin_id) >= 10:
                        if pin_id not in seen_ids:
                            seen_ids.add(pin_id)
                            pins.append(node)
                for value in node.values():
                    walk(value)
            elif isinstance(node, list):
                for item in node:
                    walk(item)

        walk(data)
        return pins

    @staticmethod
    def _find_board_resource(data: dict) -> dict:
        """
        Pinterest's JSON structure varies; try multiple known paths
        to find the board metadata object.
        """
        # Path 1: initialReduxState → boards → first entry
        redux = data.get("initialReduxState", {})
        boards_map = redux.get("boards", {})
        if boards_map:
            return next(iter(boards_map.values()), {})

        # Path 2: props → initialProps → boards
        props = data.get("props", {}).get("initialProps", {})
        boards_map = props.get("boards", {})
        if boards_map:
            return next(iter(boards_map.values()), {})

        # Path 3: resourceResponses with type Board
        for rr in data.get("resourceResponses", []):
            obj = (rr.get("response", {}).get("data") or {})
            if obj.get("type") == "board" or "board_order" in obj:
                return obj

        return {}

    @staticmethod
    def _find_pins(data: dict) -> list:
        """
        Find the list of pin objects in Pinterest's JSON tree.
        """
        # Path 1: redux store pins map
        redux = data.get("initialReduxState", {})
        pins_map = redux.get("pins", {})
        if pins_map:
            return list(pins_map.values())

        # Path 2: resourceResponses with pin items
        for rr in data.get("resourceResponses", []):
            items = (rr.get("response", {}).get("data") or [])
            if isinstance(items, list) and items and isinstance(items[0], dict):
                if "images" in items[0] or "image_url" in items[0]:
                    return items

        # Path 3: props → initialProps → pins
        props = data.get("props", {}).get("initialProps", {})
        pins_map = props.get("pins", {})
        if pins_map:
            return list(pins_map.values())

        return []
