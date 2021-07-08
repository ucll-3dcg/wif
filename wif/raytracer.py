import wif.gui.viewer
from wif.bgworker import perform_async
import wif.io


RAYTRACER = r"G:\repos\ucll\3dcg\raytracer\raytracer\x64\Release\raytracer.exe"


async def render_script(script, stdout_processor, stderr_processor):
    wif.io.open_subprocess(
        RAYTRACER,
        '-s',
        '-',
        stdout_processor=stdout_processor,
        stderr_processor=stderr_processor)


def render_script_to_collectors(script):
    async def stdout_processor(stream):
        blocks = wif.io.read_blocks_from_async_stream(stream)
        images = wif.io.read_images(blocks)
        async for image in wif.gui.viewer.convert_images(images):
            yield image

    async def stderr_processor(stream):
        while True:
            line = await stream.readline()
            if not line:
                break
            yield line.decode('ascii')

    return wif.io.open_subprocess_to_collectors(
        RAYTRACER,
        '-s',
        '-',
        input=script,
        stdout_processor=stdout_processor,
        stderr_processor=stderr_processor)
