# Error Handling and Monitoring

Runs alongside the main loop to keep the system healthy 24/7.

```mermaid
flowchart TD
    A([Main Loop Running]) --> B[Monitor System Health]
    B --> C{Health OK?}
    C -->|Yes| D[Log Detection Events]
    D --> A
    C -->|No| E{What failed?}
    E -->|Camera disconnect| F[Attempt Camera Reconnect]
    E -->|Servo stall| G[Reset Servos to Home Position]
    E -->|Overheating| H[Pause and Cool Down]
    E -->|Other exception| I[Log Error]
    F --> J{Reconnected?}
    J -->|Yes| A
    J -->|No| K[Alert and Halt]
    G --> A
    H --> A
    I --> A

    style A fill:#60a5fa
    style C fill:#fbbf24
    style E fill:#fbbf24
    style K fill:#f87171
```

## Notes

- **Temperature**: RK3588 can run warm under sustained NPU load — add a heatsink and small fan; log CPU temp each cycle
- **FPS tracking**: if inference drops below 5 FPS, log a warning — may indicate thermal throttling or model issue
- **Camera disconnect**: most common outdoor failure; implement a reconnect retry loop before halting
- **Systemd service**: run the main script as a systemd service with `Restart=always` so the OS auto-restarts after a crash
- **Optional alerts**: send a Telegram or email message on first detection of the day, or on any system fault

[Back to Overview](overview.md)
