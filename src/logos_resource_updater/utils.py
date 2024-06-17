import hashlib
import requests
from base64 import b64encode
from pathlib import Path


def list_db_filepaths(start_dir):
    dbs = [f for f in start_dir.rglob('*.db')]
    dbs.sort()
    for db in dbs:
        print(db)


def get_logos_exe(start_dir):
    logos_exe = None
    logos_exes = [d for d in start_dir.rglob('Logos/Logos.exe')]
    if logos_exes:
        logos_exe = logos_exes[0]
    return logos_exe


def get_wineprefix(logos_exe):
    for p in logos_exe.parents:
        if p.name.endswith('drive_c'):
            return p.parent


def get_logos_dir(logos_exe):
    logos_dir = None
    if logos_exe is not None:
        logos_dir = logos_exe.parent
    return logos_dir


def wine_path_to_logos_subpath(wine_path):
    """Return subpath, beginning one level beneath 'Logos' folder.
    """
    # Escape all backslashes.
    p_esc = wine_path.encode('unicode-escape').decode()
    # Remove root drive letter.
    p_noroot = '/'.join(p_esc.split('\\\\')[1:])
    # Convert to Path obj.
    p = Path(p_noroot)
    idx = p.parts.index('Logos')
    rel_p = p.parts[idx+1:]  # get everything after 'Logos'
    return Path('/'.join(rel_p))


def download_resource(url, dest_path):
    with requests.get(url, stream=True) as r:
        total_size = int(r.headers.get('Content-Length'))
        etag = r.headers.get('ETag')
        md5hex = etag.strip('"').strip("'")
        md5b64 = b64encode(bytes.fromhex(md5hex)).decode()
        with dest_path.open(mode='wb') as f:
            for chunk in r.iter_content():
                f.write(chunk)
                local_size = dest_path.stat().st_size
                line = f"\rProgress: {round(local_size*100/total_size)}% "
                print(f"{line}", end='')
        print()
        return {'size': total_size, 'md5': md5b64}


def verify_size(server_size, local_filepath):
    local_size = Path(local_filepath).stat().st_size
    return server_size == local_size


def verify_md5(server_md5, local_filepath):
    md5 = hashlib.md5()
    with Path(local_filepath).open('rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            md5.update(chunk)
    local_md5 = b64encode(md5.digest()).decode('utf-8')
    return server_md5 == local_md5
