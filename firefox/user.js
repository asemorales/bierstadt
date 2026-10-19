// Bierstadt for Firefox. Firefox copies these into prefs.js on every start.

// Load chrome/userChrome.css and chrome/userContent.css.
user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);

// The default "System theme", so the chrome follows the room. A dark or
// coloured theme would pin it to one look.
user_pref("extensions.activeThemeID", "default-theme@mozilla.org");

// Let xfwm4 draw the title bar, so the window matches the Bierstadt frames.
user_pref("browser.tabs.inTitlebar", 0);

// New tab: the current room's painting and the search box, nothing else.
// bierstadt-mode writes chrome/userContent.css with the painting in it.
user_pref("browser.newtabpage.activity-stream.feeds.topsites", false);
user_pref("browser.newtabpage.activity-stream.feeds.section.topstories", false);
user_pref("browser.newtabpage.activity-stream.feeds.section.highlights", false);
user_pref("browser.newtabpage.activity-stream.showSponsored", false);
user_pref("browser.newtabpage.activity-stream.showSponsoredTopSites", false);
user_pref("browser.newtabpage.activity-stream.showWeather", false);
user_pref("browser.newtabpage.activity-stream.showSearch", true);
