# Baseline checks in the Git distribution

The [frozen SHA-256 manifest](baseline_sha256.csv) is unchanged. In the public checkout, the audit checks the **142** retained baseline members against that same manifest. The **24** other historical members consist of 21 runtime bytecode files and the older `README.md`, `README.zh-CN.md` and `pytest.ini`. The complete **166** members remain available in the local frozen Stage 7 package.

From `Week7Remake`, run the public check with `python -B week7/audit/check_preservation.py`. For the full check, add `--archive-root <absolute path to the archived LC1-main>`. Stage 5/6 record the scope used by the source preflight. Reproducing the frozen package also requires inspecting the checks and references in the original research archive.
