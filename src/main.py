import asyncio
import threading

from search_engine.engine import SearchEngine


async def loader(board):
    engine = SearchEngine()

    threads = await engine.search_for_in_threads(board=board, include=["сап"], exclude=["фап"])
    for thread in threads:
        await thread.download_all_files_from_thread(board)


def task(board):
    asyncio.run(loader(board))


def main():
    boards = ["b"]

    threads = []

    for board in boards:
        _task = threading.Thread(target=task, args=(board,))
        _task.start()
        threads.append(_task)

    for _task in threads:
        _task.join()


if __name__ == "__main__":
    main()
