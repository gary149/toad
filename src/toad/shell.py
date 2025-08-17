from __future__ import annotations


import os
import asyncio
import codecs
import fcntl
import pty
import struct
import termios


from toad.widgets.ansi_log import ANSILog


def resize_pty(fd, cols, rows):
    """Resize the pseudo-terminal"""
    # Pack the dimensions into the format expected by TIOCSWINSZ
    size = struct.pack("HHHH", rows, cols, 0, 0)
    fcntl.ioctl(fd, termios.TIOCSWINSZ, size)


class Shell:
    def __init__(self, command: str) -> None:
        self._command = command

    async def run(self, ansi_log: ANSILog) -> None:
        master, slave = pty.openpty()

        flags = fcntl.fcntl(master, fcntl.F_GETFL)
        fcntl.fcntl(master, fcntl.F_SETFL, flags | os.O_NONBLOCK)

        env = os.environ.copy()
        process = await asyncio.create_subprocess_shell(
            self._command,
            stdin=slave,
            stdout=slave,
            stderr=slave,
            # env=env,
        )

        width = ansi_log.scrollable_content_region.width
        height = 24

        os.close(slave)

        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)

        loop = asyncio.get_event_loop()
        transport, _ = await loop.connect_read_pipe(
            lambda: protocol, os.fdopen(master, "rb", 0)
        )

        unicode_decoder = codecs.getincrementaldecoder("utf-8")(errors="replace")
        try:
            resize_pty(master, width, height)
            while True:
                try:
                    # Read with timeout
                    data = await asyncio.wait_for(reader.read(1024 * 16), timeout=None)
                    if not data:
                        break
                    line = unicode_decoder.decode(data)
                    if line:
                        ansi_log.write(line)
                except asyncio.TimeoutError:
                    # Check if process is still running
                    if process.returncode is not None:
                        break
        finally:
            transport.close()

        line = unicode_decoder.decode(b"", final=True)
        ansi_log.write(line)

        await process.wait()
