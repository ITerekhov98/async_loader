from aiohttp import web    
import aiofiles
import argparse
import asyncio
import os
import logging
from functools import partial
from environs import Env
INTERVAL_SECS = 1


logger = logging.getLogger(__name__)

async def handle_index_page(request):
    async with aiofiles.open('index.html', mode='r') as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type='text/html')

async def initialize_archiving(request, photos_dir_path):
    archive_hash = request.match_info.get('archive_hash')
    archive_path = os.path.join(photos_dir_path, archive_hash)
    if not os.path.exists(archive_path):
        raise web.HTTPNotFound(text='Архив не существует или был удален')

    process = await asyncio.create_subprocess_exec('zip', '-', '-r', '.',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=archive_path
    )
    return process


async def recieve_arhcive(request, response_delay, photos_dir_path):

    process = await initialize_archiving(request, photos_dir_path)

    response = web.StreamResponse()
    response.headers['Content-Type'] = 'text/html'
    response.headers['Content-Disposition'] = 'attachment; filename="test_photos.zip"'

    await response.prepare(request)

    try:
        while not process.stdout.at_eof():   
            batch = await process.stdout.read(100*1024)
            logger.info('Sending archive chunk ...')
            if response_delay:
                await asyncio.sleep(response_delay)
            await response.write(batch)
    except asyncio.CancelledError:
        logger.warning('Download was interrupted')
        raise
    finally:
        if process.returncode:
            process.kill()
            await process.communicate()
    return response    




if __name__ == '__main__':
    env = Env()
    env.read_env()
    photos_dir_path = env.str('PHOTOS_DIR_PATH', 'test_photos')
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--response_delay',
        help='Задержка перед отправкой порции данных',
        type=int,
        default=0,
    )
    parser.add_argument(
        '--skip_logging',
        help='Подробное логгирование, по умолчанию True.'
             'Если указать значение False, будут выводиться'
             'сообщения уровня WARNING и выше',
        action='store_true',
        default=False
    )
    args = parser.parse_args()

    logging_level = logging.DEBUG if not args.skip_logging else logging.WARNING
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging_level
    )
    app = web.Application()
    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/archive/{archive_hash}/', partial(recieve_arhcive, response_delay=args.response_delay, photos_dir_path=photos_dir_path)),
    ])
    web.run_app(app)