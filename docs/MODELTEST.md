# ModelTest

`/modeltest` runs live, non-destructive checks against the selected provider and model.

It checks a basic chat response, JSON-mode output, a three-step Planner response, short-context retention, and whether the model emits two tool calls in one response. The probe tools are fictitious: NEXUS inspects the returned tool-call requests but never executes them.

If the active model is configured for image input, the command asks separately before capturing and sending the desktop. Close private windows before approving. The screenshot is also saved locally.

The command asks for confirmation before making API calls because the checks may consume provider quota. Provider/model identity is taken from local configuration, not from the model's verbal self-identification.

Results:
- `PASS`: the observable check passed.
- `PARTIAL`: an optional capability was rejected by the endpoint/model.
- `FAIL`: the request failed or did not meet the expected result.
- `SKIP`: the check was not run.

A pass does not guarantee that every NEXUS tool works in real tasks. Windows acceptance tests remain separate.
