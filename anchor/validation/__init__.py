"""Validation framework: pose, drone, paired-tag, online corpus, auto-clip.

This subpackage produces ground-truth label streams that feed the existing
``anchor.behavior.labels`` BORIS/VIA → window-projection pipeline. Each module
is independently usable; the CLI in ``anchor.cli`` exposes one subcommand
per module.

Paper §5 cross-species credibility chain:
    WS (CATS video + paired AXY) → calibrates HMM-state ↔ video agreement
    → licenses AXY-only HMM inference for LS, TS, BR (no onboard video)
    → BR online-corpus K calibration anchors swim-speed scaling
    → future MBA aquarium filming closes the LS+BR video gap
"""
from __future__ import annotations
from anchor.validation.pose import Keypoints, keypoints_to_kinematics, load_keypoints_from_dlc_csv, load_keypoints_from_sleap_h5
from anchor.validation.drone import DroneFrame, DroneMetadata, extract_trajectory_from_keypoints, load_dji_srt, pixel_to_world, world_speed_from_trajectory
from anchor.validation.drone_corpus import DroneClip, DroneCorpus, calibrate_drone_clip, calibrate_drone_corpus, cross_validate_drone_axy
from anchor.validation.paired_tag import align_clocks_xcorr, cross_tag_agreement, harmonize_to_rate
from anchor.validation.paired_tag_runner import DeploymentRound, PairedTagResult, aggregate_paired_tag_results, load_paired_tag_round, run_paired_tag_validation
from anchor.validation.online_corpus import OnlineCorpusEntry, bootstrap_k, compute_k_from_kinematics
from anchor.validation.corpus import Corpus, OnlineClip, calibrate_clip, calibrate_corpus, cycle_swim_speed, extract_diverse_frames, metres_per_pixel_from_pose, swim_speed_from_pose
from anchor.validation.auto_clip import clip_uncertain_windows, clip_window
from anchor.validation.stream_kinematics import AMPLITUDE_GRADE_MIN_PX, FREQUENCY_GRADE_MIN_PX, Clip, ClosePass, MotionEnergy, TailBeat, Track, body_frame_tail_excursion, build_capture_manifest, grade_for_px, mine_close_passes, motion_energy_frequency, segment_animal, speed_bl_per_s, strouhal_k, track_blobs, write_segment_manifest
from anchor.validation.pose_overlay import DEFAULT_SKELETON_BY_SPECIES, default_skeleton_for_species, render_pose_overlay
__all__ = ['Keypoints', 'keypoints_to_kinematics', 'load_keypoints_from_dlc_csv', 'load_keypoints_from_sleap_h5', 'DroneFrame', 'DroneMetadata', 'extract_trajectory_from_keypoints', 'load_dji_srt', 'pixel_to_world', 'world_speed_from_trajectory', 'DroneClip', 'DroneCorpus', 'calibrate_drone_clip', 'calibrate_drone_corpus', 'cross_validate_drone_axy', 'align_clocks_xcorr', 'cross_tag_agreement', 'harmonize_to_rate', 'DeploymentRound', 'PairedTagResult', 'aggregate_paired_tag_results', 'load_paired_tag_round', 'run_paired_tag_validation', 'OnlineCorpusEntry', 'bootstrap_k', 'compute_k_from_kinematics', 'Corpus', 'OnlineClip', 'calibrate_clip', 'calibrate_corpus', 'cycle_swim_speed', 'extract_diverse_frames', 'metres_per_pixel_from_pose', 'swim_speed_from_pose', 'clip_uncertain_windows', 'clip_window', 'AMPLITUDE_GRADE_MIN_PX', 'FREQUENCY_GRADE_MIN_PX', 'Clip', 'ClosePass', 'MotionEnergy', 'TailBeat', 'Track', 'body_frame_tail_excursion', 'build_capture_manifest', 'grade_for_px', 'mine_close_passes', 'motion_energy_frequency', 'segment_animal', 'speed_bl_per_s', 'strouhal_k', 'track_blobs', 'write_segment_manifest', 'DEFAULT_SKELETON_BY_SPECIES', 'default_skeleton_for_species', 'render_pose_overlay']
