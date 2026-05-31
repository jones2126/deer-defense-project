# System Overview

High-level flow of the deer defense system. Click into each section for detail.

```mermaid
flowchart LR
    A([Boot]) --> B[Initialize]
    B --> C([Main Loop])
    C --> D{Deer Detected?}
    D -->|No| C
    D -->|Yes| E[Aim Servos]
    E --> F[Fire Water]
    F --> G[Cooldown]
    G --> C

    style A fill:#4ade80
    style C fill:#60a5fa
    style D fill:#fbbf24
    style F fill:#f87171
```

## Detail Views

| Section | Description |
|---|---|
| [Initialization](01-initialization.md) | Boot sequence: loading model, camera, servos, config, calibration |
| [Detection and Targeting](02-detection-loop.md) | Frame capture → YOLO inference → servo aim → fire |
| [Error Handling and Monitoring](03-error-handling.md) | Temperature, FPS, logging, exception recovery |
