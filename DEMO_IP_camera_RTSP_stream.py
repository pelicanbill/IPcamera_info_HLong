#!/usr/bin/python
# encoding: utf-8
# -*- coding: utf-8 -*-
# Python 2.7
#
# DEMO_IP_camera_RTSP_stream.py
#
# Program description: Demo RTSP communication with HLong Asia camera
# Date: Oct 2017
#
# References from web
# https://stackoverflow.com/questions/28022432/receiving-rtp-packets-after-rtsp-setup
# http://www.cs.columbia.edu/~hgs/rtsp/draft/draft-ietf-mmusic-rtsp-03.html
# https://www.csee.umbc.edu/~pmundur/courses/CMSC691C/lab5-kurose-ross.html
#
"""
A demo python code that ..
uses some code written 2015 by Sampsa Riikonen.
Done for educative/demonstrative purposes,
run with # /usr/bin/python DEMO_IP_camera_RTSP_stream.py > RTSP_output.txt
"""

import socket
import re
import time
import bitstring # if you don't have this from your linux distro, install with "pip install bitstring"
dbg = True
dbg = False

# extract the session number etc here
def split_result(recst):
	#
	pieces = recst.split('\r\n')
	if dbg: print "pieces=",pieces
	
	if len(pieces) < 3:
		return ('999', None)
	cnt = 0
	status = '888'
	sessnum = None
	streamsrc = -1
	sport = 0 # server port
	cport = 0  # client port
	if 'ERROR' in recst:
		if dbg: print "ERROR in received string"
		return(status,sessnum,cport,sport,streamsrc)
	# Transport: RTP/AVP;unicast;mode=PLAY;source=192.168.1.10;client_port=9527-0;server_port=40000-40001;ssrc=0
	for p in pieces:
		if dbg: print "p=",p	
		p1 = p.strip()		
		p2 = p1.split(':')
		if p2[0] == "Session":			
			sessnum = p2[1].strip() # session number for later
			if ';' in sessnum:
				sessall = sessnum.split(';')
				sessnum = sessall[0]
			# print "Session Number: ["+sessnum+"]"
		p3 = p1.split() # into spaces
		if cnt == 0:
			if p3[0] == "RTSP/1.0":
				status = p3[1]
		if ';' in p:
			pieces2 = p.split(';')
			for semis in pieces2:
				if dbg: print "semis=",semis
				if 'client_port=' in semis:
					cportzero = semis.split('client_port=')[1] # client_port=9527-0
					cport = cportzero.split('-')[0] # 9527
				if 'server_port=' in semis:
					sportrange = semis.split('server_port=')[1]	# 40000-40001
					sport = sportrange.split('-')[0] # 40000
				if 'ssrc=' in semis:
					streamsrc = semis.split('ssrc=')[1]	# 0
		cnt += 1
	#
	if sessnum is None:
		if dbg: print "No session number"	
		return(status,sessnum,cport,sport,streamsrc)

	if dbg: print "status=",status,"sessnum=",sessnum,"cport=",cport,"sport=",sport,"streamsrc=",streamsrc
	return(status,sessnum,cport,sport,streamsrc)
# ===========================================
#
# ************************ FOR QUICK-TESTING EDIT THIS AREA *********************************************************
ip="192.168.1.10" # IP address of your cam for socket connections
adr="rtsp://192.168.1.10:554/user=admin&password=&channel=1&stream=0.sdp?" #RTSP preamble
clientports=[9527,9530] # the client ports we are going to use for receiving video (not sure about 9530)
fname="stream.h264" # filename for dumping the stream
rn=1000 # receive this many packets
# *******************************************************************************************************************
#
#
#
#
# *********** THE MAIN PROGRAM STARTS HERE ****************

# ==============================================
# Create an TCP socket for RTSP command communication
# further reading: 
# https://docs.python.org/2.7/howto/sockets.html
# ==============================================
try:
	s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except:
	raise
print "Connecting to IP:",ip,"Port: 554...."
s.settimeout(5) #
try:	
	s.connect((ip,554)) # RTSP should peek out from port 554
except:
	raise
print "...Connected"
# ==============================================

		
# ============================================
# send OPTIONS
# ============================================
seq = 1
opts="OPTIONS "+adr+" RTSP/1.0\r\nCSeq: "+str(seq)+"\r\nRequire: implicit-play\r\nProxy-Require: gzipped-messages\r\n\r\n"
print
print "*** SENDING OPTIONS ***"
print "====>>>["+opts.strip()+"]"
s.send(opts)
print
# -----------------------
recst=s.recv(4096)
print "<<<====["+recst.strip()+"]" # OPTIONS, DESCRIBE, SETUP, TEARDOWN, GET_PARAMETER, PLAY, PAUSE
res = split_result(recst)
# print "status=",res[0],"sessnum=",res[1],"cport=",res[2],"sport=",res[3],"streamsrc=",res[4]
print
if res[0] != '200':
	print "Error:",recst
	quit()

time.sleep(2) # dont need this

# ============================================
# send DESCRIBE
# ============================================
seq += 1
dest="DESCRIBE "+adr+" RTSP/1.0\r\nCSeq: "+str(seq)+"\r\nAccept: application/sdp\r\n\r\n"
print "*** SENDING DESCRIBE ***"
print "====>>>["+dest.strip()+"]"
s.send(dest)
print
# -----------------------
recst=s.recv(4096)
print "<<<====["+recst.strip()+"]" # OPTIONS, DESCRIBE, SETUP, TEARDOWN, GET_PARAMETER, PLAY, PAUSE
res = split_result(recst)
# print "status=",res[0],"sessnum=",res[1],"cport=",res[2],"sport=",res[3],"streamsrc=",res[4]
print
if res[0] != '200':
	print "Error:",recst
	quit()

time.sleep(2) # dont need this

# ============================================
# SETUP
# ============================================
seq += 1
setu="SETUP "+adr+" RTSP/1.0\r\nCSeq: "+str(seq)+"\r\nTransport: RTP/AVP;unicast; client_port= "+str(clientports[0])+","+str(clientports[1])+"\r\n\r\n" # ;port="+str(clientports[0])+","+str(clientports[1]) RTP/UDP
print
print "*** SENDING SETUP ***"
print "====>>>["+setu.strip()+"]"
s.send(setu)
print
# -----------------------
recst=s.recv(4096)
print "<<<====["+recst.strip()+"]" # OPTIONS, DESCRIBE, SETUP, TEARDOWN, GET_PARAMETER, PLAY, PAUSE
res = split_result(recst)
# print "status=",res[0],"sessnum=",res[1],"cport=",res[2],"sport=",res[3],"streamsrc=",res[4]
print
if res[0] != '200':
	print "Error:",recst
	quit()
sessnum = res[1] # save for use in all other RTSP commands

time.sleep(2) # dont need this



# ===============================================
# Open the client port for video feed
# ===============================================
print
print "Opening sockets s1 on client port",clientports[0]
s1=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s1.bind(("", clientports[0])) # we open a port that is visible to the whole internet (the empty string "" takes care of that)
s1.settimeout(5) # if the socket is dead for 5 s., its thrown into trash
# further reading:
# https://wiki.python.org/moin/UdpCommunication
# https://pymotw.com/3/socket/multicast.html
# Now our port is open for receiving shitloads of videodata.  Give the camera the PLAY command..




# ===================================================
# PLAY
# ===================================================
seq += 1
play="PLAY "+adr+" RTSP/1.0\r\nCSeq: "+str(seq)+"\r\nSession:"+str(sessnum)+"\r\nTransport: RTP/UDP; client_port= "+str(clientports[0])+"\r\n\r\n" #
print
print "*** SENDING PLAY ***"
print "====>>>["+play.strip()+"]"
s.send(play)
print
# -----------------------
recst=s.recv(4096)
print "<<<====["+recst.strip()+"]" # OPTIONS, DESCRIBE, SETUP, TEARDOWN, GET_PARAMETER, PLAY, PAUSE
res = split_result(recst)
# print "status=",res[0],"sessnum=",res[1],"cport=",res[2],"sport=",res[3],"streamsrc=",res[4]
print
if res[0] != '200':
	print "Error:",recst
	quit()

time.sleep(2) # dont need this

# ===================================================
# GET_PARAMETER - needs parameter added
# ===================================================
'''
seq += 1
gparms="GET_PARAMETER "+adr+" RTSP/1.0\r\nCSeq: "+str(seq)+"\r\nSession:"+str(sessnum)+"\r\nContent-Type: text/rtsp-parameters\r\n\r\n"
print
print "*** SENDING GET_PARAMETER ***"
print "====>>>["+gparms.strip()+"]"
s.send(gparms)
print
# -----------------------
recst=s.recv(4096)
print "<<<====["+recst.strip()+"]" # OPTIONS, DESCRIBE, SETUP, TEARDOWN, GET_PARAMETER, PLAY, PAUSE
res = split_result(recst)
print "status=",res[0],"sessnum=",res[1],"cport=",res[2],"sport=",res[3],"streamsrc=",res[4]
print
if res[0] != '200':
	print "Error:",recst
	quit()

time.sleep(2) # dont need this
'''

# ===================================================
# PAUSE - (not for cameras perhaps)
# ===================================================
'''
seq += 1
paws="PAUSE "+adr+" RTSP/1.0\r\nCSeq: "+str(seq)+"\r\nSession:"+str(sessnum)+"\r\n\r\n"
print
print "*** SENDING PAUSE ***"
print "====>>>["+paws.strip()+"]"
s.send(paws)
print
# -----------------------
recst=s.recv(4096)
print "<<<====["+recst.strip()+"]" # OPTIONS, DESCRIBE, SETUP, TEARDOWN, GET_PARAMETER, PLAY, PAUSE
res = split_result(recst)
# print "status=",res[0],"sessnum=",res[1],"cport=",res[2],"sport=",res[3],"streamsrc=",res[4]
print
if res[0] != '200':
	print "Error:",recst
	quit()
'''



# ============================================
# now the video feed is playing from camera
# Strip headers and save the frames here
# ============================================
print
print "============================================="
print "** DUMPING VIDEO INTO FILE %s **" % (fname,)
try:
	with open(fname, 'wb') as f:
		for i in range(rn):
			try:
				recst=s1.recv(4096) # receive block from stream
				# print "read",len(recst),"bytes"
			except:
				print "stream read failure"
				f.close
				break # continue with teardown
			
			st = recst # may need to strip RTSP headers off video feed perhaps
			# print "Video block",str(i),"dumping",len(st),"bytes to file"
			f.write(st)
	print "============================================="		
except:
	print "=============================="
	print "Failure to write somehow"
	print "=============================="
	# continue with teardown to RTSP





# ============================================
# send TEARDOWN
# ============================================
seq += 1
teard="TEARDOWN "+adr+" RTSP/1.0\r\nCSeq: "+str(seq)+"\r\nSession:"+str(sessnum)+"\r\n\r\n" # 
print
print "*** SENDING TEARDOWN ***"
print "====>>>["+teard.strip()+"]"
s.send(teard)
print
# -----------------------
recst=s.recv(4096)
print "<<<====["+recst.strip()+"]" # OPTIONS, DESCRIBE, SETUP, TEARDOWN, GET_PARAMETER, PLAY, PAUSE
res = split_result(recst)
#print "status=",res[0],"sessnum=",res[1],"cport=",res[2],"sport=",res[3],"streamsrc=",res[4]
print
if res[0] != '200':
	print "Error:",recst
	quit()

# ===================================================
# finish
# ===================================================
print "======== end =========="
# close both sockets
s.close()
s1.close()
# ==============================
