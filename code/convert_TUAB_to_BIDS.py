# Convert TUAB to BIDS
# > This script is used to convert the TUAB dataset to BIDS format.

import os
import re
import pandas as pd
import shutil

from pathlib import Path
from tqdm import tqdm
from mne.io import read_raw_edf
from mne_bids import write_raw_bids, BIDSPath

# Define mapping for channel name harmonization
channel_name_mapping = {
    "EEG A1-REF": "A1",
    "EEG A2-REF": "A2",
    "EEG CZ-REF": "Cz",
    "EEG C3-REF": "C3",
    "EEG C4-REF": "C4",
    "EEG FP1-REF": "Fp1",
    "EEG FP2-REF": "Fp2",
    "EEG F3-REF": "F3",
    "EEG F4-REF": "F4",
    "EEG F7-REF": "F7",
    "EEG F8-REF": "F8",
    "EEG FZ-REF": "Fz",
    "EEG O1-REF": "O1",
    "EEG O2-REF": "O2",
    "EEG OZ-REF": "Oz",
    "EEG P3-REF": "P3",
    "EEG P4-REF": "P4",
    "EEG PZ-REF": "Pz",
    "EEG T3-REF": "T7",
    "EEG T4-REF": "T8",
    "EEG T5-REF": "P7",
    "EEG T6-REF": "P8",
    "EEG T1-REF": "T1",
    "EEG T2-REF": "T2",
    "EEG C3P-REF": "CP3",
    "EEG C4P-REF": "CP4",
    "EEG PG1-REF": "PG1",
    "EEG PG2-REF": "PG2",
    "EEG SP1-REF": "SP1",
    "EEG SP2-REF": "SP2",
    "EEG 26-REF": "EEG 26",
    "EEG 27-REF": "EEG 27",
    "EEG 28-REF": "EEG 28",
    "EEG 29-REF": "EEG 29",
    "EEG 30-REF": "EEG 30",
    "EEG 31-REF": "EEG 31",
    "EEG 32-REF": "EEG 32",
    "ECG EKG-REF": "ECG",
    "EEG EKG1-REF": "ECG",
    "EMG-REF": "EMG",
    "EEG LOC-REF": "LOC",
    "EEG ROC-REF": "ROC",
    "BURSTS": "BURSTS",
    "SUPPR": "SUPPR",
    "PHOTIC-REF": "PHOTIC",
    "IBI": "IBI",
    "PULSE RATE": "PULSE",
}

# Define mapping for channel types
channel_type_mapping = {
    "EEG A1-REF": "eeg",
    "EEG A2-REF": "eeg",
    "EEG CZ-REF": "eeg",
    "EEG C3-REF": "eeg",
    "EEG C4-REF": "eeg",
    "EEG FP1-REF": "eeg",
    "EEG FP2-REF": "eeg",
    "EEG F3-REF": "eeg",
    "EEG F4-REF": "eeg",
    "EEG F7-REF": "eeg",
    "EEG F8-REF": "eeg",
    "EEG FZ-REF": "eeg",
    "EEG O1-REF": "eeg",
    "EEG O2-REF": "eeg",
    "EEG OZ-REF": "eeg",
    "EEG P3-REF": "eeg",
    "EEG P4-REF": "eeg",
    "EEG PZ-REF": "eeg",
    "EEG T3-REF": "eeg",
    "EEG T4-REF": "eeg",
    "EEG T5-REF": "eeg",
    "EEG T6-REF": "eeg",
    "EEG T1-REF": "eeg",
    "EEG T2-REF": "eeg",
    "EEG C3P-REF": "eeg",
    "EEG C4P-REF": "eeg",
    "EEG PG1-REF": "eeg",
    "EEG PG2-REF": "eeg",
    "EEG SP1-REF": "eeg",
    "EEG SP2-REF": "eeg",
    "EEG 26-REF": "eeg",
    "EEG 27-REF": "eeg",
    "EEG 28-REF": "eeg",
    "EEG 29-REF": "eeg",
    "EEG 30-REF": "eeg",
    "EEG 31-REF": "eeg",
    "EEG 32-REF": "eeg",
    "ECG EKG-REF": "ecg",
    "EEG EKG1-REF": "ecg",
    "EMG-REF": "emg",
    "EEG LOC-REF": "eog",
    "EEG ROC-REF": "eog",
    "BURSTS": "misc",
    "SUPPR": "misc",
    "PHOTIC-REF": "stim",
    "IBI": "misc",
    "PULSE RATE": "misc",
}

# Ensure this script is executed from repository root, i.e. the parent directory of the `code` directory
current_dir = Path(__file__).parents[1]
os.chdir(current_dir)

sourcedata_dir = Path("sourcedata/v3.0.1/edf")
rawdata_dir = Path("rawdata")  # Where the BIDSified data should be written to

# Delete rawdata directory if it already exists to ensure a clean slate
if rawdata_dir.exists():
    print(f"Deleting existing rawdata directory: {rawdata_dir}")
    shutil.rmtree(rawdata_dir)


## Convert TUAB to BIDS
#

files = list(sourcedata_dir.glob("**/*.edf"))
errors = []

for file in tqdm(files):
    try:
        # Extract information from the file path
        split, normality, _, fname = file.relative_to(sourcedata_dir).parts
        subject, session, run = fname.replace(".edf", "").split("_")

        # Format entity values
        session = session.replace("s", "")
        run = run.replace("t", "").replace(".edf", "")

        # Extract subject information from edf header
        with open(file, "rb") as f:
            f.seek(8)  # skip the first 8 bytes
            header = f.read(80).decode("utf-8")  # extract patient information

            # Extract age
            age_match = re.search(r'Age:(\d+)', header)
            age = int(age_match.group(1)) if age_match else None

            # Extract sex
            sex_match = re.search(r'\s([MF])\s', header)
            sex = sex_match.group(1) if sex_match else None

        # Create BIDSPath
        bids_path = BIDSPath(
            root=rawdata_dir,
            subject=subject,
            session=session,
            run=run,
            task="rest",
        )

        # Read data
        raw = read_raw_edf(file, verbose=False)

        # Set channel types
        raw.set_channel_types({k: v for k, v in channel_type_mapping.items() if k in raw.ch_names}, on_unit_change="ignore")

        # Harmonize channel names
        raw.rename_channels({k: v for k, v in channel_name_mapping.items() if k in raw.ch_names})

        # Write BIDS
        write_raw_bids(raw, bids_path=bids_path, overwrite=True, verbose=False)

        # Add subject information
        participants_tsv = pd.read_csv(rawdata_dir / "participants.tsv", sep="\t")
        participants_tsv.loc[participants_tsv.participant_id == f"sub-{subject}", "age"] = age
        participants_tsv.loc[participants_tsv.participant_id == f"sub-{subject}", "sex"] = sex
        participants_tsv.loc[participants_tsv.participant_id == f"sub-{subject}", "official_split"] = split
        participants_tsv.to_csv(rawdata_dir / "participants.tsv", sep="\t", index=False, na_rep="n/a")

        # Add recording information
        scans_tsv = pd.read_csv(rawdata_dir / f"sub-{subject}" / f"ses-{session}" / f"sub-{subject}_ses-{session}_scans.tsv", sep="\t")
        # Classification of recordings into "normal" and "abnormal" is not always consistent across recordings of a subject.
        # TUAB contains a few subjects with both normal and abnormal recordings. Therefore we store the normality information
        # in the scans.tsv file instead of in the participants.tsv file.
        scans_tsv.loc[scans_tsv.filename == f"eeg/sub-{subject}_ses-{session}_task-rest_run-{run}_eeg.edf", "normality"] = normality
        scans_tsv.to_csv(rawdata_dir / f"sub-{subject}" / f"ses-{session}" / f"sub-{subject}_ses-{session}_scans.tsv", sep="\t", index=False, na_rep="n/a")
    except Exception as e:
        print(f"Error processing file {file}: {e}")
        errors.append(file)
        continue


## Curate participants.tsv
#

participants_tsv = pd.read_csv(rawdata_dir / "participants.tsv", sep="\t")

# Replace missing / unrealistic age values with NaN
# The original participants.tsv file contains some age values of 999 years.
participants_tsv.loc[participants_tsv["age"] > 120, "age"] = None

# Add n_normal_recordings and n_abnormal_recordings columns
# The labels are stored in the scans.tsv files. For some subjects, we have multiple scans.
# We will count the number of normal and abnormal scans for each subject.
participants_tsv["normal"] = 0
participants_tsv["abnormal"] = 0

# Collect lables from scants.tsv files in BIDS dataset
for sub in participants_tsv.participant_id:
    scans_tsv_files = (rawdata_dir / sub).rglob("*_scans.tsv")
    for scans_tsv_file in scans_tsv_files:
        scans_tsv = pd.read_csv(scans_tsv_file, sep="\t")
        normality = scans_tsv["normality"].item()
        participants_tsv.loc[participants_tsv.participant_id == sub, normality] += 1

participants_tsv = participants_tsv.rename(columns={"normal": "n_normal_recordings", "abnormal": "n_abnormal_recordings"})


## Add custom train/val/test split
#

# Split according to official split
participants_test = participants_tsv.loc[participants_tsv.official_split == "eval"]
participants_train = participants_tsv.loc[participants_tsv.official_split == "train"]
assert set(participants_test.participant_id).isdisjoint(set(participants_train.participant_id))

# Split train into train and validation
train_size = 0.9  # Use 10% of the official train split for validation
participants_val = participants_train.sample(frac=1-train_size, random_state=42)
participants_train = participants_train.drop(participants_val.index)
assert set(participants_val.participant_id).isdisjoint(set(participants_train.participant_id))

# Add new split column to participants_tsv
participants_tsv["train_val_test_split"] = "none"
participants_tsv.loc[participants_tsv.participant_id.isin(participants_train.participant_id), "train_val_test_split"] = "train"
participants_tsv.loc[participants_tsv.participant_id.isin(participants_val.participant_id), "train_val_test_split"] = "val"
participants_tsv.loc[participants_tsv.participant_id.isin(participants_test.participant_id), "train_val_test_split"] = "test"

# Save curated participants.tsv
participants_tsv.to_csv(rawdata_dir / "participants.tsv", sep="\t", index=False, na_rep="n/a")


## Print summary
#

print(f"BIDS conversion completed. {len(files)- len(errors)}/{len(files)} files were successfully processed.")
if errors:
    print("Errors occurred for the following files:")
    print("\n".join(errors))
