# Native lab archive

The archive replaces embedded official pages with native layouts at `#lab/professor`, `#lab/members`, `#lab/alumni`, `#lab/publications`, `#lab/conferences`, `#lab/awards`, and `#lab/works`.

## Synchronization

Run `python -m pip install beautifulsoup4`, then `python pnu-fashion-lab/scripts/sync_archive.py` from the repository root. The script fetches every official list page, verifies advertised totals and unique publication identifiers, and retrieves work images and publication attachment links. It writes `archive-data.json` only after every category succeeds. Do not publish a partial result. Review the data diff before committing; preserve source wording, including apparent inconsistencies in official dates.

Professor details in `archive.js` must cover EVERY factual statement on the official biography, arranged into education/appointments, doctoral research/interests, design/exhibitions, teaching and contact sections. Do not shorten it into a selective summary. If `professor.sourceDigest` changes, reread the complete official biography and update all three language versions, preserving names, dates, institutions, roles, dissertation terminology and exhibition venues. The source office room is 310; the homepage's lab room is intentionally independent. Missing fields stay missing; do not invent names, roles, translations or awards.

After changes, check JavaScript syntax, count/uniqueness validation, category links, search/year filters, work image navigation, close/back return position, and mobile wrapping. Keep original links explicitly labelled as sources. PDFs and external publication links may open separately; no official HTML pages are embedded.

## Design references inspected

- https://styles.refero.design/style/dc541737-8bf2-4b31-b729-0352f696e82f : editorial reading order, restrained borders and readable line height.
- https://www.cta.gallery/cta/hello-world-studio : clear action hierarchy and compact action placement.

Implementation is original. Preserve the existing lilac, lime, warm-white and ink palette; do not adopt reference branding. No third-party component code or paid assets were copied. Original work and professor images remain source-hosted.
