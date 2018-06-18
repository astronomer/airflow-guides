# Airflow Guides
A curated collection of guides to help with building specific ETL pipelines using Airflow.

These are stepwise instructions and use various repositories from the open-source [Airflow Plugins Organization](https://github.com/airflow-plugins).

---

## How to Update Astronomer's Website with Latest Guides
1) Commit your latest changes to `master` in this repo
2) Login to CircleCI and make sure you are following the `astronomerio/website` project
3) Choose the `dato-production` workflow under the `website` repo in Circle
4) Click the "rerun" button under the lastest _successful_ build
5) Choose the `Rerun from beginning` option from the dropdown

_Once Circle has successfully rebuilt the `website` repo, the lastest changes to Guides will be reflected on the site._
