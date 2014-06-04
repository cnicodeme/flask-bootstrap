# -*- coding:utf-8 -*-

from flask.templating import DispatchingJinjaLoader
from flask.globals import _request_ctx_stack

class ModifiedLoader(DispatchingJinjaLoader):
    """
    This modification first looks in the "template" folder of
    the blueprint if exists, then in the global template.

    It's way more logical and better :)
    """
    def _iter_loaders(self, template):
        bp = _request_ctx_stack.top.request.blueprint
        if bp is not None and bp in self.app.blueprints:
            loader = self.app.blueprints[bp].jinja_loader
            if loader is not None:
                yield loader, template

        loader = self.app.jinja_loader
        if loader is not None:
            yield loader, template