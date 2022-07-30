import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or "@ABUU254"
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', '').replace(
        'postgres://', 'postgresql://') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_PATH = os.path.join(basedir, 'app/uploads')
    UPLOAD_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif','.tif', '.heic', '.bmp', '.HEIF']
    LISTINGS_PER_PAGE = 20