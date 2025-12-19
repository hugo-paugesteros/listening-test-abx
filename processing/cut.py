import librosa
import numpy as np

features = {}
for excerpt in ["glazounov", "sibelius", "tchai", "sibelius-synth"]:
    y, sr = librosa.load(f"../data/cut-references/{excerpt}.wav", sr=None)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    features[excerpt] = chroma


def snap_to_onset(y, sr, estimated_time, search_window=0.3, backtrack=True):
    center_sample = estimated_time
    window_samples = int(search_window * sr)

    start_sample = max(0, center_sample - window_samples)
    end_sample = min(len(y[0]), center_sample + window_samples)

    y_window = y[0, start_sample:end_sample]

    hop_length = 256
    onset_env = librosa.onset.onset_strength(y=y_window, sr=sr, hop_length=hop_length)

    onset_frames = librosa.onset.onset_detect(
        onset_envelope=onset_env,
        sr=sr,
        hop_length=hop_length,
        backtrack=backtrack,
        units="frames",
    )

    center_of_window = len(y_window) // 2
    closest_idx = np.argmin(np.abs(onset_frames - center_of_window))
    best_onset_frame = onset_frames[closest_idx]
    refined_sample_in_window = best_onset_frame * hop_length
    refined_global_sample = start_sample + refined_sample_in_window

    print(estimated_time, refined_global_sample)
    input()
    return refined_global_sample


def cut(y, sr, excerpt):
    chroma_target = librosa.feature.chroma_cqt(y=y[0], sr=sr)
    D, wp = librosa.sequence.dtw(features[excerpt], chroma_target, subseq=True)

    target_start_frame = wp[wp[:, 0] == 0][0, 1]
    target_end_frame = wp[wp[:, 0] == features[excerpt].shape[1] - 1][0, 1]

    target_start_sample = 512 * target_start_frame
    target_end_sample = 512 * target_end_frame

    # target_start_sample = snap_to_onset(
    #     y, sr, target_start_sample, search_window=0.3, backtrack=True
    # )
    # target_end_sample = snap_to_onset(
    #     y, sr, target_end_sample, search_window=0.3, backtrack=True
    # )

    return y[:, target_start_sample:target_end_sample]
