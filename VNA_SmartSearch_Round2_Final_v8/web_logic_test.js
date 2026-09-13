#!/usr/bin/env node
/* Regression tests for bilingual parsing and fail-closed trip planning. */

const fs = require("fs");
const vm = require("vm");

const html = fs.readFileSync("web/index.html", "utf8");
const aiHtml = fs.readFileSync("web/index-ai.html", "utf8");
function between(start, end, from = 0) {
  const a = html.indexOf(start, from);
  const b = html.indexOf(end, a + start.length);
  if (a < 0 || b < 0) throw new Error(`Cannot extract ${start}`);
  return html.slice(a, b);
}
function functionBlock(name, nextName) {
  return between(`function ${name}`, `function ${nextName}`);
}

const parserCode =
  functionBlock("foldText", "detectLang") + "\n" +
  functionBlock("parseMultiOrigin", "tool_plan_multi_origin_trip") +
  "\nresult=parseMultiOrigin(input);";

const plannerCode =
  between("const FLIGHTS = [", "// ===========================================================================\n//  i18n") + "\n" +
  functionBlock("tool_search_flights", "parseIntent") + "\n" +
  between("function tool_plan_multi_origin_trip", "async function run") +
  "\nresult=tool_plan_multi_origin_trip(input);";

function runPlanner(input) {
  const context = {input, result: null};
  vm.createContext(context);
  vm.runInContext(plannerCode, context);
  return context.result;
}

function runAiPlanner(input) {
  const start = aiHtml.indexOf("const FLIGHTS = [");
  const end = aiHtml.indexOf("//  TOOL SCHEMAS", start);
  if (start < 0 || end < 0) throw new Error("Cannot extract optional AI planner");
  const context = {input, result: null};
  vm.createContext(context);
  vm.runInContext(aiHtml.slice(start, end) + "\nresult=TOOLS.plan_multi_origin_trip(input);", context);
  return context.result;
}

const expected = JSON.stringify([
  {passengers: 2, origin: "SYD"},
  {passengers: 2, origin: "MEL"},
]);

const cases = [
  {text: "2 người từ Sydney và 2 người từ Melbourne cùng về Hà Nội dịp Tết 2027, vé một chiều, với ngân sách chung 4000 AUD.", budget: 4000},
  {text: "Two adults from Sydney and two from Melbourne want to meet in Hanoi for Tết 2027, one-way, with a shared budget of AUD 4,000.", budget: 4000},
  {text: "hai người đi từ Sydney và hai người đi từ Melbourne về Hà Nội dịp Tết 2027."},
  {text: "hai người bay từ Sydney và hai người bay từ Melbourne về Hà Nội dịp Tết 2027."},
  {text: "2 nguoi di tu Sydney va 2 nguoi di tu Melbourne cung ve Ha Noi dip Tet 2027."},
];

for (const testCase of cases) {
  const input = testCase.text;
  const context = {input, result: null};
  vm.createContext(context);
  vm.runInContext(parserCode, context);
  const result = context.result;
  const total = result.groups.reduce((sum, group) => sum + group.passengers, 0);
  if (JSON.stringify(result.groups) !== expected || result.destination !== "HAN" || total !== 4 || !result.isComplex ||
      (testCase.budget && result.total_budget !== testCase.budget)) {
    throw new Error(`Multi-origin parse failed: ${input}\n${JSON.stringify(result)}`);
  }
}

console.log("PASS: bilingual multi-origin logic (SYD ×2 + MEL ×2 → HAN; total 4)");

const missingRoute = runPlanner({
  groups: [{origin: "BNE", passengers: 2}, {origin: "PER", passengers: 2}],
  destination: "HAN", date_from: "2027-02-01", date_to: "2027-02-10",
  total_budget: 4000, tier: "none",
});
if (missingRoute.error !== "route_unavailable" ||
    !missingRoute.unavailable_routes.some(route => route.origin === "BNE" && route.destination === "HAN") ||
    missingRoute.grand_total_aud !== null || missingRoute.within_budget !== null ||
    missingRoute.budget_headroom_aud !== null) {
  throw new Error(`Missing route was not rejected safely:\n${JSON.stringify(missingRoute)}`);
}

const melbourneToDaNang = runPlanner({
  groups: [{origin: "SYD", passengers: 1}, {origin: "MEL", passengers: 1}],
  destination: "DAD", date_from: "2027-02-01", date_to: "2027-02-10",
  total_budget: 2500, tier: "none",
});
if (melbourneToDaNang.error !== "route_unavailable" ||
    !melbourneToDaNang.unavailable_routes.some(route => route.origin === "MEL" && route.destination === "DAD")) {
  throw new Error(`MEL→DAD was not rejected safely:\n${JSON.stringify(melbourneToDaNang)}`);
}

const duplicateOrigin = runPlanner({
  groups: [{origin: "SYD", passengers: 2}, {origin: "SYD", passengers: 2}],
  destination: "HAN", date_from: "2027-02-01", date_to: "2027-02-10",
  total_budget: 5000, tier: "none",
});
if (duplicateOrigin.error || duplicateOrigin.total_passengers !== 4 ||
    duplicateOrigin.legs.length !== 1 || duplicateOrigin.legs[0].passengers !== 4 ||
    duplicateOrigin.normalised_groups.length !== 1) {
  throw new Error(`Duplicate origins were not merged:\n${JSON.stringify(duplicateOrigin)}`);
}

const threeOrigins = runPlanner({
  groups: [
    {origin: "SYD", passengers: 1},
    {origin: "MEL", passengers: 1},
    {origin: "PER", passengers: 1},
  ],
  destination: "HAN", date_from: "2027-02-01", date_to: "2027-02-10",
  total_budget: 4000, tier: "none",
});
if (threeOrigins.error || threeOrigins.legs.length !== 3 || threeOrigins.total_passengers !== 3) {
  throw new Error(`Three-origin planning failed:\n${JSON.stringify(threeOrigins)}`);
}

console.log("PASS: unavailable routes fail closed (no partial total or budget verdict)");
console.log("PASS: duplicate origins merge; three-origin planning remains valid");

const aiMissingRoute = runAiPlanner({
  groups: [{origin: "BNE", passengers: 2}, {origin: "PER", passengers: 2}],
  destination: "HAN", date_from: "2027-02-01", date_to: "2027-02-10",
  total_budget: 4000, tier: "none",
});
const aiDuplicateOrigin = runAiPlanner({
  groups: [{origin: "SYD", passengers: 2}, {origin: "SYD", passengers: 2}],
  destination: "HAN", date_from: "2027-02-01", date_to: "2027-02-10",
  total_budget: 5000, tier: "none",
});
if (aiMissingRoute.error !== "route_unavailable" || aiMissingRoute.grand_total_aud !== null ||
    aiMissingRoute.within_budget !== null) {
  throw new Error(`Optional AI page did not reject a missing route safely:\n${JSON.stringify(aiMissingRoute)}`);
}
if (aiDuplicateOrigin.error || aiDuplicateOrigin.total_passengers !== 4 || aiDuplicateOrigin.legs.length !== 1) {
  throw new Error(`Optional AI page did not merge duplicate origins:\n${JSON.stringify(aiDuplicateOrigin)}`);
}
console.log("PASS: optional AI page matches stable fail-closed planning behavior");
