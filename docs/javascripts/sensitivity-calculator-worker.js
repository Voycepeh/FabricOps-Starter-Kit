/* global loadPyodide */
const runtimeURL = "https://cdn.jsdelivr.net/pyodide/v0.27.7/full/";
let runtime;

async function start() {
  importScripts(runtimeURL + "pyodide.js");
  const [python, bundle] = await Promise.all([
    loadPyodide({ indexURL: runtimeURL }),
    fetch(new URL("../assets/sensitivity-calculator.zip", self.location.href)),
  ]);
  if (!bundle.ok) throw new Error("The calculator engine is unavailable.");
  python.unpackArchive(await bundle.arrayBuffer(), "zip", { extractDir: "/fabricops" });
  python.runPython(`
import sys
sys.path[:0] = ["/fabricops", "/fabricops/src"]
from sensitivity_calculator import handle_message
`);
  return python;
}

self.onmessage = async ({ data }) => {
  let python;
  try {
    runtime ??= start();
    python = await runtime;
  } catch {
    runtime = undefined;
    self.postMessage({ error: "Could not start the calculator. Check your connection and try again." });
    return;
  }

  try {
    python.globals.set("calculator_request", JSON.stringify(data));
    const response = python.runPython(`
try:
    calculator_response = handle_message(calculator_request)
except (ValueError, TypeError, KeyError, OverflowError) as exc:
    import json
    calculator_response = json.dumps({"error": str(exc)})
finally:
    del calculator_request
calculator_response
`);
    self.postMessage(JSON.parse(response));
    python.globals.delete("calculator_response");
  } catch {
    self.postMessage({ error: "The assessment could not finish. Check the profile and try again." });
  }
};
