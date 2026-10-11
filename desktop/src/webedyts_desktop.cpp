#include "include/cef_app.h"
#include "include/cef_browser_process_handler.h"
#include "include/cef_client.h"
#include "include/cef_download_handler.h"
#include "include/cef_download_item.h"
#include "include/cef_display_handler.h"
#include "include/cef_frame.h"
#include "include/cef_load_handler.h"
#include "include/cef_command_line.h"
#include "include/cef_path_util.h"
#include "include/cef_parser.h"
#include "include/views/cef_browser_view.h"
#include "include/views/cef_fill_layout.h"
#include "include/views/cef_window.h"

#include "../../src/security/license_guard.hpp"

#include <filesystem>
#include <fstream>
#include <cstdlib>
#include <iostream>
#include <string>
#include <system_error>

#if defined(_WIN32)
#include <windows.h>
#if defined(CEF_USE_BOOTSTRAP)
#include "include/cef_sandbox_win.h"
#endif
#endif

namespace {

CefRefPtr<CefWindow> g_main_window;

std::filesystem::path PathFromCefString(const CefString& value);

class EditorClient final : public CefClient,
                          public CefDownloadHandler,
                          public CefDisplayHandler,
                          public CefLoadHandler {
 public:
  EditorClient(bool smoke_test,
               CefString smoke_marker_path,
               CefString expected_url)
      : smoke_test_(smoke_test),
        smoke_marker_path_(smoke_marker_path),
        expected_url_(expected_url) {}

  CefRefPtr<CefLoadHandler> GetLoadHandler() override {
    return this;
  }

  void OnLoadEnd(CefRefPtr<CefBrowser> /*browser*/,
                 CefRefPtr<CefFrame> frame,
                 int /*http_status_code*/) override {
    if (!IsSmokeTestMainFrame(frame)) {
      return;
    }

    const std::string loaded_url = frame->GetURL().ToString();
    const std::string expected_url = expected_url_.ToString();
    FinishSmokeTest(
        loaded_url == expected_url ? "loaded" : "unexpected_url",
        loaded_url);
  }

  void OnLoadError(CefRefPtr<CefBrowser> /*browser*/,
                   CefRefPtr<CefFrame> frame,
                   ErrorCode error_code,
                   const CefString& error_text,
                   const CefString& failed_url) override {
    if (!IsSmokeTestMainFrame(frame)) {
      return;
    }

    std::cerr << "WEBEDYTS startup test could not load the editor page ("
              << error_code << "): " << error_text.ToString() << "\n";
    FinishSmokeTest("load_error", failed_url.ToString());
  }
  CefRefPtr<CefDownloadHandler> GetDownloadHandler() override {
    return this;
  }

  CefRefPtr<CefDisplayHandler> GetDisplayHandler() override {
    return this;
  }

  void SetWindow(CefWindow* window) {
    window_ = window;
  }

  void OnTitleChange(CefRefPtr<CefBrowser> /*browser*/,
                     const CefString& title) override {
    if (window_) {
      window_->SetTitle(title.empty() ? CefString("WEBEDYTS") : title);
    }
  }

  bool OnBeforeDownload(
      CefRefPtr<CefBrowser> /*browser*/,
      CefRefPtr<CefDownloadItem> /*download_item*/,
      const CefString& suggested_name,
      CefRefPtr<CefBeforeDownloadCallback> callback) override {
    if (!callback) {
      return false;
    }

    // Use the operating system's Save As dialog for exported websites and media.
    callback->Continue(suggested_name, true);
    return true;
  }

  void OnDownloadUpdated(
      CefRefPtr<CefBrowser> /*browser*/,
      CefRefPtr<CefDownloadItem> download_item,
      CefRefPtr<CefDownloadItemCallback> /*callback*/) override {
    if (!download_item) {
      return;
    }

    if (download_item->IsComplete()) {
      std::cerr << "WEBEDYTS saved "
                << download_item->GetReceivedBytes() << " bytes to "
                << download_item->GetFullPath().ToString() << "\n";
    } else if (download_item->IsCanceled()) {
      std::cerr << "WEBEDYTS export canceled by the user.\n";
    } else if (download_item->IsInterrupted()) {
      std::cerr << "WEBEDYTS export was interrupted. Reason: "
                << download_item->GetInterruptReason() << "\n";
    }
  }

 private:
  bool IsSmokeTestMainFrame(CefRefPtr<CefFrame> frame) const {
    return smoke_test_ && frame && frame->IsMain();
  }

  void FinishSmokeTest(const std::string& status, const std::string& url) {
    const auto marker_path = PathFromCefString(smoke_marker_path_);
    if (!marker_path.empty()) {
      std::ofstream marker(marker_path, std::ios::binary | std::ios::trunc);
      if (marker) {
        marker << "status=" << status << "\n";
        marker << "url=" << url << "\n";
      } else {
        std::cerr << "WEBEDYTS could not write its startup test marker.\n";
      }
    }

    if (g_main_window) {
      g_main_window->Close();
    } else {
      CefQuitMessageLoop();
    }
  }

  bool smoke_test_ = false;
  CefString smoke_marker_path_;
  CefString expected_url_;
  CefWindow* window_ = nullptr;  // Owned by CEF; cleared before window teardown.

  IMPLEMENT_REFCOUNTING(EditorClient);
};

class EditorBrowserViewDelegate final : public CefBrowserViewDelegate {
 public:
  cef_runtime_style_t GetBrowserRuntimeStyle() override {
    return CEF_RUNTIME_STYLE_ALLOY;
  }

 private:
  IMPLEMENT_REFCOUNTING(EditorBrowserViewDelegate);
};

class EditorWindowDelegate final : public CefWindowDelegate {
 public:
  EditorWindowDelegate(CefRefPtr<EditorClient> client, CefString start_url)
      : client_(client), start_url_(start_url) {}

  CefRect GetInitialBounds(CefRefPtr<CefWindow> /*window*/) override {
    return CefRect(60, 50, 1440, 900);
  }

  void OnWindowCreated(CefRefPtr<CefWindow> window) override {
    client_->SetWindow(window.get());
    CefBrowserSettings browser_settings;
    browser_view_ = CefBrowserView::CreateBrowserView(
        client_, start_url_, browser_settings, nullptr, nullptr,
        new EditorBrowserViewDelegate());
    if (!browser_view_) {
      window->Close();
      return;
    }

    window->SetTitle("WEBEDYTS");
    window->SetToFillLayout();
    window->AddChildView(browser_view_);
    window->Show();
    browser_view_->RequestFocus();
  }

  bool CanClose(CefRefPtr<CefWindow> /*window*/) override {
    if (!browser_view_) {
      return true;
    }
    const auto browser = browser_view_->GetBrowser();
    return !browser || browser->GetHost()->TryCloseBrowser();
  }

  cef_runtime_style_t GetWindowRuntimeStyle() override {
    return CEF_RUNTIME_STYLE_ALLOY;
  }

  void OnWindowDestroyed(CefRefPtr<CefWindow> /*window*/) override {
    client_->SetWindow(nullptr);
    browser_view_ = nullptr;
    g_main_window = nullptr;
    CefQuitMessageLoop();
  }

 private:
  CefRefPtr<EditorClient> client_;
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

  void OnBeforeCommandLineProcessing(
      const CefString& process_type,
      CefRefPtr<CefCommandLine> command_line) override {
    // The Views API is needed by the native window and browser-view classes.
    if (process_type.empty()) {
      command_line->AppendSwitch("use-views");
      smoke_test_ = command_line->HasSwitch("webedyts-smoke-test");
      if (smoke_test_) {
        smoke_marker_path_ =
            command_line->GetSwitchValue("webedyts-smoke-test-marker");
      }
    }
  }

  void OnContextInitialized() override {
    g_main_window = CefWindow::CreateTopLevelWindow(
        new EditorWindowDelegate(
            new EditorClient(smoke_test_, smoke_marker_path_, start_url_),
            start_url_));
    if (!g_main_window) {
      std::cerr << "WEBEDYTS could not create its desktop window.\n";
      CefQuitMessageLoop();
    }
  }

 private:
  CefString start_url_;
  bool smoke_test_ = false;
  CefString smoke_marker_path_;

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
  ReplaceAll(escaped, "%3A", ":");
  ReplaceAll(escaped, "%3a", ":");

#if defined(_WIN32)
  return "file:///" + escaped;
#else
  return "file://" + escaped;
#endif
}

std::filesystem::path DefaultUserDataRoot() {
#if defined(_WIN32)
  const wchar_t* local_app_data = _wgetenv(L"LOCALAPPDATA");
  if (local_app_data && *local_app_data) {
    return std::filesystem::path(local_app_data) / "WEBEDYTS";
  }
#else
  const char* xdg_config_home = std::getenv("XDG_CONFIG_HOME");
  if (xdg_config_home && *xdg_config_home) {
    return std::filesystem::path(xdg_config_home) / "WEBEDYTS";
  }

  const char* home = std::getenv("HOME");
  if (home && *home) {
#if defined(__APPLE__)
    return std::filesystem::path(home) / "Library" / "Application Support" /
           "WEBEDYTS";
#else
    return std::filesystem::path(home) / ".config" / "WEBEDYTS";
#endif
  }
#endif

  std::error_code error;
  const auto temporary = std::filesystem::temp_directory_path(error);
  if (error) {
    return {};
  }
  return temporary / "WEBEDYTS";
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
    user_data = DefaultUserDataRoot();
  } else {
    user_data = PathFromCefString(data_dir) / "WEBEDYTS";
  }

  if (user_data.empty()) {
    std::cerr << "WEBEDYTS could not determine a writable user-data directory.\\n";
    return false;
  }

  std::error_code error;
  if (!std::filesystem::is_regular_file(editor_html, error) || error) {
    std::cerr << "WEBEDYTS could not find its bundled editor at:\n"
              << PathUtf8(editor_html) << "\n"
              << "The application package is incomplete.\n";
    return false;
  }

  error.clear();
  std::filesystem::create_directories(user_data / "Cache", error);
  if (error) {
    std::cerr << "WEBEDYTS could not create its browser cache directory: "
              << error.message() << "\n";
    return false;
  }

  error.clear();
  std::filesystem::create_directories(user_data / "Logs", error);
  if (error) {
    std::cerr << "WEBEDYTS could not create its log directory: "
              << error.message() << "\n";
    return false;
  }

  return true;
}

int RunWebedyts(const CefMainArgs& main_args, void* sandbox_info) {
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
  CefString(&settings.log_file) = PathUtf8(user_data / "Logs" / "webedyts.log");
  CefString(&settings.cache_path) = PathUtf8(user_data / "Cache");

#if defined(_WIN32) || defined(__linux__)
  // The CEF resource packs and locale directory are staged beside the app.
  CefString(&settings.resources_dir_path) = PathUtf8(executable_dir);
  CefString(&settings.locales_dir_path) =
      PathUtf8(executable_dir / "locales");
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

#if defined(__APPLE__)
extern "C" void webedyts_request_terminate() {
  if (g_main_window) {
    g_main_window->Close();
  } else {
    CefQuitMessageLoop();
  }
}

extern "C" int webedyts_run_main(int argc, char* argv[]) {
  return RunWebedyts(CefMainArgs(argc, argv), nullptr);
}
#endif

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
#elif !defined(__APPLE__)
int main(int argc, char* argv[]) {
  return RunWebedyts(CefMainArgs(argc, argv), nullptr);
}
#endif
