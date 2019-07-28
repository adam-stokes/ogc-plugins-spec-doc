import toml
import tempfile
import sh
import os
import datetime
import textwrap
import re
import yaml
from pathlib import Path
from ogc.spec import SpecPlugin, SpecConfigException, SpecProcessException
from ogc.state import app

__version__ = "0.0.1"
__author__ = "Adam Stokes"
__author_email__ = "adam.stokes@gmail.com"
__maintainer__ = "Adam Stokes"
__maintainer_email__ = "adam.stokes@gmail.com"
__description__ = (
    "ogc-plugins-spec-doc, an ogc plugin for building documentation from spec files"
)
__git_repo__ = "https://github.com/battlemidget/ogc-plugins-spec-doc"


class SpecDoc(SpecPlugin):
    friendly_name = "OGC Spec Doc Plugin"
    description = __description__

    options = [
        {
            "key": "file_glob",
            "required": True,
            "description": "Simple file globs, ie '**/*spec.toml",
        },
        {
            "key": "top_level_dir",
            "required": True,
            "description": "Where to start the top down search for specs",
        },
    ]

    def _get_tomls(self):
        glob_pat = self.get_plugin_option('file_glob')
        top_level_dir = self.get_plugin_option('top_level_dir')
        for p in Path(top_level_dir).glob(glob_pat):
            yield p

    def conflicts(self):
        top_level_dir = self.get_plugin_option('top_level_dir')
        if not (Path(top_level_dir) / 'mkdocs.yml').exists():
            raise SpecProcessException(f"Must have a `mkdocs.yml` file created in {top_level_dir} in order for OGC to generate mkdoc config and pages.")

    def process(self):
        top_level_dir = self.get_plugin_option('top_level_dir')
        docs_dir = Path(top_level_dir) / 'docs'

        for spec in self._get_tomls():
            app.log.info(f" -- Reading {spec}")
            page_obj = []
            spec_toml = toml.loads(spec.read_text(encoding="utf8"))
            if 'Info' not in spec_toml:
                app.log.debug(f"No `Info` metadata found in {spec}")
                continue
            doc = spec_toml['Info']
            if 'mkdocs' not in doc:
                app.log.debug(f"No `mkdocs` metadata found in {spec}")
                continue
            if 'destination' not in doc['mkdocs']:
                raise SpecProcessException(f"Can not generate doc without a `destination` in {spec}")

            page_obj.append(f"# {doc['name']}\n\n")
            if 'description' in doc:
                page_obj.append(f"{doc['description']}\n\n")
            if 'long_description' in doc:
                page_obj.append(f"{doc['long_description']}\n\n")

            # Process any top level plugin definitions
            if any(key != 'Info' for key in spec_toml.keys()):
                page_obj.append("## Steps\n")
            for key in spec_toml.keys():
                if key == 'Info':
                    continue
                if key == 'Runner':
                    # We'll process any runner information next
                    continue
                plug_obj = spec_toml.get(key)
                if 'name' in plug_obj:
                    page_obj.append(f"### {plug_obj['name']}\n\n")
                if 'description' in plug_obj:
                    page_obj.append(f"{plug_obj['description']}\n\n")
                if 'long_description' in plug_obj:
                    page_obj.append(f"{plug_obj['long_description']}\n\n")

            # Process runner objects
            if 'Runner' in spec_toml.keys():
                runner_objs = spec_toml.get('Runner')
                for runner in runner_objs:
                    if 'name' in runner:
                        page_obj.append(f"### {runner['name']}\n\n")
                    if 'description' in runner:
                        page_obj.append(f"{runner['description']}\n\n")
                    if 'long_description' in runner:
                        page_obj.append(f"{runner['long_description']}\n\n")

            dst = Path(doc['mkdocs']['destination'])
            out_path_dir = docs_dir  / dst.parent
            out_path_file = out_path_dir / dst.parts[-1]
            os.makedirs(str(out_path_dir), exist_ok=True)
            out_path_file.write_text("".join(page_obj))

__class_plugin_obj__ = SpecDoc
