# Notes

## Merge resolution

I merged `feature/de-locale` into `feature/rajat-locale-qa` and resolved the
conflict in `locales/en.json` from the command line.

What I kept:

- `nav.support` from `main`, because it was already added after the German branch
  diverged.
- `nav.help` from `feature/de-locale`, because it is a distinct source string and
  does not conflict structurally with `nav.support`.
- `battery.status` from `main`: `Battery: {percent}%`. This looked like the newer
  house style for the English source.
- `footer.copyright` from `main`, because `Lenovo Group Limited` is a more specific
  legal name and looks like the newer product/legal update.

What I deliberately discarded:

- `Battery level: {percent}%` from the German branch, in favor of the shorter main
  wording.
- `Copyright {year} Lenovo. All rights reserved.` from the German branch, in favor
  of the main branch's newer legal wording.

Product question I would ask:

- Should `nav.help` and `nav.support` both exist in the product navigation, or was
  one meant to replace the other? I kept both because they are distinct keys and
  dropping either one would be a product decision rather than a technical cleanup.

After resolving, I confirmed `locales/en.json` is valid JSON and reran the
validator. The German file is now included and has expected issues for missing
keys and the `{prozent}` placeholder mismatch.

## CI behavior

I made locale validation failures fail the Jenkins build instead of marking it
unstable. My reasoning is that missing keys and placeholder mismatches can cause
user-visible broken UI or runtime formatting bugs, so they should block a release.

The Jenkins pipeline captures the validator exit code, archives
`reports/locale-report.txt`, and then fails the build if validation failed. This
keeps the report available even on failed builds.

## Unfinished work

Nothing is intentionally unfinished.

I did not run a real Jenkins container in this environment. I verified the local
scripts directly and wrote the `Jenkinsfile` so it can be validated or run in the
container flow described in the assignment.

## AI tools used

I used ChatGPT/Codex to help implement the validator, shell wrapper, Jenkinsfile,
merge resolution, and notes.

Corrections and decisions I made while reviewing the output:

- The outer setup script said Python 3.9 was supported, but used
  `Path.write_text(newline=...)`, which fails on the local Python 3.9.6. I patched
  only the exercise generator so the repo could be created.
- I adjusted the shell wrapper to prefer `python3` and fall back to `python`,
  because this machine has `python3` but not `python` on PATH.
- I changed the Jenkins pipeline so the report is archived before the build is
  failed. A plain failing `sh` step would skip the later Report stage.
- I reviewed the merge conflict manually and chose which English source strings to
  keep rather than accepting either side wholesale.
