-- Bierstadt colour scheme, after the bierstadt and bierstadt-dark desktop themes.
-- The greys come from themes/bierstadt/gtk-3.0/_palette.css and the few hues
-- from the terminal palettes in bierstadt-mode. Like the desktop, the screen
-- stays mostly ink on paper: hues mark strings, numbers and diagnostics only.
-- Follows `background`: dark is the dark room, light the paper room.

vim.cmd("highlight clear")
if vim.fn.exists("syntax_on") == 1 then vim.cmd("syntax reset") end
vim.g.colors_name = "bierstadt"

local rooms = {
  dark = {
    bg = "#191612", panel = "#25211C", hover = "#3A342D", rule = "#4D463E",
    frame = "#615950", mid = "#81786D", dim = "#9E958A", fg = "#EFE6D6",
    bright = "#FBF4E8",
    red = "#D0704F", green = "#9DB07A", yellow = "#D9B46A",
    blue = "#7FA3C2", magenta = "#B98AA2", cyan = "#86B5AE",
    add = "#262A1E", del = "#33201A", chg = "#2E2818",
  },
  light = {
    bg = "#F2ECDF", panel = "#ECE5D5", hover = "#E3DBC9", rule = "#DDD4C1",
    frame = "#C9BFAB", mid = "#9A9183", dim = "#6E6965", fg = "#231A15",
    bright = "#000000",
    red = "#B04A2A", green = "#5B6E3A", yellow = "#85651B",
    blue = "#2F5470", magenta = "#7D4B63", cyan = "#3E6F6A",
    add = "#E3E6CF", del = "#F0D9CC", chg = "#EDE2C2",
  },
}

local c = rooms[vim.o.background] or rooms.dark

local groups = {
  -- Editor chrome
  Normal       = { fg = c.fg, bg = c.bg },
  NormalFloat  = { fg = c.fg, bg = c.panel },
  FloatBorder  = { fg = c.frame, bg = c.panel },
  NormalNC     = { link = "Normal" },
  Cursor       = { fg = c.bg, bg = c.fg },
  CursorLine   = { bg = c.panel },
  CursorColumn = { link = "CursorLine" },
  ColorColumn  = { bg = c.panel },
  LineNr       = { fg = c.frame },
  CursorLineNr = { fg = c.fg },
  SignColumn   = { bg = c.bg },
  FoldColumn   = { fg = c.mid, bg = c.bg },
  Folded       = { fg = c.dim, bg = c.panel, italic = true },
  VertSplit    = { fg = c.rule, bg = c.bg },
  WinSeparator = { link = "VertSplit" },
  StatusLine   = { fg = c.fg, bg = c.panel },
  StatusLineNC = { fg = c.mid, bg = c.panel },
  TabLine      = { fg = c.dim, bg = c.panel },
  TabLineFill  = { bg = c.panel },
  TabLineSel   = { fg = c.fg, bg = c.bg, bold = true },
  Visual       = { bg = c.hover },
  VisualNOS    = { link = "Visual" },
  Search       = { fg = c.bg, bg = c.dim },
  IncSearch    = { fg = c.bg, bg = c.fg },
  CurSearch    = { link = "IncSearch" },
  Substitute   = { link = "IncSearch" },
  MatchParen   = { fg = c.bright, bg = c.hover, bold = true },
  Pmenu        = { fg = c.fg, bg = c.panel },
  PmenuSel     = { fg = c.bg, bg = c.fg },
  PmenuSbar    = { bg = c.panel },
  PmenuThumb   = { bg = c.mid },
  WildMenu     = { link = "PmenuSel" },
  NonText      = { fg = c.rule },
  EndOfBuffer  = { fg = c.bg },
  Whitespace   = { fg = c.rule },
  SpecialKey   = { fg = c.mid },
  Directory    = { fg = c.fg, bold = true },
  Title        = { fg = c.bright, bold = true },
  Question     = { fg = c.fg },
  MoreMsg      = { fg = c.dim },
  ModeMsg      = { fg = c.dim },
  ErrorMsg     = { fg = c.red },
  WarningMsg   = { fg = c.yellow },
  Conceal      = { fg = c.mid },
  SpellBad     = { sp = c.red, undercurl = true },
  SpellCap     = { sp = c.yellow, undercurl = true },
  SpellRare    = { sp = c.magenta, undercurl = true },
  SpellLocal   = { sp = c.cyan, undercurl = true },

  -- Syntax: mostly ink, with emphasis carried by weight and slant
  Comment      = { fg = c.dim, italic = true },
  Constant     = { fg = c.magenta },
  String       = { fg = c.green },
  Character    = { link = "String" },
  Number       = { fg = c.magenta },
  Boolean      = { link = "Number" },
  Float        = { link = "Number" },
  Identifier   = { fg = c.fg },
  Function     = { fg = c.bright },
  Statement    = { fg = c.fg, bold = true },
  Operator     = { fg = c.dim },
  PreProc      = { fg = c.cyan },
  Type         = { fg = c.fg, italic = true },
  Special      = { fg = c.yellow },
  Delimiter    = { fg = c.dim },
  Underlined   = { underline = true },
  Ignore       = { fg = c.rule },
  Error        = { fg = c.red },
  Todo         = { fg = c.bg, bg = c.yellow, bold = true },

  -- Diffs and git
  DiffAdd      = { bg = c.add },
  DiffDelete   = { fg = c.red, bg = c.del },
  DiffChange   = { bg = c.chg },
  DiffText     = { bg = c.hover, bold = true },
  diffAdded    = { fg = c.green },
  diffRemoved  = { fg = c.red },
  diffChanged  = { fg = c.yellow },

  -- Diagnostics
  DiagnosticError = { fg = c.red },
  DiagnosticWarn  = { fg = c.yellow },
  DiagnosticInfo  = { fg = c.blue },
  DiagnosticHint  = { fg = c.cyan },
  DiagnosticUnderlineError = { sp = c.red, undercurl = true },
  DiagnosticUnderlineWarn  = { sp = c.yellow, undercurl = true },
  DiagnosticUnderlineInfo  = { sp = c.blue, undercurl = true },
  DiagnosticUnderlineHint  = { sp = c.cyan, undercurl = true },

  -- Markdown, which reads like the website
  markdownH1         = { fg = c.bright, bold = true },
  markdownH2         = { fg = c.bright, bold = true },
  markdownHeadingDelimiter = { fg = c.mid },
  markdownCode       = { fg = c.yellow },
  markdownCodeBlock  = { fg = c.yellow },
  markdownUrl        = { fg = c.dim, underline = true },
  markdownLinkText   = { fg = c.fg, underline = true },
  markdownItalic     = { italic = true },
  markdownBold       = { bold = true },
}

for name, spec in pairs(groups) do
  vim.api.nvim_set_hl(0, name, spec)
end

-- The built-in :terminal uses the same ANSI colours as Xfce Terminal.
local term = {
  dark = { "#100D0A", "#D0704F", "#9DB07A", "#D9B46A", "#7FA3C2", "#B98AA2", "#86B5AE", "#E3D8C4",
           "#978A79", "#E08A6B", "#B3C496", "#E6C88A", "#9DBAD3", "#CDA4B8", "#A3C9C3", "#EFE6D6" },
  light = { "#231A15", "#B04A2A", "#5B6E3A", "#85651B", "#2F5470", "#7D4B63", "#3E6F6A", "#DDD4C1",
            "#6E6965", "#AA4A2B", "#5A6E38", "#82641A", "#3A6588", "#8E5672", "#3F716C", "#FFFFFF" },
}
for i, hex in ipairs(term[vim.o.background] or term.dark) do
  vim.g["terminal_color_" .. (i - 1)] = hex
end
