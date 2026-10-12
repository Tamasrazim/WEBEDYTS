/*
 * What this does:
 * Starts WEBEDYTS on macOS and wires up the platform-specific app startup and shutdown path.
 */

#import <Cocoa/Cocoa.h>

#include "include/cef_application_mac.h"
#include "include/wrapper/cef_helpers.h"
#include "include/wrapper/cef_library_loader.h"

extern "C" int webedyts_run_main(int argc, char* argv[]);
extern "C" void webedyts_request_terminate();

@interface WebedytsApplication : NSApplication <CefAppProtocol> {
 @private
  BOOL handlingSendEvent_;
}
@end

@implementation WebedytsApplication

- (BOOL)isHandlingSendEvent {
  return handlingSendEvent_;
}

- (void)setHandlingSendEvent:(BOOL)handlingSendEvent {
  handlingSendEvent_ = handlingSendEvent;
}

- (void)sendEvent:(NSEvent*)event {
  CefScopedSendingEvent sendingEventScoper;
  [super sendEvent:event];
}

// Route Cocoa quit through CEF so Chromium can close the browser cleanly.
- (void)terminate:(id)sender {
  webedyts_request_terminate();
}

@end

int main(int argc, char* argv[]) {
  CefScopedLibraryLoader library_loader;
  if (!library_loader.LoadInMain()) {
    return 1;
  }

  @autoreleasepool {
    [WebedytsApplication sharedApplication];
    return webedyts_run_main(argc, argv);
  }
}
