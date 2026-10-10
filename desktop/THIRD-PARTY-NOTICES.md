# Third-party runtime notices

WEBEDYTS desktop builds bundle the Chromium Embedded Framework (CEF) and its
Chromium runtime. The build must include the CEF `LICENSE.txt` file and
retain the required notices for Chromium and other components included in the
selected CEF distribution. CEF also exposes its bundled licence and credits
pages through `about:license` and `about:credits`.

Do not remove language packs, resource packs, runtime libraries, or licence
files merely to make a package look smaller. Each release should use the full
runtime for its target OS and CPU architecture, and should record the exact CEF
version and download source in its release notes.

CEF/Chromium are third-party components. Their terms apply to those components
and do not replace the WEBEDYTS proprietary notice for original WEBEDYTS code
and assets. Review the notices shipped with the selected CEF binary distribution
before redistributing a release.
