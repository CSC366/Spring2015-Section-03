#!/usr/bin/env ruby
require 'json'

class Converter
   def Converter.main io
      converter = Converter.new
      io.each do |line|
         converter.process line
      end
      return converter.getQuestions
   end

   def initialize
      @questions = []
      init_parse
   end

   def getQuestions
      return @questions
   end

   def process line
      input = line.strip
      case @state
      when :start
         addQuestion input
      when :notes
         addNote input
      when :text
         addText input
      end
   end

   def addQuestion line
      if /^#/ =~ line
         # This is a new team's question section
         # We're going to ignore this for now.
      elsif not line.empty?
         @question = line
         @state = :notes
      end
   end

   def addNote line
      if /^- / =~ line
         @notes << line
      else
         @state = :text
         addText line
      end
   end

   def addText line
      if /^keys: / =~ line
         @state = :keys
         addKeys line
      elsif not /^\s*$/ =~ line
         @description << line
      else
         finishQuestion
      end
   end

   def addKeys line
      @keys = line.split[1..-1]
      finishQuestion
   end

   def finishQuestion
      @questions << {
         "Q" => @question,
         "A" => @description.join(' '),
         "keys" => @keys
      }
      init_parse
   end

   def init_parse
      @state = :start
      @notes = []
      @keys = []
      @description = []
   end
end

questions = Converter.main $<
puts JSON.generate(questions)
