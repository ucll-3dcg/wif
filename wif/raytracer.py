import wif.gui.imgview
import wif.io
import wif.config


def _raytracer_path():
    return wif.config.configuration['raytracer']


async def render_script(script, stdout_processor, stderr_processor):
    wif.io.open_subprocess(
        _raytracer_path(),
        '-s',
        '-',
        stdout_processor=stdout_processor,
        stderr_processor=stderr_processor)


def render_script_to_collectors(script):
    async def stdout_processor(stream):
        blocks = wif.io.read_blocks_from_async_stream(stream)
        images = wif.io.read_images(blocks)
        async for image in wif.gui.imgview.convert_images(images):
            yield image

    async def stderr_processor(stream):
        while True:
            line = await stream.readline()
            if not line:
                break
            yield line.decode('ascii')

    return wif.io.open_subprocess_to_collectors(
        _raytracer_path(),
        '-s',
        '-',
        input=script,
        stdout_processor=stdout_processor,
        stderr_processor=stderr_processor)
