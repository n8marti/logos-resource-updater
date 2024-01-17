

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
