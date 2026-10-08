# Your GitHub profile dashboard

## Publish in about five minutes

1. Create a **public repository named `bran-dot-flake`** in your `bran-dot-flake` account. This is a separate repo from your portfolio website. Use `main` as the default branch.
2. Extract this ZIP. Upload the **contents** of `profile-dashboard`, not the enclosing folder, to the repo root. Include the hidden `.github` folder. The workflow belongs at `.github/workflows/dashboard.yml`.
3. Open **Actions → Refresh profile dashboard → Run workflow**. If GitHub asks you to enable Actions, do so. The workflow requests write access to this repo and uses GitHub's automatically provided token; no personal token or secret is needed.
4. Visit `https://github.com/bran-dot-flake`. The README appears above pinned repos. Pin your best projects using GitHub's profile controls; README code cannot set pins.

If using Git locally, run these from the extracted `profile-dashboard` directory after creating the empty GitHub repo:

```sh
git init -b main
git add .
git commit -m "Add profile dashboard"
git remote add origin https://github.com/bran-dot-flake/bran-dot-flake.git
git push -u origin main
```

Do not initialize the remote with a README if following those commands. If the profile repo already exists, copy these files into its existing checkout and commit normally; preserve any existing material you want to keep.

## What refreshes

| Element | Source | Maintenance |
| --- | --- | --- |
| Lines of code and language bars | cloc scan of default-branch public originals | Daily |
| Files | git ls-files, including images and documentation | Daily |
| Commits and sparkline | GitHub default-branch commit API, last 90 days | Daily |
| Specialization network | Repository topic tags mapped in config.json | Daily |
| Project dates and stars | GitHub repository metadata | Daily |
| Skills and project descriptions | config.json and README template in scripts/update.py | Curated |

The current included snapshot is real collected data, not mock numbers. See data/metrics.json for totals and data/source.json for evidence. The dashboard excludes forks, archived repos, and its own repo. Newly created public repositories automatically enter the next scan. The workflow runs at 10:23 UTC daily; schedules can be delayed by GitHub.

### Accurate interpretation

- LOC excludes blanks/comments according to cloc, documentation, JSON/YAML/XML/SVG and other listed data/config formats, and common vendor/build directories. HTML/CSS count as code. The counter is not proof that every line was personally authored. It cannot identify all copied/generated code; extend the exclusions if needed.
- Tracked files include docs, screenshots and binary files, so they have a broader scope than LOC.
- Commits are across all authors on the included repositories' default branches, with identifiable bots removed and commit hashes deduplicated. This is not the profile contribution total. Thirteen weekly buckets cover 90 days; the oldest is partial.
- Topic counts overlap: a repository can support both DFIR and automation. A zero means no matching topic, not no experience. No inferred mastery percentages.
- A failed fetch/scan fails the run, preserving the previously committed dashboard. At very large repo sizes, adjust the workflow timeout or exclude asset-heavy repos.
- GitHub may disable schedules after 60 days of repository inactivity. Re-enable in Actions if needed.

## Quick edits

- **Choose featured projects:** edit `featured` in `config.json`. Keep four entries, short titles and two short description lines. Their dates/stars update automatically.
- **Skills:** edit the supported Skill Icons IDs in `skills`. Also update the corresponding alt text in the README template if changing tools. Icons are requested from skillicons.dev; all core charts are local SVGs.
- **Network:** add aliases under `specializations[].topics`. Current matching uses your real topics: `dfir`, `incident-response`, `splunk`, `threat-hunting`, `soar`, `python`, `azure`, `sentinel`, `wireshark`, `packet-analysis`, etc. Keep five categories for the included layout.
- **Intro:** edit the README template in `scripts/update.py`; direct README edits will be overwritten on refresh.
- **Less motion:** remove the `class="flow"` assignments in the renderer. Reduced-motion preferences are already respected where supported.
- **Website profile stats:** this edition doesn't scrape HTB/KC7/LetsDefend. It avoids stale or unauthenticated counters. You can later adapt your existing website updater; retain each source's last successful timestamp and handle failures separately.

## Preview and limitations

`preview.html` previews the composition locally; `preview.png` is a static composition preview, not a screenshot of a published GitHub profile. They are review files and do not refresh daily. The GitHub README uses normal Markdown, linked SVG images, an icon strip, and a collapsed methodology section. It does not require Pages, JavaScript, custom CSS in Markdown, or a hosted dashboard. Animation lives inside the SVG; clients that disable SVG animation still get the complete static graphic. Embedded SVGs aren't interactive: click the featured cards for projects, and use the All repositories link to explore. No hover-only information.

On smaller screens, GitHub scales the main 900px graphic. Featured images scale in two columns. The image has a comprehensive alt description, and the collapsed methodology is accessible as text. The compact graphic is about 438px high at full width; the complete README is longer once the skills and featured repos are included. Native pinned repos remain below it.

## Local regeneration

Install Git, Python 3.12+ and cloc, then run:

```sh
python scripts/update.py
```

`GH_TOKEN` is optional locally but recommended to avoid GitHub API rate limits. Never commit tokens. For layout-only changes using the existing snapshot:

```sh
python scripts/update.py --render-only
```

## References

- https://docs.github.com/en/account-and-profile/how-tos/profile-customization/managing-your-profile-readme
- https://docs.github.com/en/actions/how-tos/manage-workflow-runs/disable-and-enable-workflows
- https://github.com/AlDanial/cloc
- https://skillicons.dev
