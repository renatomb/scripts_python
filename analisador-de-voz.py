import sys, json, numpy as np
import librosa
from scipy.signal import lfilter, find_peaks

path = sys.argv[1] if len(sys.argv) > 1 else "oracao arcanjo miguel.mp3"
y, sr = librosa.load(path, sr=None, mono=True)

# Duração e energia
duration = len(y) / sr
rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=512)[0]
rms_db = 20 * np.log10(np.maximum(rms, 1e-12))
dynamic_range_db = float(np.percentile(rms_db, 95) - np.percentile(rms_db, 5))
noise_rms = float(np.percentile(rms, 10))
signal_rms = float(np.percentile(rms, 90))
snr_db = float(20 * np.log10(max(signal_rms, 1e-12) / max(noise_rms, 1e-12)))

# Pitch e estabilidade
f0 = librosa.yin(y, fmin=50, fmax=400, sr=sr, frame_length=2048, hop_length=256)
voiced = ~np.isnan(f0)
if np.any(voiced):
    f0v = f0[voiced]
    f0_mean = float(np.mean(f0v))
    f0_min = float(np.min(f0v))
    f0_max = float(np.max(f0v))
    periods = 1.0 / np.maximum(f0v, 1e-6)
    jitter_local = float(np.mean(np.abs(np.diff(periods))) / (np.mean(periods) + 1e-12))
else:
    f0_mean = f0_min = f0_max = jitter_local = float("nan")

# Shimmer aproximado (corrigido com np.interp)
rms_resamp = np.interp(
    np.linspace(0, len(rms) - 1, num=len(f0)),
    np.arange(len(rms)),
    rms
)
if np.any(voiced):
    amp = rms_resamp[voiced]
    shimmer_local = float(np.mean(np.abs(np.diff(amp))) / (np.mean(amp) + 1e-12))
else:
    shimmer_local = float("nan")

# Espectro
centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr, roll_percent=0.85)[0]
mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
mfcc_means = [float(np.mean(m)) for m in mfcc]

# Sibilância (5–8 kHz / 0–8 kHz)
S = np.abs(librosa.stft(y, n_fft=2048, hop_length=512)) ** 2
freqs = librosa.fft_frequencies(sr=sr, n_fft=2048)
hi = (freqs >= 5000) & (freqs <= 8000)
up = (freqs <= 8000)
sib_ratio = float(np.mean(np.sum(S[hi, :], 0) / (np.sum(S[up, :], 0) + 1e-12)))

# Taxa de fala aproximada (WPM) - corrigido com scipy.signal.find_peaks
onset_env = librosa.onset.onset_strength(y=y, sr=sr)
onset_norm = onset_env / (np.max(onset_env) + 1e-12)
onset_peaks, _ = find_peaks(onset_norm, height=0.05, distance=10)
syllables_est = int(len(onset_peaks))
syll_per_sec = float(syllables_est / max(duration, 1e-6))
wpm = float((syll_per_sec / 1.5) * 60.0)

# Formantes (LPC) em um trecho vocalizado
formants = {"F1": None, "F2": None, "F3": None}
try:
    idx = np.where(voiced)[0]
    if len(idx) > 200:
        mid = idx[len(idx) // 2]
        start = int(max(0, (mid - 64) * 256))
        end = int(min(len(y), (mid + 64) * 256))
        seg = lfilter([1, -0.97], [1], y[start:end])
        order = max(8, min(int(2 + sr / 1000), 18))
        a = librosa.lpc(seg, order=order)
        roots = np.roots(a)
        roots = roots[np.imag(roots) >= 0.01]
        ang = np.arctan2(np.imag(roots), np.real(roots))
        freqs_form = ang * (sr / (2 * np.pi))
        bw = -0.5 * (sr / (2 * np.pi)) * np.log(np.abs(roots) + 1e-12)
        valid = (freqs_form > 90) & (freqs_form < 5000) & (bw < 400)
        f = np.sort(freqs_form[valid])
        if len(f) >= 1:
            formants["F1"] = float(f[0])
        if len(f) >= 2:
            formants["F2"] = float(f[1])
        if len(f) >= 3:
            formants["F3"] = float(f[2])
except Exception as e:
    formants["error"] = str(e)

summary = {
    "sample_rate": int(sr),
    "duration_sec": float(duration),
    "dynamic_range_db": float(dynamic_range_db),
    "snr_db_estimate": float(snr_db),
    "f0_mean_hz": float(f0_mean),
    "f0_min_hz": float(f0_min),
    "f0_max_hz": float(f0_max),
    "jitter_local": float(jitter_local),
    "shimmer_local": float(shimmer_local),
    "spectral_centroid_mean_hz": float(np.mean(centroid)),
    "spectral_rolloff_85_mean_hz": float(np.mean(rolloff)),
    "mfcc_means": mfcc_means,
    "sibilance_ratio_5_8k": float(sib_ratio),
    "voiced_unvoiced_ratio": float(np.mean(voiced.astype(float))) if len(f0) > 0 else float("nan"),
    "syllables_est": syllables_est,
    "syll_per_sec": syll_per_sec,
    "wpm_est": wpm,
    "formants": formants,
}

print(json.dumps(summary, indent=2))