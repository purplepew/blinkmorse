# BlinkMorse — AI Agent Project Guide

## 1. Project Overview

BlinkMorse is an undergraduate Computer Science thesis prototype titled:

> **BlinkMorse: An Android-Based Eye-Blink Communication System with Adaptive Morse Decoding**

The intended final system is an Android application that uses the device's front-facing camera to detect intentional eye blinks, convert blink patterns into Morse code, and display the decoded message as text.

The current work is a **Python computer-vision prototype** used to validate the core detection and decoding logic before the Android implementation.

---

## 2. Thesis Scope

### Core requirements

The final BlinkMorse system should include:

1. Android application
2. Front-facing camera input
3. Facial/eye landmark detection
4. Eye Aspect Ratio (EAR) calculation
5. Blink detection
6. Blink-duration measurement
7. Morse dot/dash classification
8. Adaptive blink-duration thresholding
9. Morse decoding
10. Text output
11. Basic system evaluation

### Nice-to-have features

These should not take priority over the core thesis objectives:

- Text-to-speech (TTS)
- Basic user calibration/training
- Additional accessibility features
- Other UI enhancements

If time becomes limited, nice-to-have features should be removed rather than expanding the core scope.

---

## 3. Main Research Contribution

The main proposed contribution is:

> **Adaptive Blink-Duration Thresholding / Adaptive Morse Decoding**

The project is NOT claiming that the following are novel:

- Camera-based eye tracking
- MediaPipe
- Facial landmarks
- Eye Aspect Ratio (EAR)
- Blink detection
- Morse code

These are established technologies/components.

The research focus is on whether an adaptive blink-duration classification boundary can better accommodate variation in a user's intentional blink timing.

The system should therefore distinguish between:

- established computer-vision components, and
- the project's adaptive classification mechanism.

Do not describe MediaPipe, EAR, camera input, or Morse code itself as the thesis novelty.

---

## 4. Current Development Stage

The current Python prototype has reached:

```text
Camera
  ↓
MediaPipe Face Landmarker
  ↓
Facial landmarks
  ↓
Eye landmarks
  ↓
EAR calculation
  ↓
Blink state detection
  ↓
Blink duration measurement
```

The current blink threshold is still static and temporary:

```text
EAR < 0.22
```

This is NOT the final adaptive mechanism.

The next development milestone is to log reliable blink-duration measurements before designing the adaptive dot/dash threshold.

---

## 5. Current Technology

The current prototype uses:

- Python 3.13
- MediaPipe 1.0.1
- MediaPipe Tasks API
- Face Landmarker
- OpenCV
- NumPy through MediaPipe/OpenCV dependencies

### Important MediaPipe rule

Do NOT use the old Solutions API:

```python
mp.solutions.face_mesh
```

The current environment uses MediaPipe 1.0.1 and the newer Tasks API:

```python
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
```

Use `FaceLandmarker` rather than attempting to restore the old `solutions.face_mesh` implementation.

---

## 6. Current Project Structure

The intended prototype structure is:

```text
BLINKMORSE THESIS/
│
├── source code/
│   │
│   ├── main.py
│   ├── config.py
│   │
│   ├── vision/
│   │   ├── __init__.py
│   │   ├── face_landmarker.py
│   │   └── ear.py
│   │
│   ├── blink/
│   │   ├── __init__.py
│   │   └── detector.py
│   │
│   └── models/
│       └── face_landmarker.task
│
├── tests/
│
└── AGENTS.md
```

Keep the architecture simple. This is an undergraduate thesis with a narrow development window. Do not introduce unnecessary frameworks, services, databases, or complex abstractions.

---

## 7. Module Responsibilities

### `main.py`

Application entry point.

Responsibilities:

- Open webcam
- Capture frames
- Pass frames to Face Landmarker
- Calculate/display EAR
- Pass EAR measurements to blink detector
- Display prototype status
- Coordinate the other modules

Do not put the adaptive algorithm directly into `main.py`.

---

### `config.py`

Central configuration.

Current configuration includes:

- Face Landmarker model path
- Number of faces
- Detection confidence
- Presence confidence
- Tracking confidence
- Temporary static EAR threshold
- Camera index

Configurable values should generally live here rather than being duplicated throughout the project.

---

### `vision/face_landmarker.py`

Responsible only for MediaPipe Face Landmarker functionality.

It should:

- Initialize the MediaPipe Face Landmarker
- Accept image frames
- Run landmark detection
- Return landmark results
- Close/release the landmarker

Do not put Morse logic here.

---

### `vision/ear.py`

Responsible for:

- Eye landmark indices
- Eye-point extraction
- Euclidean distance
- EAR calculation
- Average left/right EAR

Current eye landmark indices:

```python
LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 384, 263, 373, 380]
```

The EAR formula currently used is:

```text
EAR = (Vertical1 + Vertical2) / (2 × Horizontal)
```

---

### `blink/detector.py`

Responsible for blink state transitions and blink duration.

The intended state model is:

```text
OPEN
  ↓ EAR below threshold
CLOSED
  ↓ EAR above threshold
OPEN
```

A completed blink should produce:

```text
blink duration in milliseconds
```

The detector should reject obviously invalid durations using minimum/maximum duration constraints.

Future adaptive classification should be implemented in a separate module rather than making `detector.py` unnecessarily complex.

---

## 8. Planned Future Modules

As development progresses, modules may be added:

```text
blink/
├── detector.py
└── adaptive_threshold.py

morse/
└── decoder.py
```

### `adaptive_threshold.py`

This should contain the thesis-specific adaptive blink-duration classification logic.

Potential conceptual flow:

```text
Recent intentional blink durations
          ↓
Estimate/update classification boundary
          ↓
Compare new blink duration
          ↓
SHORT / LONG
          ↓
DOT / DASH
```

Do not implement the algorithm by simply choosing an arbitrary fixed boundary such as:

```text
< 300 ms = dot
>= 300 ms = dash
```

unless this is explicitly being used as a baseline for comparison.

The adaptive method should be designed and documented separately.

---

### `morse/decoder.py`

Future responsibility:

```text
DOT / DASH sequence
        ↓
Morse symbol
        ↓
Character
        ↓
Decoded text
```

Keep Morse decoding independent from camera and MediaPipe code.

---

## 9. Development Order

Follow this sequence unless there is a strong technical reason to change it:

### Phase 1 — Computer vision

```text
Camera
↓
Face landmarks
↓
Eye landmarks
↓
EAR
```

### Phase 2 — Blink measurement

```text
EAR
↓
Blink state
↓
Blink start/end
↓
Blink duration
```

### Phase 3 — Data collection/logging

```text
Blink events
↓
Duration records
↓
Basic inspection/statistics
```

### Phase 4 — Dot/dash classification

```text
Blink duration
↓
Short/long classification
↓
Dot/dash
```

### Phase 5 — Morse decoding

```text
Dot/dash
↓
Morse symbols
↓
Characters
↓
Text
```

### Phase 6 — Adaptive mechanism

```text
Recent blink durations
↓
Adaptive threshold
↓
Personalized short/long classification
```

### Phase 7 — Evaluation

Evaluate the system using a manageable experimental setup appropriate for an undergraduate thesis.

Do not expand the scope unnecessarily.

---

## 10. Coding Principles

### Keep modules focused

Prefer:

```text
face_landmarker.py → landmarks
ear.py             → EAR
detector.py        → blink events
adaptive_threshold.py → adaptive classification
decoder.py         → Morse decoding
main.py            → orchestration
```

Avoid putting all functionality into one large file.

### Avoid premature abstraction

Do not create:

- unnecessary classes
- unnecessary design patterns
- unnecessary interfaces
- databases
- APIs
- cloud services
- complicated dependency injection

unless they become necessary.

### Preserve working functionality

When modifying code:

1. Make the smallest reasonable change.
2. Keep the existing working pipeline intact.
3. Test the affected component.
4. Only then proceed to the next feature.

---

## 11. Testing Expectations

Every major development step should have a simple observable test.

Examples:

### EAR

Verify that:

- a face is detected
- eye landmarks appear
- EAR is displayed
- EAR decreases when eyes close

### Blink detector

Verify that:

- opening eyes does not create a blink
- closing eyes starts a blink
- reopening eyes ends a blink
- a duration is recorded

### Morse classifier

Verify that:

- a short blink can be classified
- a long blink can be classified
- classification does not depend on arbitrary values without justification

### Adaptive threshold

Verify that:

- the threshold can update from recent blink-duration data
- the mechanism remains stable enough to avoid excessive threshold changes
- classification can accommodate timing variation

---

## 12. Important Thesis Constraints

The project is intended for an undergraduate Computer Science thesis with a narrow implementation period.

Therefore:

- Prioritize a working core system over feature quantity.
- Keep the Android target explicit.
- Do not turn the project into a general accessibility platform.
- Do not add medical-diagnosis functionality.
- Do not claim the system is a medical device.
- Do not claim clinical effectiveness.
- Do not claim that MediaPipe/EAR/blink detection/Morse code are novel.
- Clearly separate existing technologies from the proposed adaptive contribution.
- Avoid unsupported claims of superiority over other systems.
- Use measurable evaluation criteria.

---

## 13. AI Agent Rules

When an AI coding agent works on this project:

### Before changing architecture

Explain why the change is necessary.

### Before adding dependencies

Check whether an existing dependency can solve the problem.

Do not add a library just for convenience.

### When changing MediaPipe code

Preserve compatibility with:

```text
Python 3.13
MediaPipe 1.0.1
MediaPipe Tasks API
```

Do not revert to:

```python
mp.solutions
```

### When implementing thesis functionality

Identify whether the feature is:

1. Core system functionality,
2. Thesis research contribution, or
3. Nice-to-have.

Prioritize in that order.

### When suggesting research claims

Do not invent experimental results.

Do not state that the adaptive method improves accuracy until it has actually been evaluated.

Use language such as:

> "The system will evaluate whether..."

rather than:

> "The system improves..."

before evaluation has been performed.

---

## 14. Current Next Task

The immediate next task is:

> **Implement a blink-duration logger that records completed blink events and their durations.**

Expected output:

```text
Blink #1: 164 ms
Blink #2: 189 ms
Blink #3: 177 ms
Blink #4: 521 ms
Blink #5: 548 ms
```

The collected data will be used to inform the later design of the adaptive dot/dash threshold.

Do not implement the adaptive threshold yet.

---

## 15. Running the Prototype

From:

```text
BLINKMORSE THESIS/source code/
```

run:

```bash
python main.py
```

Press:

```text
Q
```

to exit the webcam window.

---

## 16. Definition of Done for the Current Prototype Stage

The current stage is considered successful when:

- MediaPipe Face Landmarker initializes successfully.
- The webcam opens.
- A face is detected.
- Eye landmarks are visible.
- EAR is calculated continuously.
- Blink state changes are detected.
- Completed blinks produce a duration in milliseconds.
- The application does not require the old `mp.solutions` API.

Only after these are working should Morse classification be implemented.
