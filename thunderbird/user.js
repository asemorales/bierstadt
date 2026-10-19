// Bierstadt for Thunderbird. Thunderbird copies these into prefs.js on every start.

// Load chrome/userChrome.css.
user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);

// Mail in Inter, even when an email asks for a generic serif; DM Mono for plain text.
user_pref("font.default.x-western", "sans-serif");
user_pref("font.name.sans-serif.x-western", "Inter");
user_pref("font.name.serif.x-western", "Inter");
user_pref("font.name.monospace.x-western", "DM Mono");

// Leave the message pane empty instead of showing the donation start page.
user_pref("mailnews.start_page.enabled", false);

// Let xfwm4 draw the title bar, so the window matches the Bierstadt frames.
user_pref("mail.tabs.drawInTitlebar", false);
