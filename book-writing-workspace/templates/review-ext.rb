# review-ext.rb — Auto-wrap long code lines in Re:VIEW PDF output
#
# Place this file next to config.yml in your Re:VIEW project root.
# Requires: gem install unicode-display_width
#
# Adjust WRAP_WIDTH constants to match your page layout:
#   10pt / 40zw → 76
#    9pt / 43zw → 82

module ReVIEW
  module LATEXBuilderOverride
    require 'unicode/display_width'
    require 'unicode/display_width/string_ext'

    CR = "\u{21B5}" # ↵ continuation marker

    # Normal code blocks
    WRAP_WIDTH = 82
    WRAP_WIDTH_COLUMN = 65

    # Line-numbered code blocks
    WRAP_WIDTH_NUM = 65
    WRAP_WIDTH_NUM_COLUMN = 60

    # Scale factor for CJK characters (adjust if needed)
    ZWSCALE = 0.875

    def split_line(s, n)
      a = []
      l = ''
      w = 0
      s.each_char do |c|
        cw = c.display_width(2)
        cw *= ZWSCALE if cw == 2
        if w + cw > n
          a.push(l)
          l = c
          w = cw
        else
          l << c
          w += cw
        end
      end
      a.push(l)
      a
    end

    def code_line(type, line, idx, id, caption, lang)
      n = @doc_status[:column] ? WRAP_WIDTH_COLUMN : WRAP_WIDTH
      a = split_line(unescape(detab(line)), n)
      escape(a.join("\x01\n")).gsub("\x01", CR) + "\n"
    end

    def code_line_num(type, line, first_line_num, idx, id, caption, lang)
      n = @doc_status[:column] ? WRAP_WIDTH_NUM_COLUMN : WRAP_WIDTH_NUM
      a = split_line(unescape(detab(line)), n)
      (idx + first_line_num).to_s.rjust(2) + ': ' + escape(a.join("\x01\n    ")).gsub("\x01", CR) + "\n"
    end
  end

  class LATEXBuilder
    prepend LATEXBuilderOverride
  end
end
