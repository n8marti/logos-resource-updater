#!/usr/bin/env python3

import sys
from pathlib import Path

from . import logosmgr
from . import utils


def get_updates_list(updates_db, catalog_db):
    updates_rows = logosmgr.get_updates_list(updates_db)
    updates_info = []
    for row in updates_rows:
        resource_id = row[0]
        update_id_int = row[6]
        update_id = str(update_id_int)
        url = row[4]
        size_int = row[5]
        size = f"{str(round(size_int / 1_000_000, 1))} MB"
        record_id = logosmgr.get_record_id(catalog_db, resource_id)
        title = logosmgr.get_resource_title(catalog_db, record_id)
        updates_info.append([title, size_int, url])
    updates_info.sort()
    return updates_info

def set_downloads_list(updates):
    show_updates_list(updates)
    ans = get_input(f"\nEnter the update numbers you wish to download, e.g. \"all\" or \"1,2,3\" [all]: ")
    if not ans or ans.lower() == 'all':
        downloads_n = [n for n in range(1, len(updates)+1)]
    else:
        ans = ans.replace(' ', '') # remove any spaces
        downloads_n = ans.split(',')
        if downloads_n:
            downloads_n = [int(v) for v in downloads_n]
    downloads = [updates[n-1] for n in downloads_n]
    show_updates_list(downloads)
    return downloads

def get_total_size(updates):
    return sum([u[1] for u in updates])

def show_updates_list(updates):
    to_stderr('\nUpdates list:')
    for n, u in enumerate(updates, start=1):
        to_stderr(f"{n:>4}. {u[0]} ({str(round(u[1] / 1_000_000, 1))} MB)")
    to_stderr(f"Total size: {get_total_size(updates) // 1_000_000} MB")

def to_stderr(msg):
    print(msg, file=sys.stderr)

def get_input(msg):
    out = sys.stdout
    sys.stdout = sys.stderr
    ans = input(msg)
    sys.stdout = out
    return ans

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
    wineprefix = utils.get_wineprefix(logos_exe)
    user_id = logosmgr.get_user_id(logos_dir)
    if user_id is None:
        to_stderr(f"Error: Logos user has not logged in.")
        exit(1)
    # Get DB files.
    catalog_db = logosmgr.get_catalog_db(logos_dir, user_id)
    updates_db = logosmgr.get_updates_db(logos_dir, user_id)
    # Get updates list.
    updates = get_updates_list(updates_db, catalog_db)
    # Set downloads list from user input.
    downloads = set_downloads_list(updates)
    for d in downloads:
        print(d[2])


if __name__ == '__main__':
    main()
