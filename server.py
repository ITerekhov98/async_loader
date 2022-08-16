from aiohttp import web    
import aiofiles
import datetime
import asyncio
import os
import logging

INTERVAL_SECS = 1


logger = logging.getLogger(__name__)

async def handle_index_page(request):
    async with aiofiles.open('index.html', mode='r') as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type='text/html')


async def archive(request):
    archive_hash = request.match_info.get('archive_hash')
    archive_path = f'test_photos/{archive_hash}'
    if not os.path.exists(archive_path):
        raise web.HTTPNotFound(text='Архив не существует или был удален')

    response = web.StreamResponse()
    response.headers['Content-Type'] = 'text/html'
    response.headers['Content-Disposition'] = 'attachment; filename="test_photos.zip"'

    await response.prepare(request)

    process = await asyncio.create_subprocess_exec('zip', '-', '-r', '.',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd= f'test_photos/{archive_hash}'
    )
    while True:
        if process.stdout.at_eof():
            break    

        archive_batch = await process.stdout.read(100*1024)
        logger.debug('Sending archive chunk ...')
        await response.write(archive_batch)

    return response
    


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.DEBUG
    )
    app = web.Application()
    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/archive/{archive_hash}/', archive),
    ])
    web.run_app(app)