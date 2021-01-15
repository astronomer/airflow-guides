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
5) Store all images (inline and hero) in the `astronomer-cdn` bucket on s3 in the `/website/img/guides` directory, and reference them using  `https://assets.astronomer.io/website/img/guides/{filename}`
6) When the guide is finished, commit all changes to `master`
7) Rebuild the Astronomer website using the `How to deploy guides` steps below

## How to deploy guides

1. All changes pushed to airflow-guides will trigger a webhook to rebuild preview.astronomer.io.
2. To deploy to www.astronomer.io, publish a new release. We are starting at v1.0.0, using semantic versioning. This means, if you publish a new guide, bump the 2nd number eg `v1.1.0`. If you have to edit a guide, bump the 3rd number `v1.1.1`.

## CI/CD Pipeline

A GitHub Actions CI/CD Pipeline is used to verify each markdown file is free from formatting errors, spelling errors, and broken links. To see logs from this pipeline go to `Actions` section of the GitHub repo. Run the commands outlined below locally to fix errors before contributing posts.

Fix pipeline errors from all posts as old links may break and need to be replaced.

### Markdown Lint

The pipeline uses [markdownlint](https://github.com/DavidAnson/markdownlint) to ensure proper markdown formatting to ensure consistency. The rules followed by the linter can be found [here](https://github.com/DavidAnson/markdownlint/blob/main/doc/Rules.md). To run the linter locally run the following.

```shell
yarn lint
```

To include lines of code that break certain markdown rules follow the code example below.

```markdown
<!-- markdownlint-disable MD033 -->
<hr/>
```

### Spell Check

The pipeline features a [spell checker](https://github.com/lukeapage/node-markdown-spellcheck) to ensure that there are no misspelled words in our guides. You may want to run the spell checker locally in "interactive" mode to add proper nouns to the dictionary.

```shell
yarn spellcheck-interactive
```

Output should be similar too

```shell
Spelling - <your-guide>.md
 shows you the context of the speling mistake and gives you options
?   (Use arrow keys)
  Ignore
  Add to file ignores
  Add to dictionary - case insensitive
> Enter correct spelling
  spelling
  spieling
  spewing
  selling
  peeling
```

You can run locally in "report" mode too by running `yarn spellcheck`.

You can also add words directly to dictionary by adding the word to the [.spelling](https://github.com/astronomer/astro-blog/blob/main/.spelling) file located in this repo.

### Link Check

The last check in the pipeline in the [Markdown Link Checker](https://github.com/tcort/markdown-link-check) which checks for broken links. This check may fail wether you have dead links or not because of "too many request" status code. If you believe this has happened just run the pipeline again.

If the check is failing use the `GitHub Actions` logs to see what links are dead. Links from old guides may have broke since that last time the pipeline has run. Please fix these links to keep our site up to date.

> Hint: search for `dead link` in the logs to find all the dead links that need to be fixed.
