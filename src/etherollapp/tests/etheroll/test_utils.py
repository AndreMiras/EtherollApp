from threading import Thread

from etherollapp.etheroll.utils import run_in_thread


class TestUtils:

    def test_run_in_thread(fn):
        @run_in_thread
        def threaded_sleep(seconds):
            from time import sleep
            sleep(seconds)

        thread = threaded_sleep(0.1)
        assert isinstance(thread, Thread)
        assert thread.is_alive() is True
        thread.join()
        assert thread.is_alive() is False
