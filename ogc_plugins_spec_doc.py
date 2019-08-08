import tempfile
import sh
import os
import datetime
import textwrap
import re
import yaml
from pathlib import Path
from ogc.spec import SpecPlugin, SpecConfigException, SpecProcessException
from ogc.enums import SPEC_PHASES
from ogc.state import app

__version__ = "0.0.4"
__author__ = "Adam Stokes"
__author_email__ = "adam.stokes@gmail.com"
__maintainer__ = "Adam Stokes"
__maintainer_email__ = "adam.stokes@gmail.com"
__plugin_name__ = "ogc-plugins-spec-doc"
__description__ = (
    "ogc-plugins-spec-doc, an ogc plugin for building documentation from spec files"
)
__ci_status__ = """
[![Build Status](https://travis-ci.org/battlemidget/ogc-plugins-spec-doc.svg?branch=master)](https://travis-ci.org/battlemidget/ogc-plugins-spec-doc)
"""
__git_repo__ = "https://github.com/battlemidget/ogc-plugins-spec-doc"

__example__ = """
## Example 1

```yaml
plan:
  - spec-doc:
    file-glob: **/*spec.yml
    top-level-dir: specs
"""


class SpecDoc(SpecPlugin):
    friendly_name = "OGC Spec Doc Plugin"
    description = __description__

    options = [
        {
            "key": "file-glob",
            "required": True,
            "description": "Simple file globs, ie '**/*spec.yml",
        },
        {
            "key": "top-level-dir",
            "required": True,
            "description": "Where to start the top down search for specs",
        },
    ]

    def _get_specs(self):
        glob_pat = self.get_plugin_option("file-glob")
        top_level_dir = self.get_plugin_option("top-level-dir")
        for p in Path(top_level_dir).glob(glob_pat):
            yield p

    def conflicts(self):
        top_level_dir = self.get_plugin_option("top-level-dir")
        if not (Path(top_level_dir) / "mkdocs.yml").exists():
            raise SpecProcessException(
                f"Must have a `mkdocs.yml` file created in {top_level_dir} in order for OGC to generate mkdoc config and pages."
            )

    def process(self):
        top_level_dir = self.get_plugin_option("top-level-dir")
        docs_dir = Path(top_level_dir) / "docs"

        for spec in self._get_specs():
            app.log.info(f" -- Reading {spec}")
            page_obj = []
            spec_yml = yaml.safe_load(spec.read_text(encoding="utf8"))
            if "meta" not in spec_yml:
                app.log.debug(f"No `Info` metadata found in {spec}")
                continue
            doc = spec_yml["meta"]
            if "mkdocs" not in doc:
                app.log.debug(f"No `mkdocs` metadata found in {spec}")
                continue
            if "destination" not in doc["mkdocs"]:
                raise SpecProcessException(
                    f"Can not generate doc without a `destination` in {spec}"
                )

            page_obj.append(f"# {doc['name']}\n")
            if "description" in doc:
                page_obj.append(f"{doc['description']}\n")
            if "long-description" in doc:
                page_obj.append(f"{doc['long-description']}\n")

            # Process any phases
            for phase in spec_yml.keys():
                if phase not in SPEC_PHASES:
                    continue

                page_obj.append(f"## {phase.capitalize()} Phase\n")

                plugins = spec_yml[phase]
                for plug in plugins:
                    key, val = next(iter(plug.items()))
                    page_obj.append(f"### Plugin: **{key}**\n")
                    page_obj.append(f"{val['description']}\n")
                    if "long-description" in val:
                        page_obj.append(f"{val['long-description']}\n")

            if not isinstance(doc["mkdocs"]["destination"], list):
                doc["mkdocs"]["destination"] = [doc["mkdocs"]["destination"]]

            for dst in doc["mkdocs"]["destination"]:
                dst = Path(dst)
                app.log.info(f" -- Writing to {str(dst)}")
                out_path_dir = docs_dir / dst.parent
                out_path_file = out_path_dir / dst.parts[-1]
                os.makedirs(str(out_path_dir), exist_ok=True)
                out_path_file.write_text("".join(page_obj))


__class_plugin_obj__ = SpecDoc
