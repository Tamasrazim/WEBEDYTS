#include "include/cef_app.h"
#include "include/cef_browser_process_handler.h"
#include "include/cef_client.h"
#include "include/cef_path_util.h"
#include "include/cef_parser.h"
#include "include/views/cef_browser_view.h"
#include "include/views/cef_fill_layout.h"
#include "include/views/cef_window.h"

#include "../../src/security/license_guard.hpp"

#include <filesystem>
#include <iostream>
#include <string>
#include <system_error>

#if defined(_WIN32)
#include <windows.h>
#if defined(CEF_USE_BOOTSTRAP)
#include "include/cef_sandbox_win.h"
#endif
#endif

#if defined(__APPLE__)
#include "include/wrapper/cef_library_loader.h"
#endif

namespace {

class EditorClient final : public CefClient {
 private:
  IMPLEMENT_REFCOUNTING(EditorClient);
};

class EditorWindowDelegate final : public CefWindowDelegate {
 public:
  EditorWindowDelegate(CefRefPtr<CefClient> client, CefString start_url)
      : client_(client), start_url_(start_url) {}

  CefRect GetInitialBounds(CefRefPtr<CefWindow> /*window*/) override {
    return CefRect(60, 50, 1440, 900);
  }

  void OnWindowCreated(CefRefPtr<CefWindow> window) override {
    CefBrowserSettings browser_settings;
    browser_view_ = CefBrowserView::CreateBrowserView(
        client_, start_url_, browser_settings, nullptr, nullptr, nullptr);
    if (!browser_view_) {
      CefQuitMessageLoop();
      return;
    }

    window->SetTitle("WEBEDYTS");
    window->AddChildView(browser_view_);
    window->SetLayout(std::make_unique<CefFillLayout>());
    window->Show();
  }

  void OnWindowDestroyed(CefRefPtr<CefWindow> /*window*/) override {
    browser_view_ = nullptr;
    CefQuitMessageLoop();
  }

 private:
  CefRefPtr<CefClient> client_;
  CefString start_url_;
  CefRefPtr<CefBrowserView> browser_view_;

  IMPLEMENT_REFCOUNTING(EditorWindowDelegate);
};

class WebedytsApp final : public CefApp,
                          public CefBrowserProcessHandler {
 public:
  explicit WebedytsApp(CefString start_url) : start_url_(start_url) {}

  CefRefPtr<CefBrowserProcessHandler> GetBrowserProcessHandler() override {
    return this;
  }

  void OnContextInitialized() override {
    CefWindow::CreateTopLevelWindow(
        new EditorWindowDelegate(new EditorClient(), start_url_));
  }

 private:
  CefString start_url_;

  IMPLEMENT_REFCOUNTING(WebedytsApp);
};

void ReplaceAll(std::string& text,
                const std::string& search,
                const std::string& replacement) {
  std::string::size_type position = 0;
  while ((position = text.find(search, position)) != std::string::npos) {
    text.replace(position, search.size(), replacement);
    position += replacement.size();
  }
}

std::filesystem::path PathFromCefString(const CefString& value) {
#if defined(_WIN32)
  return std::filesystem::path(value.ToWString());
#else
  return std::filesystem::path(value.ToString());
#endif
}

std::string PathUtf8(const std::filesystem::path& path) {
  const auto value = path.u8string();
  return std::string(reinterpret_cast<const char*>(value.data()), value.size());
}

std::string FileUrl(const std::filesystem::path& file_path) {
  std::string escaped = CefURIEncode(PathUtf8(file_path), false).ToString();
  ReplaceAll(escaped, "%2F", "/");
  ReplaceAll(escaped, "%2f", "/");

#if defined(_WIN32)
  return "file:///" + escaped;
#else
  return "file://" + escaped;
#endif
}

bool GetRuntimePaths(std::filesystem::path& executable_dir,
                     std::filesystem::path& editor_html,
                     std::filesystem::path& user_data) {
  CefString exe_dir;
  CefString data_dir;
  if (!CefGetPath(PK_DIR_EXE, exe_dir) || exe_dir.empty()) {
    std::cerr << "WEBEDYTS could not locate its application directory.\n";
    return false;
  }

  executable_dir = PathFromCefString(exe_dir);

#if defined(__APPLE__)
  editor_html = (executable_dir / ".." / "Resources" / "app" / "index.html")
                    .lexically_normal();
#else
  editor_html = executable_dir / "resources" / "app" / "index.html";
#endif

  if (!CefGetPath(PK_USER_DATA, data_dir) || data_dir.empty()) {
    user_data = executable_dir / "user-data";
  } else {
    user_data = PathFromCefString(data_dir) / "WEBEDYTS";
  }

  if (!std::filesystem::is_regular_file(editor_html)) {
    std::cerr << "WEBEDYTS could not find its bundled editor at:\n"
              << PathUtf8(editor_html) << "\n"
              << "The application package is incomplete.\n";
    return false;
  }

  std::error_code error;
  std::filesystem::create_directories(user_data / "Cache", error);
  if (error) {
    std::cerr << "WEBEDYTS could not create its browser cache directory: "
              << error.message() << "\n";
    return false;
  }

  return true;
}

int RunWebedyts(const CefMainArgs& main_args, void* sandbox_info) {
#if defined(__APPLE__)
  CefScopedLibraryLoader library_loader;
  if (!library_loader.LoadInMain()) {
    std::cerr << "WEBEDYTS could not load the Chromium framework.\n";
    return 1;
  }
#endif

  if (!webedyts::security::verify_embedded_license_notice()) {
    std::cerr << "WEBEDYTS license integrity check failed.\n";
    return 2;
  }

  CefRefPtr<CefApp> process_app = new WebedytsApp("");
  const int process_exit_code =
      CefExecuteProcess(main_args, process_app, sandbox_info);
  if (process_exit_code >= 0) {
    return process_exit_code;
  }

  std::filesystem::path executable_dir;
  std::filesystem::path editor_html;
  std::filesystem::path user_data;
  if (!GetRuntimePaths(executable_dir, editor_html, user_data)) {
    return 3;
  }

  CefSettings settings;
  settings.log_severity = LOGSEVERITY_WARNING;
  CefString(&settings.cache_path) = PathUtf8(user_data / "Cache");

#if defined(_WIN32) || defined(__linux__)
  // The CEF resource packs and locale directory are staged beside the app.
  CefString(&settings.resources_dir_path) = PathUtf8(executable_dir);
  CefString(&settings.locales_dir_path) =
      PathUtf8(executable_dir / "locales");
#endif

#if defined(__APPLE__)
  const auto helper =
      (executable_dir / ".." / "Frameworks" / "WEBEDYTS Helper.app" /
       "Contents" / "MacOS" / "WEBEDYTS Helper").lexically_normal();
  CefString(&settings.browser_subprocess_path) = PathUtf8(helper);
#endif

  CefRefPtr<CefApp> app = new WebedytsApp(FileUrl(editor_html));
  if (!CefInitialize(main_args, settings, app, sandbox_info)) {
    std::cerr << "WEBEDYTS could not initialize the Chromium runtime.\n";
    return 4;
  }

  CefRunMessageLoop();
  CefShutdown();
  return 0;
}

}  // namespace

#if defined(_WIN32) && defined(CEF_USE_BOOTSTRAP)
CEF_BOOTSTRAP_EXPORT int RunWinMain(HINSTANCE instance,
                                    LPTSTR /*command_line*/,
                                    int /*show_command*/,
                                    void* sandbox_info,
                                    cef_version_info_t* /*version_info*/) {
  return RunWebedyts(CefMainArgs(instance), sandbox_info);
}
#elif defined(_WIN32)
int APIENTRY wWinMain(HINSTANCE instance,
                      HINSTANCE /*previous_instance*/,
                      LPTSTR /*command_line*/,
                      int /*show_command*/) {
  return RunWebedyts(CefMainArgs(instance), nullptr);
}
#else
int main(int argc, char* argv[]) {
  return RunWebedyts(CefMainArgs(argc, argv), nullptr);
}
#endif
