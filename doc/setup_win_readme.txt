About
=====

The setup_win.py script builds an EXE or MSI installer for Windows.


Requirements
============


Python 3
--------

The script currently requires Python 3.4, because PyGObject for
Windows doesn't yet work with newer Python versions.

You will need the 32-bit version of Python so that the generated EXE
and the installer will work on both 32 and 64 bit Windows.


PyGObject
---------

For now, the script only works with PyGObject for Windows:

    https://sourceforge.net/projects/pygobjectwin32/

The tested version is 3.24.1_rev1.


cx_Freeze
---------

You will need cx_Freeze version 4.3.4. This is the only version that
works with Python 3.4 without issues.

    py -3.4 -m pip install cx_Freeze==4.3.4


Gettext
-------

To create translations, you will need Gettext (namely, the msgfmt
utility). The script will first try to find the GNU msgfmt in a
directory mentioned in the PATH environment variable or in the current
directory. Then it will fall back to the msgfmt shipped with Python.

If you prefer GNU version of msgfmt over Python's, there are two ways
to get it:

 1. Install it with PyGObject for Windows. Choose "Additional Tools"
    during the installation. The executable will be in
    "Lib\site-packages\gnome\" within your Python's installation
    directory.

 2. Download it from one of the following places:

    * https://mlocati.github.io/articles/gettext-iconv-windows.html
    * https://download.gnome.org/binaries/win32/dependencies/


Building
========


EXE
---

To generate a directory with an executable, run:

    py -3.4 setup_win.py build_exe

The generated files will be in the "build\exe.win32-3.4\" directory.


MSI installer
-------------

To generate an MSI installer, run:

    py -3.4 setup_win.py bdist_msi

The installer will be in the "dist" directory.
