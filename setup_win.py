import os
import site
from glob import glob

from cx_Freeze import setup, Executable

from gtimecalc import app_info


site_dir = site.getsitepackages()[1]
include_path = os.path.join(site_dir, 'gnome')


inc_bin = [
    'gspawn-win32-helper.exe',
    'libatk-1.0-0.dll',
    'libcairo-gobject-2.dll',
    'libepoxy-0.dll',
    'libgdk-3-0.dll',
    'libgdk_pixbuf-2.0-0.dll',
    'libgtk-3-0.dll',
    'libharfbuzz-0.dll',
    'libjasper-1.dll',
    'libjpeg-8.dll',
    'libpango-1.0-0.dll',
    'libpangocairo-1.0-0.dll',
    'libpangoft2-1.0-0.dll',
    'libpangowin32-1.0-0.dll',
    'librsvg-2-2.dll',
    'libtiff-5.dll',
    'libwebp-5.dll',
    ]


inc_data = [
    ('etc', 'fonts'),
    ('etc', 'gtk-3.0'),
    ('etc', 'pango'),
    ('lib', 'gdk-pixbuf-2.0'),
    ('lib', 'girepository-1.0'),
    ('share', 'fontconfig'),
    ('share', 'glib-2.0'),
    ('share', 'icons', 'Adwaita'),
    ('share', 'icons', 'hicolor'),
    # ('share', 'fonts'),
    # ('share', 'locale'),
    ]


def iter_inc_files():
    for path in inc_bin:
        yield path

    for path_parts in inc_data:
        path = os.path.join(*path_parts)
        yield path


include_files = []

for path in iter_inc_files():
    include_files.append((os.path.join(include_path, path), path))

for path in glob(
        os.path.join('data', 'icons', 'hicolor', '*x*', '*', '*.png')):
    include_files.append((path, path.replace('data', 'share', 1)))

include_files.append((
    os.path.join('data', 'icons', 'hicolor', 'scalable'),
    os.path.join('share', 'icons', 'hicolor', 'scalable')
    ))


setup(
    name='gTimeCalc',
    description='Time calculator',
    version=app_info.VERSION,
    author='Daniel Plakhotich',
    author_email='daniel.plakhotich@gmail.com',
    url=app_info.WEBSITE,
    options=dict(
        build_exe=dict(
            includes=['gi'],
            packages=['gi'],
            include_files=include_files
            ),
        bdist_msi=dict(
            upgrade_code='{1ab63180-c6bb-11e5-b5d4-0002a5d5c51b}',
            )
        ),
    executables=[
        Executable(
            os.path.join('bin', 'gtimecalc'),
            base='Win32GUI',
            icon=os.path.join('data', 'icons', 'gtimecalc.ico'),
            shortcutName='gTimeCalc',
            shortcutDir='ProgramMenuFolder',
        )
    ]
)
