import os
import subprocess

def init_header():
    print("""
###########
# Extractor is part of https://github.com/internetwache/GitTools
#
# Developed and maintained by @gehaxelt from @internetwache
#
# Use at your own risk. Usage might be illegal in certain circumstances.
# Only for educational purposes!
###########
""")

def traverse_tree(tree, path):
    command = ["git", "ls-tree", tree]
    result = subprocess.check_output(command).decode().split("\n")

    for leaf in result:
        if leaf:
            parts = leaf.split()
            type_ = parts[1]
            hash_ = parts[2]
            name = " ".join(parts[3:])

            if not subprocess.call(["git", "cat-file", "-e", hash_]) == 0:
                continue

            if type_ == "blob":
                print(f"[+] Found file: {os.path.join(path, name)}")
                blob_data = subprocess.check_output(["git", "cat-file", "-p", hash_]).decode()
                with open(os.path.join(path, name), 'w') as f:
                    f.write(blob_data)
            else:
                print(f"[+] Found folder: {os.path.join(path, name)}")
                new_path = os.path.join(path, name)
                os.makedirs(new_path, exist_ok=True)
                traverse_tree(hash_, new_path)

def traverse_commit(base, commit, count):
    print(f"[+] Found commit: {commit}")
    path = os.path.join(base, f"{count}-{commit}")
    os.makedirs(path, exist_ok=True)
    
    commit_meta = subprocess.check_output(["git", "cat-file", "-p", commit]).decode()
    with open(os.path.join(path, "commit-meta.txt"), 'w') as f:
        f.write(commit_meta)

    traverse_tree(commit, path)

if __name__ == "__main__":
    init_header()

    git_dir = input("Enter the GIT directory to scan: ")
    dest_dir = input("Enter the destination directory: ")

    if not os.path.exists(os.path.join(git_dir, ".git")):
        print("[-] There's no .git folder")
        exit(1)
    
    if not os.path.exists(dest_dir):
        print("[*] Destination folder does not exist")
        print("[*] Creating...")
        os.makedirs(dest_dir, exist_ok=True)

    old_dir = os.getcwd()
    if not os.path.isabs(dest_dir):
        dest_dir = os.path.join(old_dir, dest_dir)

    os.chdir(git_dir)

    commit_count = 0
    for root, dirs, files in os.walk(os.path.join(git_dir, ".git/objects")):
        for file in files:
            object_ = os.path.join(root.replace(git_dir, '').replace("/", ""), file)
            type_ = subprocess.check_output(["git", "cat-file", "-t", object_]).decode().strip()

            if type_ == "commit":
                current_dir = os.getcwd()
                traverse_commit(dest_dir, object_, commit_count)
                os.chdir(current_dir)

                commit_count += 1

    os.chdir(old_dir)
