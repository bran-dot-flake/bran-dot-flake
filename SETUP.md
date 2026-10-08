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
| Skills and tool badges | config.json and scripts/update.py | Curated |

The current included snapshot is real collected data, not mock numbers. See data/metrics.json for totals and data/source.json for evidence. The dashboard excludes forks, archived repos, and its own repo. Newly created public repositories automatically enter the next scan. The workflow runs at 10:23 UTC daily; schedules can be delayed by GitHub.

### Accurate interpretation

- LOC excludes blanks/comments according to cloc, documentation, JSON/YAML/XML/SVG and other listed data/config formats, and common vendor/build directories. HTML/CSS count as code. The counter is not proof that every line was personally authored. It cannot identify all copied/generated code; extend the exclusions if needed.
- Tracked files include docs, screenshots and binary files, so they have a broader scope than LOC.
- Commits are across all authors on the included repositories' default branches, with identifiable bots removed and commit hashes deduplicated. This is not the profile contribution total. Thirteen weekly buckets cover 90 days; the oldest is partial.
- Topic counts overlap: a repository can support both DFIR and automation. A zero means no matching topic, not no experience. No inferred mastery percentages.
- A failed fetch/scan fails the run, preserving the previously committed dashboard. At very large repo sizes, adjust the workflow timeout or exclude asset-heavy repos.
- GitHub may disable schedules after 60 days of repository inactivity. Re-enable in Actions if needed.

## Quick edits

- **Skills:** change the Skill Icons IDs in config.json; update the matching alt text in scripts/update.py.
- **Tool badges:** edit the `tools` list in scripts/update.py.
- **Network:** update the five categories and topic aliases in config.json. Topics measure repository coverage, not proficiency.
- **Colors:** edit the SVG renderer in scripts/update.py.
- **Less motion:** remove the `sweep` and `flow` classes. Reduced-motion preferences disable CSS animations where supported. The network retains its subtle moving connections.

## Layout and motion

The profile contains the summary dashboard, skill icons, and tool badges. The name banner and the marked intro, explanatory notes and featured-project section were removed. GitHub's native pinned repos remain managed separately in your profile.

The weekly activity line has a repeating highlight over actual weekly commit counts; animation is decorative, not live incoming events. Stat cards use distinct tinted blocks. SVG images work without JavaScript or Pages; clients that disable animation retain the full static layout.

`preview.html` shows the animated composition locally. `preview.png` is a static composition preview, not a screenshot of a published profile. These preview files do not update daily. The README and SVGs do. The dashboard image URL gets a new version value on each successful refresh so GitHub requests the latest SVG.

The code scan walks each fresh clone's checkout directly, excluding .git and common build/vendor folders. It aborts if a repository has tracked source files but the counter returns no code. The included data snapshot comes from a previous successful scan. Running Actions collects fresh data.

## If GitHub shows stale or zero metrics

1. Confirm the root `README.md` uses `assets/dashboard.svg?v=...`, and that `assets/dashboard.svg` in the **same repository root** shows the latest value in its source. If it does, reload the profile. The version changes after each successful workflow run.
2. Open **Actions → Refresh profile dashboard** and run it manually. A successful run commits updated `README.md`, `assets/dashboard.svg` and `data/source.json`. If it fails, read the first failed step in that run; the prior dashboard stays intact.
3. If the root README refers to `assets/dashboard.svg` but the new files are under `profile-dashboard/assets`, upload the contents of `profile-dashboard` to the repository root. GitHub does not unpack the ZIP for you.
4. If the workflow never appears, confirm `.github/workflows/dashboard.yml` is at the root and the repo uses `main` as its default branch. The old unreferenced `assets/header.svg` can be deleted later in the web interface.

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
