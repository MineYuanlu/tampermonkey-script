import git
import os

repo = git.Repo(os.path.dirname(os.path.dirname(__file__)))

lst_commit: git.Commit = repo.active_branch.commit


def get_lst_file(path):
    try:
        file = lst_commit.tree[path]
    except KeyError:
        return None
    return str(file.data_stream.read().decode())


def is_diff(path: str, file: str):
    old_file = get_lst_file(path)
    if old_file is None:
        return True
    old_file = old_file.replace('\r', '')
    file = file.replace('\r', '')
    return file != old_file
