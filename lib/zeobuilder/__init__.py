# Zeobuilder is an extensible GUI-toolkit for molecular model construction.
# Copyright (C) 2007 Toon Verstraelen <Toon.Verstraelen@UGent.be>
#
# This file is part of Zeobuilder.
#
# Zeobuilder is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# Zeobuilder is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>
#
# Contact information:
#
# Supervisors
#
# Prof. Dr. Michel Waroquier and Prof. Dr. Ir. Veronique Van Speybroeck
#
# Center for Molecular Modeling
# Ghent University
# Proeftuinstraat 86, B-9000 GENT - BELGIUM
# Tel: +32 9 264 65 59
# Fax: +32 9 264 65 60
# Email: Michel.Waroquier@UGent.be
# Email: Veronique.VanSpeybroeck@UGent.be
#
# Author
#
# Ir. Toon Verstraelen
# Center for Molecular Modeling
# Ghent University
# Proeftuinstraat 86, B-9000 GENT - BELGIUM
# Tel: +32 9 264 65 56
# Email: Toon.Verstraelen@UGent.be
#
# --


import os, sys

class Context(object):
    def __init__(self):
        self.title = "Zeobuilder"
        self.version = "0.1.0"
        self.user_dir = os.path.expanduser("~/.zeobuilder")
        if not os.path.isdir(self.user_dir):
            os.mkdir(self.user_dir)
        self.share_dirs = [
            os.path.join(sys.prefix, "share/zeobuilder"),
            self.user_dir
        ]
        self.config_filename = os.path.join(self.user_dir, "settings")

    def get_share_file(self, filename):
        for dir in self.share_dirs:
            result = os.path.join(dir, filename)
            if os.path.isfile(result):
                return result
        raise ValueError("No file '%s' found in the share directories." % filename)


context = Context()


