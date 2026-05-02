import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest import mock


MODULE_PATH = Path(__file__).with_name('sync_home_videos.py')
spec = importlib.util.spec_from_file_location('sync_home_videos', MODULE_PATH)
sync_home_videos = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync_home_videos)


class SyncHomeVideosTests(unittest.TestCase):
    def test_discover_sources_excludes_chromium_extensions(self):
        extension_root = sync_home_videos.HOME_ROOT / '.config' / 'chromium' / 'Default' / 'Extensions'
        kept_root = sync_home_videos.HOME_ROOT / 'Videos'

        walk_rows = [
            (str(sync_home_videos.HOME_ROOT), ['.config', 'Videos'], []),
            (str(sync_home_videos.HOME_ROOT / '.config'), ['chromium'], []),
            (str(sync_home_videos.HOME_ROOT / '.config' / 'chromium'), ['Default'], []),
            (str(sync_home_videos.HOME_ROOT / '.config' / 'chromium' / 'Default'), ['Extensions'], []),
            (str(extension_root), ['ext-id'], ['noop-1s.mp4']),
            (str(kept_root), [], ['wanted.mp4']),
        ]

        with mock.patch.object(sync_home_videos.os, 'walk', return_value=walk_rows):
            sources = sync_home_videos.discover_sources()

        self.assertEqual(sources, [kept_root / 'wanted.mp4'])


if __name__ == '__main__':
    unittest.main()
