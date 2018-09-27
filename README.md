# Airflow Guides

A curated collection of guides to help with building specific ETL pipelines using Airflow.

These are stepwise instructions for using Astronomer and Apache Airflow, and use various repositories from the open-source [Airflow Plugins Organization](https://github.com/airflow-plugins).

---

## How to use this repo for contributions to www.astronomer.io/guides

The Astronomer website uses the `/guides` directory in this repo as a CMS for it's "Airflow Guides" content. To add a new guide to that content, a `.md` file will need to be created inside the `/guides` repo with appropriate GitHub markdown formatting and some standardized front-matter. Until the Astronomer website is rebuilt, no changes to this repo will be reflected there. Also, only content from the `/guides` directory will be parsed and used - no other files or directories will affect the site.

*Note: ONLY `.md` files may be added to the `/guides` directory - no subdirectories or other file-types may be used. The rest of the repo may include files and directories of any kind.*

## Building a new guide
1) Duplicate an existing guide inside the `/guides` directory
2) Update the file-name and front-matter, and pay close attention to formatting
3) Make sure to use `hyphen-seperated-case` when naming your file and declaring your slug
4) The filename and slug _must match_: i.e `astronomer-roadmap.md` and `slug: "astronomer-roadmap"`
5) Store all images (inline and hero) in the `astronomer-cdn` bucket on s3 in the `/website/img/guides` directory, and reference them using  `https://cdn.astronomer.io/website/img/guides/{filename}`
6) When the guide is finished, commit all changes to `master`
7) Rebuild the Astronomer website using the `How to deploy guides` steps below

## How to deploy guides

1. All changes pushed to airflow-guides will trigger a webhook to rebuild preview.astronomer.io.
2. To deploy to www.astronomer.io, publish a new release. We are starting at v1.0.0, using semantic versioning. This means, if you publish a new guide, bumb the 2nd number eg `v1.1.0`. If you have to edit a guide, bump the 3rd number `v1.1.1`.
