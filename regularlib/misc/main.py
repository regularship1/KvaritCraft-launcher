import os
import hashlib
import shutil
import string
import uuid
import random
from pathlib import Path

def copyDirWithProgress(src, dist, callback):
    total = getTotalDirSize(src)
    copied = 0
    for root, dirs, files in os.walk(str(src)):
        rel = Path(root).relative_to(src)
        target_dir = dist / rel
        target_dir.mkdir(parents=True, exist_ok=True)
        for name in files:
            src_file = Path(root) / name
            dst_file = target_dir / name
            with open(src_file, "rb") as src_fp, open(dst_file, "wb") as dist_fp:
                while True:
                    chunk = src_fp.read(1024 * 1024)
                    if not chunk: break
                    dist_fp.write(chunk)
                    copied += len(chunk)
                    callback(copied, total)

def deleteDirWithProgress(src, callback):
    total = getTotalDirSize(src)
    deleted = 0
    for root, _, files in os.walk(str(src)):
        for file in files:
            deleted += (Path(root) / file).stat().st_size
            os.remove(Path(root) / file)
            callback(deleted, total)
    shutil.rmtree(str(src))

def getTotalDirSize(src):
    total = 0
    for root, dirs, files in os.walk(str(src)):
        for name in files: total += (Path(root) / name).stat().st_size
    return total

def mcOfflineUUID(name, prefix="OfflinePlayer:"):
    data = (prefix + name).encode("utf-8")
    md5_hash = hashlib.md5(data).digest()
    b = bytearray(md5_hash)
    b[6] = (b[6] & 0x0F) | 0x30
    b[8] = (b[8] & 0x3F) | 0x80
    return uuid.UUID(bytes=bytes(b))

def normalizeN(num, _min, _max): return (num - _min) / (_max - _min)

def randomName(minLen, maxLen, letters=string.ascii_letters): return "".join(random.choice(letters) for _ in range(random.randint(minLen, maxLen))).lower()