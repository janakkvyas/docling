-- pandoc filter for the Vallabh Vani booklets (see vallabh_vani/booklets/SPEC.md)
-- * fenced divs with a class get the Word paragraph style of that name (::: verse -> "Verse")
-- * "* * *" (a horizontal rule) starts a new page; two in a row leave a blank page
-- * Hindi booklets: bold text becomes the 13 pt "Quotation" character style, as in the exemplar
-- * Hindi booklets: occasion and speaker from the metadata complete the title page

local STYLES = {
  ["verse"] = "Verse", ["verse-prose"] = "Verse Prose", ["colophon"] = "Colophon",
  ["figure"] = "Figure", ["pada"] = "Pada", ["pada-heading"] = "Pada Heading",
  ["chart-text"] = "Chart Text", ["center"] = "Center", ["label"] = "Label",
  ["label-left"] = "Label Left", ["verse-iast"] = "Verse IAST", ["commentary"] = "Commentary",
  ["signature"] = "Signature",
}
local PAIRED = { ["title"] = { "Book Title", "Book Title IAST" }, ["author"] = { "Book Author", "Book Author IAST" } }
local kind = "hindi"

local function styled(blocks, name)
  return pandoc.Div(blocks, pandoc.Attr("", {}, { ["custom-style"] = name }))
end

local function meta(m)
  if m.booklet then kind = pandoc.utils.stringify(m.booklet) end
end

local function div(el)
  for _, c in ipairs(el.classes) do
    if STYLES[c] then
      return styled(el.content, STYLES[c])
    end
    if PAIRED[c] then
      local out, i = {}, 0
      for _, b in ipairs(el.content) do
        i = i + 1
        table.insert(out, styled({ b }, PAIRED[c][math.min(i, 2)]))
      end
      return out
    end
  end
end

local function hr()
  return pandoc.RawBlock("openxml", '<w:p><w:pPr><w:pStyle w:val="PageBreak"/></w:pPr></w:p>')
end

local function strong(el)
  if kind == "hindi" then
    return pandoc.Span(el.content, pandoc.Attr("", {}, { ["custom-style"] = "Quotation" }))
  end
end

local function doc(d)
  if kind == "english" then
    d.meta.title = nil
    d.meta.subtitle = nil
  end
  if kind == "hindi" then
    local front = {}
    local occ = d.meta.occasion
    if occ then
      if pandoc.utils.type(occ) == "List" then
        local inl = {}
        for i, line in ipairs(occ) do
          if i > 1 then table.insert(inl, pandoc.LineBreak()) end
          table.insert(inl, pandoc.Str(pandoc.utils.stringify(line)))
        end
        table.insert(front, styled({ pandoc.Para(inl) }, "Occasion"))
      else
        table.insert(front, styled({ pandoc.Para(pandoc.utils.stringify(occ)) }, "Occasion"))
      end
    end
    if d.meta.speaker then
      table.insert(front, styled({ pandoc.Para(pandoc.utils.stringify(d.meta.speaker)) }, "Speaker"))
    end
    for i = #front, 1, -1 do table.insert(d.blocks, 1, front[i]) end
  end
  return d
end

return {
  { Meta = meta },
  { Div = div, HorizontalRule = hr, Strong = strong },
  { Pandoc = doc },
}
