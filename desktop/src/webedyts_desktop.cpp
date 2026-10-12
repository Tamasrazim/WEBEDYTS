/*
 * What this does:
 * Hosts the editor in a native desktop window, connects browser events and downloads, and handles app-level startup and shutdown.
 */

#include "include/cef_app.h"
#include "include/cef_browser.h"
#include "include/cef_browser_process_handler.h"
#include "include/cef_client.h"
#include "include/cef_download_handler.h"
#include "include/cef_download_item.h"
#include "include/cef_display_handler.h"
#include "include/cef_frame.h"
#include "include/cef_load_handler.h"
#include "include/cef_life_span_handler.h"
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

#if !defined(_WIN32)
#include <unistd.h>
#endif

#if defined(_WIN32)
#include <windows.h>
#if defined(CEF_USE_BOOTSTRAP)
#include "include/cef_sandbox_win.h"
#endif
#endif

namespace {

CefRefPtr<CefWindow> g_main_window;

#if defined(_WIN32)
HWND g_native_window = nullptr;
CefRefPtr<CefBrowser> g_native_browser;
bool g_native_close_requested = false;
#endif

std::filesystem::path PathFromCefString(const CefString& value);
#if defined(_WIN32)
void ResizeNativeBrowser();
#endif

void TraceStartup(const std::string& message) {
  const char* trace_path = std::getenv("WEBEDYTS_STARTUP_TRACE_PATH");
  if (!trace_path || !*trace_path) {
    return;
  }
  std::ofstream trace(trace_path, std::ios::app);
  if (!trace) {
    return;
  }
#if defined(_WIN32)
  const auto process_id = GetCurrentProcessId();
#else
  const auto process_id = getpid();
#endif
  trace << "[" << process_id << "] " << message << "\n";
}

class EditorClient final : public CefClient,
                          public CefDownloadHandler,
                          public CefDisplayHandler,
                          public CefLoadHandler,
                          public CefLifeSpanHandler {
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

  CefRefPtr<CefLifeSpanHandler> GetLifeSpanHandler() override {
    return this;
  }

  void OnAfterCreated(CefRefPtr<CefBrowser> browser) override {
#if defined(_WIN32)
    if (browser && !browser->IsPopup()) {
      g_native_browser = browser;
      TraceStartup("main browser created");
      ResizeNativeBrowser();
    }
#else
    (void)browser;
#endif
  }

  void OnBeforeClose(CefRefPtr<CefBrowser> browser) override {
#if defined(_WIN32)
    if (browser && !browser->IsPopup()) {
      g_native_browser = nullptr;
      TraceStartup("main browser closed");
      if (g_native_window) {
        PostMessageW(g_native_window, WM_CLOSE, 0, 0);
      } else {
        CefQuitMessageLoop();
      }
    }
#else
    (void)browser;
#endif
  }

  void OnLoadEnd(CefRefPtr<CefBrowser> /*browser*/,
                 CefRefPtr<CefFrame> frame,
                 int /*http_status_code*/) override {
    if (!IsSmokeTestMainFrame(frame)) {
      return;
    }

    TraceStartup("main-frame load completed");
    if (IsPreviewSafetyTest()) {
      TraceStartup("waiting for in-browser preview safety regression result");
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

    TraceStartup("main-frame load error");
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
    const CefString safe_title = title.empty() ? CefString("WEBEDYTS") : title;
#if defined(_WIN32)
    if (g_native_window) {
      const std::wstring wide_title = safe_title.ToWString();
      SetWindowTextW(g_native_window, wide_title.c_str());
    }
#else
    if (window_) {
      window_->SetTitle(safe_title);
    }
#endif
    const std::string changed_title = safe_title.ToString();
    const std::string test_prefix = "WEBEDYTS_PREVIEW_TEST_RESULT:";
    if (IsPreviewSafetyTest() && changed_title.rfind(test_prefix, 0) == 0) {
      const bool passed = changed_title == "WEBEDYTS_PREVIEW_TEST_RESULT:PASS";
      TraceStartup(passed ? "in-browser preview regression test passed"
                          : "in-browser preview regression test failed");
      FinishSmokeTest(passed ? "loaded" : "test_failed", expected_url_.ToString());
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
  bool IsPreviewSafetyTest() const {
    return smoke_test_ &&
        expected_url_.ToString().find("webedyts_preview_safety_test=1") != std::string::npos;
  }

  bool IsSmokeTestMainFrame(CefRefPtr<CefFrame> frame) const {
    return smoke_test_ && frame && frame->IsMain();
  }

  void FinishSmokeTest(const std::string& status, const std::string& url) {
    TraceStartup("finishing smoke test with status=" + status);
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

#if defined(_WIN32)
    if (g_native_window) {
      PostMessageW(g_native_window, WM_CLOSE, 0, 0);
    } else {
      CefQuitMessageLoop();
    }
#else
    if (g_main_window) {
      g_main_window->Close();
    } else {
      CefQuitMessageLoop();
    }
#endif
  }

  bool smoke_test_ = false;
  CefString smoke_marker_path_;
  CefString expected_url_;
  CefWindow* window_ = nullptr;  // Owned by CEF; cleared before window teardown.

  IMPLEMENT_REFCOUNTING(EditorClient);
};

#if defined(_WIN32)

void ResizeNativeBrowser() {
  if (!g_native_window || !g_native_browser) {
    return;
  }
  HWND browser_window = g_native_browser->GetHost()->GetWindowHandle();
  if (!browser_window) {
    return;
  }
  RECT client_rect{};
  if (!GetClientRect(g_native_window, &client_rect)) {
    return;
  }
  const int width = client_rect.right - client_rect.left;
  const int height = client_rect.bottom - client_rect.top;
  SetWindowPos(browser_window, nullptr, 0, 0, width, height,
               SWP_NOZORDER | SWP_NOACTIVATE);
}

LRESULT CALLBACK NativeWindowProc(HWND window,
                                  UINT message,
                                  WPARAM wparam,
                                  LPARAM lparam) {
  switch (message) {
    case WM_SIZE:
      ResizeNativeBrowser();
      return 0;

    case WM_CLOSE:
      if (g_native_browser) {
        if (!g_native_close_requested) {
          g_native_close_requested = true;
          TraceStartup("requesting browser close");
          g_native_browser->GetHost()->CloseBrowser(false);
        }
        return 0;
      }
      DestroyWindow(window);
      return 0;

    case WM_DESTROY:
      if (g_native_window == window) {
        g_native_window = nullptr;
        g_native_close_requested = false;
      }
      TraceStartup("native window destroyed");
      CefQuitMessageLoop();
      return 0;

    default:
      return DefWindowProcW(window, message, wparam, lparam);
  }
}

bool CreateNativeMainWindow(CefRefPtr<EditorClient> client,
                            const CefString& start_url) {
  const HINSTANCE instance = GetModuleHandleW(nullptr);
  constexpr wchar_t kWindowClass[] = L"WEBEDYTSNativeMainWindow";

  WNDCLASSEXW window_class{};
  window_class.cbSize = sizeof(window_class);
  window_class.style = CS_HREDRAW | CS_VREDRAW;
  window_class.lpfnWndProc = NativeWindowProc;
  window_class.hInstance = instance;
  window_class.hCursor = LoadCursorW(nullptr, IDC_ARROW);
  window_class.hIcon = LoadIconW(nullptr, IDI_APPLICATION);
  window_class.hbrBackground =
      reinterpret_cast<HBRUSH>(static_cast<INT_PTR>(COLOR_WINDOW + 1));
  window_class.lpszClassName = kWindowClass;

  if (!RegisterClassExW(&window_class) &&
      GetLastError() != ERROR_CLASS_ALREADY_EXISTS) {
    std::cerr << "WEBEDYTS could not register its Windows window class.\n";
    return false;
  }

  HWND window = CreateWindowExW(
      0, kWindowClass, L"WEBEDYTS", WS_OVERLAPPEDWINDOW,
      60, 50, 1440, 900, nullptr, nullptr, instance, nullptr);
  if (!window) {
    std::cerr << "WEBEDYTS could not create its Windows window.\n";
    return false;
  }

  g_native_window = window;
  g_native_close_requested = false;
  ShowWindow(window, SW_SHOW);
  UpdateWindow(window);

  RECT client_rect{};
  if (!GetClientRect(window, &client_rect)) {
    DestroyWindow(window);
    return false;
  }

  const CefRect browser_rect(
      0, 0, client_rect.right - client_rect.left,
      client_rect.bottom - client_rect.top);
  CefWindowInfo window_info;
  window_info.SetAsChild(window, browser_rect);
  CefBrowserSettings browser_settings;
  TraceStartup("before creating native Windows browser");
  if (!CefBrowserHost::CreateBrowser(
          window_info, client, start_url, browser_settings, nullptr, nullptr)) {
    std::cerr << "WEBEDYTS could not create its Windows browser.\n";
    DestroyWindow(window);
    return false;
  }

  TraceStartup("native Windows browser creation accepted");
  return true;
}

#endif  // defined(_WIN32)

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
    TraceStartup("window delegate entered");
    client_->SetWindow(window.get());
    CefBrowserSettings browser_settings;
    TraceStartup("before CreateBrowserView");
    browser_view_ = CefBrowserView::CreateBrowserView(
        client_, start_url_, browser_settings, nullptr, nullptr,
        new EditorBrowserViewDelegate());
    TraceStartup(browser_view_ ? "CreateBrowserView succeeded"
                               : "CreateBrowserView returned null");
    if (!browser_view_) {
      window->Close();
      return;
    }

    TraceStartup("before adding browser view to window");
    window->SetTitle("WEBEDYTS");
    window->SetToFillLayout();
    window->AddChildView(browser_view_);
    TraceStartup("before showing window");
    window->Show();
    TraceStartup("before requesting browser focus");
    browser_view_->RequestFocus();
    TraceStartup("window shown and browser focus requested");
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

  void SetStartUrl(const CefString& start_url) {
    std::string url = start_url.ToString();
    if (preview_safety_test_) {
      url += (url.find('?') == std::string::npos ? "?" : "&");
      url += "webedyts_preview_safety_test=1";
    }
    start_url_ = url;
  }

  CefRefPtr<CefBrowserProcessHandler> GetBrowserProcessHandler() override {
    return this;
  }

  void OnBeforeCommandLineProcessing(
      const CefString& process_type,
      CefRefPtr<CefCommandLine> command_line) override {
    if (process_type.empty()) {
#if !defined(_WIN32)
      // CEF Views powers the Linux/macOS shell. Windows uses a native HWND
      // parent because the CEF Views window path crashes under bootstrap.
      command_line->AppendSwitch("use-views");
#endif
      smoke_test_ = command_line->HasSwitch("webedyts-smoke-test");
      preview_safety_test_ = command_line->HasSwitch("webedyts-preview-safety-test");
      if (smoke_test_) {
        smoke_marker_path_ =
            command_line->GetSwitchValue("webedyts-smoke-test-marker");
      }
    }
  }

  void OnContextInitialized() override {
    TraceStartup("CEF context initialized");
#if defined(_WIN32)
    TraceStartup("before creating native Windows window");
    if (!CreateNativeMainWindow(
            new EditorClient(smoke_test_, smoke_marker_path_, start_url_),
            start_url_)) {
      TraceStartup("native Windows window creation failed");
      CefQuitMessageLoop();
    }
#else
    TraceStartup("before CreateTopLevelWindow");
    g_main_window = CefWindow::CreateTopLevelWindow(
        new EditorWindowDelegate(
            new EditorClient(smoke_test_, smoke_marker_path_, start_url_),
            start_url_));
    TraceStartup(g_main_window ? "CreateTopLevelWindow succeeded"
                               : "CreateTopLevelWindow returned null");
    if (!g_main_window) {
      std::cerr << "WEBEDYTS could not create its desktop window.\n";
      CefQuitMessageLoop();
    }
#endif
  }

 private:
  CefString start_url_;
  bool smoke_test_ = false;
  bool preview_safety_test_ = false;
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
  // CEF expects forward slashes in file URLs. Encoding a Windows path before
  // normalizing its separators turns every backslash into %5C and breaks load.
  std::string path = PathUtf8(file_path);
  ReplaceAll(path, "\\", "/");

  std::string escaped = CefURIEncode(path, false).ToString();
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
  TraceStartup("RunWebedyts entered");
  if (!webedyts::security::verify_embedded_license_notice()) {
    std::cerr << "WEBEDYTS license integrity check failed.\n";
    return 2;
  }

  TraceStartup("license integrity check passed");

  // CEF expects the same application object to be supplied to both
  // CefExecuteProcess and CefInitialize. The URL is filled in only after the
  // browser process is identified, so child processes can exit cleanly first.
  CefRefPtr<WebedytsApp> app = new WebedytsApp("");
  TraceStartup("before CefExecuteProcess");
  const int process_exit_code =
      CefExecuteProcess(main_args, app, sandbox_info);
  TraceStartup("CefExecuteProcess returned " + std::to_string(process_exit_code));
  if (process_exit_code >= 0) {
    return process_exit_code;
  }

  std::filesystem::path executable_dir;
  std::filesystem::path editor_html;
  std::filesystem::path user_data;
  TraceStartup("before GetRuntimePaths");
  if (!GetRuntimePaths(executable_dir, editor_html, user_data)) {
    TraceStartup("GetRuntimePaths failed");
    return 3;
  }
  TraceStartup("GetRuntimePaths succeeded");

  CefSettings settings;
  settings.log_severity = LOGSEVERITY_WARNING;
#if defined(_WIN32) && defined(CEF_USE_BOOTSTRAP)
  // The bootstrap executable owns the application icon resource.
  settings.chrome_app_icon_id = 32512;  // IDI_APPLICATION
#endif
  CefString(&settings.log_file) = PathUtf8(user_data / "Logs" / "webedyts.log");
  CefString(&settings.cache_path) = PathUtf8(user_data / "Cache");

#if defined(_WIN32) || defined(__linux__)
  // The CEF resource packs and locale directory are staged beside the app.
  CefString(&settings.resources_dir_path) = PathUtf8(executable_dir);
  CefString(&settings.locales_dir_path) =
      PathUtf8(executable_dir / "locales");
#endif


  app->SetStartUrl(FileUrl(editor_html));
  TraceStartup("before CefInitialize");
  if (!CefInitialize(main_args, settings, app, sandbox_info)) {
    TraceStartup("CefInitialize returned false");
    std::cerr << "WEBEDYTS could not initialize the Chromium runtime.\n";
    return 4;
  }

  TraceStartup("CefInitialize returned true");
  TraceStartup("before CefRunMessageLoop");
  CefRunMessageLoop();
  TraceStartup("CefRunMessageLoop returned");
  CefShutdown();
  TraceStartup("CefShutdown returned");
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
