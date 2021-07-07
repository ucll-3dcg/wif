import asyncio


RAYTRACER = r"G:\repos\ucll\3dcg\raytracer\raytracer\x64\Release\raytracer.exe"


async def render_script(script, stdout_receiver, stderr_receiver):
    process = await asyncio.create_subprocess_exec(RAYTRACER, "-s", "-", stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    process.stdin.write(script.encode('ascii'))
    await process.stdin.drain()
    process.stdin.close()

    await asyncio.gather(stdout_receiver(process.stdout), stderr_receiver(process.stderr))

    await process.wait()
