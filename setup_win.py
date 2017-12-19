import os
import site
from glob import glob
import shutil
import subprocess

import cx_Freeze
from cx_Freeze import setup, Executable

from gtimecalc import app_info


site_dir = site.getsitepackages()[1]
include_path = os.path.join(site_dir, 'gnome')


inc_bin = (
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
    )


inc_data = (
    ('etc', 'fonts'),
    ('etc', 'gtk-3.0'),
    ('etc', 'pango'),
    ('lib', 'gdk-pixbuf-2.0'),
    # ('lib', 'girepository-1.0'),  # See inc_typelibs
    ('share', 'fontconfig'),
    ('share', 'glib-2.0'),
    ('share', 'icons', 'Adwaita'),
    ('share', 'icons', 'hicolor'),
    # ('share', 'fonts'),
    # ('share', 'locale'),  # See build_mo()
    )


inc_typelibs = (
    'Atk-1.0',
    'cairo-1.0',
    'Gdk-3.0',
    'GdkPixbuf-2.0',
    'Gio-2.0',
    'GLib-2.0',
    'GModule-2.0',
    'GObject-2.0',
    'Gtk-3.0',
    'Pango-1.0',
    )


def iter_inc_files():
    for path in inc_bin:
        yield path

    for path_parts in inc_data:
        path = os.path.join(*path_parts)
        yield path

    for typelib in inc_typelibs:
        yield os.path.join('lib', 'girepository-1.0', typelib + '.typelib')


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


def build_mo(msgfmt_path, tmp_dir):
    po_dir = 'po'
    for lang in open(os.path.join(po_dir, 'LINGUAS'), 'r', encoding='utf-8'):
        lang = lang.strip()
        if not lang or lang.startswith('#'):
            continue

        mo_dir = os.path.join(tmp_dir, lang, 'LC_MESSAGES')
        os.makedirs(mo_dir, exist_ok=True)

        cmd = (
            msgfmt_path,
            os.path.join(po_dir, lang + '.po'),
            '-o',
            os.path.join(mo_dir, app_info.NAME + '.mo')
        )
        subprocess.call(cmd)

        # Copy .mo for Glib/Gtk
        for mo_name in ('glib20', 'gtk30'):
            mo_path = os.path.join(
                include_path, 'share', 'locale', lang, 'LC_MESSAGES',
                mo_name + '.mo')

            try:
                shutil.copy(mo_path, mo_dir)
            except FileNotFoundError:
                pass


msgfmt_path = shutil.which('msgfmt')
if msgfmt_path is not None:
    locale_build_dir = os.path.join('build', 'locale')
    build_mo(msgfmt_path, locale_build_dir)
    include_files.append((locale_build_dir, os.path.join('share', 'locale')))
else:
    print('msgfmt is not found; translations will not be included')


build_exe_options = dict(
    # Remove unused modules, which will make the installer almost
    # 2 Mb smaller.
    excludes=['bz2', 'decimal', 'hashlib', 'lzma', 'pyexpat', 'ssl'],
    includes=['gi'],
    packages=['gi'],
    include_files=include_files
    )

if int(cx_Freeze.version.split('.', 1)[0]) > 4:
    build_exe_options.update(
        zip_exclude_packages=[],
        zip_include_packages=['*']
        )


setup(
    name='gTimeCalc',
    description='Time calculator',
    version=app_info.VERSION,
    author='Daniel Plakhotich',
    author_email='daniel.plakhotich@gmail.com',
    url=app_info.WEBSITE,
    options=dict(
        build_exe=build_exe_options,
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
