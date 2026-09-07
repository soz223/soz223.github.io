# Songlin Zhao — research portfolio

Public website: https://soz223.github.io/

An English research portfolio covering multimodal foundation models, medical imaging, neuroimaging and research agents. The site uses static HTML, CSS and JavaScript with a small Python generator and no build dependencies.

## Update content

- Edit `data/content.json` for projects, publications and the introduction.
- Edit `scripts/build.py` for the other page content and navigation.
- Run `python scripts/build.py` to generate and validate the 15 pages.
- `_site/` contains the deployment output and is excluded from version control.
- The earlier homepage is preserved at `archive/p-mimicgraphrag.html`.

## Public activity and AI collaboration

`scripts/update_activity.py` uses GitHub's REST API to inspect commits authored by `soz223` on the default branches of owned public, non-fork repositories over the last 365 days. It follows pagination and deduplicates commits by SHA. It does not read private repositories, conversation logs, source code or local workspaces.

AI attribution comes from explicit AI trailers, recognized AI co-author identities, or the separately documented records in `data/ai-evidence.json`. A commit without evidence stays unattributed. Counts do not represent tokens, time spent, productivity or all historical AI activity.

The GitHub Actions workflow refreshes the snapshot daily, validates the site and deploys the public Pages artifact. API failures fail the workflow instead of replacing counts with invented zeroes. The last successful deployment remains available.

The interactive dashboard supports date ranges, tool filters, animation pause and individual commit inspection. The README images share the same snapshot.

## Design

The broad idea of linked profile sections and an AI collaboration record was inspired by [Wenyu Chiou's public profile](https://github.com/WenyuChiou). Content, layout, diagrams and implementation here are tailored to Songlin Zhao. Institutional artwork attribution is in `THIRD_PARTY_NOTICES.md`.
