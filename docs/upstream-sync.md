# Upstream synchronization

The scheduled sync workflow fetches the latest `alltheplaces/alltheplaces` default branch and opens a pull request only when the pinned submodule commit changes. It never merges the update automatically.

Review the upstream diff, confirm every allowlisted spider is still registered, run the Korea tests, and inspect crawl output before merging. Fixes useful outside Korea belong upstream; overlay changes should remain limited to selection, validation, publishing, and post-processing.

