# sequential decisions

## Reinforcement learning and sequential decisions

**Documented:** RL optimizes cumulative reward through interaction with an environment, with states/observations, actions and a policy. Action choices can change later states and rewards; this differs from static supervised prediction. [Spinning Up RL concepts](https://spinningup.openai.com/en/latest/spinningup/rl_intro.html)

**Decision synthesis:** Use a sequential-decision route only when delayed consequences matter. If decisions affect only immediate outcomes, assess simpler optimization/contextual-bandit or causal-policy approaches. Specify reward, constraints, termination, observation limitations and safe exploration. Compare a heuristic/existing controller; do not assume simulation validity or deploy an exploratory policy automatically. Logged-data learning needs defensible action coverage and off-policy evaluation; absent coverage makes counterfactual claims unsupported.

**Documented:** RL results vary across seeds; evaluation should use a separate test environment. Model-free methods can be sample-inefficient, and reward design needs expertise. [Stable-Baselines3 RL tips](https://stable-baselines3.readthedocs.io/en/master/guide/rl_tips.html)

**Decision synthesis:** Report multiple runs, return distributions, failure rates and constraint violations. Distinguish true termination from time-limit truncation, test wrappers and environment transitions, and check reward hacking. Use staged simulation/shadow evaluation and explicit operating constraints before any real-world trial. Escalate unsafe exploration, unreliable simulators or unverifiable reward alignment; a supervised train/test split alone cannot establish RL deployment readiness.
