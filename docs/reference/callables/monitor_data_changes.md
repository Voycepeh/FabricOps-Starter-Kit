# monitor_data_changes

**Module:** `drift`  
**Classification:** Essential

## Purpose

Profile data, compare against the approved baseline, and return a drift guardrail result.

## Function manifest

- Fully qualified function name: `fabricops_kit.drift.monitor_data_changes`
- Short name: `monitor_data_changes`
- Module: `drift`
- Classification: Essential
- Related module: `drift`
- Source file path: `src/fabricops_kit/drift.py`
- Source reference: <a href="../../api/modules/drift/#monitor_data_changes">Module source anchor</a>
- Inbound references count: 0
- Outbound references count: 8

## Outbound references
- <a href="../profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>
- <a href="../internal/drift/_as_monitor_only_result/"><code>fabricops_kit.drift._as_monitor_only_result</code></a>
- <a href="../internal/drift/_check_profile_drift/"><code>fabricops_kit.drift._check_profile_drift</code></a>
- <a href="../internal/drift/_data_change_preset_config/"><code>fabricops_kit.drift._data_change_preset_config</code></a>
- <a href="../internal/drift/_extract_categorical_distribution_categories/"><code>fabricops_kit.drift._extract_categorical_distribution_categories</code></a>
- <a href="../internal/drift/_extract_numeric_distribution_bin_edges/"><code>fabricops_kit.drift._extract_numeric_distribution_bin_edges</code></a>
- <a href="../internal/drift/_load_latest_profile/"><code>fabricops_kit.drift._load_latest_profile</code></a>
- <a href="../internal/drift/_normalize_profile/"><code>fabricops_kit.drift._normalize_profile</code></a>
