#!/usr/bin/env python
"""
================================================================================
:mod:`builder` -- Base deb builder for programs
================================================================================

.. module:: builder
   :synopsis: Base deb builder for programs

.. inheritance-diagram:: pymontecarlo.util.dist.deb.builder

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2014 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
import subprocess
import textwrap
import gzip
from io import BytesIO, StringIO
import shutil
import tempfile

# Third party modules.
from debian.deb822 import Deb822
from debian.changelog import Changelog

from deb_pkg_tools.package import build_package

# Local modules.

# Globals and constants variables.

class ManPage(object):

    def __init__(self, package, name, short_description='', synopsis='',
                 long_description='', see_also=''):
        self.package = package
        self.name = name
        self.short_description = short_description
        self.synopsis = synopsis
        self.long_description = long_description
        self.see_also = see_also

    def write(self, fp):
        def e(s):
            return s.replace('-', '\\-')

        lines = []
        lines.append('.TH %s 1 "" "" %s' % (e(self.name), e(self.package)))
        lines.append('')
        lines.append('.SH NAME')
        lines.append('%s \\- %s' % (e(self.name), e(self.short_description)))
        if self.synopsis:
            lines.append('')
            lines.append('.SH SYNOPSIS')
            lines.append('%s' % e(self.synopsis))
        if self.long_description:
            lines.append('')
            lines.append('.SH DESCRIPTION')
            lines.append(e(self.long_description))
        if self.see_also:
            lines.append('')
            lines.append('.SH SEE ALSO')
            lines.append('%s' % e(self.see_also))
        fp.write('\n'.join(lines))

class DesktopEntry(object):

    TYPE_APPLICATION = 'Application'
    TYPE_LINK = 'Link'
    TYPE_DIRECTORY = 'Directory'

    def __init__(self, type_, name, version=1.0, genericname=None,
                 nodisplay=None, comment=None, icon=None, hidden=None,
                 onlyshowin=None, notshowin=None, dbusactivatable=None,
                 tryexec=None, exec_=None, path=None, terminal=None,
                 actions=None, mimetype=None, categories=None, keywords=None,
                 startupnotify=None, startupwmclass=None, url=None):
        """
        Creates a desktop entry.
        """
        if type_ is self.TYPE_LINK and url is None:
            raise ValueError('url is required')

        self.type_ = type_
        self.name = name
        self.version = version
        self.genericname = genericname
        self.nodisplay = nodisplay
        self.comment = comment
        self.icon = icon
        self.hidden = hidden
        self.onlyshowin = tuple(onlyshowin or ())
        self.notshowin = tuple(notshowin or ())
        self.dbusactivatable = dbusactivatable
        self.tryexec = tryexec
        self.exec_ = exec_
        self.path = path
        self.terminal = terminal
        self.actions = actions
        self.mimetype = tuple(mimetype or ())
        self.categories = tuple(categories or ())
        self.keywords = tuple(keywords or ())
        self.startupnotify = startupnotify
        self.startupwmclass = startupwmclass
        self.url = url

    def write(self, fp):
        def b(v):
            return 'true' if v else 'false'
        def l(v):
            return ';'.join(map(lambda x: x.replace(';', '\\;'), v)) + ';'

        lines = []
        lines.append('[Desktop Entry]')
        lines.append('Type=%s' % self.type_)
        lines.append('Version=%s' % self.version)
        lines.append('Name=%s' % self.name)
        if self.genericname is not None:
            lines.append('GenericName=%s' % self.genericname)
        if self.comment is not None:
            lines.append('Comment=%s' % self.comment)
        if self.nodisplay is not None:
            lines.append('NoDisplay=%s' % b(self.nodisplay))
        if self.icon is not None:
            lines.append('Icon=%s' % self.icon)
        if self.hidden is not None:
            lines.append('Hidden=%s' % b(self.hidden))
        if self.onlyshowin:
            lines.append('OnlyShowIn=%s' % l(self.onlyshowin))
        if self.notshowin:
            lines.append('NotShowIn=%s' % l(self.notshowin))
        if self.dbusactivatable is not None:
            lines.append('DBusActivatable=%s' % b(self.dbusactivatable))
        if self.tryexec is not None:
            lines.append('TryExec=%s' % self.tryexec)
        if self.exec_ is not None:
            lines.append('Exec=%s' % self.exec_)
        if self.path is not None:
            lines.append('Path=%s' % self.path)
        if self.terminal is not None:
            lines.append('Terminal=%s' % b(self.terminal))
        if self.actions:
            lines.append('Actions=%s' % l(self.actions))
        if self.mimetype:
            lines.append('MimeType=%s' % l(self.mimetype))
        if self.categories:
            lines.append('Categories=%s' % l(self.categories))
        if self.keywords:
            lines.append('Keywords=%s' % l(self.keywords))
        if self.startupnotify is not None:
            lines.append('StartupNotify=%s' % b(self.startupnotify))
        if self.startupwmclass is not None:
            lines.append('StartupWMClass=%s' % self.startupwmclass)
        if self.url is not None:
            lines.append('URL=%s' % self.url)

        fp.write('\n'.join(lines))

def extract_exe_info(filepath):
    cwd = os.path.dirname(__file__)
    command = ['wine', 'sigcheck.exe', '-a', '-q', filepath]
    proc = subprocess.Popen(command, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, cwd=cwd)
    proc.wait()

    exe_info = {}
    for line in proc.stdout.readlines():
        if not line.startswith(b'\t'):
            continue
        key, value = line.split(b':', 1)
        exe_info[key.strip().decode('ascii', 'ignore')] = \
            value.strip().decode('ascii', 'ignore')

    return exe_info

def _format_debian_date(dt):
    s = dt.strftime('%a, %d %b %Y %H:%M:%S %z')
    if dt.tzinfo is None:
        s += ' +0000'
    return s

class _DebBuilder(object):

    def __init__(self, package, fullname, version,
                 maintainer, authors,
                 section, short_description, long_description, date, license,
                 homepage, priority='standard', depends=None, recommends=None):
        self.package = package
        self.fullname = fullname
        self.version = version.rstrip('-1')
        self.maintainer = maintainer
        self.authors = tuple(authors)
        self.section = section
        self.short_description = short_description
        self.long_description = long_description
        self.date = date
        self.license = license
        self.homepage = homepage
        self.priority = priority
        self.depends = tuple(depends or ())
        self.recommends = tuple(recommends or ())

    def _create_temp_dir(self, *args, **kwargs):
        return tempfile.mkdtemp()

    def _create_control(self, temp_dir, *args, **kwargs):
        wrapper = textwrap.TextWrapper(initial_indent=' ',
                                       subsequent_indent=' ',
                                       width=80)
        description = \
            self.short_description + '\n' + wrapper.fill(self.long_description)

        fields = {'Package': self.package,
                  'Version': self.version + '-1',
                  'Section': self.section,
                  'Priority': self.priority,
                  'Architecture': 'all',
                  'Depends': ', '.join(self.depends),
                  'Recommends': ', '.join(self.recommends),
                  'Maintainer': self.maintainer,
                  'Description': description,
                  'Homepage': self.homepage,
                  }
        control = Deb822()
        control.update(fields)
        return control

    def _write_control(self, control, temp_dir, *args, **kwargs):
        os.makedirs(os.path.join(temp_dir, 'DEBIAN'), exist_ok=True)
        control_filepath = os.path.join(temp_dir, 'DEBIAN', 'control')
        with open(control_filepath, 'wb') as fp:
            control.dump(fp)

    def _create_preinst(self, temp_dir, *args, **kwargs):
        lines = []
        lines.append('#!/bin/sh')
        lines.append('set -e')
        lines.append('if [ "$1" = "install" ] ; then')
        lines.append('  echo "Installing %s"' % self.package)
        lines.append('fi')
        lines.append('')
        lines.append('if [ "$1" = "upgrade" ] ; then')
        lines.append('  echo "Upgrading %s"' % self.package)
        lines.append('fi')
        lines.append('exit 0')
        return lines

    def _write_preinst(self, lines, temp_dir, *args, **kwargs):
        os.makedirs(os.path.join(temp_dir, 'DEBIAN'), exist_ok=True)
        filepath = os.path.join(temp_dir, 'DEBIAN', 'preinst')
        with open(filepath, 'w') as fp:
            fp.write('\n'.join(lines))
        os.chmod(filepath, 0o555)

    def _create_postinst(self, temp_dir, *args, **kwargs):
        lines = []
        lines.append('#!/bin/sh')
        lines.append('set -e')
        lines.append('if [ "$1" = "configure" ] ; then')
        lines.append('  echo "Configuring %s"' % self.package)
        lines.append('fi')
        lines.append('exit 0')
        return lines

    def _write_postinst(self, lines, temp_dir, *args, **kwargs):
        os.makedirs(os.path.join(temp_dir, 'DEBIAN'), exist_ok=True)
        filepath = os.path.join(temp_dir, 'DEBIAN', 'postinst')
        with open(filepath, 'w') as fp:
            fp.write('\n'.join(lines))
        os.chmod(filepath, 0o555)

    def _create_prerm(self, temp_dir, *args, **kwargs):
        lines = []
        lines.append('#!/bin/sh')
        lines.append('set -e')
        lines.append('if [ "$1" = "remove" ] ; then')
        lines.append('  echo "Removing %s"' % self.package)
        lines.append('fi')
        lines.append('exit 0')
        return lines

    def _write_prerm(self, lines, temp_dir, *args, **kwargs):
        os.makedirs(os.path.join(temp_dir, 'DEBIAN'), exist_ok=True)
        filepath = os.path.join(temp_dir, 'DEBIAN', 'prerm')
        with open(filepath, 'w') as fp:
            fp.write('\n'.join(lines))
        os.chmod(filepath, 0o555)

    def _create_postrm(self, temp_dir, *args, **kwargs):
        lines = []
        lines.append('#!/bin/sh')
        lines.append('set -e')
        lines.append('if [ "$1" = "purge" ] ; then')
        lines.append('  echo "Purging %s"' % self.package)
        lines.append('fi')
        lines.append('exit 0')
        return lines

    def _write_postrm(self, lines, temp_dir, *args, **kwargs):
        os.makedirs(os.path.join(temp_dir, 'DEBIAN'), exist_ok=True)
        filepath = os.path.join(temp_dir, 'DEBIAN', 'postrm')
        with open(filepath, 'w') as fp:
            fp.write('\n'.join(lines))
        os.chmod(filepath, 0o555)

    def _write_man_page(self, manpage, temp_dir, *args, **kwargs):
        os.makedirs(os.path.join(temp_dir, 'usr', 'share', 'man', 'man1'),
                    exist_ok=True)
        filepath = os.path.join(temp_dir, 'usr', 'share', 'man', 'man1',
                                '%s.1.gz' % manpage.name)
        with gzip.open(filepath, 'wb', 9) as z:
            buf = StringIO()
            manpage.write(buf)
            z.write(buf.getvalue().encode('ascii'))

    def _write_desktop_entry(self, entry, temp_dir, *args, **kwargs):
        os.makedirs(os.path.join(temp_dir, 'usr', 'share', 'applications'),
                    exist_ok=True)

        name = os.path.basename(entry.exec_)
        filepath = os.path.join(temp_dir, 'usr', 'share', 'applications',
                                '%s.desktop' % name)
        with open(filepath, 'wt') as fp:
            entry.write(fp)

    def _create_copyright(self, temp_dir, *args, **kwargs):
        wrapper = textwrap.TextWrapper(initial_indent=' ',
                                       subsequent_indent=' ',
                                       width=80)

        lines = []
        lines.append('Format: http://www.debian.org/doc/packaging-manuals/copyright-format/1.0/')
        lines.append('Upstream-Name: %s' % self.fullname)
        lines.append('Upstream-Contact: %s' % self.maintainer)
        lines.append('')
        lines.append('Files: *')
        lines.append('Copyright: %i %s' % (self.date.year, ', '.join(self.authors)))
        lines.append('License: Custom')
        lines.append(wrapper.fill(self.license))
        return lines

    def _write_copyright(self, lines, temp_dir, *args, **kwargs):
        os.makedirs(os.path.join(temp_dir, 'usr', 'share', 'doc', self.package),
                    exist_ok=True)
        filepath = os.path.join(temp_dir, 'usr', 'share', 'doc',
                                self.package, 'copyright')
        with open(filepath, 'w') as fp:
            fp.write('\n'.join(lines))

    def _create_changelog(self, temp_dir, *args, **kwargs):
        changelog = Changelog()
        changelog.new_block()
        changelog.set_version(self.version)
        changelog.set_package(self.package)
        changelog.set_distributions('all')
        changelog.set_urgency('low')
        changelog.set_author(self.maintainer)
        changelog.set_date(_format_debian_date(self.date))
        changelog.add_change('  * Release of %s' % self.version)
        return changelog

    def _write_changelog(self, changelog, temp_dir, *args, **kwargs):
        os.makedirs(os.path.join(temp_dir, 'usr', 'share', 'doc', self.package),
                    exist_ok=True)
        filepath = os.path.join(temp_dir, 'usr', 'share', 'doc',
                                self.package, 'changelog.Debian.gz')
        with gzip.open(filepath, 'wb', 9) as z:
            buf = BytesIO()
            buf.write(changelog.__bytes__())
            z.write(buf.getvalue())

    def _build_deb(self, temp_dir, outputdir, *args, **kwargs):
        build_package(temp_dir, outputdir)

    def _cleanup(self, temp_dir, *args, **kwargs):
        shutil.rmtree(temp_dir)

    def build(self, outputdir, *args, **kwargs):
        try:
            temp_dir = self._create_temp_dir(*args, **kwargs)
            self._build(temp_dir, *args, **kwargs)
            self._build_deb(temp_dir, outputdir)
        finally:
            self._cleanup(temp_dir)

    def _build(self, temp_dir, *args, **kwargs):
        pass
