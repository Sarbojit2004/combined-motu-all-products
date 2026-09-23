import { Config } from "@remotion/cli/config";

Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);
Config.setEntryPoint("./src/index.ts");
Config.setChromiumOpenGlRenderer("angle");

// This environment's network policy blocks Remotion's Chrome Headless Shell
// download, but a Chromium is already installed for Playwright. Point Remotion
// at that instead of trying to fetch one.
const LOCAL_CHROME = "/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell";
Config.setBrowserExecutable(process.env.REMOTION_CHROME ?? LOCAL_CHROME);
