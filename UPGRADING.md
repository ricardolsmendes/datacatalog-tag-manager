# Beta Version Migration Guide

The beta version of `datacatalog-tag-manager`, based on the current state of the `master` branch,
depends on `google-cloud-datacatalog` version `2.0.0+`. Upgrading `google-cloud-datacatalog` is
expected to be the only required change to use the beta version of this library.

If you experience issues or have questions, please file an [issue][2].

# 2.1.x Migration Guide

The 2.1 release of `datacatalog-tag-manager` adds support for tagging [Custom Entries][1]. Existing
CSV input files written for earlier versions of this library will likely require updates to use
this version. This document describes the changes that have been made, and what you need to do to
update your usage.

If you experience issues or have questions, please file an [issue][2].

## Supported CSV Schema

> **WARNING**: Breaking change!

The old column `linked_resource` was renamed to `linked_resource OR entry_name`, and from now it
accepts the full name of the BigQuery or PubSub asset the Entry refers to, or an Entry name if you
intend to tag [Custom Entries][1].

[1]: https://cloud.google.com/data-catalog/docs/how-to/custom-entries
[2]: https://github.com/ricardolsmendes/datacatalog-tag-manager/issues
