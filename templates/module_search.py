import glob
import imp
import logging
import os
import re

class ModuleSearch(object):
    def _load_single_module(self, f):
        return imp.load_source(f[:-3], f)

    def _load_modules(self):
        return [self._load_single_module(x) for x in self.modules]

    def _try_match_url(self, link, matchingURL):
        return True if re.match(matchingURL, link) is not None else False

    def _try_match_module_section(self, link, section):
        urls = section['urls']
        matches = [section['function'] for x in urls
                    if self._try_match_url(link, x) is not False]
        return True if len(matches) > 0 else False

    def _try_match_module(self, link, module):
        sections = module.matching_urls
        return [x['function'] for x in sections
                if self._try_match_module_section(link, x) is not False]
