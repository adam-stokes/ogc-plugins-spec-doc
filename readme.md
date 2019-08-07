[![Build Status](https://travis-ci.org/battlemidget/ogc-plugins-spec-doc.svg?branch=master)](https://travis-ci.org/battlemidget/ogc-plugins-spec-doc)

# ogc-plugins-spec-doc

generate documentation from spec files

# usage

In a ogc spec, place the following:

```yaml
plan:
  - specdoc:
    file-glob: **/*spec.yml
    top-level-dir: specs
```

In order for documentation to be generated for a spec the following is required:

```yaml
meta:
  name: Name of spec
  description: Description of spec
  long-description: |
    # Longer markdown supported text
```

These are the minimum requirements for the spec to be processed into documentation.

### see `ogc spec-doc specdoc` for more information.
