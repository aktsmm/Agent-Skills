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

    CR = ''

    # Normal code blocks
    WRAP_WIDTH = 82
    WRAP_WIDTH_COLUMN = 65

    # Line-numbered code blocks
    WRAP_WIDTH_NUM = 65
    WRAP_WIDTH_NUM_COLUMN = 60

    # Scale factor for CJK characters (adjust if needed)
    ZWSCALE = 0.875

    BREAKABLE_CHARS = [
      ' ', "\t", '/', '-', '_', '.', ',', ':', ';', ')', ']', '}',
      '>', '、', '。', '：', '）', '】', '』', '」'
    ].freeze

    def breakable_char?(char)
      BREAKABLE_CHARS.include?(char)
    end

    def split_line(s, n)
      lines = []
      remaining = s

      until remaining.empty?
        width = 0
        last_break_index = nil
        break_index = nil
        chars = remaining.each_char.to_a

        chars.each_with_index do |char, idx|
          char_width = char.display_width(2)
          char_width *= ZWSCALE if char_width == 2
          if width + char_width > n
            break_index = idx
            break
          end
          width += char_width
          last_break_index = idx + 1 if breakable_char?(char)
        end

        if break_index.nil?
          lines << remaining
          break
        end

        split_index = last_break_index || break_index
        head = chars[0...split_index].join
        tail = chars[split_index..].join

        if last_break_index
          lines << head.rstrip
          remaining = tail.lstrip
        else
          lines << head
          remaining = tail
        end
      end

      lines
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
