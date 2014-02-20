# -*- coding: utf-8 -*-
"""
    flask.ext.sass
    ~~~~~~~~~~~~~~

    A small Flask extension that makes it easy to use Sass (SCSS) with your
    Flask application.

    Code unabashedly adapted from https://github.com/weapp/flask-coffee2js

    :copyright: (c) 2012 by Ivan Miric.
    :license: MIT, see LICENSE for more details.
"""

import os
import os.path
import codecs

from scss import Scss

def _convert(src, dst):
    css = Scss()
    source = codecs.open(src, 'r', encoding='utf-8').read()
    output = css.compile(source)
    outfile = codecs.open(dst, 'w')
    outfile.write(output)
    outfile.close()

def sass(app, input_dir='assets/sass', output_dir='css', syntax='scss', force=False):
    if syntax not in ('scss', 'sass'):
        raise ValueError('syntax must be either "scss" or "sass"')
    if not hasattr(app, 'static_url_path'):
        app.logger.warning(DeprecationWarning('static_path is called '
                                    'static_url_path since Flask 0.7'))
        static_url_path = app.static_path
    else:
        static_url_path = app.static_url_path

    original_wd = os.getcwd()

    if not os.path.isdir(input_dir):
        input_dir = os.path.join(app.root_path, input_dir)

    def _sass(filepath):
        sassfile = "%s/%s.%s" % (input_dir, filepath, syntax)
        filename = "%s/%s.css" % (output_dir, filepath)
        cssfile = "%s%s/%s" % (app.root_path, static_url_path, filename)

        if os.path.isfile(sassfile) and (force or not os.path.isfile(cssfile) or \
           os.path.getmtime(sassfile) > os.path.getmtime(cssfile)):
            if os.path.isdir(input_dir):
                # TODO: Sigh... fix this. Needed so that pyScss can find all the assets.
                os.chdir(input_dir)
            _convert(sassfile, cssfile)
            app.logger.debug('Compiled %s into %s' % (sassfile, cssfile))
            if os.getcwd() != original_wd:
                os.chdir(original_wd)
            
        return app.send_static_file(filename)
        
    app.add_url_rule("%s/%s/<path:filepath>.css" %(static_url_path, output_dir), 'sass', _sass)
