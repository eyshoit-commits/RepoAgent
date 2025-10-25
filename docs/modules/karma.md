## Karma System

The karma subsystem tracks community contributions and automatically promotes members to the
**specialist** role once they accumulate sufficient points. Configuration lives in `config/karma.yaml`:

```yaml
default_role: novice
thresholds:
  novice: 0
  contributor: 40
  specialist: 100
storage:
  path: ../var/karma_state.json
```

- `thresholds` defines the minimum karma required for each role.
- `default_role` is applied to new members that have not earned karma yet.
- `storage.path` persists balances so that promotions survive restarts.

Use the CLI to interact with the system:

```bash
spooky-cli karma award alice --points 10   # grant karma
spooky-cli karma status alice              # inspect current role
spooky-cli karma leaderboard --limit 5     # view top performers
```

When a member crosses the configured `specialist` threshold, their role automatically updates
without restarting the application, enabling hot-swappable promotions aligned with the platform's
modular principles.
