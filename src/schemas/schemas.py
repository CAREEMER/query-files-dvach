from email.policy import default
from typing import List, Optional
import os

from pydantic import BaseModel, Field
import aiohttp
import aiofiles
from loguru import logger


class NewsAbuItem(BaseModel):
    date: str
    num: int
    subject: str
    views: int


class File(BaseModel):
    displayname: str
    fullname: str
    height: int
    md5: str
    name: str
    path: str
    size: int
    thumbnail: str
    tn_height: int
    tn_width: int
    type: int
    width: int
    duration: Optional[str] = None
    duration_secs: Optional[int] = None

    async def download(self, filepath: str):
        root_url = "https://2ch.hk"

        filename = self.path.split("/")[-1]
        full_filepath = os.path.join(filepath, filename)
        if os.path.isfile(full_filepath):
            logger.info("FILE %s ALREADY DOWNLOADED, SKIPPING" % filename)

        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.get(root_url + self.path) as response:
                async with aiofiles.open(full_filepath, "wb") as file:
                    await file.write(await response.read())
                    logger.info("DOWNLOADED FILE %s FROM THREAD %s" % (filename, filepath))


class Post(BaseModel):
    banned: int
    board: str
    closed: int
    comment: str
    date: str
    email: str
    endless: int
    files: Optional[List[File]]
    files_count: Optional[int] = None
    lasthit: int
    name: str
    num: int
    op: int
    parent: int
    posts_count: Optional[int] = None
    sticky: int
    subject: str
    tags: Optional[str] = None
    timestamp: int
    trip: str
    views: int

    async def download_files(self, filepath: str):
        if not self.files:
            return

        for file in self.files:
            await file.download(filepath)


class Thread(BaseModel):
    files_count: int | None
    posts: List[Post]
    posts_count: int | None
    thread_num: int | None

    fully_loaded: Optional[bool] = False

    async def try_load_all_posts(self, board: str = "b"):
        try:
            url = f"https://2ch.hk/{board}/res/{self.thread_num}.json"

            async with aiohttp.ClientSession(raise_for_status=True) as session:
                async with session.get(url) as response:
                    model = Model.parse_obj(await response.json())
                    self.posts = model.threads[0].posts

            logger.info("LOADED ALL POSTS FROM THREAD %s/%s" % (board, self.thread_num))
            self.fully_loaded = True
        except aiohttp.ClientResponseError as e:
            logger.error("UNABLE TO LOAD THREAD %s\n%s" % (self.thread_num, e))

    async def download_all_files_from_thread(self, board: str):
        if not self.fully_loaded:
            await self.try_load_all_posts(board)

        if not self.fully_loaded:
            return

        os.makedirs(f"{board}", exist_ok=True)

        filepath = os.path.join(board, str(self.thread_num))
        os.makedirs(filepath, exist_ok=True)

        for post in self.posts:
            await post.download_files(filepath)


class TopItem(BaseModel):
    board: str
    info: str
    name: str


class Board(BaseModel):
    bump_limit: int
    category: str
    default_name: str
    enable_dices: bool
    enable_flags: bool
    enable_icons: bool
    enable_likes: bool
    enable_names: bool
    enable_oekaki: bool
    enable_posting: bool
    enable_sage: bool
    enable_shield: bool
    enable_subject: bool
    enable_thread_tags: bool
    enable_trips: bool
    file_types: List[str]
    id: str
    info: str
    info_outer: str
    max_comment: int
    max_files_size: int
    max_pages: int
    name: str
    threads_per_page: int


class Model(BaseModel):
    advert_bottom_image: str
    advert_bottom_link: str
    advert_mobile_image: str
    advert_mobile_link: str
    advert_top_image: str
    advert_top_link: str
    board: Board
    board_banner_image: str
    board_banner_link: str
    board_speed: int | None
    current_page: int | None
    current_thread: int
    is_board: bool
    is_index: bool
    pages: List[int] | None
    threads: List[Thread]
