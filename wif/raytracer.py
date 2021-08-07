import wif.gui.imgview
import wif.io
import wif.config
import wif.reading
import wif.concurrency


def _raytracer_path():
    return wif.config.configuration['raytracer']


def invoke_raytracer(script):
    (stdout, stderr) = wif.reading.open_subprocess(
        [_raytracer_path(), '-s', '-'],
        script)

    blocks = (block.decode('ascii') for block in wif.reading.read_blocks_from_stream(stdout))
    messages = wif.reading.read_lines_from_stream(stderr)

    return (blocks, messages)

    # block_channel = wif.concurrency.generate_in_background(blocks)
    # message_channel = wif.concurrency.generate_in_background(messages)

    # return (block_channel, message_channel)


# def render_script_to_collectors(script):
#     async def stdout_processor(stream):
#         blocks = wif.io.read_blocks_from_async_stream(stream)
#         images = wif.io.read_images(blocks)
#         async for image in wif.gui.imgview.convert_images(images):
#             yield image

#     async def stderr_processor(stream):
#         while True:
#             line = await stream.readline()
#             if not line:
#                 break
#             yield line.decode('ascii')

#     return wif.io.open_subprocess_to_collectors(
#         _raytracer_path(),
#         '-s',
#         '-',
#         input=script,
#         stdout_processor=stdout_processor,
#         stderr_processor=stderr_processor)
