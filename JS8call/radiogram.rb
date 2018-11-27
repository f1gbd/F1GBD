
# Automatic sending of a direct radiogram via SMTP with JS8call
# by F1GBD (ADRASEC 77) on nov,26 2018 - radiogram.rb v 1.00
# Opensource under GNU licence
# https://github.com/f1gbd/F1GBD
#
# usage on JS8call, from another station : SEND A DIRECT MESSAGE to YOURCALL 
#  %EMAIL_ADRESS@GMAIL.COM%THIS IS A TEST MESSAGE

require 'file/tail'
require 'maidenhead'

# PUT YOUR CALL STATION
STATIONCALL = "YOURCALL"
#
JS8CALL = "/home/pi/.local/share/JS8Call/save/messages/#{STATIONCALL}.txt"

 File::Tail::Logfile.open(JS8CALL) do |log|
  log.backward(1).tail do |radiogram|

  log.interval # 10
 
  if radiogram.split('%')[1] then
  date = radiogram.split('%')[0].split(' ')[0]
  time = radiogram.split('%')[0].split(' ')[1]
  adr = radiogram.split('%')[1].split(' ')[0]
  msg = radiogram.split('%')[2]

  system "printf \"Subject: Radiogramme de #{STATIONCALL} #{date} a #{time}\\n\n#{msg}\n\n*** NE PAS REPONDRE A CE MESSAGE SVP ***\" | ssmtp #{adr}\n"
  puts "Radiogram sent to : #{adr} on #{date} at #{time}"

   end
  end
 end




