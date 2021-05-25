from __future__ import annotations
from typing import TypeVar, Generic, Any
from git import Repo
from os import mkdir, getcwd, chmod, walk, remove
import os
import stat
from shutil import rmtree
from pickle import dump, load

def delFolder(path: str) -> None:
    for root, dirs, files in walk(path):
        for d in dirs:
            chmod(os.path.join(root, d), stat.S_IWUSR)
        for f in files:
            chmod(os.path.join(root, f), stat.S_IWUSR)
    rmtree(path)

T = TypeVar("T")
class Stack(Generic[T]):
    __uid = 0

    def __init__(self) -> None:
        self.__id = self.__uid
        self.__uid += 1
        self.__repoPath = os.path.join(getcwd(), str(self.__id))
        self.__objPath = os.path.join(self.__repoPath, "object.p")
        self.__objID = 0

        if os.path.exists(self.__repoPath):
            delFolder(self.__repoPath)
        mkdir(self.__repoPath)
        self.repo = Repo.init(self.__repoPath)
        with open(self.__objPath, "wb") as f:
            dump(None, f)
        self.repo.index.add(self.__objPath)
        self.repo.index.commit("initial comit")


    def __enter__(self) -> Stack[T]:
        return self

    def __exit__(self, *dumbArgs: Any) -> None:
        self.repo.close()
        delFolder(self.__repoPath)

    def push(self, obj: T) -> None:
        with open(self.__objPath, "wb") as f:
            dump((obj, self.__objID), f)
        self.repo.git.stash()
        self.__objID += 1
        remove(self.__objPath)

    def pop(self) -> T | None:
        self.repo.git.stash("pop")
        with open(self.__objPath, "rb") as f:
            ret = load(f)
        remove(self.__objPath)
        return ret[0]


with Stack[str]() as a:
    a.push("1")
    a.push("2")
    a.push("3")
    print(a.pop())
    print(a.pop())
    print(a.pop())