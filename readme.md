[![Build Status](https://travis-ci.org/battlemidget/ogc-plugins-spec-doc.svg?branch=master)](https://travis-ci.org/battlemidget/ogc-plugins-spec-doc)

# ogc-plugins-spec-doc

generate documentation from spec files

# usage

In a ogc spec, place the following:

```toml
[SpecDoc]
spec_file_naming = "^(spec\.toml)"
```

In order for documentation to be generated for a spec the following is required:

```toml
[Info]
name = "Name of spec"
description = "Description of spec"
long_description = """
# Longer markdown supported text
"""

These are the minimum requirements for the spec to be processed into documentation.

### see `ogc spec-doc SpecDoc` for more information.
