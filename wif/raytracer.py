import asyncio


RAYTRACER = r"G:\repos\ucll\3dcg\raytracer\raytracer\x64\Release\raytracer.exe"


async def render_script(script):
    process = await asyncio.create_subprocess_exec(RAYTRACER, "-s", "-", stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    process.stdin.write(script)
    await process.stdin.drain()

