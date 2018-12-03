# Gives the QTH locator with the GPS position
# by F1GBD (ADRASEC 77) on dec,2 2018 - getloc.rb v 1.00
# Opensource under GNU licence
# https://github.com/f1gbd/F1GBD

require 'gpsd_client'
require 'maidenhead'
require 'socket'
require 'json'

gpsd = GpsdClient::Gpsd.new()
gpsd.start()

# GPS ready ?
if gpsd.started?
  pos = gpsd.get_position
  maid = Maidenhead.to_maidenhead(pos[:lat], pos[:lon], precision = 5)
  puts "lat = #{pos[:lat]}, lon = #{pos[:lon]}, QTH loc = #{maid}"
end