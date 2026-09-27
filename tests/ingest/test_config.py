"""Config loader: YAML inheritance + pydantic validation."""
from __future__ import annotations
from pathlib import Path
from anchor.ingest.config import load_config

def test_load_leopard_shark_deployment():
    ...

def test_load_bat_ray_deployment():
    ...

def test_trajectory_defaults_present_when_omitted():
    """A deployment whose YAML has no `trajectory:` block still gets defaults."""
    ...

def test_trajectory_block_parsed_from_species_yaml():
    """bat_ray.yaml carries an explicit trajectory block; it must parse."""
    ...

def test_trajectory_override_via_inheritance():
    ...

def test_load_white_shark_deployment():
    ...

def test_every_deployment_config_loads():
    """Every YAML under configs/deployments/ must validate without errors.

    Catches drift when the pydantic schema evolves and some deployment
    configs forget to update. Run before every batch of new W0 configs
    lands.
    """
    ...

def test_every_species_config_has_v2_fields():
    """Species YAMLs must carry the v2 fields (locomotion_mode, body_length_m_default).

    Deployment configs inherit from species, so missing a v2 field on a
    species YAML silently breaks any deployment using it.
    """
    ...

def _write_deployment(tmp_path: Path, species: str, **extra) -> Path:
    """Minimal deployment YAML inheriting from a species file."""
    ...

def test_strouhal_k_inherited_from_species(tmp_path):
    """The declared field must still pick up the species YAML value.

    The values are the 2026-07-10 stride-length audit ported from AXY+ on
    2026-09-04 (bat ray 0.25 -> 0.85, leopard shark 0.40 -> 0.75, white shark
    0.40 -> 0.65; thresher unaudited, stays 0.40). See
    docs/strouhal_calibration.md. Asserting all four here is what makes a
    silent drift back to the pre-audit constants a test failure.
    """
    ...

def test_strouhal_k_deployment_override_wins(tmp_path):
    ...

def test_strouhal_k_defaults_to_module_constant(tmp_path):
    """A config with no strouhal_k anywhere falls back to DEFAULT_STROUHAL_K."""
    ...

def test_strouhal_k_out_of_range_rejected(tmp_path):
    """A literal 0 (or any out-of-band K) must fail validation, not silently
    fall back to the default — the pre-QW8 `getattr(...) or DEFAULT` did."""
    ...

def test_every_deployment_has_valid_strouhal_k():
    """All seven deployment configs still load and carry an in-range K."""
    ...

def test_all_seven_deployment_configs_load_under_closed_schema():
    """The schema is `extra="forbid"`; every shipped deployment must still load.

    This is the regression guard for the migration: any future YAML key added
    without a matching field declaration fails here rather than being silently
    dropped on the floor.
    """
    ...

def test_unknown_top_level_key_is_rejected(tmp_path):
    """A misspelt key must fail loudly instead of being absorbed by extra=allow."""
    ...

def test_unknown_nested_key_is_rejected(tmp_path):
    """Nested models are closed too, so `trajectory:` typos cannot hide."""
    ...

def test_clip_round_trip_and_validation(tmp_path):
    """`clip` is a non-negative, strictly increasing [start, end] sample pair."""
    ...

def test_release_and_recovery_round_trip(tmp_path):
    """Endpoints parse into a typed model, with sigma_m defaulting to 10 m."""
    ...

def test_bat_ray_deployment_carries_its_endpoints_and_length_source():
    """BR_260318_S3's release/recovery are versioned, not shell history."""
    ...

def test_bat_ray_measured_length_reaches_the_speed_model():
    """The promoted length must resolve to 0.465 m, not the 0.9 m default.

    `animal.length_cm` is only a config field; what matters is the metre value
    the speed model `U = K * L * TBF` actually multiplies. Both resolvers —
    `anchor.pipeline` and `anchor.trajectory.run_deployment` — must return the
    measured length and report its provenance, or the section 10 arm silently
    becomes the section 9 arm.
    """
    ...

def test_every_shipped_species_declares_its_own_strouhal_k():
    """DEFAULT_STROUHAL_K = 0.4 is documented as pre-audit and unreachable.

    That comment is only true while every species YAML sets `strouhal_k`; a new
    species config that omits the key would silently pick up the unaudited
    fallback. This is the test that keeps the comment honest.
    """
    ...

def test_bathymetry_mode_fields_declared_with_filter_defaults(tmp_path):
    """Defaults must match FilterConfig's, so declaring them changes nothing."""
    ...

def test_event_method_defaults_to_the_rule_the_pipeline_already_used():
    """The new field must be a declaration of current behaviour, not a change.

    ``pipeline.extract_events_for`` hard-coded ``"robust_scale"`` and the module
    constants before ``EventConfig`` could express them, so a YAML could not
    select the percentile rule and adding ``method:`` to one failed validation
    (``extra="forbid"``). The defaults below are what that hard-coded path did.
    """
    ...

def test_event_method_and_scale_factors_round_trip_from_yaml(tmp_path):
    """...and a YAML can now select the percentile rule and retune the factors."""
    ...

def test_smooth_sigma_that_does_not_match_the_sampling_rate_warns(tmp_path, caplog):
    """A sample-count copied between tags must not pass silently.

    ``gaussian_filter1d``'s sigma is in *samples*, so the bat ray's 1.66 at
    fs = 25 becomes a different filter on a 50 Hz tag; when the corner lands
    inside the species' own tail-beat band it caps reported tail-beat frequency
    and that propagates through ``U = K * L * TBF`` into every reconstructed
    metre. The loader cannot reject it — a deliberately narrower band is a valid
    choice — but it must say so.
    """
    ...

def test_shipped_configs_do_not_trip_the_smooth_sigma_warning(caplog):
    """Every deployment's smooth_sigma must already match its own rate."""
    ...
LS_CAST_LON, LS_CAST_LAT = (-121.73649, 36.81924)

def _ls(name: str):
    ...

def test_every_ls_deployment_carries_the_metadata_cast_position():
    """G-k cannot be profiled at all while the LS configs have no release anchor.

    `sigma_m` is 80 rather than a handheld fix's 10 because this coordinate is
    one site constant standing in for 22 casts across 13 months; 82.6 m is its
    measured distance from the independently recorded release `BR_260318_S3`
    actually uses, and that is the only calibration of it the repository has.
    """
    ...

def test_no_leopard_shark_has_a_second_positional_boundary_condition():
    """The design's central structural claim, as an executable invariant.

    Neither metadata workbook has a recovery-position column, and nothing in
    `data/raw/` or `docs/` holds a recovery coordinate, acoustic detection or
    receiver log for any LS deployment — only recovery *times*. If this ever
    starts failing, a second boundary condition has appeared and every "no
    positional claim is defensible" caveat in the design and in
    `docs/boundary_conditions.md` needs revisiting on purpose.
    """
    ...

def test_ls_timezone_is_utc_on_all_four():
    """Resolved from the tags' own power-off rows; see the YAML comments."""
    ...

def test_ls_260311_s1_declares_the_operator_clip_and_not_a_second_window():
    """The operator's own clip is the declaration; `deploy_window` is null.

    `AXY_DeploymentMetadata.xlsx` row `LS_260311` carries `clip start point`
    15000 and `clip point end` 635000. The 2026-09-04 first pass replaced a
    disjoint local-clock guess with TagDeployed 18:47 .. TagRecovered 10:07
    local converted at +7:00, i.e. `[01:47:00, 17:07:00]` — which retains
    8 h 22 min the operator had excluded, and which the accelerometer refutes:
    from 08:46:22 the tag is motionless for 8 h 20 min, to 17:06:22 — median
    within-minute per-axis sd 0.0066/0.0070/0.0070 g over 500 consecutive
    blocks, the sensor's noise floor, though across the whole span the attitude
    drifts ~0.07 g for a whole-span sd of 0.0124/0.0078/0.0108 g. The last
    11 min 49 s are motion again (per-axis sd to 0.73 g), starting 17:06:53,
    which is `TagRecovered 10:07` local + 7:00 to within 7 s: the collection is
    in the record, and the tag came off the animal 8 h 21 min before it.
    The clip is the honest statement of the on-animal span, and it is
    `clip:` rather than a rewritten `deploy_window` because the vendor
    `Timestamp` column is non-monotonic (936 backward steps of -58 s, one per
    1500 rows), so no wall-clock window selects a contiguous row range on this
    file. Setting both would clip twice. See `docs/boundary_conditions.md`.
    """
    ...

def test_ls_260311_s1_stays_on_the_vendor_export_not_the_cleaned_one():
    """The drop's third `_CLEAN` file is inspected and rejected, not ignored.

    `data/raw/data_drop_260502/LS26031101/LS260311_CLEAN.csv` is raw rows
    30250..635249 plus a constant per-axis offset (+0.46126, +0.13346,
    +0.02269 g; max deviation 5.55e-16 over all 605 000 rows x 3 axes, against
    an sd of 0.093/0.107/0.172 g at the offset 30000 its own `t` column
    implies). It corroborates the clip at ONE END only: its last row is 250
    samples (10.0 s) past the clip's last kept row 634999, but its first row is
    15 250 samples (10 min 10 s) after the clip start 15000. The start
    disagreement is what proves the two independent — a file made by applying
    [15000, 635000] would agree at both ends — and it means the clean export is
    evidence about the end boundary and nothing else. On those identical
    samples the vendor export's median |a| is 0.9690 raw and 0.8852 after
    `data/interim/calib/accel.json`; the clean export's is 1.2732 raw and
    1.2018 after — 27% above gravity before this repo's calibration touches it.
    It spans 6.72 h against 15.61 h, and the workbook's `file cleaned` column
    is blank for `LS_260311` (populated only for `BR_260318` and
    `LS_26041501`). All three checks reject it.
    """
    ...

def test_ls_260311_s1_length_comes_off_the_field_sheet():
    """98.5 cm TL, from the field-sheet photograph and the SP26 sheet alike.

    The design quotes 98.55, which is the AXY sheet's `TL(in) = 38.8` converted
    back; 98.5/2.54 = 38.78, so the inches are the derived number and the
    centimetres are what the tape recorded. Against the 1.2 m species default
    this is a 1.22x change in every reconstructed metre, since U = K * L * TBF.
    """
    ...

def test_every_ls_deployment_declares_a_length_and_its_source():
    ...

def test_include_depth_is_true_on_the_three_ls_tags_that_recorded_depth():
    """LS_260311_S1's raw CSV has no Depth column; the other three do.

    Its header is `...;magZ;Temp. (?C);Battery Voltage (V);Metadata`, which is
    why the drop names that tag's tail-beat export
    `NO_DEPTH_BAD_TEMP_LS260311_CLEAN_tb_5min.csv`. The species default is
    `false`, so the three `true`s are the deployment-level override and
    `LS_260311_S1`'s `false` is written out explicitly rather than inherited.
    """
    ...

def test_ls_250326_s2_stays_on_the_vendor_export_not_the_cleaned_one():
    """The design's Phase 0 repoint to `LS25032603_CLEAN.csv` is deliberately NOT taken.

    `calibration.accel` on this deployment is a raw-frame fit and is applied at
    ingest (`anchor/ingest/io.py`), so the file this points at decides whether
    calibration moves median |a| toward 1 g or away from it. On the vendor
    export it goes 0.9659 -> 0.9727; on the clean export 1.0382 -> 1.0547. The
    clean file also spans 6.75 h against 14.14 h and is unattested by the
    workbook's `file cleaned` column. See `docs/boundary_conditions.md`.
    """
    ...

def test_the_only_ls_clean_exports_configured_are_the_two_already_investigated():
    """A blind repoint onto a `_CLEAN` export must fail here, not silently ship.

    Pointing a config at a pre-conditioned export while a raw-frame calibration
    stays configured is the specific mistake this pass made and reverted. Two
    deployments legitimately read `_CLEAN` files: `LS_260415_S3` (attested by
    `AXY_DeploymentMetadata.xlsx`'s `file cleaned` column, and the pairing that
    lands nearest gravity) and `LS_250326_S8` (no vendor export exists, and its
    scaling is an open question recorded in `docs/boundary_conditions.md`).
    Any third one is a regression until the same check is done for it.
    """
    ...

def test_every_ls_raw_csv_path_is_shaped_like_the_others():
    """A repoint typo that drops a directory level must fail here, not at ingest."""
    ...

def test_the_bathymetry_switch_round_trips_through_a_deployment_yaml(tmp_path):
    """`enable_bathymetry_constraint` used to exist only as `--no-bathymetry`,
    so a deployment could not record that its depth likelihood was off and the
    run's `provenance.config_hash` could not see it (§13.7). It defaults to
    True, and a `trajectory:` block that sets it False is honoured by the
    loader alone, with no flag in play."""
    ...
