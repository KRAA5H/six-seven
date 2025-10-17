# six-seven
Recognition of when an individual does the 'six seven' meme

## Project Overview
This project uses computer vision to detect and recognize the 'six seven' hand gesture meme. It combines OpenCV and MediaPipe to analyze hand movements in real-time video feeds.

## How It Works

### Technologies Used
- **OpenCV**: A powerful Python library for computer vision tasks. We use it to handle video capture and frame processing
- **MediaPipe**: Google's framework for building multimodal machine learning pipelines. Specifically, we use MediaPipe Hands for hand gesture recognition

## Detecting the "Juggling" Motion

This project detects a “juggling-like” motion as an alternating up–down oscillation of the left and right hands with a consistent rhythm, sufficient amplitude, and a phase offset between the two hands (they move out of phase). The logic combines spatial constraints (where the hands are) and temporal constraints (how the hands move over time) using MediaPipe Hands landmarks.

## Signals we compute each frame
From MediaPipe Hands, we get 21 2D/3D landmarks per detected hand. For each hand, we derive:

- Hand center: average or weighted centroid of key landmarks (e.g., wrist, MCPs).
- Vertical position y(t): the y-coordinate of the hand center in image pixels. Note: in image coordinates, y increases downward; we invert when discussing “up/down”.
- Vertical velocity vy(t): the time derivative of y(t), used to find peaks/valleys.
- Palm orientation (optional): computed from the wrist–index MCP–pinky MCP plane to derive a palm normal. Helps reject false positives (e.g., hands sideways).
- Visibility/confidence: MediaPipe’s per-landmark visibility scores to ensure stable tracking.

To reduce jitter, we smooth these signals with an exponential moving average (EMA).

- y_smooth[t] = alpha * y[t] + (1 - alpha) * y_smooth[t-1]
- Typical alpha: 0.2–0.4 (tune based on camera noise and FPS)

## What counts as “juggling” here
- Two hands visible and confidently tracked for a short window (e.g., last 1–2 seconds).
- Each hand’s vertical position oscillates with:
  - Sufficient amplitude (peak-to-peak above a pixel threshold scaled by frame height).
  - A plausible cadence (frequency within a human gesture range, e.g., 0.8–3.0 Hz).
- Alternation: peaks of left and right hands interleave consistently (one hand up while the other is down). This implies a phase difference near 180°.
- Consistency: at least N alternating cycles (e.g., N ≥ 3) within a rolling window.

## Temporal features and thresholds
- Amplitude threshold A_min: e.g., 3–6% of frame height. Reject tiny oscillations.
- Period range T_min…T_max: e.g., 0.33–1.25 s (3–0.8 Hz). Reject too fast/slow motion.
- Alternation consistency: require that the hand with the last peak switches on each subsequent peak.
- Phase check (simple): the time between a left-hand peak and the nearest right-hand peak should be ≈ 0.4–0.6 of the dominant period.
- Visibility/continuity: hands should be detected in >80% of frames in the window.

## Simple state machine
- Idle: Not enough data or only one hand tracked.
- Candidate: Two hands tracked; amplitude and period look plausible for at least one cycle.
- In-Motion: Alternating peaks detected for ≥ N cycles with correct cadence.
- Confirmed: Declare “juggling” while cadence and alternation persist; decay back to Idle if conditions fail for M frames.

## Peak and cadence detection
We detect local maxima/minima on the smoothed y-signal using zero-crossings of vy(t) or a small peak window. To make it FPS-robust, use timestamps to measure periods instead of frame counts.

- Peak: vy crosses from positive to negative (top) or negative to positive (bottom)
- Period: time delta between two consecutive peaks of the same type (e.g., two tops)
- Amplitude: difference between a top and the adjacent bottom

## Alternation and phase check
- Interleave constraint: If the last peak was from Left, the next should be from Right, and vice versa, for K consecutive peaks (e.g., K ≥ 6, which is ~3 full cycles).
- Phase constraint: Let T be the average period of the two hands. For each Left peak time tL, find the nearest Right peak time tR and measure Δ = |tR - tL| / T. Require Δ ∈ [0.35, 0.65].

## Spatial sanity checks
- Horizontal separation: hands should not fully overlap; require |x_left - x_right| > S_min (e.g., 8–12% of frame width).
- Palm orientation (optional): prefer palms roughly facing camera (based on palm normal z-component) to reduce false positives from sideways arm swings.
- Z-depth stability (if 3D landmarks available): reject large in–out movements that mimic vertical oscillations in 2D.

## Learnings & Challenges

### Setting Up the Environment
One of the biggest hurdles was dealing with dependency compatibility issues:
- **MediaPipe Compatibility**: MediaPipe doesn't support Python 3.13, so I initially tried creating a virtual environment with Python 3.9
- **SSL Certificate Issues**: When using Python 3.9, I ran into SSL errors while trying to install packages
- **Solution**: Downgraded to Python 3.12 instead using `python3.12 -m venv myenv`, which resolved both the MediaPipe compatibility and SSL issues

### Version Control Lesson
Initially, I committed my virtual environment files to Git, which created around 900 unnecessary commits. The key takeaway: **always use .gitignore** to exclude virtual environments and other generated files from version control.

### Libraries & Frameworks
- **Initial Approach**: I first tried using the OS module to display video output, but it didn't work as expected
- **Final Solution**: Switched to **PyGame**, which provided a reliable and efficient way to render the video feed with overlaid detection data

## Key Takeaways
This project taught me the importance of understanding library dependencies, the value of proper project setup practices (like .gitignore), and how to troubleshoot compatibility issues systematically.
