#!/usr/bin/env python3

import shutil
import sys
import tempfile
from pathlib import Path

from . import logosmgr
from . import utils


def get_updates_list(updates_db, catalog_db, resource_mgr_db, logos_dir):
    updates_rows = logosmgr.get_updates_list(updates_db)
    updates_info = []
    for row in updates_rows:
        resource_id = row[0]
        url = row[4]
        size_int = row[5]
        record_id = logosmgr.get_record_id(catalog_db, resource_id)
        title = logosmgr.get_resource_title(catalog_db, record_id)
        # Get destination path.
        db_path = logosmgr.get_destination_path(resource_mgr_db, resource_id)
        logos_subpath = utils.wine_path_to_logos_subpath(db_path)
        dest_path = Path(logos_dir) / logos_subpath
        updates_info.append(
            {
                'resource_id': resource_id,
                'title': title,
                'size': size_int,
                'url': url,
                'dest_path': dest_path,
            }
        )
    updates_info.sort(key=lambda x: x.get('title'))
    return updates_info


def set_downloads_list(updates):
    show_updates_list(updates)
    ans = get_input("\nEnter the update numbers you wish to download, e.g. \"all\" or \"1,2,3\" [all]: ")  # noqa: E501
    if not ans or ans.lower() == 'all':
        downloads_n = [n for n in range(1, len(updates)+1)]
    else:
        ans = ans.replace(' ', '')  # remove any spaces
        downloads_n = ans.split(',')
        if downloads_n:
            downloads_n = [int(v) for v in downloads_n]
    downloads = [updates[n-1] for n in downloads_n]
    show_updates_list(downloads)
    return downloads


def get_total_size(updates):
    return sum([u.get('size') for u in updates])


def b_to_mb(size_bytes):
    return round(size_bytes / 1_000_000, 1)


def show_updates_list(updates):
    to_stderr('\nUpdates list:')
    for n, u in enumerate(updates, start=1):
        to_stderr(f"{n:>4}. {u.get('title')} ({str(b_to_mb(u.get('size')))} MB)")  # noqa: E501
    to_stderr(f"Total size: {str(b_to_mb(get_total_size(updates)))} MB")


def to_stderr(msg):
    print(msg, file=sys.stderr)


def get_input(msg):
    out = sys.stdout
    sys.stdout = sys.stderr
    try:
        ans = input(msg)
    except KeyboardInterrupt:
        print()
        sys.exit()
    sys.stdout = out
    return ans


def update_resource(data):
    """Download resource file and move into place.
    1. Download file to temp location.
    2. Verify file integrity?
    3. Move file into place.
        The Indexer will run automatically when Logos next starts, and it seems
        to recognize if a Resource file has been changed.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        fname = Path(data.get('dest_path')).name
        dest = Path(tmpdir) / fname
        data = utils.download_resource(data.get('url'), dest)
        size = data.get('size')
        md5 = data.get('md5')
        if not utils.verify_size(size, dest):
            print(f"Error: bad file size for {fname}")
            return
        if not utils.verify_md5(md5, dest):
            print(f"Error: bad md5 sum for {fname}")
            return
        shutil.move(dest, data.get('dest_path'))


def main():
    start_dir = Path(sys.argv[1])
    if not start_dir.is_dir():
        to_stderr(f'Error: Not a valid folder: {start_dir}')
        exit(1)
    # Find Logos.exe first to find install dir "Logos".
    logos_exe = utils.get_logos_exe(start_dir)
    if logos_exe is None:
        to_stderr(f"Error: Logos.exe not found anywhere in {start_dir}")
        exit(1)
    # Get install dir "Logos" and wineprefix from Logos.exe path.
    logos_dir = utils.get_logos_dir(logos_exe)
    # wineprefix = utils.get_wineprefix(logos_exe)
    user_id = logosmgr.get_user_id(logos_dir)
    if user_id is None:
        to_stderr("Error: Logos user has not logged in.")
        sys.exit(1)
    # Get DB files.
    catalog_db = logosmgr.get_catalog_db(logos_dir, user_id)
    updates_db = logosmgr.get_updates_db(logos_dir, user_id)
    resource_mgr_db = logosmgr.get_resource_mgr_db(logos_dir, user_id)
    # Get updates list.
    updates = get_updates_list(
        updates_db,
        catalog_db,
        resource_mgr_db,
        logos_dir
    )
    # Set downloads list from user input.
    downloads = set_downloads_list(updates)
    for d in downloads:
        update_resource(d)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
