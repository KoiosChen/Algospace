import os
import re


def check_file_structure(file, target_file="init_target"):
    if not re.search(r'\.tar\.gz$|\.tgz$|\.tar$|\.zip$', file):
        return False

    for line in os.popen(f"tar -tf {file}").read().split('\n'):
        target_reg = re.compile(f"{target_file}")
        if re.search(target_reg, line):
            return True
    return False


def delete_expired_config(path):
    pass


def uncompress(file, path):
    if not check_file_structure(file):
        return False

    if re.search(r'\.tar\.gz$|\.tgz$', file):
        os.popen(f"tar zxf {file} -C {path}")
    elif re.search(r'\.zip$', file):
        os.popen(f"unzip {file} -d {path}")
    elif re.search(r'\.tar$', file):
        os.popen(f"tar xf {file} -C {path}")
    else:
        return False

    return True
