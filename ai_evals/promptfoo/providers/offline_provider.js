// Offline provider used by CI (OFFLINE_LLM=true). Returns recorded fixture
// responses keyed by `task`; promptfoo assertions then run against them.

const fs = require("fs");
const path = require("path");

const FIXTURES = JSON.parse(
  fs.readFileSync(path.join(__dirname, "..", "..", "fixtures", "offline_responses.json"), "utf-8"),
);

class OfflineProvider {
  constructor(options) {
    this.id = "offline-fixture";
    this.options = options || {};
  }

  async callApi(_prompt, context) {
    const task = (context && context.vars && context.vars.task) || "signal_hypothesis";
    const data = FIXTURES[task];
    if (!data) {
      return { error: `no fixture for task=${task}` };
    }
    const text = typeof data === "string" ? data : JSON.stringify(data);
    return { output: text };
  }
}

module.exports = OfflineProvider;
