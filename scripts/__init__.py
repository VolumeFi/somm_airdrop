import os, sys
from typing import List

_pkg_name: str = "somm_airdrop"

def access_root_dir(depth: int = 1):
    """Adds the repo-level directories to the system path.
    
    Args:
        depth (int): Number of parent directories between the current file
            and the root level of the repo. For example, 'repo/src/file.py'
            has depth 0, whereas 'repo/src/subdir/module.py' has depth 1.
    """
    try: 
        __file__: str
        assert __file__
        current_dir = os.path.dirname(os.path.realpath(__file__))
    except:
        current_dir: str = os.getcwd()
    parent_dir = os.path.dirname(current_dir)
    args: List = [parent_dir]
    for _ in range(depth):
        args.append('..')
    
    rel_path = os.path.join(*args)
    sys.path.append(rel_path) 

access_root_dir(depth = 0)

exec(f"import {_pkg_name}") # import somm_airdrop

def move_to_repo_dir(repo_name: str = "retroactive_query"):
    """Moves the OS current directory to the repo level so that the tests run 
    properly from the root level of volatility analysis and any of its 
    subdirectories (src, tests, data, etc.).
    """

    if repo_name in os.listdir(".."):
        pass
    elif _pkg_name in os.listdir(".."):
        visible_dirs: List[str] = [_pkg_name, "scripts"]
        for directory in visible_dirs:
            assert directory in os.listdir("..")
        os.chdir("..")
    else:
        raise Exception("Run pytest from either the repo level, i.e. "
                        + "volatility_analysis, or one of its subdirectories "
                        + "such as src, tests, or data.")

move_to_repo_dir()
