ignore "/env/"

directories %w(carnatic makam) \
 .select{|d| Dir.exists?(d) ? d : UI.warning("Directory #{d} does not exist")}

less_options = {
  all_on_start: true,
  patterns: [/^.+\.less$/],
}

guard :less, less_options do
  less_options[:patterns].each { |pattern| watch(pattern) }
end
