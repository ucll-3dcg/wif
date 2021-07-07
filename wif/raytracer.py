import asyncio


RAYTRACER = r"G:\repos\ucll\3dcg\raytracer\raytracer\x64\Release\raytracer.exe"


async def _read_output_stream(stream):
    data = await stream.read()
    # print(data)


async def _read_error_stream(stream):
    while True:
        data = await stream.readline()
        print(data.decode('ascii'))
        if not data:
            break


async def render_script(script):
    process = await asyncio.create_subprocess_exec(RAYTRACER, "-s", "-", stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    process.stdin.write(script.encode('ascii'))
    await process.stdin.drain()
    process.stdin.close()

    asyncio.gather(_read_output_stream(process.stdout), _read_error_stream(process.stderr))

    await process.wait()
