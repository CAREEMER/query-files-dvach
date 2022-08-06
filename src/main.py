import asyncio
from multiprocessing import Process

from search_engine.engine import SearchEngine


async def loader(board: str):
    engine = SearchEngine()

    threads = await engine.search_for_in_threads(board=board, include=["сап"], exclude=["фап"])
    for thread in threads:
        await thread.download_all_files_from_thread(board)


def task(board):
    asyncio.run(loader(board))


def main():
    boards = ["b", "vg"]

    threads = []

    for board in boards:
        process = Process(target=task, args=(board,))
        process.start()
        threads.append(process)

    for process in threads:
        process.join()


if __name__ == "__main__":
    main()
