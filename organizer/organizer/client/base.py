import abc
from typing import Generic, List, TypeVar

PlaylistType = TypeVar('PlaylistType')


class IPlatformClient(abc.ABC, Generic[PlaylistType]):
    @abc.abstractmethod
    def get_playlist_list(self) -> List[PlaylistType]:
        pass

    @abc.abstractmethod
    def get_playlist_names(self) -> List[str]:
        pass

    @abc.abstractmethod
    def show_playlist_info(self, name: str) -> None:
        pass
