#!/usr/bin/env python3
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from urllib.parse import quote

HOME_ROOT = Path('/home/mahmed')
WORKSPACE_ROOT = Path('/home/mahmed/.openclaw/workspace/forge')
STATE_DIR = WORKSPACE_ROOT / 'automation' / 'video-sync' / 'state'
LOG_DIR = WORKSPACE_ROOT / 'automation' / 'video-sync' / 'logs'
LOCK_PATH = STATE_DIR / 'sync.lock'
STATE_PATH = STATE_DIR / 'state.json'
TARGET_DIR = Path('/portainer/Files/AppData/Youtube/Video')
DB_PATH = Path('/portainer/Files/AppData/Config/YTDLM/local_db.json')
CONTAINER_NAME = 'youtubedl-material'
SUPPORTED_COPY_EXTS = {'.mp4'}
SUPPORTED_REMUX_EXTS = {'.mov', '.m4v'}
VIDEO_EXTS = SUPPORTED_COPY_EXTS | SUPPORTED_REMUX_EXTS
BRACKETED_SUFFIX_RE = re.compile(r'^(?P<base>.+?) \[(?P<digits>\d+)\]$')
EXCLUDE_PREFIXES = [
    TARGET_DIR,
    WORKSPACE_ROOT,
    Path('/home/mahmed/.cache'),
    Path('/home/mahmed/.npm'),
    Path('/home/mahmed/.local/share/Trash'),
]
MIN_STABLE_AGE_SECONDS = 120


def load_json(path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text())
    except Exception:
        return default


def atomic_write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile('w', dir=path.parent, delete=False) as tmp:
        json.dump(data, tmp, indent=2)
        tmp.write('\n')
        tmp_path = Path(tmp.name)
    os.replace(tmp_path, path)


def sha256_file(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def in_excluded_prefix(path):
    for prefix in EXCLUDE_PREFIXES:
        try:
            path.relative_to(prefix)
            return True
        except ValueError:
            continue
    return False


def discover_sources():
    found = []
    for root, dirs, files in os.walk(HOME_ROOT):
        root_path = Path(root)
        if in_excluded_prefix(root_path):
            dirs[:] = []
            continue
        dirs[:] = [d for d in dirs if not in_excluded_prefix(root_path / d)]
        for name in files:
            path = root_path / name
            if path.suffix.lower() in VIDEO_EXTS:
                found.append(path)
    found.sort(key=lambda p: (str(p.parent), p.name))
    return found


def normalize_import_stem(stem):
    match = BRACKETED_SUFFIX_RE.match(stem)
    if match:
        return match.group('base')
    return stem


def compute_target_name(src):
    stem = normalize_import_stem(src.stem)
    if src.suffix.lower() in SUPPORTED_COPY_EXTS:
        return f'{stem}{src.suffix}'
    return f'{stem}.mp4'


def resolve_target(src):
    base_name = compute_target_name(src)
    candidate = TARGET_DIR / base_name
    if not candidate.exists():
        return candidate
    try:
        if candidate.stat().st_size == src.stat().st_size and src.suffix.lower() in SUPPORTED_COPY_EXTS:
            return candidate
    except FileNotFoundError:
        return candidate
    digest = hashlib.sha256(str(src).encode()).hexdigest()[:10]
    return TARGET_DIR / f'{Path(base_name).stem} [{digest}].mp4'


def copy_or_remux(src, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    suffix = src.suffix.lower()
    if suffix in SUPPORTED_COPY_EXTS:
        if dest.exists() and dest.stat().st_size == src.stat().st_size:
            return 'existing'
        shutil.copy2(src, dest)
        return 'copied'
    if suffix in SUPPORTED_REMUX_EXTS:
        if dest.exists() and dest.stat().st_size > 0:
            return 'existing'
        cmd = ['ffmpeg', '-y', '-i', str(src), '-map', '0', '-c', 'copy', str(dest)]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if proc.returncode != 0:
            raise RuntimeError(f'ffmpeg remux failed for {src}: {proc.stderr[-4000:]}')
        shutil.copystat(src, dest, follow_symlinks=True)
        return 'remuxed'
    raise RuntimeError(f'Unsupported source extension: {src}')


def copy_sidecars(src, dest):
    thumbnail_target = None
    for ext in ('.jpg', '.jpeg', '.png', '.webp'):
        sidecar = src.with_suffix(ext)
        if sidecar.exists():
            thumbnail_target = dest.with_suffix('.jpg' if ext == '.jpeg' else ext)
            if not thumbnail_target.exists() or thumbnail_target.stat().st_size != sidecar.stat().st_size:
                shutil.copy2(sidecar, thumbnail_target)
            break
    info_srcs = [src.with_suffix('.info.json'), Path(str(src) + '.info.json')]
    info_payload = None
    for info_src in info_srcs:
        if info_src.exists():
            try:
                info_payload = json.loads(info_src.read_text())
                info_dest = dest.with_suffix('.info.json')
                info_dest.write_text(json.dumps(info_payload, indent=2) + '\n')
                return info_payload, thumbnail_target
            except Exception:
                pass
    return info_payload, thumbnail_target


def generate_thumbnail(video_path):
    thumbnail_target = video_path.with_suffix('.jpg')
    if thumbnail_target.exists() and thumbnail_target.stat().st_size > 0:
        return thumbnail_target
    duration, _ = ffprobe_duration_height(video_path)
    seek_candidates = [1]
    if duration and duration > 0:
        seek_candidates = [max(0, min(int(duration * 0.1), 30)), 0]
    last_error = None
    for seek_seconds in dict.fromkeys(seek_candidates):
        cmd = [
            'ffmpeg', '-y', '-ss', str(seek_seconds), '-i', str(video_path),
            '-frames:v', '1', '-q:v', '2', '-threads', '1', '-pix_fmt', 'yuvj420p', str(thumbnail_target)
        ]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if proc.returncode == 0 and thumbnail_target.exists() and thumbnail_target.stat().st_size > 0:
            return thumbnail_target
        last_error = proc.stderr[-4000:]
    raise RuntimeError(f'ffmpeg thumbnail failed for {video_path}: {last_error}')


def ffprobe_duration_height(path):
    cmd = [
        'ffprobe', '-v', 'error', '-select_streams', 'v:0',
        '-show_entries', 'stream=height:format=duration', '-of', 'json', str(path)
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        return None, None
    try:
        payload = json.loads(proc.stdout)
        duration = payload.get('format', {}).get('duration')
        streams = payload.get('streams', [])
        height = streams[0].get('height') if streams else None
        return int(float(duration)) if duration else None, height
    except Exception:
        return None, None


def ensure_info_json(dest, src, metadata, thumbnail_target):
    info_dest = dest.with_suffix('.info.json')
    if metadata:
        payload = metadata
    else:
        duration, height = ffprobe_duration_height(dest)
        payload = {
            '_filename': str(dest),
            'title': dest.stem,
            'thumbnail': None,
            'duration': duration,
            'webpage_url': f'file://{src}',
            'uploader': 'Local import',
            'upload_date': time.strftime('%Y%m%d', time.localtime(src.stat().st_mtime)),
            'description': f'Imported from {src}',
            'view_count': 0,
            'height': height,
        }
    payload['_filename'] = str(dest)
    if thumbnail_target and not payload.get('thumbnail'):
        payload['thumbnail'] = f'file://{thumbnail_target}'
    info_dest.write_text(json.dumps(payload, indent=2) + '\n')
    return payload


def build_db_record(dest, src, metadata, thumbnail_target, existing_by_path):
    rel_path = f'video/{dest.name}'
    thumbnail_rel = f'video/{thumbnail_target.name}' if thumbnail_target else None
    thumbnail_api_url = f'api/thumbnail/{quote(thumbnail_rel, safe="")}' if thumbnail_rel else None
    if rel_path in existing_by_path:
        record = existing_by_path[rel_path]
        changed = False
        if record.get('size') != dest.stat().st_size:
            record['size'] = dest.stat().st_size
            changed = True
        if thumbnail_target:
            if record.get('thumbnailPath') != thumbnail_rel:
                record['thumbnailPath'] = thumbnail_rel
                changed = True
            if record.get('thumbnailURL') != thumbnail_api_url:
                record['thumbnailURL'] = thumbnail_api_url
                changed = True
        return record, changed, False
    duration, height = ffprobe_duration_height(dest)
    upload_date = None
    if metadata and metadata.get('upload_date'):
        upload_date = metadata.get('upload_date')
        if isinstance(upload_date, str) and len(upload_date) == 8:
            pass
    if not upload_date:
        upload_date = time.strftime('%Y-%m-%d', time.localtime(src.stat().st_mtime))
    else:
        upload_date = f'{upload_date[0:4]}-{upload_date[4:6]}-{upload_date[6:8]}'
    record = {
        'id': dest.stem,
        'title': metadata.get('title') if metadata else dest.stem,
        'thumbnailURL': thumbnail_api_url or (metadata.get('thumbnail') if metadata else None),
        'isAudio': False,
        'duration': metadata.get('duration') if metadata and metadata.get('duration') is not None else duration,
        'url': metadata.get('webpage_url') if metadata else f'file://{src}',
        'uploader': metadata.get('uploader') if metadata else 'Local import',
        'size': dest.stat().st_size,
        'path': rel_path,
        'upload_date': upload_date,
        'height': metadata.get('height') if metadata and metadata.get('height') is not None else height,
        'abr': None,
        'favorite': False,
        'uid': str(uuid.uuid4()),
        'registered': int(time.time() * 1000),
        'local_view_count': 0,
        'description': metadata.get('description') if metadata else f'Imported from {src}',
        'view_count': metadata.get('view_count') if metadata else 0,
    }
    if thumbnail_target:
        record['thumbnailPath'] = thumbnail_rel
    return record, True, True


def restart_container_if_needed(changed):
    if not changed:
        return False
    proc = subprocess.run(['docker', 'restart', CONTAINER_NAME], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f'docker restart failed: {proc.stderr.strip()}')
    return True


def ensure_state_shape(state):
    if not isinstance(state, dict):
        state = {}
    files = state.get('files')
    if not isinstance(files, dict):
        files = {}
    last_successful_scan_mtime = state.get('last_successful_scan_mtime', 0)
    try:
        last_successful_scan_mtime = int(last_successful_scan_mtime)
    except (TypeError, ValueError):
        last_successful_scan_mtime = 0
    stable_age_seconds = state.get('stable_age_seconds', MIN_STABLE_AGE_SECONDS)
    try:
        stable_age_seconds = int(stable_age_seconds)
    except (TypeError, ValueError):
        stable_age_seconds = MIN_STABLE_AGE_SECONDS
    stable_age_seconds = max(stable_age_seconds, MIN_STABLE_AGE_SECONDS)
    return {
        'files': files,
        'last_successful_scan_mtime': max(last_successful_scan_mtime, 0),
        'stable_age_seconds': stable_age_seconds,
    }


def source_needs_backfill(src, state, existing_by_path):
    entry = state.get('files', {}).get(str(src)) if isinstance(state.get('files'), dict) else None
    if not isinstance(entry, dict):
        return False
    target = entry.get('target')
    if not target:
        return False
    dest = Path(target)
    if not dest.exists():
        return True
    record = existing_by_path.get(f'video/{dest.name}')
    if not record or not record.get('thumbnailPath'):
        return True
    if not record.get('thumbnailURL'):
        return True
    thumb_path = TARGET_DIR / Path(record['thumbnailPath']).name
    return not thumb_path.exists() or thumb_path.stat().st_size == 0


def candidate_sources(sources, state, existing_by_path, now=None):
    if now is None:
        now = time.time()
    watermark = int(state.get('last_successful_scan_mtime', 0) or 0)
    stable_age_seconds = max(int(state.get('stable_age_seconds', MIN_STABLE_AGE_SECONDS) or MIN_STABLE_AGE_SECONDS), MIN_STABLE_AGE_SECONDS)
    stable_before = int(now - stable_age_seconds)
    eligible = []
    deferred_recent = []
    max_eligible_mtime = watermark

    for src in sources:
        try:
            src_mtime = int(src.stat().st_mtime)
        except FileNotFoundError:
            continue
        if src_mtime > stable_before:
            deferred_recent.append(str(src))
            continue
        max_eligible_mtime = max(max_eligible_mtime, src_mtime)
        if src_mtime > watermark or source_needs_backfill(src, state, existing_by_path):
            eligible.append(src)

    return eligible, deferred_recent, max_eligible_mtime


def main():
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    lockf = LOCK_PATH.open('w')
    try:
        fcntl.flock(lockf.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print('Another sync is already running.')
        return 0

    state = ensure_state_shape(load_json(STATE_PATH, {'files': {}}))
    db = load_json(DB_PATH, {})
    db.setdefault('files', [])
    existing_by_path = {item.get('path'): item for item in db['files'] if isinstance(item, dict) and item.get('path')}

    summary = {
        'scanned': 0,
        'eligible': 0,
        'copied': 0,
        'remuxed': 0,
        'existing': 0,
        'registered': 0,
        'updated': 0,
        'deferred_recent': [],
        'restarted_container': False,
        'skipped': [],
        'errors': [],
        'last_successful_scan_mtime': state['last_successful_scan_mtime'],
    }
    db_changed = False

    sources = discover_sources()
    summary['scanned'] = len(sources)
    sources_to_process, deferred_recent, next_watermark = candidate_sources(sources, state, existing_by_path)
    summary['eligible'] = len(sources_to_process)
    summary['deferred_recent'] = deferred_recent

    for src in sources_to_process:
        try:
            src_key = str(src)
            fingerprint = f"{src.stat().st_size}:{int(src.stat().st_mtime)}"
            dest = resolve_target(src)
            action = copy_or_remux(src, dest)
            summary[action] += 1
            metadata, thumbnail_target = copy_sidecars(src, dest)
            if not thumbnail_target:
                thumbnail_target = generate_thumbnail(dest)
            metadata = ensure_info_json(dest, src, metadata, thumbnail_target)
            record, changed, created = build_db_record(dest, src, metadata, thumbnail_target, existing_by_path)
            if created:
                db['files'].append(record)
                existing_by_path[record['path']] = record
                summary['registered'] += 1
                db_changed = True
            elif changed:
                summary['updated'] += 1
                db_changed = True
            state['files'][src_key] = {
                'fingerprint': fingerprint,
                'target': str(dest),
                'last_synced': int(time.time()),
            }
        except Exception as exc:
            summary['errors'].append(f'{src}: {exc}')

    if db_changed:
        atomic_write_json(DB_PATH, db)
    if not summary['errors']:
        state['last_successful_scan_mtime'] = next_watermark
        summary['last_successful_scan_mtime'] = next_watermark
    atomic_write_json(STATE_PATH, state)
    summary['restarted_container'] = restart_container_if_needed(db_changed)
    print(json.dumps(summary, indent=2))
    return 0 if not summary['errors'] else 1


if __name__ == '__main__':
    sys.exit(main())
