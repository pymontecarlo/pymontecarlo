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
from io import BytesIO
import shutil
import tempfile

# Third party modules.
from debian.deb822 import Deb822
from debian.changelog import Changelog

from deb_pkg_tools.package import build_package

# Local modules.

# Globals and constants variables.

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
                 homepage, priority='standard', depends=None):
        self._package = package
        self._fullname = fullname
        self._version = version.rstrip('-1')
        self._maintainer = maintainer
        self._authors = tuple(authors)
        self._section = section
        self._short_description = short_description
        self._long_description = long_description
        self._date = date
        self._license = license
        self._homepage = homepage
        self._priority = priority

        if depends is None:
            depends = ()
        self._depends = tuple(depends)

    def _create_temp_dir(self, *args, **kwargs):
        return tempfile.mkdtemp()

    def _create_control(self, temp_dir, *args, **kwargs):
        wrapper = textwrap.TextWrapper(initial_indent=' ',
                                       subsequent_indent=' ',
                                       width=80)
        description = \
            self._short_description + '\n' + wrapper.fill(self._long_description)

        fields = {'Package': self._package,
                  'Version': self._version + '-1',
                  'Section': self._section,
                  'Priority': self._priority,
                  'Architecture': 'all',
                  'Depends': ', '.join(self._depends),
                  'Maintainer': self._maintainer,
                  'Description': description,
                  'Homepage': self._homepage,
                  }
        control = Deb822()
        control.update(fields)
        return control

    def _write_control(self, control, temp_dir, *args, **kwargs):
        control_filepath = os.path.join(temp_dir, 'DEBIAN', 'control')
        with open(control_filepath, 'wb') as fp:
            control.dump(fp)

    def _create_preinst(self, temp_dir, *args, **kwargs):
        lines = []
        lines.append('#!/bin/sh')
        lines.append('set -e')
        lines.append('if [ "$1" = "install" ] ; then')
        lines.append('  echo "Installing %s"' % self._package)
        lines.append('fi')
        lines.append('')
        lines.append('if [ "$1" = "upgrade" ] ; then')
        lines.append('  echo "Upgrading %s"' % self._package)
        lines.append('fi')
        lines.append('exit 0')
        return lines

    def _write_preinst(self, lines, temp_dir, *args, **kwargs):
        filepath = os.path.join(temp_dir, 'DEBIAN', 'preinst')
        with open(filepath, 'w') as fp:
            fp.write('\n'.join(lines))
        os.chmod(filepath, 0o555)

    def _create_postinst(self, temp_dir, *args, **kwargs):
        lines = []
        lines.append('#!/bin/sh')
        lines.append('set -e')
        lines.append('if [ "$1" = "configure" ] ; then')
        lines.append('  echo "Configuring %s"' % self._package)
        lines.append('fi')
        lines.append('exit 0')
        return lines

    def _write_postinst(self, lines, temp_dir, *args, **kwargs):
        filepath = os.path.join(temp_dir, 'DEBIAN', 'postinst')
        with open(filepath, 'w') as fp:
            fp.write('\n'.join(lines))
        os.chmod(filepath, 0o555)

    def _create_prerm(self, temp_dir, *args, **kwargs):
        lines = []
        lines.append('#!/bin/sh')
        lines.append('set -e')
        lines.append('if [ "$1" = "remove" ] ; then')
        lines.append('  echo "Removing %s"' % self._package)
        lines.append('fi')
        lines.append('exit 0')
        return lines

    def _write_prerm(self, lines, temp_dir, *args, **kwargs):
        filepath = os.path.join(temp_dir, 'DEBIAN', 'prerm')
        with open(filepath, 'w') as fp:
            fp.write('\n'.join(lines))
        os.chmod(filepath, 0o555)

    def _create_postrm(self, temp_dir, *args, **kwargs):
        lines = []
        lines.append('#!/bin/sh')
        lines.append('set -e')
        lines.append('if [ "$1" = "purge" ] ; then')
        lines.append('  echo "Purging %s"' % self._package)
        lines.append('fi')
        lines.append('exit 0')
        return lines

    def _write_postrm(self, lines, temp_dir, *args, **kwargs):
        filepath = os.path.join(temp_dir, 'DEBIAN', 'postrm')
        with open(filepath, 'w') as fp:
            fp.write('\n'.join(lines))
        os.chmod(filepath, 0o555)

    def _create_man_page(self, temp_dir, *args, **kwargs):
        def e(s):
            return s.replace('-', '\\-')

        lines = []
        lines.append('.TH %s 1' % e(self._package))
        lines.append('')
        lines.append('.SH NAME')
        lines.append('%s \\- %s' % (e(self._package), e(self._short_description)))
        lines.append('')
        lines.append('.SH SYNOPSYS')
        lines.append('.B %s' % e(self._package))
        lines.append('')
        lines.append('.SH DESCRIPTION')
        lines.append(textwrap.fill(e(self._long_description), 80))
        lines.append('')
        lines.append('.SH AUTHOR')
        for author in self._authors:
            lines.append('%s' % e(author))
        lines.append('')
        lines.append('.SH COPYRIGHT ')
        lines.append('Copyright (c) %i %s' % (self._date.year, ', '.join(map(e, self._authors))))
        lines.append('')
        lines.append('.SH SEE ALSO')
        lines.append('%s' % e(self._homepage))
        return lines

    def _write_man_page(self, lines, temp_dir, *args, **kwargs):
        filepath = os.path.join(temp_dir, 'usr', 'share', 'man', 'man1',
                                '%s.1.gz' % self._package)
        with gzip.open(filepath, 'wb', 9) as z:
            for line in lines:
                z.write(line.encode('ascii') + b'\n')

    def _create_copyright(self, temp_dir, *args, **kwargs):
        wrapper = textwrap.TextWrapper(initial_indent=' ',
                                       subsequent_indent=' ',
                                       width=80)

        lines = []
        lines.append('Format: http://www.debian.org/doc/packaging-manuals/copyright-format/1.0/')
        lines.append('Upstream-Name: %s' % self._fullname)
        lines.append('Upstream-Contact: %s' % self._maintainer)
        lines.append('')
        lines.append('Files: *')
        lines.append('Copyright: %i %s' % (self._date.year, ', '.join(self._authors)))
        lines.append('License: Custom')
        lines.append(wrapper.fill(self._license))
        return lines

    def _write_copyright(self, lines, temp_dir, *args, **kwargs):
        filepath = os.path.join(temp_dir, 'usr', 'share', 'doc',
                                self._package, 'copyright')
        with open(filepath, 'w') as fp:
            fp.write('\n'.join(lines))

    def _create_changelog(self, temp_dir, *args, **kwargs):
        changelog = Changelog()
        changelog.new_block()
        changelog.set_version(self._version)
        changelog.set_package(self._package)
        changelog.set_distributions('all')
        changelog.set_urgency('low')
        changelog.set_author(self._maintainer)
        changelog.set_date(_format_debian_date(self._date))
        changelog.add_change('  * Release of %s' % self._version)
        return changelog

    def _write_changelog(self, changelog, temp_dir, *args, **kwargs):
        buf = BytesIO()
        buf.write(changelog.__bytes__())

        filepath = os.path.join(temp_dir, 'usr', 'share', 'doc',
                                self._package, 'changelog.Debian.gz')
        with gzip.open(filepath, 'wb', 9) as z:
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
