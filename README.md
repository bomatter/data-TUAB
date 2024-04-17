# TUAB Dataset

This is a curated version of the [TUH Abnormal EEG Corpus (TUAB)](https://isip.piconepress.com/projects/tuh_eeg/html/downloads.shtml) v3.0.1.



- The original file names (e.g. "aaaaamye_s001_t000.edf") with subject identifier, session, and token number, are mapped to subject, session, and run BIDS entities.
- Age and sex information are extracted from the edf headers and added to the participants.tsv file.
- The official split (train, eval) is specified in the participants.tsv file.
- The "normal" vs "abnormal" annotations are specified in the scants.tsv files. The reason for this is that TUAB contains a few subjects with both "normal" and "abnormal" recordings – hence this information cannot be specified on the subject level in participants.tsv.
- Channel names and types are harmonised.



## Reproduce from the Source Data

1. Clone repository

   ```
   git clone https://github.com/bomatter/data-TUAB.git TUAB
   ```

2. Install dependencies or use an existing environment with mne and mne-bids installed.
   Example using mamba:

   ```
   mamba create -n bidsify python=3.10 mne mne-bids
   mamba activate bidsify
   ```

3. (optional) Modify or delete the `.gitignore` file to start tracking the data folders with [DataLad](https://www.datalad.org/).
   
   ```
   mamba install datalad
   rm .gitignore
   datalad save -m"start tracking data folders"
   ```
   
4. [Request access](https://isip.piconepress.com/projects/tuh_eeg/html/downloads.shtml) and download TUAB to `sourcedata/`

   ```
   mkdir sourcedata
   rsync -auxvL nedc-eeg@www.isip.piconepress.com:data/eeg/tuh_eeg_abnormal/v3.0.1/ sourcedata/v3.0.1
   ```

   Save if you are using DataLad to track the data folders:

   ```
   datalad save -m"downloaded sourcedata"
   ```

5. Run the BIDS conversion script.

   ```
   python code/convert_TUAB_to_BIDS.py
   ```

   or using DataLad:
   
   ```
   datalad run \
   	-m "run data curation" \
   	-i "sourcedata/*" \
   	-o "rawdata/*" \
   	-o "derivatives/*" \
   	"python code/convert_TUAB_to_BIDS.py"
   ```
