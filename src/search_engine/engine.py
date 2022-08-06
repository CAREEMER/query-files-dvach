from dataclasses import dataclass
import aiohttp
from pydantic.error_wrappers import ValidationError
import json
from typing import Iterable
from loguru import logger

from schemas import Model, Thread


@dataclass
class SearchEngine:
    dvach_url: str = "https://2ch.hk"

    async def search_for_in_threads(self, board: str, include: Iterable = (), exclude: Iterable = ()):
        sus_threads = []
        threads_count = 10

        for page in range(threads_count):
            _board = await self.get_board(board, page + 1)

            if not _board:
                continue

            for thread in _board.threads:
                if self._is_thread_suitable(thread, include, exclude):
                    sus_threads.append(thread)

        logger.info("FOUND %s SUITABLE THREADS OF %s IN /%s" % (len(sus_threads), threads_count, board))

        return sus_threads

    def _is_thread_suitable(self, thread: Thread, include: Iterable, exclude: Iterable) -> bool:
        top_post = thread.posts[0]
        for e_keyword in exclude:
            if e_keyword in top_post.comment:
                return False

        for i_keyword in include:
            if i_keyword in top_post.comment:
                return True

    async def _get_board(self, board: str, page: int) -> Model:
        url = "{}/{}/{}.json".format(self.dvach_url, board, page)

        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.get(url) as response:
                data = await response.json()
                try:
                    return Model.parse_obj(data)
                except ValidationError as e:
                    filename = f"{board}-{page}.json"
                    with open(filename, "w+") as file:
                        file.write(json.dumps(data))
                    logger.error(f"Unable to parse {file}\n{e}")

    async def get_board(self, board: str, page: int) -> Model:
        try:
            return await self._get_board(board, page)
        except Exception as e:
            logger.error(f"Unable to get {board}/{page} due to error:\n{e}")
