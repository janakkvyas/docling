-- Print each line of a verse block on its own line: inside block quotes, soft line breaks become hard ones.
function BlockQuote(el)
  return el:walk({ SoftBreak = function() return pandoc.LineBreak() end })
end
