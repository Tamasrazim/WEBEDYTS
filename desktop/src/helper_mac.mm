#include "include/cef_app.h"

#if defined(CEF_USE_SANDBOX)
#include "include/cef_sandbox_mac.h"
#endif

#include "include/wrapper/cef_library_loader.h"
#include "../../src/security/license_guard.hpp"

int main(int argc, char* argv[]) {
  if (!webedyts::security::verify_embedded_license_notice()) {
    return 2;
  }

#if defined(CEF_USE_SANDBOX)
  CefScopedSandboxContext sandbox_context;
  if (!sandbox_context.Initialize(argc, argv)) {
    return 1;
  }
#endif

  CefScopedLibraryLoader library_loader;
  if (!library_loader.LoadInHelper()) {
    return 1;
  }

  CefMainArgs main_args(argc, argv);
  return CefExecuteProcess(main_args, nullptr, nullptr);
}
