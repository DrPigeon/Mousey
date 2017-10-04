# -*- coding: utf-8 -*-
import asyncio


async def shell(command: str) -> str:
    """Runs a subprocess in shell and returns the output."""
    process = await asyncio.create_subprocess_shell(
        command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    results = await process.communicate()
    # stdout and stderr are separate
    return ''.join(x.decode('utf-8') for x in results)
