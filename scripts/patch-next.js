const fs = require("fs");
const path = require("path");

const targets = [
  path.join(__dirname, "..", "node_modules", "next", "dist", "lib", "find-pages-dir.js"),
  path.join(__dirname, "..", "node_modules", "next", "dist", "esm", "lib", "find-pages-dir.js"),
];

targets.forEach((filePath) => {
  if (!fs.existsSync(filePath)) return;
  let content = fs.readFileSync(filePath, "utf-8");

  // If already patched, skip
  if (content.includes("prioritize ./src/${name}")) return;

  // Replace prioritization logic
  const searchPatternCJS = `function findDir(dir, name) {
    // prioritize ./\${name} over ./src/\${name}
    let curDir = _path.default.join(dir, name);
    if (_fs.default.existsSync(curDir)) return curDir;
    curDir = _path.default.join(dir, 'src', name);
    if (_fs.default.existsSync(curDir)) return curDir;
    return null;
}`;

  const replacePatternCJS = `function findDir(dir, name) {
    // prioritize ./src/\${name} over ./\${name} to support Python backend in ./app
    let srcDir = _path.default.join(dir, 'src', name);
    if (_fs.default.existsSync(srcDir)) return srcDir;
    let curDir = _path.default.join(dir, name);
    if (_fs.default.existsSync(curDir)) return curDir;
    return null;
}`;

  const searchPatternESM = `export function findDir(dir, name) {
    // prioritize ./\${name} over ./src/\${name}
    let curDir = path.join(dir, name);
    if (fs.existsSync(curDir)) return curDir;
    curDir = path.join(dir, 'src', name);
    if (fs.existsSync(curDir)) return curDir;
    return null;
}`;

  const replacePatternESM = `export function findDir(dir, name) {
    // prioritize ./src/\${name} over ./\${name} to support Python backend in ./app
    let srcDir = path.join(dir, 'src', name);
    if (fs.existsSync(srcDir)) return srcDir;
    let curDir = path.join(dir, name);
    if (fs.existsSync(curDir)) return curDir;
    return null;
}`;

  content = content.replace(searchPatternCJS, replacePatternCJS);
  content = content.replace(searchPatternESM, replacePatternESM);
  fs.writeFileSync(filePath, content, "utf-8");
  console.log(`Patched Next.js findDir in: ${filePath}`);
});
