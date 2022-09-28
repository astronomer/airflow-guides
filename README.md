# Airflow Guides

## This repo is currently frozen
**Note:** Our Airflow guides will be moving to a new home shortly. Until that migration is complete, this repo is frozen to any changes. If you need to submit an issue for guides updates/errors, please do so in our docs repo: https://github.com/astronomer/docs/issues. If you have questions about what to do for now, please reach out to Kenten (kenten@astronomer.io).

## How to use this repo for contributions to www.astronomer.io/guides

The Astronomer website uses the `/guides` directory in this repo as a CMS for it's "Airflow Guides" content. To add a new guide to that content, a `.md` file will need to be created inside the `/guides` repo with appropriate GitHub markdown formatting and some standardized front-matter. Until the Astronomer website is rebuilt, no changes to this repo will be reflected there. Also, only content from the `/guides` directory will be parsed and used - no other files or directories will affect the site.

*Note: ONLY `.md` files may be added to the `/guides` directory - no subdirectories or other file-types may be used. The rest of the repo may include files and directories of any kind.*

## Creating or updating a guide
1. Clone the repo, and make a branch for your work
2. If updating an existing guide, find the `.md` file for the guide in question and make the changes. Then skip to step 5. If creating a new guide, move to the next step
3. Create a new `.md` file in the `/guides` directory
4. Copy the block that contains title, description, date, slug, and tags from another guide and paste them at the top of your new file. Ensure the formatting stays the same. Update the information for your new guide.

    **Note:** the date field will determine where the guide shows up on the guides site. If you want your guide to have the 'New' banner while it is the most recent, ensure the date is accurate

    **Another note:** the slug **must** match the filename, and should use `hyphen-separated-case`. For example, you might have `guide-123.md` which would have `guide-123` as its slug

5. Add your content to your guide file using markdown formatting
6. If your guide has images, add them to the web-assets repo under `main/guides/your-guide-folder`. Reference them in your guide `.md` file with

    `![Image title](<https://assets2.astronomer.io/main/guides/your-guide-folder/your_image.png>)`

7. Ensure that all supporting code for your guide is hosted on the [Astronomer Registry](https://registry.astronomer.io/) or in a public GitHub repo, and link to it from the guide.
8. Optional: run the markdown lint and spellcheck locally. This will save you time if there are any issues that will be caught by the CI/CD pipeline. For more instructions on this, see the CI/CD Pipeline section below.
9. Push your branch to the repo and create a pull request and add reviewers. If you aren't sure who to add, add @kentdanas. It is a good idea to have someone from the docs team review for grammar and readability in addition to a content review.
10. Once your PR has been approved, merge it into the `main` branch.

## Submitting a guide issue
You can request a change to the Airflow Guides site either in the form of a new guide or a change to an existing guide by submitting an issue in this repo. Please be descriptive in the issue, and use one of the relevant labels:

 - `New Guide`: for new guides
 - `Guide Enhancement`: for additions to existing guides
 - `Guide Error/Update`: for content updates to existing guides including to fix technical errors or update content based on new releases
 - `Guide Typo/Formatting`: for fixes for typos, grammar, formatting, etc.

If you are unsure of who to assign the issue to, you can leave it unassigned. If you are planning on creating a new guide yourself, feel free to create an issue and assign yourself so we know who is working on it.

## CI/CD Pipeline

A GitHub Actions CI/CD Pipeline is used to verify each markdown file is free from formatting errors, typos, and broken links. To see logs from this pipeline go to `Actions` section of the GitHub repo.

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

The pipeline features a [spell checker](https://github.com/crate-ci/typos) to ensure that there are no typos in our guides.

It is recommended that you run a spell checker locally before committing to save time fixing CI errors. VS Code has a good [spell check integration](https://marketplace.visualstudio.com/items?itemName=streetsidesoftware.code-spell-checker), or you can use any other options. 

### Link Check

The last check in the pipeline in the [Markdown Link Checker](https://github.com/tcort/markdown-link-check) which checks for broken links. This check may fail whether you have dead links or not because of "too many request" status code. If you believe this has happened just run the pipeline again.

If the check is failing use the `GitHub Actions` logs to see what links are dead. Links from old guides may have broke since that last time the pipeline has run. Please fix these links to keep our site up to date.

> Hint: search for `dead link` in the logs to find all the dead links that need to be fixed.

