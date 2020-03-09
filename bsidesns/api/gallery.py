import os
import shutil

from flask import current_app
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from freenit.schemas.paging import PageInSchema, paginate
from werkzeug.utils import secure_filename

from ..models.event import Event
from ..models.gallery import GalleryAlbum, GalleryFile
from ..schemas.gallery import (
    GalleryAlbumPageOutSchema,
    GalleryAlbumSchema,
    GalleryUploadSchema,
    ResumableGalleryUploadSchema
)

blueprint = Blueprint('gallery', 'gallery')


@blueprint.route('', endpoint='albums')
@blueprint.route('/<int:year>', endpoint='year_albums')
class GalleryAlbumListAPI(MethodView):
    @blueprint.arguments(PageInSchema(), location='headers')
    @blueprint.response(GalleryAlbumPageOutSchema)
    def get(self, pagination, year=None):
        """Get list of albums"""
        if year is None:
            return paginate(GalleryAlbum.select(), pagination)
        try:
            event = Event.get(year=year)
        except Event.DoesNotExist:
            abort(404, message='No such event')
        return paginate(event.albums, pagination)


@blueprint.route('/album/<name>', endpoint='album')
@blueprint.route('/album/<name>/<int:year>', endpoint='year_album')
class GalleryAlbumAPI(MethodView):
    @blueprint.arguments(PageInSchema(), location='headers')
    @blueprint.response(GalleryAlbumSchema)
    def get(self, pagination, name, year=None):
        """Get album details"""
        if year is not None:
            try:
                event = Event.get(year=year)
            except Event.DoesNotExist:
                abort(404, message='No such event')
        else:
            event = None
        try:
            album = GalleryAlbum.get(name=name, event=event)
        except GalleryAlbum.DoesNotExist:
            abort(404, message='No such album')
        album.files = paginate(
            album.files.order_by(GalleryFile.filename),
            pagination,
        )
        prefix = current_app.config.get('MEDIA_URL', None)
        if prefix is None:
            abort(409, message='Backend misconfiguration, no MEDIAL_URL')
        album.prefix = prefix
        return album

    @blueprint.arguments(GalleryUploadSchema, location='files')
    @blueprint.arguments(ResumableGalleryUploadSchema, location='form')
    @blueprint.response(ResumableGalleryUploadSchema)
    def post(self, fileargs, formargs, name, year=None):
        """Upload picture to album"""
        if year is not None:
            try:
                event = Event.get(year=year)
            except Event.DoesNotExist:
                abort(404, message='No such event')
        else:
            event = None
        try:
            album = GalleryAlbum.get(name=name, event=event)
        except GalleryAlbum.DoesNotExist:
            abort(404, message='No such album')
        album.prefix = current_app.config.get('MEDIA_URL', None)
        if album.prefix is None:
            abort(409, message='Backend misconfiguration, no MEDIAL_URL')
        uploadFile = fileargs['file']
        chunkNumber = formargs['resumableChunkNumber']
        chunkSize = formargs['resumableChunkSize']
        total = formargs['resumableTotalChunks']
        identifier = formargs['resumableIdentifier']
        media_path = os.path.abspath(
            current_app.config.get(
                'MEDIA_PATH',
                None,
            )
        )
        filePath = f'/tmp/{identifier}'
        with open(filePath, 'ab') as tempfile:
            offset = (chunkNumber - 1) * chunkSize
            tempfile.seek(offset)
            tempfile.write(uploadFile.read())
        if chunkNumber == total:
            try:
                filename = secure_filename(uploadFile.filename)
                formargs['resumableFilename'] = filename
                finalFile = GalleryFile.get(album=album, filename=filename)
            except GalleryFile.DoesNotExist:
                finalFile = GalleryFile(
                    album=album,
                    filename=secure_filename(uploadFile.filename),
                )
            if event is None:
                file_dir = f'{media_path}/{album.name}'
            else:
                file_dir = f'{media_path}/{event.year}/{album.name}'
            if not os.path.exists(file_dir):
                os.makedirs(file_dir)
            finalPath = finalFile.url(prefix=media_path)
            shutil.move(filePath, finalPath)
            os.chmod(finalPath, 0o644)
            finalFile.save()
        return formargs
