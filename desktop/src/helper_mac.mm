#include "include/cef_app.h"
#include "../../src/security/license_guard.hpp"
#include "include/wrapper/cef_library_loader.h"

int main(int argc, char* argv[]) {
  if (!webedyts::security::verify_embedded_license_notice()) {
    return 2;
  }

  CefScopedLibraryLoader library_loader;
  if (!library_loader.LoadInHelper()) {
    return 1;
  }

  CefMainArgs main_args(argc, argv);
  return CefExecuteProcess(main_args, nullptr, nullptr);
}
