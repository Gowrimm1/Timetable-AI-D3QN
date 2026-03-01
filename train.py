"""
train.py — Train Dueling Double DQN (D3QN) for MEC Timetable
"""

from stable_baselines3 import DQN
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.callbacks import BaseCallback
import time

from timetable_env import TimetableEnv

env = TimetableEnv()

print("🔍 Checking environment...")
check_env(env, warn=True)

# ── Progress Callback ────────────────────────────────────────────────────────
class ProgressCallback(BaseCallback):
    def __init__(self, total_steps, print_every=5000):
        super().__init__()
        self.total_steps  = total_steps
        self.print_every  = print_every
        self.start_time   = None
        self.best_reward  = -float("inf")

    def _on_training_start(self):
        self.start_time = time.time()
        print(f"\n{'─'*55}")
        print(f"  Steps       │ Progress │ Elapsed  │ ETA")
        print(f"{'─'*55}")

    def _on_step(self) -> bool:
        if self.num_timesteps % self.print_every == 0:
            elapsed   = time.time() - self.start_time
            progress  = self.num_timesteps / self.total_steps
            eta       = (elapsed / progress - elapsed) if progress > 0 else 0
            bar_len   = 20
            filled    = int(bar_len * progress)
            bar       = "█" * filled + "░" * (bar_len - filled)
            print(
                f"  {self.num_timesteps:>8,} / {self.total_steps:,} │ "
                f"[{bar}] {progress*100:5.1f}% │ "
                f"{elapsed:6.0f}s  │ ~{eta:.0f}s"
            )
        return True

    def _on_training_end(self):
        elapsed = time.time() - self.start_time
        print(f"{'─'*55}")
        print(f"  ✅ Done in {elapsed:.0f}s")

# ── Dueling DQN Architecture ─────────────────────────────────────────────────
policy_kwargs = dict(
    net_arch=[128, 128],   # smaller network = faster training on CPU
)

TOTAL_STEPS = 50_000       # ← Fast first run (~2–4 min on CPU)
                           #   Increase to 150_000 or 300_000 for better results

model = DQN(
    "MlpPolicy",
    env,
    policy_kwargs           = policy_kwargs,
    learning_rate           = 1e-4,
    buffer_size             = 50_000,       # reduced for speed
    learning_starts         = 1_000,        # start learning sooner
    batch_size              = 64,
    tau                     = 0.005,
    gamma                   = 0.99,
    train_freq              = 4,
    gradient_steps          = 1,
    target_update_interval  = 500,
    exploration_fraction    = 0.5,
    exploration_initial_eps = 1.0,
    exploration_final_eps   = 0.05,
    verbose                 = 0,            # silenced — callback handles output
)

print(f"🚀 Training D3QN — {TOTAL_STEPS:,} steps  (CPU-optimised)")
print(f"   Network : 128×128  │  Buffer: 50k  │  Batch: 64")
print(f"   To improve quality later: set TOTAL_STEPS = 300_000\n")

callback = ProgressCallback(total_steps=TOTAL_STEPS, print_every=5000)
model.learn(total_timesteps=TOTAL_STEPS, callback=callback)
model.save("d3qn_timetable_model")
print("💾 Model saved → d3qn_timetable_model.zip")
print("\n▶  Next step: python test_model.py")