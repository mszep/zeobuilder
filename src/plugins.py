#
# This file is part of Zeobuilder.
#
# Zeobuilder is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# --


from zeobuilder import context

import os, imp


class PluginCategory(object):
    def __init__(self, singular, plural, init):
        self.singular = singular
        self.plural = plural
        self.init = init


def init_nodes(nodes):
    from zeobuilder.nodes import init_nodes
    init_nodes(nodes)
    from zeobuilder.expressions import add_locals
    add_locals(nodes)

def init_actions(actions):
    from zeobuilder.actions.composed import init_actions
    init_actions(actions)

def init_load_filters(load_filters):
    from zeobuilder.filters import init_load_filters
    init_load_filters(load_filters)

def init_dump_filters(dump_filters):
    from zeobuilder.filters import init_dump_filters
    init_dump_filters(dump_filters)

def init_cache_plugins(cache_plugins):
    from zeobuilder.selection_cache import init_cache_plugins
    init_cache_plugins(cache_plugins)

def init_utility_functions(utility_functions):
    from zeobuilder.expressions import add_locals
    add_locals(utility_functions)


builtin_categories = [
    PluginCategory("plugin_category", "plugin_categories", None),
    PluginCategory("node", "nodes", init_nodes),
    PluginCategory("action", "actions", init_actions),
    PluginCategory("load_filter", "load_filters", init_load_filters),
    PluginCategory("dump_filter", "dump_filters", init_dump_filters),
    PluginCategory("interactive_group", "interactive_groups", None),
    PluginCategory("cache_plugin", "cache_plugins", init_cache_plugins),
    PluginCategory("utility_function", "utility_functions", init_utility_functions)
]



class PluginNotFoundError(Exception):
    def __init__(self, name):
        self.name = name
        Exception.__init__(self, "Plugin %s not found" % name)


class PluginsCollection(object):
    def __init__(self):
        self.module_descriptions = set([])
        for directory in context.share_dirs:
            self.find_modules(os.path.join(directory, "plugins"))
        #self.module_descriptions = list(sorted(self.module_descriptions))
        self.load_modules()
        self.load_plugins()

    def find_modules(self, directory):
        if not os.path.isdir(directory):
            return
        for filename in os.listdir(directory):
            fullname = os.path.join(directory, filename)
            if os.path.isdir(fullname) and not fullname.endswith(".skip"):
                self.find_modules(fullname)
            elif filename.endswith(".py"):
                self.module_descriptions.add((directory, filename[:-3]))

    def load_modules(self):
        self.modules = []
        for directory, name in self.module_descriptions:
            #print name, directory
            (f, pathname, description) = imp.find_module(name, [directory])
            try:
                self.modules.append(imp.load_module(name, f, pathname, description))
            finally:
                f.close()

    def load_plugins(self):
        for category in builtin_categories:
            self.load_category(category)

        for category in self.plugin_categories.itervalues():
            self.load_category(category)

        for category in builtin_categories:
            self.plugin_categories[category.plural] = category

    def load_category(self, category):
        d = {}

        #print category.plural
        for module in self.modules:
            #print "  %s.py" % module.__name__
            plugins = module.__dict__.get(category.plural)
            if plugins is not None:
                for id, plugin in plugins.iteritems():
                    #print "    %s" % id
                    assert id not in d, "A plugin with id '%s' is already loaded (%s)" % (id, name)
                    d[id] = plugin

        if category.init is not None:
            category.init(d)

        self.__dict__[category.plural] = d

        def get_plugin(name):
            plugin = d.get(name)
            if plugin is None:
                raise PluginNotFoundError(name)
            else:
                return plugin
        self.__dict__["get_%s" % category.singular] = get_plugin
