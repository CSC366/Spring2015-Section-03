task default: ["data.json"]

file "data.json" => "answers" do |t|
   sh "ruby convert.rb #{t.source} > #{t.name}"
end
